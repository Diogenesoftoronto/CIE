package storage

import (
	"database/sql"
	"encoding/json"
	"errors"
	"time"

	"github.com/cie-team/cie/internal/core"
	_ "modernc.org/sqlite"
)

// SQLite persists to a SQLite database (pure Go driver).
type SQLite struct {
	db *sql.DB
}

// NewSQLite opens or creates the DB at path.
func NewSQLite(path string) (*SQLite, error) {
	dsn := "file:" + path + "?mode=rwc"
	db, err := sql.Open("sqlite", dsn)
	if err != nil {
		return nil, err
	}
	s := &SQLite{db: db}
	if err := s.migrate(); err != nil {
		_ = db.Close()
		return nil, err
	}
	return s, nil
}

func (s *SQLite) migrate() error {
	stmts := []string{
		`CREATE TABLE IF NOT EXISTS trials (
			id INTEGER PRIMARY KEY,
			policy_name TEXT NOT NULL,
			workload TEXT NOT NULL,
			metrics TEXT NOT NULL,
			score REAL NOT NULL,
			created_at TEXT NOT NULL,
			artifact_id TEXT,
			notes TEXT,
			metadata TEXT
		)`,
		`CREATE TABLE IF NOT EXISTS policies (
			name TEXT PRIMARY KEY,
			params TEXT NOT NULL,
			actions TEXT NOT NULL,
			created_at TEXT NOT NULL,
			metadata TEXT
		)`,
		`CREATE TABLE IF NOT EXISTS prompts (
			id TEXT PRIMARY KEY,
			content TEXT NOT NULL,
			description TEXT,
			tags TEXT,
			created_at TEXT NOT NULL,
			updated_at TEXT NOT NULL,
			metadata TEXT
		)`,
	}
	for _, q := range stmts {
		if _, err := s.db.Exec(q); err != nil {
			return err
		}
	}
	return nil
}

func (s *SQLite) SaveTrial(t *core.Trial) error {
	mb, _ := json.Marshal(t.Metrics)
	mtb, _ := json.Marshal(t.Metadata)
	var art sql.NullString
	if t.ArtifactID != nil {
		art.String = *t.ArtifactID
		art.Valid = true
	}
	_, err := s.db.Exec(`
		INSERT INTO trials (id, policy_name, workload, metrics, score, created_at, artifact_id, notes, metadata)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
		t.ID, t.PolicyName, t.Workload, mb, t.Score, t.CreatedAt.Format(time.RFC3339Nano),
		art, t.Notes, mtb,
	)
	return err
}

func (s *SQLite) GetTrials(limit int) ([]core.Trial, error) {
	q := `SELECT id, policy_name, workload, metrics, score, created_at, artifact_id, notes, metadata
		FROM trials ORDER BY created_at DESC`
	args := []any{}
	if limit > 0 {
		q += ` LIMIT ?`
		args = append(args, limit)
	}
	rows, err := s.db.Query(q, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []core.Trial
	for rows.Next() {
		var t core.Trial
		var mb, mtb []byte
		var art sql.NullString
		var ts string
		if err := rows.Scan(&t.ID, &t.PolicyName, &t.Workload, &mb, &t.Score, &ts, &art, &t.Notes, &mtb); err != nil {
			return nil, err
		}
		t.CreatedAt, _ = time.Parse(time.RFC3339Nano, ts)
		if art.Valid {
			v := art.String
			t.ArtifactID = &v
		}
		_ = json.Unmarshal(mb, &t.Metrics)
		_ = json.Unmarshal(mtb, &t.Metadata)
		out = append(out, t)
	}
	return out, rows.Err()
}

func (s *SQLite) SavePolicy(p *core.Policy) error {
	pb, _ := json.Marshal(p.Params)
	ab, _ := json.Marshal(p.Actions)
	mb, _ := json.Marshal(p.Metadata)
	_, err := s.db.Exec(`
		INSERT OR REPLACE INTO policies (name, params, actions, created_at, metadata)
		VALUES (?, ?, ?, ?, ?)`,
		p.Name, pb, ab, p.CreatedAt.Format(time.RFC3339Nano), mb,
	)
	return err
}

func (s *SQLite) GetPolicies() ([]core.Policy, error) {
	rows, err := s.db.Query(`SELECT name, params, actions, created_at, metadata FROM policies`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []core.Policy
	for rows.Next() {
		var p core.Policy
		var pb, ab, mb []byte
		var ts string
		if err := rows.Scan(&p.Name, &pb, &ab, &ts, &mb); err != nil {
			return nil, err
		}
		p.CreatedAt, _ = time.Parse(time.RFC3339Nano, ts)
		_ = json.Unmarshal(pb, &p.Params)
		_ = json.Unmarshal(ab, &p.Actions)
		_ = json.Unmarshal(mb, &p.Metadata)
		out = append(out, p)
	}
	return out, rows.Err()
}

func (s *SQLite) SavePrompt(p *core.Prompt) error {
	tb, _ := json.Marshal(p.Tags)
	mb, _ := json.Marshal(p.Metadata)
	_, err := s.db.Exec(`
		INSERT OR REPLACE INTO prompts (id, content, description, tags, created_at, updated_at, metadata)
		VALUES (?, ?, ?, ?, ?, ?, ?)`,
		p.ID, p.Content, p.Description, tb,
		p.CreatedAt.Format(time.RFC3339Nano), p.UpdatedAt.Format(time.RFC3339Nano), mb,
	)
	return err
}

func (s *SQLite) GetPrompts() ([]core.Prompt, error) {
	rows, err := s.db.Query(`SELECT id, content, description, tags, created_at, updated_at, metadata FROM prompts`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []core.Prompt
	for rows.Next() {
		var p core.Prompt
		var tb, mb []byte
		var cts, uts string
		if err := rows.Scan(&p.ID, &p.Content, &p.Description, &tb, &cts, &uts, &mb); err != nil {
			return nil, err
		}
		p.CreatedAt, _ = time.Parse(time.RFC3339Nano, cts)
		p.UpdatedAt, _ = time.Parse(time.RFC3339Nano, uts)
		_ = json.Unmarshal(tb, &p.Tags)
		_ = json.Unmarshal(mb, &p.Metadata)
		out = append(out, p)
	}
	return out, rows.Err()
}

func (s *SQLite) DeletePrompt(id string) error {
	_, err := s.db.Exec(`DELETE FROM prompts WHERE id = ?`, id)
	return err
}

func (s *SQLite) ClearAll() error {
	for _, t := range []string{"trials", "policies", "prompts"} {
		if _, err := s.db.Exec("DELETE FROM " + t); err != nil {
			return err
		}
	}
	return nil
}

func (s *SQLite) Close() error {
	if s.db == nil {
		return nil
	}
	return s.db.Close()
}

// ErrNotFound for callers.
var ErrNotFound = errors.New("not found")

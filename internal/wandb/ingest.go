package wandb

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

// HistoryRow is one parsed wandb history line.
type HistoryRow struct {
	Step    float64
	Metrics map[string]float64
	Raw     map[string]any
}

// ResolveRunPath returns an absolute run directory.
// order: explicitPath, $CIE_WANDB_RUN, ./wandb/latest-run
func ResolveRunPath(explicit string) (string, error) {
	p := strings.TrimSpace(explicit)
	if p == "" {
		p = os.Getenv("CIE_WANDB_RUN")
	}
	if p == "" {
		p = filepath.Join("wandb", "latest-run")
	}
	abs, err := filepath.Abs(p)
	if err != nil {
		return "", err
	}
	st, err := os.Stat(abs)
	if err != nil {
		return "", fmt.Errorf("wandb run path %q: %w", abs, err)
	}
	if !st.IsDir() {
		return "", fmt.Errorf("wandb run path %q is not a directory", abs)
	}
	return abs, nil
}

// LoadHistoryRows reads files/wandb-history.jsonl from a W&B offline run.
func LoadHistoryRows(runDir string) ([]HistoryRow, error) {
	path := filepath.Join(runDir, "files", "wandb-history.jsonl")
	f, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("open %s: %w", path, err)
	}
	defer f.Close()
	var rows []HistoryRow
	sc := bufio.NewScanner(f)
	// Large metric lines
	buf := make([]byte, 0, 64*1024)
	sc.Buffer(buf, 1024*1024)
	line := 0
	for sc.Scan() {
		line++
		raw := map[string]any{}
		if err := json.Unmarshal(sc.Bytes(), &raw); err != nil {
			continue
		}
		step := 0.0
		if v, ok := raw["_step"]; ok {
			step = anyToFloat(v)
		}
		metrics := map[string]float64{}
		for k, v := range raw {
			if k == "" || k[0] == '_' {
				continue
			}
			fv, ok := toFloatMetric(v)
			if !ok {
				continue
			}
			metrics[k] = fv
		}
		if len(metrics) == 0 {
			continue
		}
		rows = append(rows, HistoryRow{Step: step, Metrics: metrics, Raw: raw})
	}
	if err := sc.Err(); err != nil {
		return nil, err
	}
	if len(rows) == 0 {
		return nil, fmt.Errorf("no metric rows parsed from %s", path)
	}
	return rows, nil
}

func anyToFloat(v any) float64 {
	f, _ := toFloatMetric(v)
	return f
}

func toFloatMetric(v any) (float64, bool) {
	switch x := v.(type) {
	case float64:
		return x, true
	case float32:
		return float64(x), true
	case int:
		return float64(x), true
	case int64:
		return float64(x), true
	case json.Number:
		f, err := x.Float64()
		return f, err == nil
	case string:
		f, err := strconv.ParseFloat(strings.TrimSpace(x), 64)
		return f, err == nil
	default:
		return 0, false
	}
}

// RowDedupKey builds a stable id for deduplicating ingested rows.
func RowDedupKey(r HistoryRow, index int) string {
	if r.Step != 0 {
		return "step:" + strconv.FormatFloat(r.Step, 'f', -1, 64)
	}
	return "idx:" + strconv.Itoa(index)
}

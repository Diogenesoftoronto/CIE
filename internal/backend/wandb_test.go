package backend

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/cie-team/cie/internal/config"
)

func TestIngestWandBRun(t *testing.T) {
	dir := t.TempDir()
	files := filepath.Join(dir, "files")
	if err := os.MkdirAll(files, 0o755); err != nil {
		t.Fatal(err)
	}
	jsonl := filepath.Join(files, "wandb-history.jsonl")
	if err := os.WriteFile(jsonl, []byte(`{"_step":0,"latency_p95":120,"task_success":0.9,"cost_per_req":0.001}
`), 0o644); err != nil {
		t.Fatal(err)
	}
	cfg := config.Default()
	cfg.Storage.Backend = "memory"
	cfg.ExpandPaths()
	b, err := New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	defer b.Close()
	got, err := b.IngestWandBRun(dir)
	if err != nil {
		t.Fatal(err)
	}
	if len(got) != 1 {
		t.Fatalf("ingested %d", len(got))
	}
	if len(b.Trials) != 1 {
		t.Fatalf("trials %d", len(b.Trials))
	}
	if b.Trials[0].PolicyName != "wandb-import" {
		t.Fatal(b.Trials[0].PolicyName)
	}
	_, err = b.IngestWandBRun(dir)
	if err != nil {
		t.Fatal(err)
	}
	if len(b.Trials) != 1 {
		t.Fatalf("duplicate ingest should skip, got %d trials", len(b.Trials))
	}
}

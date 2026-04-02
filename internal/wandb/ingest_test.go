package wandb

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadHistoryRows(t *testing.T) {
	dir := t.TempDir()
	files := filepath.Join(dir, "files")
	if err := os.MkdirAll(files, 0o755); err != nil {
		t.Fatal(err)
	}
	jsonl := filepath.Join(files, "wandb-history.jsonl")
	content := `{"_step":0,"loss":1.5,"accuracy":0.2,"_runtime":1}
{"_step":1,"loss":1.1,"accuracy":0.55}
`
	if err := os.WriteFile(jsonl, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	rows, err := LoadHistoryRows(dir)
	if err != nil {
		t.Fatal(err)
	}
	if len(rows) != 2 {
		t.Fatalf("rows %d", len(rows))
	}
	if rows[0].Metrics["loss"] != 1.5 || rows[1].Metrics["accuracy"] != 0.55 {
		t.Fatalf("%v %v", rows[0].Metrics, rows[1].Metrics)
	}
}

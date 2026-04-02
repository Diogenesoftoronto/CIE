package backend

import (
	"fmt"
	"path/filepath"
	"time"

	"github.com/cie-team/cie/internal/core"
	"github.com/cie-team/cie/internal/wandb"
)

// IngestWandBRun imports metric rows from a local W&B run dir as trials.
func (b *Backend) IngestWandBRun(path string) ([]core.Trial, error) {
	runDir, err := wandb.ResolveRunPath(path)
	if err != nil {
		return nil, err
	}
	rows, err := wandb.LoadHistoryRows(runDir)
	if err != nil {
		return nil, err
	}
	existing := map[string]struct{}{}
	for i := range b.Trials {
		t := &b.Trials[i]
		if t.Metadata == nil {
			continue
		}
		if id, ok := t.Metadata["wandb_row_id"].(string); ok && id != "" {
			existing[id] = struct{}{}
		}
	}
	var ingested []core.Trial
	for i, row := range rows {
		key := wandb.RowDedupKey(row, i)
		if _, ok := existing[key]; ok {
			continue
		}
		score := b.Score(row.Metrics)
		b.trialID++
		tr := core.Trial{
			ID:         b.trialID,
			PolicyName: "wandb-import",
			Metrics:    row.Metrics,
			Score:      score,
			Workload:   "wandb:" + filepath.Base(runDir),
			CreatedAt:  time.Now().UTC(),
			Metadata: map[string]any{
				"source":        "wandb",
				"wandb_run_dir": runDir,
				"wandb_row_id":  key,
				"wandb_step":    row.Step,
			},
		}
		if err := b.stor.SaveTrial(&tr); err != nil {
			return ingested, fmt.Errorf("save trial: %w", err)
		}
		b.Trials = append(b.Trials, tr)
		ingested = append(ingested, tr)
		existing[key] = struct{}{}
	}
	if len(ingested) > 0 {
		b.rebuildPareto()
	}
	return ingested, nil
}

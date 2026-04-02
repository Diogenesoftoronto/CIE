package backend

import (
	"time"

	"github.com/cie-team/cie/internal/core"
)

// SeedDemo adds synthetic trials for TUI demos (memory backend recommended).
func SeedDemo(b *Backend, scenario string) {
	_ = scenario
	now := time.Now().UTC()
	demos := []core.Trial{
		{
			PolicyName: "HillClimb", Workload: "MicroEval:basic",
			Score: 0.42,
			Metrics: map[string]float64{
				"latency_p95": 120, "cost_per_req": 0.0012, "task_success": 0.91,
				"context_usage": 0.3, "tool_error_rate": 0.02,
			},
			CreatedAt: now.Add(-2 * time.Hour),
		},
		{
			PolicyName: "RandomProbe", Workload: "TextEval:classify",
			Score: 0.55,
			Metrics: map[string]float64{
				"latency_p95": 200, "cost_per_req": 0.002, "task_success": 0.82,
				"context_usage": 0.45, "tool_error_rate": 0.04,
				"text_similarity": 0.78,
			},
			CreatedAt: now.Add(-30 * time.Minute),
		},
	}
	for _, dt := range demos {
		b.trialID++
		t := dt
		t.ID = b.trialID
		b.Trials = append(b.Trials, t)
		_ = b.stor.SaveTrial(&b.Trials[len(b.Trials)-1])
	}
	b.rebuildPareto()
}

package backend

import (
	"testing"

	"github.com/cie-team/cie/internal/config"
	"github.com/cie-team/cie/internal/core"
)

func TestScoreAndPareto(t *testing.T) {
	cfg := config.Default()
	cfg.Storage.Backend = "memory"
	b, err := New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	defer b.Close()

	p := b.Opts[1].Propose(nil)
	if p == nil || p.Name == "" {
		t.Fatal("expected policy")
	}
	tr, err := b.EvalPolicy(p, 0)
	if err != nil {
		t.Fatal(err)
	}
	if tr.ID != 1 {
		t.Fatalf("trial id %d", tr.ID)
	}
	if len(b.Pareto) < 1 {
		t.Fatal("expected pareto")
	}
}

func TestAdoptGuardrails(t *testing.T) {
	cfg := config.Default()
	cfg.Storage.Backend = "memory"
	b, err := New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	defer b.Close()

	b.Trials = append(b.Trials, core.Trial{
		ID: 1, PolicyName: "X", Workload: "w",
		Metrics: map[string]float64{
			"latency_p95":     100,
			"cost_per_req":    0.001,
			"task_success":    0.5,
			"tool_error_rate": 0.01,
		},
		Score: 0.1,
	})
	if b.AdoptPolicy(1) {
		t.Fatal("should fail success guardrail")
	}
}

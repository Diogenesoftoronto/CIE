package backend

import (
	"math"
	"slices"
	"testing"

	"github.com/cie-team/cie/internal/config"
	"github.com/cie-team/cie/internal/core"
	"pgregory.net/rapid"
)

func testConfigMemory(t *testing.T) *config.Config {
	t.Helper()
	cfg := config.Default()
	cfg.Storage.Backend = "memory"
	cfg.Evaluation.DefaultEvaluator = "mock"
	cfg.ExpandPaths()
	return cfg
}

func TestProperty_OptimizeLoopAddsTrials(t *testing.T) {
	rapid.Check(t, func(rt *rapid.T) {
		n := rapid.IntRange(1, 24).Draw(rt, "n")
		opt := rapid.IntRange(0, 1).Draw(rt, "optimizer")
		wl := rapid.IntRange(0, 4).Draw(rt, "workload")

		b, err := New(testConfigMemory(t))
		if err != nil {
			rt.Fatal(err)
		}
		defer b.Close()

		for i := 0; i < n; i++ {
			pol, err := b.ProposeOnce(opt)
			if err != nil {
				rt.Fatal(err)
			}
			if pol == nil || pol.Name == "" {
				rt.Fatalf("empty policy")
			}
			tr, err := b.EvalPolicy(pol, wl)
			if err != nil {
				rt.Fatal(err)
			}
			if math.IsNaN(tr.Score) || math.IsInf(tr.Score, 0) {
				rt.Fatalf("bad score %v", tr.Score)
			}
		}
		if len(b.Trials) != n {
			rt.Fatalf("trials %d want %d", len(b.Trials), n)
		}
		idSet := map[int]bool{}
		for _, tr := range b.Trials {
			if idSet[tr.ID] {
				rt.Fatalf("duplicate trial id %d", tr.ID)
			}
			idSet[tr.ID] = true
		}
	})
}

func TestProperty_ParetoIsNonDominatedFront(t *testing.T) {
	rapid.Check(t, func(rt *rapid.T) {
		n := rapid.IntRange(1, 20).Draw(rt, "n")
		b, err := New(testConfigMemory(t))
		if err != nil {
			rt.Fatal(err)
		}
		defer b.Close()
		for i := 0; i < n; i++ {
			pol, err := b.ProposeOnce(rapid.IntRange(0, 1).Draw(rt, "o"))
			if err != nil {
				rt.Fatal(err)
			}
			_, err = b.EvalPolicy(pol, rapid.IntRange(0, 4).Draw(rt, "w"))
			if err != nil {
				rt.Fatal(err)
			}
		}
		assertParetoConsistent(rt, b)
	})
}

func assertParetoConsistent(rt *rapid.T, b *Backend) {
	rt.Helper()
	for _, pt := range b.Pareto {
		for _, other := range b.Trials {
			if other.ID == pt.ID {
				continue
			}
			if dominates(&other, &pt) {
				rt.Fatalf("Pareto trial %d dominated by trial %d", pt.ID, other.ID)
			}
		}
	}
	seen := map[int]struct{}{}
	for _, pt := range b.Pareto {
		if _, ok := seen[pt.ID]; ok {
			rt.Fatalf("duplicate pareto id %d", pt.ID)
		}
		seen[pt.ID] = struct{}{}
		if !slices.ContainsFunc(b.Trials, func(trial core.Trial) bool { return trial.ID == pt.ID }) {
			rt.Fatalf("pareto id %d not in trials", pt.ID)
		}
	}
}

func TestProperty_ScoreIsFiniteForRandomMetrics(t *testing.T) {
	rapid.Check(t, func(rt *rapid.T) {
		cfg := testConfigMemory(t)
		b, err := New(cfg)
		if err != nil {
			rt.Fatal(err)
		}
		defer b.Close()
		m := map[string]float64{
			"latency_p95":     rapid.Float64Range(0, 5000).Draw(rt, "latency_p95"),
			"cost_per_req":    rapid.Float64Range(0, 0.1).Draw(rt, "cost_per_req"),
			"task_success":    rapid.Float64Range(0, 1).Draw(rt, "task_success"),
			"context_usage":   rapid.Float64Range(0, 1).Draw(rt, "context_usage"),
			"tool_error_rate": rapid.Float64Range(0, 1).Draw(rt, "tool_error_rate"),
		}
		s := b.Score(m)
		if math.IsNaN(s) || math.IsInf(s, 0) {
			rt.Fatalf("score %v", s)
		}
	})
}

func TestProperty_ReloadKeepsTrials(t *testing.T) {
	rapid.Check(t, func(rt *rapid.T) {
		n := rapid.IntRange(1, 12).Draw(rt, "n")
		b, err := New(testConfigMemory(t))
		if err != nil {
			rt.Fatal(err)
		}
		defer b.Close()
		for i := 0; i < n; i++ {
			pol, _ := b.ProposeOnce(0)
			_, err = b.EvalPolicy(pol, 0)
			if err != nil {
				rt.Fatal(err)
			}
		}
		before := len(b.Trials)
		if err := b.Reload(); err != nil {
			rt.Fatal(err)
		}
		if len(b.Trials) != before {
			rt.Fatalf("reload len %d want %d", len(b.Trials), before)
		}
		assertParetoConsistent(rt, b)
	})
}

func TestProperty_JSONPersistenceRoundTrip(t *testing.T) {
	rapid.Check(t, func(rt *rapid.T) {
		dir := t.TempDir()
		cfg := config.Default()
		cfg.Storage.Backend = "json"
		cfg.Storage.ExperimentsDir = dir
		cfg.Evaluation.DefaultEvaluator = "mock"
		cfg.ExpandPaths()

		n := rapid.IntRange(1, 10).Draw(rt, "n")
		b1, err := New(cfg)
		if err != nil {
			rt.Fatal(err)
		}
		for i := 0; i < n; i++ {
			pol, _ := b1.ProposeOnce(0)
			_, err = b1.EvalPolicy(pol, 0)
			if err != nil {
				rt.Fatal(err)
			}
		}
		_ = b1.Close()

		b2, err := New(cfg)
		if err != nil {
			rt.Fatal(err)
		}
		defer b2.Close()
		if len(b2.Trials) != n {
			rt.Fatalf("reopen trials %d want %d", len(b2.Trials), n)
		}
		assertParetoConsistent(rt, b2)
	})
}

func TestProperty_AdoptRespectsGuardrails(t *testing.T) {
	rapid.Check(t, func(rt *rapid.T) {
		cfg := testConfigMemory(t)
		b, err := New(cfg)
		if err != nil {
			rt.Fatal(err)
		}
		defer b.Close()

		lat := rapid.Float64Range(0, cfg.Evaluation.MaxLatencyP95).Draw(rt, "lat")
		succ := rapid.Float64Range(cfg.Evaluation.MinTaskSuccessRate, 1.0).Draw(rt, "succ")
		errRate := rapid.Float64Range(0, cfg.Evaluation.MaxToolErrorRate).Draw(rt, "err")

		b.Trials = append(b.Trials, core.Trial{
			ID:         4242,
			PolicyName: "Synthetic",
			Workload:   "w",
			Score:      0,
			Metrics: map[string]float64{
				"latency_p95":     lat,
				"cost_per_req":    0.001,
				"task_success":    succ,
				"context_usage":   0.2,
				"tool_error_rate": errRate,
			},
		})
		b.rebuildPareto()
		if !b.AdoptPolicy(4242) {
			rt.Fatal("expected adopt success")
		}
		if b.ActivePolicy == nil || b.ActivePolicy.Name == "" {
			rt.Fatal("missing active policy")
		}

		b.ActivePolicy = nil
		b.Trials = nil

		b.Trials = append(b.Trials, core.Trial{
			ID: 1, PolicyName: "Bad", Workload: "w",
			Metrics: map[string]float64{
				"latency_p95":     cfg.Evaluation.MaxLatencyP95 + 1,
				"cost_per_req":    0.001,
				"task_success":    1,
				"tool_error_rate": 0,
			},
		})
		if b.AdoptPolicy(1) {
			rt.Fatal("expected adopt failure on latency")
		}
	})
}

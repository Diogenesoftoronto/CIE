package evaluator

import (
	"math"
	"math/rand/v2"

	"github.com/cie-team/cie/internal/config"
	"github.com/cie-team/cie/internal/core"
)

// Mock generates realistic synthetic metrics.
type Mock struct {
	rng   *rand.Rand
	cfg   *config.Config
	count int
}

// NewMock creates a seeded mock evaluator.
func NewMock(seed int64, cfg *config.Config) *Mock {
	src := rand.NewPCG(uint64(seed), uint64(seed)^0x9e3779b97f4a7c15)
	return &Mock{rng: rand.New(src), cfg: cfg}
}

func (m *Mock) Name() string { return "mock" }

func (m *Mock) SupportedMetrics() []string {
	return []string{
		"latency_p95", "cost_per_req", "task_success", "context_usage", "tool_error_rate",
		"throughput", "memory_usage", "cpu_usage",
	}
}

func (m *Mock) ValidateWorkload(_ *core.Workload) bool { return true }

func (m *Mock) Run(policy *core.Policy, workload *core.Workload) (map[string]float64, error) {
	m.count++
	name := workload.Name
	r := m.rng

	var lat, cost, succ, thr float64
	switch {
	case containsFold(name, "micro"):
		lat = r.Float64()*150 + 50
		cost = r.Float64()*0.0009 + 0.0001
		succ = r.Float64()*0.13 + 0.85
		thr = r.Float64()*400 + 100
	case containsFold(name, "macro"):
		lat = r.Float64()*800 + 200
		cost = r.Float64()*0.009 + 0.001
		succ = r.Float64()*0.2 + 0.75
		thr = r.Float64()*90 + 10
	case containsFold(name, "synthetic"):
		lat = r.Float64()*300 + 100
		cost = r.Float64()*0.002 + 0.0005
		succ = r.Float64()*0.25 + 0.7
		thr = r.Float64()*200 + 50
	default:
		lat = r.Float64()*500 + 80
		cost = r.Float64()*0.003 + 0.0003
		succ = r.Float64()*0.3 + 0.65
		thr = r.Float64()*150 + 40
	}

	// Policy-shaped adjustments (deterministic-ish via params)
	if v, ok := floatParam(policy.Params, "temperature"); ok {
		lat *= 0.9 + v*0.2
		succ *= 1.05 - v*0.1
	}
	if v, ok := floatParam(policy.Params, "max_tokens"); ok {
		cost += v * 1e-6
		lat += v * 0.02
	}
	if v, ok := floatParam(policy.Params, "prune_ratio"); ok {
		succ *= 1.0 - v*0.05
		lat *= 1.0 - v*0.15
	}

	ctx := r.Float64()*0.4 + 0.2
	errRate := math.Max(0, 1.0-succ*1.1+r.Float64()*0.02)
	mem := 0.25 + 0.1*r.Float64() + 0.02*float64(len(policy.Params))
	cpu := math.Min(0.95, 0.35+0.04*r.Float64()*float64(1+len(policy.Name)))

	return map[string]float64{
		"latency_p95":     lat,
		"cost_per_req":    cost,
		"task_success":    clamp01(succ),
		"context_usage":   ctx,
		"tool_error_rate": clamp01(errRate),
		"throughput":      thr,
		"memory_usage":    mem,
		"cpu_usage":       cpu,
	}, nil
}

func containsFold(s, sub string) bool {
	return len(s) >= len(sub) && (indexFold(s, sub) >= 0)
}

func indexFold(s, sub string) int {
	// minimal case-insensitive contains
Outer:
	for i := 0; i+len(sub) <= len(s); i++ {
		for j := 0; j < len(sub); j++ {
			c1, c2 := s[i+j], sub[j]
			if c1 >= 'A' && c1 <= 'Z' {
				c1 += 'a' - 'A'
			}
			if c2 >= 'A' && c2 <= 'Z' {
				c2 += 'a' - 'A'
			}
			if c1 != c2 {
				continue Outer
			}
		}
		return i
	}
	return -1
}

func floatParam(m map[string]any, k string) (float64, bool) {
	if m == nil {
		return 0, false
	}
	v, ok := m[k]
	if !ok {
		return 0, false
	}
	switch x := v.(type) {
	case float64:
		return x, true
	case int:
		return float64(x), true
	case int64:
		return float64(x), true
	default:
		return 0, false
	}
}

func clamp01(x float64) float64 {
	return math.Max(0, math.Min(1, x))
}

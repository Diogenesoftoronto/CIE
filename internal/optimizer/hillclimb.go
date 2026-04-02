package optimizer

import (
	"fmt"
	"math/rand/v2"
	"time"

	"github.com/cie-team/cie/internal/core"
)

// HillClimb perturbs numeric policy parameters and keeps improving directions.
type HillClimb struct {
	stepSize      float64
	maxStagnation int
	rng           *rand.Rand
	ranges        map[string]paramRange
	current       map[string]any
	best          map[string]any
	bestScore     *float64
	stagnation    int
	iter          int
}

type paramRange struct {
	min, max float64
	isInt    bool
}

// NewHillClimb creates a hill climbing optimizer.
func NewHillClimb(step float64, maxStagn int) *HillClimb {
	if step <= 0 {
		step = 0.1
	}
	if maxStagn <= 0 {
		maxStagn = 10
	}
	src := rand.NewPCG(uint64(time.Now().UnixNano()), 0xdecafbad)
	h := &HillClimb{
		stepSize:      step,
		maxStagnation: maxStagn,
		rng:           rand.New(src),
		ranges:        defaultRanges(),
	}
	h.Reset()
	return h
}

func defaultRanges() map[string]paramRange {
	return map[string]paramRange{
		"prune_ratio":   {0, 0.8, false},
		"batch_size":    {1, 32, true},
		"temperature":   {0.1, 1.0, false},
		"max_tokens":    {100, 2000, true},
		"learning_rate": {0.001, 0.1, false},
		"dropout_rate":  {0, 0.5, false},
	}
}

func (h *HillClimb) Name() string { return "HillClimb" }

func (h *HillClimb) Reset() {
	h.current = randomParams(h.rng, h.ranges)
	h.best = cloneMap(h.current)
	h.bestScore = nil
	h.stagnation = 0
	h.iter = 0
}

func (h *HillClimb) GetState() map[string]any {
	return map[string]any{
		"iteration":        h.iter,
		"stagnation_count": h.stagnation,
		"step_size":        h.stepSize,
		"max_stagnation":   h.maxStagnation,
	}
}

func (h *HillClimb) Propose(_ map[string]any) *core.Policy {
	h.iter++
	p := h.perturb()
	artifact := fmt.Sprintf("hillclimb-%d-%d", time.Now().UnixMilli(), h.iter)
	p["artifact"] = artifact
	p["iteration"] = float64(h.iter)
	p["step_size"] = h.stepSize
	p["stagnation_count"] = float64(h.stagnation)
	return &core.Policy{
		Name:      h.Name(),
		Params:    p,
		Actions:   actionsFromParams(p),
		CreatedAt: time.Now().UTC(),
		Metadata: map[string]any{
			"optimizer": h.Name(),
		},
	}
}

func (h *HillClimb) Observe(policy *core.Policy, metrics map[string]float64) {
	score := WeightedObjectiveScore(metrics)
	if h.bestScore == nil || score < *h.bestScore {
		h.bestScore = &score
		h.best = cloneMap(policy.Params)
		h.stagnation = 0
	} else {
		h.stagnation++
		if h.stagnation >= h.maxStagnation {
			h.current = randomParams(h.rng, h.ranges)
			h.stagnation = 0
		} else {
			h.current = cloneMap(h.best)
		}
	}
}

func (h *HillClimb) perturb() map[string]any {
	out := cloneMap(h.current)
	keys := make([]string, 0, len(h.ranges))
	for k := range h.ranges {
		keys = append(keys, k)
	}
	if len(keys) == 0 {
		return out
	}
	k := keys[h.rng.IntN(len(keys))]
	pr := h.ranges[k]
	delta := h.stepSize * (pr.max - pr.min)
	if pr.isInt {
		v := asFloat(out[k])
		step := float64(h.rng.IntN(3) - 1)
		v += step * max64(1, delta/10)
		iv := intclamp(int(v+0.5), int(pr.min), int(pr.max))
		out[k] = float64(iv)
		return out
	}
	v := asFloat(out[k])
	v += (h.rng.Float64()*2 - 1) * delta
	out[k] = clamp(v, pr.min, pr.max)
	return out
}

func randomParams(rng *rand.Rand, ranges map[string]paramRange) map[string]any {
	out := map[string]any{}
	for k, pr := range ranges {
		if pr.isInt {
			out[k] = float64(rng.IntN(int(pr.max-pr.min+1)) + int(pr.min))
		} else {
			out[k] = pr.min + rng.Float64()*(pr.max-pr.min)
		}
	}
	return out
}

func cloneMap(m map[string]any) map[string]any {
	if m == nil {
		return map[string]any{}
	}
	out := make(map[string]any, len(m))
	for k, v := range m {
		out[k] = v
	}
	return out
}

func asFloat(v any) float64 {
	switch x := v.(type) {
	case float64:
		return x
	case int:
		return float64(x)
	case int64:
		return float64(x)
	default:
		return 0
	}
}

func clamp(v, low, high float64) float64 {
	if v < low {
		return low
	}
	if v > high {
		return high
	}
	return v
}

func intclamp(v, low, high int) int {
	if v < low {
		return low
	}
	if v > high {
		return high
	}
	return v
}

func max64(a, b float64) float64 {
	if a > b {
		return a
	}
	return b
}

func actionsFromParams(p map[string]any) []string {
	return []string{
		fmt.Sprintf("tune.prune(%v)", p["prune_ratio"]),
		fmt.Sprintf("tune.temperature(%v)", p["temperature"]),
		fmt.Sprintf("tune.max_tokens(%v)", p["max_tokens"]),
	}
}

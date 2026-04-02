package optimizer

import (
	"github.com/cie-team/cie/internal/config"
	"github.com/cie-team/cie/internal/core"
)

// Optimizer proposes policies and learns from metrics.
type Optimizer interface {
	Name() string
	Propose(state map[string]any) *core.Policy
	Observe(policy *core.Policy, metrics map[string]float64)
	GetState() map[string]any
	Reset()
}

// NewDefaults returns built-in optimizers (HillClimb + RandomProbe).
func NewDefaults(cfg *config.Config) []Optimizer {
	if cfg == nil {
		cfg = &config.Config{}
	}
	step := cfg.Optimization.StepSize
	if step <= 0 {
		step = 0.1
	}
	stag := cfg.Optimization.MaxStagnation
	if stag <= 0 {
		stag = 10
	}
	out := []Optimizer{
		NewHillClimb(step, stag),
		NewRandomProbe(),
		NewOpenAIPolicyOptimizer(cfg),
	}
	return out
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

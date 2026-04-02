package evaluator

import (
	"slices"

	"github.com/cie-team/cie/internal/config"
	"github.com/cie-team/cie/internal/core"
)

// Evaluator scores a policy on a workload.
type Evaluator interface {
	Name() string
	Run(policy *core.Policy, workload *core.Workload) (map[string]float64, error)
	SupportedMetrics() []string
	ValidateWorkload(w *core.Workload) bool
}

// Factory builds an evaluator from config.
type Factory func(cfg *config.Config) (Evaluator, error)

var registry = map[string]Factory{
	"mock":       func(cfg *config.Config) (Evaluator, error) { return NewMock(42, cfg), nil },
	"text-match": func(cfg *config.Config) (Evaluator, error) { return NewTextMatch(cfg), nil },
}

// Register adds a factory (for extensions).
func Register(name string, f Factory) {
	registry[name] = f
}

// Names returns registered evaluator slugs.
func Names() []string {
	out := make([]string, 0, len(registry))
	for k := range registry {
		out = append(out, k)
	}
	slices.Sort(out)
	return out
}

// Get returns an evaluator by slug.
func Get(slug string, cfg *config.Config) (Evaluator, error) {
	f, ok := registry[slug]
	if !ok {
		return nil, ErrUnknown(slug)
	}
	return f(cfg)
}

package storage

import (
	"cmp"
	"slices"

	"github.com/cie-team/cie/internal/core"
)

// Memory is an in-memory store (tests / ephemeral runs).
type Memory struct {
	trials   []core.Trial
	policies []core.Policy
	prompts  []core.Prompt
}

// NewMemory returns an empty memory backend.
func NewMemory() *Memory {
	return &Memory{}
}

func (m *Memory) SaveTrial(t *core.Trial) error {
	m.trials = append(m.trials, *t)
	return nil
}

func (m *Memory) GetTrials(limit int) ([]core.Trial, error) {
	cp := slices.Clone(m.trials)
	slices.SortFunc(cp, func(a, b core.Trial) int {
		return cmp.Compare(b.CreatedAt.UnixNano(), a.CreatedAt.UnixNano())
	})
	if limit > 0 && len(cp) > limit {
		cp = cp[:limit]
	}
	return cp, nil
}

func (m *Memory) SavePolicy(p *core.Policy) error {
	out := m.policies[:0]
	for _, x := range m.policies {
		if x.Name != p.Name {
			out = append(out, x)
		}
	}
	out = append(out, *p)
	m.policies = out
	return nil
}

func (m *Memory) GetPolicies() ([]core.Policy, error) {
	return slices.Clone(m.policies), nil
}

func (m *Memory) SavePrompt(p *core.Prompt) error {
	var pr []core.Prompt
	for _, x := range m.prompts {
		if x.ID != p.ID {
			pr = append(pr, x)
		}
	}
	pr = append(pr, *p)
	m.prompts = pr
	return nil
}

func (m *Memory) GetPrompts() ([]core.Prompt, error) {
	return slices.Clone(m.prompts), nil
}

func (m *Memory) DeletePrompt(id string) error {
	m.prompts = slices.DeleteFunc(m.prompts, func(p core.Prompt) bool { return p.ID == id })
	return nil
}

func (m *Memory) ClearAll() error {
	m.trials = nil
	m.policies = nil
	m.prompts = nil
	return nil
}

func (m *Memory) Close() error { return nil }

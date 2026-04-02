package storage

import (
	"github.com/cie-team/cie/internal/core"
)

// Backend persists trials, policies, and prompts.
type Backend interface {
	SaveTrial(t *core.Trial) error
	GetTrials(limit int) ([]core.Trial, error)
	SavePolicy(p *core.Policy) error
	GetPolicies() ([]core.Policy, error)
	SavePrompt(p *core.Prompt) error
	GetPrompts() ([]core.Prompt, error)
	DeletePrompt(id string) error
	ClearAll() error
	Close() error
}

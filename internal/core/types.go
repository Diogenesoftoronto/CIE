package core

import (
	"time"
)

// Policy is a proposed optimization configuration.
type Policy struct {
	Name      string         `json:"name"`
	Params    map[string]any `json:"params"`
	Actions   []string       `json:"actions"`
	CreatedAt time.Time      `json:"created_at"`
	Metadata  map[string]any `json:"metadata"`
}

// Trial is one evaluation result.
type Trial struct {
	ID         int                `json:"id"`
	PolicyName string             `json:"policy_name"`
	Metrics    map[string]float64 `json:"metrics"`
	Score      float64            `json:"score"`
	Workload   string             `json:"workload"`
	CreatedAt  time.Time          `json:"created_at"`
	ArtifactID *string            `json:"artifact_id,omitempty"`
	Notes      string             `json:"notes"`
	Metadata   map[string]any     `json:"metadata"`
}

// Workload defines an evaluation workload.
type Workload struct {
	Name        string         `json:"name"`
	Items       int            `json:"items"`
	Description string         `json:"description,omitempty"`
	Config      map[string]any `json:"config,omitempty"`
	Tags        []string       `json:"tags,omitempty"`
}

// Prompt is a stored prompt template.
type Prompt struct {
	ID          string         `json:"id"`
	Content     string         `json:"content"`
	Description string         `json:"description,omitempty"`
	Tags        []string       `json:"tags,omitempty"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
	Metadata    map[string]any `json:"metadata,omitempty"`
}

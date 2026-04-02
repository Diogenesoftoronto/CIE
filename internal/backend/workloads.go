package backend

import (
	_ "embed"
	"encoding/json"

	"github.com/cie-team/cie/internal/core"
)

//go:embed default_workloads.json
var defaultWorkloadsJSON []byte

func loadDefaultWorkloads() ([]core.Workload, error) {
	var raw []struct {
		Name        string         `json:"name"`
		Items       int            `json:"items"`
		Description string         `json:"description"`
		Config      map[string]any `json:"config,omitempty"`
		Tags        []string       `json:"tags,omitempty"`
	}
	if err := json.Unmarshal(defaultWorkloadsJSON, &raw); err != nil {
		return nil, err
	}
	out := make([]core.Workload, 0, len(raw))
	for _, r := range raw {
		out = append(out, core.Workload{
			Name:        r.Name,
			Items:       r.Items,
			Description: r.Description,
			Config:      r.Config,
			Tags:        r.Tags,
		})
	}
	return out, nil
}

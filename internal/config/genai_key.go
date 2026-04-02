package config

import (
	"strings"

	"github.com/maruel/genai/providers"
)

// GenAIRegistryKey returns the maruel/genai providers.All alias for this config.
// Empty means "no LLM provider" (mock / unset).
func (c *Config) GenAIRegistryKey() string {
	if c == nil {
		return ""
	}
	if k := strings.TrimSpace(c.Model.GenAIProvider); k != "" {
		return strings.ToLower(k)
	}
	p := strings.ToLower(strings.TrimSpace(c.Model.Provider))
	switch p {
	case "", "mock":
		return ""
	case "kimi":
		return "openaicompatible"
	case "openai":
		base := strings.TrimSpace(c.Model.BaseURL)
		if base != "" && !strings.Contains(strings.ToLower(base), "api.openai.com") {
			return "openaicompatible"
		}
		return "openaichat"
	default:
		if _, ok := providers.All[p]; ok {
			return p
		}
		if strings.TrimSpace(c.Model.BaseURL) != "" {
			return "openaicompatible"
		}
		return ""
	}
}

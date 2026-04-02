package config

import (
	"os"
	"strings"

	"github.com/maruel/genai/providers"
)

// ApplyEnvAPIKeys fills missing API keys from standard environment variables.
func (c *Config) ApplyEnvAPIKeys() {
	if c == nil {
		return
	}
	key := c.GenAIRegistryKey()
	if pc, ok := providers.All[key]; ok && pc.APIKeyEnvVar != "" && c.Model.APIKey == "" {
		if v := os.Getenv(pc.APIKeyEnvVar); v != "" {
			c.Model.APIKey = v
		}
	}

	switch strings.ToLower(strings.TrimSpace(c.Model.Provider)) {
	case "kimi":
		if c.Model.APIKey == "" {
			c.Model.APIKey = os.Getenv("KIMI_API_KEY")
			if c.Model.APIKey == "" {
				c.Model.APIKey = os.Getenv("MOONSHOT_API_KEY")
			}
		}
		if c.Model.BaseURL == "" {
			c.Model.BaseURL = "https://api.moonshot.cn/v1"
		}
	case "openai":
		if c.Model.APIKey == "" {
			c.Model.APIKey = os.Getenv("OPENAI_API_KEY")
		}
	default:
		if c.Model.APIKey == "" {
			if k := os.Getenv("OPENAI_API_KEY"); k != "" {
				c.Model.APIKey = k
			}
		}
	}
}

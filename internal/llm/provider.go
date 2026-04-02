package llm

import (
	"context"
	"fmt"
	"strings"

	"github.com/cie-team/cie/internal/config"
	"github.com/maruel/genai"
	"github.com/maruel/genai/providers"
)

// NewProvider builds a genai Provider for cfg. Returns (nil, nil) when LLM is disabled.
func NewProvider(ctx context.Context, cfg *config.Config) (genai.Provider, string, error) {
	if cfg == nil {
		return nil, "", nil
	}
	key := cfg.GenAIRegistryKey()
	if key == "" {
		return nil, "", nil
	}
	pc, ok := providers.All[key]
	if !ok {
		return nil, key, fmt.Errorf("unknown genai registry key %q", key)
	}
	opts := providerOptions(cfg, key)
	p, err := pc.Factory(ctx, opts...)
	return p, key, err
}

func providerOptions(cfg *config.Config, key string) []genai.ProviderOption {
	apiKey := strings.TrimSpace(cfg.Model.APIKey)
	model := strings.TrimSpace(cfg.Model.ModelName)
	base := strings.TrimSpace(cfg.Model.BaseURL)

	var opts []genai.ProviderOption
	if apiKey != "" {
		opts = append(opts, genai.ProviderOptionAPIKey(apiKey))
	}
	if model != "" {
		opts = append(opts, genai.ProviderOptionModel(model))
	}

	switch key {
	case "openaicompatible", "ollama", "llamacpp":
		remote := strings.TrimRight(base, "/")
		if remote == "" {
			switch key {
			case "ollama":
				remote = "http://127.0.0.1:11434"
			case "llamacpp":
				remote = "http://127.0.0.1:8080"
			}
		}
		if remote != "" {
			opts = append(opts, genai.ProviderOptionRemote(remote))
		}
	}
	return opts
}

// UseJSONMode is false for openaicompatible (Kimi and generic OpenAI-base URLs) where genai rejects ReplyAsJSON.
func UseJSONMode(registryKey string) bool {
	return registryKey != "openaicompatible"
}

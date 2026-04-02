package config

import (
	"encoding/json"
	"os"
	"path/filepath"
)

// Config is the on-disk configuration for CIE (JSON).
type Config struct {
	Model        ModelConfig        `json:"model"`
	Optimization OptimizationConfig `json:"optimization"`
	Evaluation   EvaluationConfig   `json:"evaluation"`
	Storage      StorageConfig      `json:"storage"`
	Debug        bool               `json:"debug"`
	LogLevel     string             `json:"log_level"`
}

// ModelConfig holds provider settings.
type ModelConfig struct {
	Provider string `json:"provider"`
	// GenAIProvider overrides GenAIRegistryKey: direct maruel/genai providers.All alias (e.g. groq, anthropic, openrouter).
	GenAIProvider string  `json:"genai_provider,omitempty"`
	ModelName     string  `json:"model_name"`
	APIKey        string  `json:"api_key,omitempty"`
	BaseURL       string  `json:"base_url,omitempty"`
	MaxTokens     int     `json:"max_tokens"`
	Temperature   float64 `json:"temperature"`
	TimeoutSecs   int     `json:"timeout_secs"`
}

// OptimizationConfig holds optimizer defaults.
type OptimizationConfig struct {
	MaxIterations        int     `json:"max_iterations"`
	ConvergenceThreshold float64 `json:"convergence_threshold"`
	StepSize             float64 `json:"step_size"`
	MaxStagnation        int     `json:"max_stagnation"`
	KShots               int     `json:"k_shots"`
	BootstrapMinSuccess  float64 `json:"bootstrap_min_task_success"`
}

// EvaluationConfig holds scoring and guardrails.
type EvaluationConfig struct {
	DefaultEvaluator   string             `json:"default_evaluator"`
	MetricWeights      map[string]float64 `json:"metric_weights"`
	MaxToolErrorRate   float64            `json:"max_tool_error_rate"`
	MinTaskSuccessRate float64            `json:"min_task_success_rate"`
	MaxLatencyP95      float64            `json:"max_latency_p95"`
}

// StorageConfig describes persistence.
type StorageConfig struct {
	Backend        string `json:"backend"`
	DatabasePath   string `json:"database_path"`
	ExperimentsDir string `json:"experiments_dir"`
}

// Default returns baseline configuration.
func Default() *Config {
	return &Config{
		Model: ModelConfig{
			Provider:    "mock",
			ModelName:   "mock",
			MaxTokens:   4096,
			Temperature: 0.7,
			TimeoutSecs: 120,
		},
		Optimization: OptimizationConfig{
			MaxIterations:        100,
			ConvergenceThreshold: 0.001,
			StepSize:             0.1,
			MaxStagnation:        10,
			KShots:               8,
			BootstrapMinSuccess:  0.78,
		},
		Evaluation: EvaluationConfig{
			DefaultEvaluator: "mock",
			MetricWeights: map[string]float64{
				"latency_p95":     0.001,
				"cost_per_req":    0.5,
				"task_success":    -1.0,
				"context_usage":   0.2,
				"tool_error_rate": 0.8,
			},
			MaxToolErrorRate:   0.03,
			MinTaskSuccessRate: 0.7,
			MaxLatencyP95:      5000,
		},
		Storage: StorageConfig{
			Backend:        "json",
			DatabasePath:   "~/.cie/cie.db",
			ExperimentsDir: "~/.cie/experiments",
		},
		Debug:    false,
		LogLevel: "INFO",
	}
}

// ExpandPaths resolves ~ and ensures experiments dir uses absolute paths where needed.
func (c *Config) ExpandPaths() {
	c.Storage.DatabasePath = expandHome(c.Storage.DatabasePath)
	c.Storage.ExperimentsDir = expandHome(c.Storage.ExperimentsDir)
}

func expandHome(p string) string {
	if len(p) > 0 && p[0] == '~' && (len(p) == 1 || p[1] == filepath.Separator) {
		home, err := os.UserHomeDir()
		if err != nil {
			return p
		}
		return filepath.Join(home, p[2:])
	}
	return p
}

// Load reads JSON from path and merges onto defaults.
func Load(path string) (*Config, error) {
	cfg := Default()
	b, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	if err := json.Unmarshal(b, cfg); err != nil {
		return nil, err
	}
	cfg.ExpandPaths()
	return cfg, nil
}

// Save writes JSON to path (0644).
func (c *Config) Save(path string) error {
	c.ExpandPaths()
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return err
	}
	b, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, b, 0o644)
}

// DefaultConfigPath is ~/.cie/config.json
func DefaultConfigPath() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".cie", "config.json"), nil
}

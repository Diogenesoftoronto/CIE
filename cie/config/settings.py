"""
Configuration settings for CIE application.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:  # PyYAML is optional for environments that only rely on JSON configs
    import yaml
except ModuleNotFoundError:  # pragma: no cover - handled in load/save
    yaml = None


@dataclass
class ModelConfig:
    """Model provider configuration."""

    provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    api_key: str | None = None
    base_url: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3

    def __post_init__(self) -> None:
        """Load API key from environment if not provided."""
        if not self.api_key:
            env_key = f"{self.provider.upper()}_API_KEY"
            self.api_key = os.getenv(env_key)
            if not self.api_key and self.provider == "openai":
                # Try common OpenAI environment variable names
                self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("KIMI_API_KEY")


@dataclass
class OptimizationConfig:
    """Optimization algorithm configuration."""

    max_iterations: int = 100
    convergence_threshold: float = 0.001
    population_size: int = 20
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    elite_size: int = 2
    # DSPy specific
    k_shots: int = 8
    bootstrap_iterations: int = 5
    # Hill climbing specific
    step_size: float = 0.1
    max_stagnation: int = 10
    # Bandit specific
    exploration_rate: float = 0.1
    learning_rate: float = 0.01


@dataclass
class EvaluationConfig:
    """Evaluation system configuration."""

    default_evaluator: str = "mock"
    default_metrics: dict[str, float] = field(
        default_factory=lambda: {
            "latency_p95": 0.0,
            "cost_per_req": 0.0,
            "task_success": 0.0,
            "context_usage": 0.0,
            "tool_error_rate": 0.0,
        }
    )
    metric_weights: dict[str, float] = field(
        default_factory=lambda: {
            "latency_p95": 0.001,
            "cost_per_req": 0.5,
            "task_success": -1.0,
            "context_usage": 0.2,
            "tool_error_rate": 0.8,
        }
    )
    evaluation_timeout: int = 300  # 5 minutes
    max_concurrent_evals: int = 3
    retry_failed_evals: bool = True
    # Guardrails
    max_tool_error_rate: float = 0.03
    min_task_success_rate: float = 0.7
    max_latency_p95: float = 5000.0  # 5 seconds


@dataclass
class UIConfig:
    """UI configuration."""

    theme: str = "dark"
    refresh_interval: int = 1  # seconds
    max_table_rows: int = 200
    auto_refresh: bool = True
    show_tooltips: bool = True
    confirm_actions: bool = True
    # Panel configuration
    panel_animations: bool = True
    minimize_to_tray: bool = False
    remember_window_size: bool = True


@dataclass
class StorageConfig:
    """Data storage configuration."""

    backend: str = "sqlite"  # sqlite, json, memory
    database_path: str = "~/.cie/cie.db"
    experiments_dir: str = "~/.cie/experiments"
    backup_enabled: bool = True
    backup_interval: int = 3600  # 1 hour
    max_experiments: int = 1000

    def __post_init__(self) -> None:
        """Expand paths."""
        self.database_path = str(Path(self.database_path).expanduser())
        self.experiments_dir = str(Path(self.experiments_dir).expanduser())


@dataclass
class CIEConfig:
    """Main CIE configuration."""

    model: ModelConfig = field(default_factory=ModelConfig)
    optimization: OptimizationConfig = field(default_factory=OptimizationConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    # Application settings
    debug: bool = False
    log_level: str = "INFO"
    config_file: str | None = None

    def __post_init__(self) -> None:
        """Load configuration from file if specified."""
        if self.config_file:
            self.load_from_file(self.config_file)

    def load_from_file(self, config_file: str) -> None:
        """Load configuration from file."""
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        with open(config_path) as f:
            if config_path.suffix.lower() in [".yml", ".yaml"]:
                if yaml is None:
                    raise RuntimeError(
                        "PyYAML is required to load YAML configuration files. "
                        "Install it via `uv sync --extra dev` or `pip install pyyaml`."
                    )
                data = yaml.safe_load(f)
            elif config_path.suffix.lower() == ".json":
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")
        self._update_from_dict(data)

    def save_to_file(self, config_file: str) -> None:
        """Save configuration to file."""
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_dict()
        with open(config_path, "w") as f:
            if config_path.suffix.lower() in [".yml", ".yaml"]:
                if yaml is None:
                    raise RuntimeError(
                        "PyYAML is required to save YAML configuration files. "
                        "Install it via `uv sync --extra dev` or `pip install pyyaml`."
                    )
                yaml.safe_dump(data, f, default_flow_style=False)
            elif config_path.suffix.lower() == ".json":
                json.dump(data, f, indent=2)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "model": {
                "provider": self.model.provider,
                "model_name": self.model.model_name,
                "base_url": self.model.base_url,
                "max_tokens": self.model.max_tokens,
                "temperature": self.model.temperature,
                "timeout": self.model.timeout,
                "retry_attempts": self.model.retry_attempts,
            },
            "optimization": {
                "max_iterations": self.optimization.max_iterations,
                "convergence_threshold": self.optimization.convergence_threshold,
                "population_size": self.optimization.population_size,
                "mutation_rate": self.optimization.mutation_rate,
                "crossover_rate": self.optimization.crossover_rate,
                "elite_size": self.optimization.elite_size,
                "k_shots": self.optimization.k_shots,
                "bootstrap_iterations": self.optimization.bootstrap_iterations,
                "step_size": self.optimization.step_size,
                "max_stagnation": self.optimization.max_stagnation,
                "exploration_rate": self.optimization.exploration_rate,
                "learning_rate": self.optimization.learning_rate,
            },
            "evaluation": {
                "default_evaluator": self.evaluation.default_evaluator,
                "default_metrics": self.evaluation.default_metrics,
                "metric_weights": self.evaluation.metric_weights,
                "evaluation_timeout": self.evaluation.evaluation_timeout,
                "max_concurrent_evals": self.evaluation.max_concurrent_evals,
                "retry_failed_evals": self.evaluation.retry_failed_evals,
                "max_tool_error_rate": self.evaluation.max_tool_error_rate,
                "min_task_success_rate": self.evaluation.min_task_success_rate,
                "max_latency_p95": self.evaluation.max_latency_p95,
            },
            "ui": {
                "theme": self.ui.theme,
                "refresh_interval": self.ui.refresh_interval,
                "max_table_rows": self.ui.max_table_rows,
                "auto_refresh": self.ui.auto_refresh,
                "show_tooltips": self.ui.show_tooltips,
                "confirm_actions": self.ui.confirm_actions,
                "panel_animations": self.ui.panel_animations,
                "minimize_to_tray": self.ui.minimize_to_tray,
                "remember_window_size": self.ui.remember_window_size,
            },
            "storage": {
                "backend": self.storage.backend,
                "database_path": self.storage.database_path,
                "experiments_dir": self.storage.experiments_dir,
                "backup_enabled": self.storage.backup_enabled,
                "backup_interval": self.storage.backup_interval,
                "max_experiments": self.storage.max_experiments,
            },
            "debug": self.debug,
            "log_level": self.log_level,
        }

    def _update_from_dict(self, data: dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if "model" in data:
            model_data = data["model"]
            self.model.provider = model_data.get("provider", self.model.provider)
            self.model.model_name = model_data.get("model_name", self.model.model_name)
            self.model.base_url = model_data.get("base_url", self.model.base_url)
            self.model.max_tokens = model_data.get("max_tokens", self.model.max_tokens)
            self.model.temperature = model_data.get("temperature", self.model.temperature)
            self.model.timeout = model_data.get("timeout", self.model.timeout)
            self.model.retry_attempts = model_data.get("retry_attempts", self.model.retry_attempts)
        if "optimization" in data:
            opt_data = data["optimization"]
            self.optimization.max_iterations = opt_data.get(
                "max_iterations", self.optimization.max_iterations
            )
            self.optimization.convergence_threshold = opt_data.get(
                "convergence_threshold", self.optimization.convergence_threshold
            )
            self.optimization.population_size = opt_data.get(
                "population_size", self.optimization.population_size
            )
            self.optimization.mutation_rate = opt_data.get(
                "mutation_rate", self.optimization.mutation_rate
            )
            self.optimization.crossover_rate = opt_data.get(
                "crossover_rate", self.optimization.crossover_rate
            )
            self.optimization.elite_size = opt_data.get("elite_size", self.optimization.elite_size)
            self.optimization.k_shots = opt_data.get("k_shots", self.optimization.k_shots)
            self.optimization.bootstrap_iterations = opt_data.get(
                "bootstrap_iterations", self.optimization.bootstrap_iterations
            )
            self.optimization.step_size = opt_data.get("step_size", self.optimization.step_size)
            self.optimization.max_stagnation = opt_data.get(
                "max_stagnation", self.optimization.max_stagnation
            )
            self.optimization.exploration_rate = opt_data.get(
                "exploration_rate", self.optimization.exploration_rate
            )
            self.optimization.learning_rate = opt_data.get(
                "learning_rate", self.optimization.learning_rate
            )
        if "evaluation" in data:
            eval_data = data["evaluation"]
            self.evaluation.default_evaluator = eval_data.get(
                "default_evaluator", self.evaluation.default_evaluator
            )
            self.evaluation.default_metrics.update(eval_data.get("default_metrics", {}))
            self.evaluation.metric_weights.update(eval_data.get("metric_weights", {}))
            self.evaluation.evaluation_timeout = eval_data.get(
                "evaluation_timeout", self.evaluation.evaluation_timeout
            )
            self.evaluation.max_concurrent_evals = eval_data.get(
                "max_concurrent_evals", self.evaluation.max_concurrent_evals
            )
            self.evaluation.retry_failed_evals = eval_data.get(
                "retry_failed_evals", self.evaluation.retry_failed_evals
            )
            self.evaluation.max_tool_error_rate = eval_data.get(
                "max_tool_error_rate", self.evaluation.max_tool_error_rate
            )
            self.evaluation.min_task_success_rate = eval_data.get(
                "min_task_success_rate", self.evaluation.min_task_success_rate
            )
            self.evaluation.max_latency_p95 = eval_data.get(
                "max_latency_p95", self.evaluation.max_latency_p95
            )
        if "ui" in data:
            ui_data = data["ui"]
            self.ui.theme = ui_data.get("theme", self.ui.theme)
            self.ui.refresh_interval = ui_data.get("refresh_interval", self.ui.refresh_interval)
            self.ui.max_table_rows = ui_data.get("max_table_rows", self.ui.max_table_rows)
            self.ui.auto_refresh = ui_data.get("auto_refresh", self.ui.auto_refresh)
            self.ui.show_tooltips = ui_data.get("show_tooltips", self.ui.show_tooltips)
            self.ui.confirm_actions = ui_data.get("confirm_actions", self.ui.confirm_actions)
            self.ui.panel_animations = ui_data.get("panel_animations", self.ui.panel_animations)
            self.ui.minimize_to_tray = ui_data.get("minimize_to_tray", self.ui.minimize_to_tray)
            self.ui.remember_window_size = ui_data.get(
                "remember_window_size", self.ui.remember_window_size
            )
        if "storage" in data:
            storage_data = data["storage"]
            self.storage.backend = storage_data.get("backend", self.storage.backend)
            self.storage.database_path = storage_data.get(
                "database_path", self.storage.database_path
            )
            self.storage.experiments_dir = storage_data.get(
                "experiments_dir", self.storage.experiments_dir
            )
            self.storage.backup_enabled = storage_data.get(
                "backup_enabled", self.storage.backup_enabled
            )
            self.storage.backup_interval = storage_data.get(
                "backup_interval", self.storage.backup_interval
            )
            self.storage.max_experiments = storage_data.get(
                "max_experiments", self.storage.max_experiments
            )
        self.debug = data.get("debug", self.debug)
        self.log_level = data.get("log_level", self.log_level)


# Global configuration instance
_config = None


def get_config(config_file: str | None = None) -> CIEConfig:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = CIEConfig(config_file=config_file)
    return _config


def set_config(config: CIEConfig) -> None:
    """Set global configuration instance."""
    global _config
    _config = config

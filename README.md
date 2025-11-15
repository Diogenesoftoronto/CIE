# CIE (Optimization & Evaluation)

A modern Python TUI (Terminal User Interface) application for running optimization experiments using different AI algorithms and evaluating their performance across various workloads.

## 🚀 Features

- **Modern TUI Interface**: Built with Textual framework, inspired by modern TUI apps like Harlequin and Dolphie
- **Real AI Model Integration**: Support for OpenAI, Kimi, and other model providers
- **Multiple Optimization Algorithms**: DSPy, Hill Climbing, Genetic Algorithms, and more
- **Comprehensive Evaluation**: Multi-dimensional metrics including latency, cost, success rate, and resource usage
- **Pareto Frontier Optimization**: Automatic identification of non-dominated solutions
- **Data Persistence**: SQLite, JSON, and in-memory storage backends
- **CLI Interface**: Full command-line interface for automation and scripting
- **Configuration Management**: Flexible YAML/JSON configuration with environment variable support
- **Real-time Monitoring**: Live updates and progress tracking
- **Extensible Architecture**: Plugin-based design for easy extension
- **Design System**: Shared Textual theme (`cie/ui/theme.tcss`) that keeps the entire TUI visually coherent
- **Evaluator Registry**: Built-in mock/text-match evaluators plus a plugin API for custom scoring flows
- **Context Introspection Workspace**: `[CTX]` tab and modal navigator to capture, reorganize, and export live agent context
- **W&B Beta LEET Ingestion**: Import `wandb/latest-run` locally with a single shortcut to visualize real Run metrics inside the Experiments dashboard
- **Demo Mode**: `cie tui --demo` loads a guided LeetCode practice lab with seeded workloads/trials/context hints
- **Benchmark Harness**: Ready-to-run benchmarking suite under `benchmark/` with CLI runner + research-ready metrics

## 📦 Installation

### Using UV (recommended)

```bash
git clone https://github.com/cie-team/cie.git
cd cie
uv sync                # install locked dependencies
uv run cie --help      # run CLI via UV
```

Optional extras:

```bash
uv sync --extra dev    # linting, tests, tooling
uv sync --extra ai     # OpenAI / DSPy integrations
```

> Pip `install -e .[dev]` still works, but the repo standardizes on UV for reproducible environments and lockfile enforcement.

## 🔧 Configuration

### Initial Setup

```bash
# Initialize configuration
cie init --model kimi --model-name kimi --storage json

# Or with OpenAI
cie init --model openai --model-name gpt-4o-mini --storage sqlite
```

### Environment Variables

Set your API keys:

```bash
export KIMI_API_KEY="your-kimi-api-key"
# or
export OPENAI_API_KEY="your-openai-api-key"
```

### Configuration File

CIE uses a JSON configuration file located at `~/.cie/config.json`:

```json
{
  "model": {
    "provider": "kimi",
    "model_name": "kimi",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "storage": {
    "backend": "sqlite",
    "database_path": "~/.cie/cie.db",
    "experiments_dir": "~/.cie/experiments"
  },
  "optimization": {
    "max_iterations": 100,
    "population_size": 20,
    "convergence_threshold": 0.001
  },
  "evaluation": {
    "default_evaluator": "mock",
    "metric_weights": {
      "latency_p95": 0.001,
      "cost_per_req": 0.5,
      "task_success": -1.0,
      "context_usage": 0.2,
      "tool_error_rate": 0.8
    }
  }
}
```

## 🎯 Quick Start

### TUI Interface

```bash
# Start the TUI application
cie tui

# Explore demo mode (seeds LeetCode-style workloads/trials)
cie tui --demo
```

> Tip: set `CIE_WANDB_RUN=/path/to/wandb/run` (defaults to `./wandb/latest-run`) before launching so the Experiments panel can import real LEET metrics with `Ctrl+Shift+W`.

Key shortcuts in TUI:
- `Tab`/`Shift+Tab`: Navigate between panels
- `O`: Run optimizer (in Optimizers panel)
- `E`: Run evaluation (in Evaluations panel)
- `P`: Toggle Pareto view (in Experiments panel)
- `A`: Adopt best policy (in Experiments panel)
- `Shift+S`: Sync latest W&B run (Experiments panel)
- `Ctrl+W`: Edit objective weights
- `Ctrl+O`: Edit configuration
- `Ctrl+Shift+W`: Global shortcut to sync W&B metrics
- `F1`: Show help

### CLI Interface

```bash
# Run optimization experiment
cie optimize --iterations 10 --optimizer 0 --workload 0

# View trial history
cie trials --limit 20

# Show Pareto frontier
cie trials --pareto

# Adopt a policy from trial #5
cie adopt --trial-id 5

# Show backend statistics
cie stats

# List available optimizers
cie optimizers

# List available workloads
cie workloads

# List / set evaluators
cie evaluators
cie evaluators --use text-match
```

## 🔄 Syncing Weights & Biases Runs

1. Ensure a local W&B run directory exists (default: `./wandb/latest-run`). Override via `export CIE_WANDB_RUN=/absolute/path/to/run`.
2. Launch the TUI and open the Experiments panel.
3. Click the “Sync W&B” toolbar button, press `Shift+S`, or use the global shortcut `Ctrl+Shift+W`.
4. Imported trials are tagged with `metadata.source == "wandb"` so subsequent syncs skip duplicates. Metric cards, sparklines, and the Pareto table refresh automatically.
5. Programmatic usage: `backend.ingest_wandb_run(path)` in `cie/core/backend.py` relies on the helpers in `cie/utils/wandb_import.py`.

## 🧪 Optimization Algorithms

### DSPy Optimizer
- **Name**: `DSPy:BootstrapFewShot`
- **Description**: Runs the real DSPy runtime (chain-of-thought `Predict` program) against the OpenAI provider for structured policy synthesis, with automatic prompt-based fallback when DSPy or an API key is unavailable
- **Parameters**: k-shots, model selection, temperature
- **Best for**: Prompt optimization, few-shot learning scenarios
- **Runtime requirements**: Install `cie[ai]` (for `dspy-ai`) and configure an OpenAI-compatible provider to enable the DSPy path

### Hill Climb Optimizer
- **Name**: `HillClimb`
- **Description**: Iterative improvement with small parameter changes
- **Parameters**: step size, stagnation limit, parameter ranges
- **Best for**: Continuous parameter optimization

### Adaptive Hill Climb
- **Name**: `AdaptiveHillClimb`
- **Description**: Hill climbing with adaptive step size
- **Parameters**: adaptation rate, improvement tracking
- **Best for**: Dynamic optimization scenarios

## 🧮 Evaluators

- **MockEvaluator**: High-signal synthetic metrics for fast iteration; simulates latency, cost, and guardrail breaches across the built-in workloads.
- **TextMatchEvaluator**: Real text evaluation loop inspired by Braintrust-style checks. It executes summarization/classification QA samples through the configured model provider, then scores with Levenshtein distance, similarity ratio, and exact-match heuristics.
- **Plugins**: Drop new modules under `cie/evaluators/plugins/` and register them via `register_evaluator()` to expose DSL-specific checks (e.g., SQL validators, retrieval benchmarks). Use `cie evaluators` to list what’s available, and `cie evaluators --use text-match` to set the default in `~/.cie/config.json`.

## 📊 Evaluation Metrics

CIE tracks multiple dimensions of performance:

- **Latency P95**: 95th percentile response time (ms)
- **Cost per Request**: API cost per request ($)
- **Task Success Rate**: Success rate (0-1)
- **Context Usage**: Context utilization (0-1)
- **Tool Error Rate**: Error rate (0-1)
- **Throughput**: Requests per second
- **Memory Usage**: Memory utilization (0-1)
- **CPU Usage**: CPU utilization (0-1)
- **Text Similarity / Exact Match / Levenshtein**: NLP-focused metrics produced by the text-match evaluator

## 🏆 Pareto Frontier

CIE automatically identifies the Pareto frontier - the set of non-dominated solutions that represent the best trade-offs between competing objectives (latency, cost, and success rate).

## 💾 Storage Backends

### SQLite (Recommended)
- **Pros**: Full-featured, ACID compliant, good performance
- **Cons**: Requires file system access
- **Use case**: Production deployments

### JSON
- **Pros**: Human-readable, easy to backup/restore
- **Cons**: No transactions, slower for large datasets
- **Use case**: Development, small experiments

### In-Memory
- **Pros**: Fastest, no persistence
- **Cons**: Data lost on restart
- **Use case**: Testing, temporary experiments

## 📐 Benchmarks & Research Drafts

- **Benchmark Harness**: `benchmark/runner.py` executes the mixed-workload suites (MicroEval, MacroEval, TextEval, context exercises). Run via `uv run python benchmark/runner.py` or integrate with CI.
- **Documentation**: `BENCHMARK_GUIDE.md`, `BENCHMARK_OVERVIEW.md`, and `benchmark/SYSTEM_SUMMARY.md` capture methodology, scoring, and current results.
- **Demo Scenario**: `cie tui --demo` mirrors the benchmarking inputs (seeded LeetCode workloads/trials) for narrative walkthroughs.
- **Research Draft**: Early paper drafts live under `papers/` and summarize the full architecture, benchmarking philosophy, and context-introspection innovations.

## 🔌 Model Providers

### OpenAI
```bash
export OPENAI_API_KEY="your-api-key"
cie init --model openai --model-name gpt-4o-mini
```

### Kimi (Moonshot)
```bash
export KIMI_API_KEY="your-api-key"
cie init --model kimi --model-name kimi
```

### Mock (Testing)
```bash
cie init --model mock --model-name mock-model
```

## 🎨 Design System

CIE uses a dedicated Textual theme file, `cie/ui/theme.tcss`, to drive colors, typography, spacing, and component layouts. Panels, tables, status bars, and every modal pull from the same CSS classes (`panel`, `panel-content`, `panel-status`, etc.), so new UI work should extend those classes or add new rules in the theme file rather than embedding inline CSS. This shared system keeps multi-agent contributions visually consistent and makes it easy to tweak the overall look in a single place.

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# End-to-end tests
pytest tests/test_end_to_end.py -v

# Unit tests
pytest tests/test_backend.py -v

# Integration tests with real models
pytest tests/test_end_to_end.py::TestRealModelIntegration -v
```

### Test with Coverage
```bash
pytest --cov=cie --cov-report=html
```

## 📈 Performance Benchmarks

The application is designed for performance:

- **Policy Generation**: < 1 second (with mock models)
- **Evaluation**: < 3 seconds per trial
- **Scalability**: Handles 50+ trials efficiently
- **Memory Usage**: Optimized for large experiment datasets

## 🔧 Development

### Project Structure
```
cie/
├── core/           # Core models and backend
├── optimizers/     # Optimization algorithms
├── evaluators/     # Evaluation systems
├── ui/             # TUI components
├── config/         # Configuration management
├── utils/          # Utilities and helpers
└── cli.py          # Command-line interface
```

### Adding New Optimizers

1. Create a new class implementing the `Optimizer` protocol
2. Add it to the backend's optimizer list
3. Update the UI to handle any new parameters

### Adding New Evaluators

1. Create a new class implementing the `Evaluator` protocol
2. Implement the required metrics
3. Add it to the backend's evaluator

### Adding New Model Providers

1. Create a new class extending `BaseModelProvider`
2. Implement `generate()` and `embed()` methods
3. Register in the model provider factory

## 🚨 Guardrails

CIE includes built-in guardrails to prevent adoption of unreliable policies:

- **Tool Error Rate**: Must be ≤ 3%
- **Task Success Rate**: Must be ≥ 70%
- **Latency P95**: Must be ≤ 5 seconds

These can be configured in the settings.

## 📚 Examples

### Basic Optimization
```python
from cie.core.backend import CIEBackend
from cie.config.settings import CIEConfig

config = CIEConfig()
config.model.provider = "mock"  # Use mock for testing
backend = CIEBackend(config)

# Generate and evaluate a policy
policy = backend.propose_once(0)  # Use first optimizer
trial = backend.eval_policy(policy, 0)  # Use first workload

print(f"Score: {trial.score}")
print(f"Metrics: {trial.metrics}")
```

### Custom Optimization Loop
```python
best_score = float('inf')
best_trial = None

for i in range(10):
    policy = backend.propose_once(0)
    trial = backend.eval_policy(policy, 0)
    
    if trial.score < best_score:
        best_score = trial.score
        best_trial = trial

print(f"Best trial: #{best_trial.id}, Score: {best_score}")
```

### Policy Adoption
```python
# Adopt the best policy
success = backend.adopt_policy(best_trial.id)
if success:
    print(f"Policy adopted: {backend.active_policy.name}")
```

## 🔍 Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```bash
   export KIMI_API_KEY="your-key"
   # or
   export OPENAI_API_KEY="your-key"
   ```

2. **Permission Denied**
   ```bash
   chmod +x ~/.cie/experiments
   ```

3. **Model Initialization Failed**
   - Check API key validity
   - Verify network connectivity
   - Try mock model for testing

4. **Storage Issues**
   - Check disk space
   - Verify write permissions
   - Try different storage backend

### Debug Mode

Enable debug mode for detailed logging:

```bash
cie --debug tui
# or
cie --debug optimize --iterations 10
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Setup

```bash
git clone https://github.com/cie-team/cie.git
cd cie
pip install -e ".[dev]"
pre-commit install

# Refresh paper assets after UI changes
python scripts/generate_tui_screenshots.py
```

### Code Style

- Use Black for formatting
- Use Ruff for linting
- Follow type hints with mypy
- Add docstrings to public functions

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Textual Framework**: For the amazing TUI framework
- **DSPy**: For inspiration on prompt optimization
- **Harlequin & Dolphie**: For modern TUI design inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/cie-team/cie/issues)
- **Discussions**: [GitHub Discussions](https://github.com/cie-team/cie/discussions)
- **Documentation**: [Full Documentation](https://cie.readthedocs.io)

---

**CIE** - Making AI optimization accessible through beautiful terminal interfaces.

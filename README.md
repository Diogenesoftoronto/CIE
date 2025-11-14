# CIE - Optimization & Evaluation Platform

A powerful Python Terminal User Interface (TUI) application for running optimization experiments using different algorithms and evaluating their performance across various workloads.

<!-- Screenshot placeholder - add actual screenshot when available -->
<!-- ![CIE TUI Screenshot](docs/screenshots/cie-tui.png) -->

## 🌟 Features

- **Interactive TUI**: Clean, keyboard-driven interface built with Textual (single-file architecture)
- **Multiple Optimization Algorithms**: Support for DSPy, Hill Climbing, and Bandit algorithms (mock implementations)
- **Real-time Evaluation**: Live performance metrics and scoring
- **Pareto Optimization**: Multi-dimensional optimization with frontier visualization
- **Policy Management**: Easy policy configuration and adoption workflow
- **Extensible Architecture**: Protocol-based design for easy algorithm integration
- **Mock-First Development**: Ready for real algorithm implementations

## 🎯 Use Cases

- **Algorithm Testing**: Compare optimization algorithms on identical workloads
- **Hyperparameter Optimization**: Find optimal parameters for ML models
- **A/B Testing**: Compare different configurations with statistical rigor
- **Performance Analysis**: Multi-dimensional performance analysis
- **Research Platform**: Framework for optimization research and experimentation

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **UV package manager** (recommended) or pip

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd cie
   ```

2. **Install dependencies**:
   ```bash
   # Using UV (recommended)
   uv sync

   # Or using pip
   pip install "textual>=0.47" "textualize>=0.1"
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

### Basic Usage

1. **Navigate** through panels using `Tab` and `Shift+Tab`
2. **Select optimizers** in the Optimizers panel (left)
3. **Configure algorithms** using keyboard shortcuts:
   - `o`: Run optimization once
   - `O`: Configure selected algorithm
   - `W`: Adjust objective weights
4. **Run evaluations** in the Evals panel (center):
   - `e`: Execute evaluation on selected workload
   - `b`: Set baseline
5. **Analyze results** in the Experiments panel (right):
   - `p`: Toggle Pareto frontier view
   - `A`: Adopt best performing policy
   - `r`: Resume experiments
   - `n`: Start new study
   - `k`: Stop current run

## 📊 Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    CIEOptimEvalsApp                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Optimizers   │  │    Evals     │  │   Experiments    │  │
│  │   Panel      │  │    Panel     │  │     Panel        │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     CIEBackend                              │
│  • Policy Management    • Trial History                     │
│  • Scoring Engine      • Pareto Optimization                │
│  • Algorithm Registry  • Objective Weights                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Algorithm Implementations                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ DSPy Opt    │  │ Hill Climb  │  │   Two-Armed Bandit  │ │
│  │ Mock/Real   │  │   Mock      │  │      Mock           │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Patterns

- **Protocol-Based Interfaces**: Clean separation between algorithms and evaluation
- **Message-Passing Architecture**: Decoupled UI components with event communication
- **Mock-First Development**: Replaceable implementations for testing and development
- **Singleton Backend**: Centralized state management across UI components
- **Reactive UI**: Automatic updates when backend state changes

## 📈 Performance Metrics

CIE optimizes across five key dimensions:

- **Latency (p95)**: 95th percentile response time in milliseconds
- **Cost per Request**: Dollar cost for each request processed
- **Task Success Rate**: Fraction of successful task completions (0.0-1.0)
- **Context Usage**: Efficiency of context/window utilization (0.0-1.0)
- **Tool Error Rate**: Fraction of tool execution failures (0.0-1.0)

### Objective Scoring

Each metric has configurable weights in the objective function:

```
score = Σ(weight[i] × metric[i])
```

- **Positive weights**: Penalize the metric (higher values = worse)
- **Negative weights**: Reward the metric (higher values = better)

## 🛠️ Development

### Project Structure

```
cie/
├── main.py              # Main application file (~650 lines, single-file architecture)
├── pyproject.toml       # Python project configuration
├── uv.lock             # UV package manager lock file
├── README.md           # This file
├── AGENTS.md           # Developer documentation
└── skills/             # Technical documentation
    └── textual.md      # Textual framework guide (comprehensive)
```

### Development Workflow

1. **Environment Setup**:
   ```bash
   # Install development dependencies
   uv add --dev pytest
   
   # Run tests
   pytest
   
   # Run the application
   python main.py
   ```

2. **Adding New Algorithms**:
   ```python
   class MyOptimizer(Optimizer):
       name = "MyCustomAlgorithm"

       def propose(self, state: Dict[str, Any]) -> Policy:
           # Implementation here
           pass

       def observe(self, policy: Policy, metrics: Dict[str, float]) -> None:
           # Update internal state
           pass
   ```

3. **Adding New Evaluators**:
   ```python
   class MyEvaluator(Evaluator):
       name = "MyCustomEvaluator"

       def run(self, policy: Policy, workload: str) -> Dict[str, float]:
           # Return metrics dict
           return {"latency_p95": 150.0, "cost_per_req": 0.002, ...}
   ```

### Testing Strategy

**Current State**: Basic test infrastructure in place

**Available Tests**:
- **Unit Tests**: Backend logic, scoring functions, data structures (`tests/test_backend.py`)
- **Mock Tests**: Algorithm behavior without external dependencies (`tests/test_optimizers.py`)
- **Integration Tests**: UI flow, message passing, panel interactions (placeholder)
- **Performance Tests**: Scoring performance, UI responsiveness (future)

**Running Tests**:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_backend.py

# Run with verbose output
pytest -v
```

## 🎮 Algorithm Details

### MockDSPyOptimizer
Simulates DSPy optimization with configurable parameters:
- `k_shots`: Number of few-shot examples (affects success rate)
- `model`: Model identifier for cost simulation
- Generates artifact-backed policies for real integration

### MockHillClimb
Implements simple hill climbing with:
- `prune_ratio`: Context pruning factor (0.0-0.6)
- `batch_size`: Processing batch size (2-16)
- Random parameter exploration

### MockBandit
Two-armed bandit simulation:
- Arms: "A" and "B"
- Equal probability selection
- Simple A/B testing framework

## 🔧 Configuration

### Objective Weights
Adjust optimization priorities using the Weights Modal (`W` key):

```python
# Default configuration
objective_weights = {
    "latency_p95": 0.001,      # Slight latency penalty
    "cost_per_req": 0.5,       # Moderate cost penalty
    "task_success": -1.0,      # Strong success reward
    "context_usage": 0.2,      # Slight context penalty
    "tool_error_rate": 0.8,    # Strong error penalty
}
```

### Workloads
Predefined evaluation workloads:
- **MicroEval:basic**: 50 items, fast feedback loop
- **MacroEval:rag-xl**: 10 items, comprehensive evaluation
- **SyntheticLoad:cpu80**: 1 item, CPU stress test

## 🚧 Current Limitations

- **Mock Implementations**: Algorithms use simulated data (ready for real implementations)
- **Single-File Architecture**: All code in main.py (~650 lines)
- **No Test Suite**: Testing infrastructure not yet implemented
- **No Persistence**: Trial history lost on application restart
- **Basic UI**: Limited visualization options
- **No Distributed Computing**: Single-process evaluation
- **Single-User**: No multi-user or concurrent session support

## 🔮 Future Roadmap

### Short Term
- [ ] Add comprehensive test suite
- [ ] Replace mock algorithms with real implementations
- [ ] Add trial history persistence (SQLite/JSON)
- [ ] Implement export/import functionality
- [ ] Refactor from single-file to modular architecture

### Medium Term
- [ ] Distributed evaluation support
- [ ] Advanced visualization (charts, graphs)
- [ ] Multi-user session management
- [ ] Integration with external evaluation systems

### Long Term
- [ ] Web interface alongside TUI
- [ ] Real-time collaboration features
- [ ] Machine learning model integration
- [ ] Production deployment tools

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following the established patterns
4. **Add tests** for new functionality
5. **Run the test suite**: `pytest`
6. **Submit a pull request**

### Development Guidelines

- **Follow existing patterns**: Protocol interfaces, message passing
- **Add comprehensive docstrings**: Document public APIs
- **Write tests**: Unit tests for backend, integration tests for UI
- **Update documentation**: README, AGENTS.md, and inline comments

## 📝 License

[Specify your license here]

## 🙏 Acknowledgments

- **Textual Framework**: For the excellent TUI framework
- **DSPy**: For optimization algorithm inspiration
- **Python Protocol Design**: For clean interface patterns

## 📚 Resources

- **Textual Documentation**: [skills/textual.md](skills/textual.md)
- **Developer Guide**: [AGENTS.md](AGENTS.md)
- **Project Architecture**: See inline documentation in `main.py`
- **Issue Tracking**: [GitHub Issues](repository-url/issues)

---

**CIE** - Where optimization meets evaluation in a powerful, user-friendly interface.
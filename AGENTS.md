# Agent Guide for CIE Project

## Project Overview

**CIE** (Optimization & Evaluation) is a Python TUI (Terminal User Interface) application built with the Textual framework. It provides an interactive interface for running optimization experiments using different algorithms and evaluating their performance across various workloads.

## Project Structure

- **main.py**: Single-file application containing all code (≈650 lines)
- **pyproject.toml**: Python project configuration with dependencies
- **uv.lock**: UV package manager lock file
- **README.md**: Comprehensive project documentation
- **AGENTS.md**: This developer guide
- **skills/**: Technical documentation directory
- **tests/**: Test infrastructure (placeholder tests)
- **.python-version**: Specifies Python 3.13

## Development Environment

### Python Requirements
- **Python 3.13+** (strict requirement: `requires-python = ">=3.13"`)
- **Package Manager**: UV (lock file present)

### Dependencies
- `textual>=0.47`: TUI framework (corrected from 6.6.0)
- `textualize>=0.1`: Textual utilities
- `pytest>=7.0.0`: Testing framework (dev dependency)

### Commands

#### Install Dependencies
```bash
# Using UV
uv sync

# Or using pip (if UV not available)
pip install "textual>=0.47" "textualize>=0.1"
```

#### Run Application
```bash
python main.py
```

#### Development Commands
```bash
# Check Python version compliance
python --version  # Should be 3.13+

# Install development tools
uv add --dev pytest  # Testing framework
# uv add --dev black ruff  # Optional: formatting and linting
```

## Testing Strategy

**Current Status**: Basic test infrastructure in place
- **Unit Tests**: `tests/test_backend.py` - Backend logic, scoring functions
- **Mock Tests**: `tests/test_optimizers.py` - Algorithm behavior tests
- **Test Configuration**: `tests/conftest.py` - Pytest fixtures

**Running Tests**:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_backend.py
```

**Note**: Tests are currently marked as skipped (placeholder) until real implementations are added.

## Code Architecture & Patterns

### Core Architecture

**Domain Models** (main.py:25-53):
```python
@dataclass
class Policy:     # Configuration for optimization algorithms
@dataclass
class Trial:      # Individual experiment results

class Optimizer(Protocol):  # Interface for optimization algorithms
class Evaluator(Protocol):  # Interface for evaluation systems
```

**Mock Implementations** (main.py:60-140):
- `MockDspyOptimizer`: DSPy-based optimization with artifact tracking
- `MockHillClimb`: Simple hill climbing optimization
- `MockBandit`: Two-armed bandit optimization
- `MockEvaluator`: Simulated evaluation metrics

**Backend Logic** (main.py:147-280):
- `CIEBackend`: Central state management and scoring
- Objective weights for multi-dimensional optimization
- Pareto frontier maintenance for non-dominated solutions
- Trial history and policy adoption mechanisms

**UI Components** (main.py:287-646):
- `WeightsModal`: Interactive weight editing
- `OptimizersPanel`: Algorithm selection and configuration
- `EvalsPanel`: Workload evaluation interface
- `ExperimentsPanel`: Trial history and results analysis
- `CIEOptimEvalsApp`: Main application shell

### Key Patterns & Conventions

#### 1. Protocol-Based Design
```python
class Optimizer(Protocol):
    name: str
    def propose(self, state: Dict[str, Any]) -> Policy: ...
    def observe(self, policy: Policy, metrics: Dict[str, float]) -> None: ...
```
- Use protocols for extensible interfaces
- Clear separation between interface and implementation

#### 2. Mock-First Development
- All major components have mock implementations
- TODO comments indicate where real implementations needed:
  ```python
  # Line 61: "Replace with Real DSPy optimizer"
  # Line 115: "Replace with real Micro/Macro evaluators"
  ```

#### 3. Message-Based UI Architecture
- Textual messages for inter-panel communication
- Message classes defined within each panel
- Example: `OptimizersPanel.OptimizerRun(Message)`

#### 4. Configuration Management
- Backend singleton pattern: `BACKEND = CIEBackend()`
- Objective weights in `BACKEND.objective_weights`
- Workload definitions in `BACKEND.workloads`

#### 5. Scoring & Optimization
```python
def score(self, metrics: Dict[str, float]) -> float:
    # Weighted linear combination of metrics
    return sum(w.get(k, 0.0) * float(metrics.get(k, 0.0)) for k in w.keys())
```

## Testing Strategy

**Current State**: No tests present
**Recommendation**: Add test suite for:
- Backend scoring logic
- Policy generation algorithms
- Pareto frontier calculations
- UI component rendering
- Message passing between panels

**Test Structure** (suggested):
```
tests/
├── unit/
│   ├── test_backend.py
│   ├── test_optimizers.py
│   └── test_evaluators.py
├── integration/
│   └── test_ui_flow.py
└── conftest.py
```

## Common Development Tasks

### Adding New Optimizer
1. Create class implementing `Optimizer` protocol
2. Add to `BACKEND.optimizers` list
3. Update `list_optimizers()` metadata handling
4. Add any optimizer-specific UI configuration

### Modifying Scoring Weights
- Edit `BACKEND.objective_weights` (main.py:150-156)
- UI: Press 'W' in Optimizers panel to open weights modal
- Weights: positive = penalize, negative = reward

### Adding New Metrics
1. Add to `objective_weights` dictionary
2. Update `MockEvaluator.run()` to generate metric
3. Modify UI columns in appropriate panels
4. Update `score()` method if needed

### Customizing Workloads
- Edit `BACKEND.workloads` list (main.py:167-171)
- Each workload: `{"name": "...", "items": N, "last_score": None}`

## Important Implementation Details

### Multi-Dimensional Optimization
- **Metrics**: latency_p95, cost_per_req, task_success, context_usage, tool_error_rate
- **Scoring**: Weighted linear combination (customizable weights)
- **Pareto Frontier**: Maintains non-dominated solutions

### Mock Implementation Details
- `MockDspyOptimizer`: Simulates artifact-backed policies, k-shot optimization
- `MockHillClimb`: Random parameter exploration (prune_ratio, batch_size)
- `MockBandit`: Random arm selection (A/B testing)
- `MockEvaluator`: Generates realistic metric distributions with parameter effects

### UI Interaction Flow
1. **Optimizers Panel**: Select and configure algorithm → Propose policy
2. **Evals Panel**: Select workload → Run evaluation → Generate trial
3. **Experiments Panel**: View results → Toggle Pareto view → Adopt best policy

### Guardrails
- Policy adoption blocked if `tool_error_rate > 0.03` (main.py:270-271)
- Prevents deployment of unreliable configurations

## Gotchas & Common Issues

### 1. Python Version Compatibility
- **Critical**: Requires Python 3.13+
- `uv sync` may fail on older Python versions
- Check `.python-version` before development

### 2. Textual Framework Specifics
- Event handling uses Textual message system
- UI updates require explicit refresh calls
- CSS styling embedded in classes using string literals

### 3. Mock Implementation Limitations
- Real algorithms need to replace mock implementations
- Current mock data generation may not reflect real-world patterns
- Artifact management (DSPy) is simulated

### 4. Scoring Edge Cases
- Missing metrics default to zero in scoring
- Pareto comparison assumes 3D: latency, cost, (1-success)
- Weight changes require trial re-scoring (handled in UI)

### 5. State Management
- Backend is a global singleton (`BACKEND`)
- UI panels maintain independent state (selected indices)
- Message passing required for inter-panel coordination

## Project-Specific Context

### Current Status (Post-Fixes)
- ✅ Comprehensive README.md with accurate information
- ✅ Technical documentation in `skills/` directory
- ✅ Basic test infrastructure (placeholder tests)
- ✅ Corrected Textual version (≥0.47, not 6.6.0+)
- ✅ Single-file architecture (documented as intentional for now)
- ✅ Development dependencies configured (pytest)

## Remaining Limitations
- Single-file architecture may need refactoring for scalability
- Mock implementations need replacement with real algorithms
- Tests are placeholders (skipped) until real implementation
- No persistence for trial history

### Future Development Priorities
1. Replace mock implementations with real algorithms
2. Add comprehensive test suite
3. Implement persistent storage for trial history
4. Add export/import functionality for experiments
5. Extend UI with more visualization options
6. Add support for distributed evaluation

### Integration Points
- **DSPy Integration**: Ready for real DSPy optimizer (artifact-based)
- **Evaluation Systems**: Protocol allows custom evaluator implementations
- **External Metrics**: Can ingest metrics from real evaluation pipelines
- **Deployment Hooks**: Policy adoption generates action sequences for rollout

## Development Workflow Recommendations

1. **Start with Mock Improvements**: Enhance mock implementations for better simulation
2. **Add Unit Tests**: Test scoring logic and data structures first
3. **Iterate on Real Algorithms**: Replace mocks incrementally
4. **Expand UI Features**: Add visualization and analysis tools
5. **Performance Optimization**: Profile scoring and UI rendering

This codebase provides a solid foundation for optimization experimentation with clear separation between UI, backend logic, and algorithmic components. The mock-first approach makes it ideal for iterative development and testing of real optimization strategies.
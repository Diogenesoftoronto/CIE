# CIE Agent Benchmark System - Comprehensive Guide

## What is This?

The CIE Agent Benchmark is a **recursive/meta-level evaluation system** designed to measure how well AI agents can use the CIE project tools and environment. It's essentially testing agents on their ability to act as software engineers working within a real codebase.

Think of it as a "Computer Use Recursive Test" - we're testing the agent's ability to:
- Navigate and understand codebases
- Read and comprehend code
- Make targeted modifications
- Debug issues autonomously
- Implement complete features
- Write and run tests
- Manage complex multi-step workflows

## Quick Navigation

- **To run benchmarks**: See [Running Benchmarks](#running-benchmarks)
- **To understand tasks**: See [Task System](#task-system)
- **To interpret results**: See [Metrics & Analysis](#metrics--analysis)
- **To add new tasks**: See [Extending the System](#extending-the-system)
- **To use programmatically**: See [Python API](#python-api)

## System Overview

### Architecture

```
benchmark/
├── tasks.py          # 15 tasks across 5 difficulty levels
├── metrics.py        # Performance metrics collection & analysis
├── runner.py         # Benchmark orchestration engine
├── cli.py            # Command-line interface
├── example_usage.py  # Usage examples and scenarios
└── README.md         # Detailed documentation
```

### The Three Layers

1. **Tasks**: Well-defined evaluation tasks with success criteria
2. **Metrics**: Comprehensive performance measurement
3. **Runner**: Orchestration of task execution and result collection

## Task System

### 15 Tasks Across 5 Difficulty Levels

#### TRIVIAL (3 tasks) - 2 minutes each
Basic navigation and file reading. Establishes baseline capability.
- Read file and summarize
- List directory structure
- Find Python files by pattern

#### EASY (3 tasks) - 3-5 minutes each
Finding patterns, understanding interfaces, tracing dependencies.
- Find symbol usage across codebase
- Understand optimizer protocol
- Trace import dependencies

#### MEDIUM (4 tasks) - 5-8 minutes each
Making modifications, writing tests, updating config.
- Locate specific bugs
- Add configuration parameters
- Add new metrics to scoring system
- Write unit tests

#### HARD (3 tasks) - 12-15 minutes each
Implementing features, debugging complex issues, refactoring.
- Implement new evaluator from scratch
- Debug complex scoring issues
- Refactor for clarity and testability

#### EXPERT (3 tasks) - 25-30 minutes each
Complete workflows, architecture changes, cross-cutting concerns.
- Full evaluator plugin with tests and docs
- Add caching layer to backend
- Implement comprehensive logging system

### Task Categories (8 Areas)

Tasks are also organized by competency:

| Category | Purpose | Example |
|----------|---------|---------|
| Navigation | Finding files & understanding structure | Locate all Policy usages |
| Comprehension | Understanding code & design | Explain optimizer protocol |
| Modification | Making targeted code changes | Add configuration parameter |
| Debugging | Finding and fixing issues | Debug scoring logic |
| Implementation | Writing new code | Create new evaluator |
| Testing | Writing and running tests | Write unit test for Policy |
| Refactoring | Improving existing code | Extract method for clarity |
| Workflow | Multi-step complex tasks | Full feature implementation |

## Running Benchmarks

### Via Command Line

```bash
# List available tasks
python -m benchmark.cli list-tasks
python -m benchmark.cli list-tasks --difficulty hard
python -m benchmark.cli list-tasks --category implementation
python -m benchmark.cli show-task hard_implement_feature

# View statistics
python -m benchmark.cli stats

# Run benchmarks
python -m benchmark.cli run --model "GPT-4"
python -m benchmark.cli run --difficulty medium --model "Claude-3"
python -m benchmark.cli run --category implementation --model "Agent"
python -m benchmark.cli run --task-id trivial_read_file --model "Test"

# Save results
python -m benchmark.cli run --model "Agent" --output report.txt
python -m benchmark.cli run --model "Agent" --json-output metrics.json

# Advanced options
python -m benchmark.cli run --stop-on-failure --max-retries 3 --timeout 600
```

### Via Python API

```python
from benchmark.runner import BenchmarkRunner
from benchmark.tasks import TRIVIAL_TASKS, TaskDifficulty

# Create runner
runner = BenchmarkRunner(
    model_name="My-Agent",
    max_retries=2,
    timeout_seconds=300
)

# Define executor (how your agent runs tasks)
def execute_task(task):
    """Execute task and return (success, output, errors)"""
    try:
        result = your_agent.execute(task)
        return result.success, result.output, result.errors
    except Exception as e:
        return False, "", [str(e)]

# Run tasks
runner.run_task_set(TRIVIAL_TASKS, execute_task)

# Get report
print(runner.generate_report())

# Get metrics
metrics = runner.get_metrics()
print(f"Pass Rate: {metrics.pass_rate:.1f}%")
print(f"Composite Score: {metrics.average_composite_score:.1f}/100")
```

## Metrics & Analysis

### Per-Task Metrics

Each task execution collects:
- **Completion Status**: completed, failed, timeout, abandoned
- **Success**: Pass/fail against criteria
- **Tool Calls**: Total, successful, failed
- **Duration**: Execution time
- **Token Usage**: Estimated tokens consumed
- **Error Recovery**: Self-corrections made
- **Code Quality**: 0-100 score
- **Autonomy**: 0-100 score (100 = no hints needed)
- **Iterations**: Attempt cycles needed

### Aggregate Metrics

Across all tasks:
- **Pass Rate**: % of tasks successfully completed
- **Tool Efficiency**: % of tool calls that succeeded
- **Average Code Quality**: Mean code quality score
- **Average Autonomy**: Mean autonomy score
- **Error Recovery Rate**: % of errors successfully recovered
- **Composite Score**: Weighted overall performance

### Composite Score Formula

```
Score = (30% × Success)
      + (20% × Tool Efficiency)
      + (20% × Code Quality)
      + (15% × Autonomy)
      + (15% × Error Recovery)
```

### Performance Tiers

| Score | Level | Assessment |
|-------|-------|-----------|
| 90-100 | Expert | Excellent autonomous performance |
| 75-90 | Proficient | Good, some minor issues |
| 60-75 | Competent | Completes tasks, some struggles |
| 40-60 | Developing | Significant struggles |
| 0-40 | Novice | Poor performance |

## Example Results

### Sample Benchmark Report

```
================================================================================
BENCHMARK REPORT
================================================================================

Run ID: a1b2c3d4
Model: Claude-3-Opus
Timestamp: 2024-01-15T10:30:00

SUMMARY
--------------------------------------------------------------------------------
Total Tasks: 15
Passed: 12/15 (80.0%)
Failed: 3/15 (20.0%)

BY DIFFICULTY
--------------------------------------------------------------------------------
  trivial      3/3 (100.0%)
  easy         3/3 (100.0%)
  medium       4/4 (100.0%)
  hard         2/3 (66.7%)
  expert       0/2 (0.0%)

BY CATEGORY
--------------------------------------------------------------------------------
  navigation           3/3 (100.0%)
  comprehension        3/3 (100.0%)
  modification         4/4 (100.0%)
  debugging            1/2 (50.0%)
  implementation       2/3 (66.7%)
  workflow             1/2 (50.0%)

METRICS SUMMARY
--------------------------------------------------------------------------------
Total Tool Calls: 247
Total Errors: 12
Average Tool Efficiency: 95.1%
Average Code Quality: 82.3/100
Average Autonomy: 88.5/100
Average Composite Score: 85.2/100

================================================================================
```

### Interpretation Guide

- **100% Trivial/Easy**: Baseline established, ready for harder tasks
- **75%+ Medium**: Core competencies solid
- **50%+ Hard**: Can handle complex tasks with help
- **>0% Expert**: Capable of major projects

**Common Patterns**:
- High efficiency, low autonomy → Needs hints
- Low efficiency, high autonomy → Works but inefficiently
- High tool efficiency, high code quality → Well-tuned agent
- High error recovery → Good self-correction

## Python API

### Working with Tasks

```python
from benchmark.tasks import (
    BenchmarkTask,
    TaskDifficulty,
    TaskCategory,
    ALL_TASKS,
    get_tasks_by_difficulty,
    get_tasks_by_category
)

# Get tasks by difficulty
hard_tasks = get_tasks_by_difficulty(TaskDifficulty.HARD)

# Get tasks by category
impl_tasks = get_tasks_by_category(TaskCategory.IMPLEMENTATION)

# Inspect a task
for task in hard_tasks:
    print(f"ID: {task.task_id}")
    print(f"Title: {task.title}")
    print(f"Objective: {task.objective}")
    print(f"Time: {task.estimated_time_minutes} min")
    print(f"Criteria:")
    for criterion in task.success_criteria:
        print(f"  - {criterion}")
    if task.hints:
        print(f"Hints:")
        for hint in task.hints:
            print(f"  - {hint}")
```

### Collecting Metrics

```python
from benchmark.metrics import MetricsCollector

# Create collector
collector = MetricsCollector("run_001", model_name="My-Agent")

# Record task metrics
collector.record_task(
    task_id="trivial_read_file",
    completion_status="completed",
    success=True,
    total_tool_calls=3,
    successful_tool_calls=3,
    failed_tool_calls=0,
    error_recovery_count=0,
    duration_seconds=1.5,
    token_count=420,
    hints_requested=0,
    hints_used=0,
    code_quality_score=95,
    autonomy_score=100,
    iterations=1
)

# Finalize and get aggregate metrics
metrics = collector.finalize()
print(f"Pass Rate: {metrics.pass_rate:.1f}%")
print(f"Tool Efficiency: {metrics.average_tool_efficiency * 100:.1f}%")
print(f"Composite Score: {metrics.average_composite_score:.1f}/100")

# Print summary
print(collector.summary_report())
```

### Advanced: Comparing Models

```python
from benchmark.runner import BenchmarkRunner
from benchmark.tasks import ALL_TASKS

models = ["GPT-4", "Claude-3", "Llama-2"]
results = {}

for model_name in models:
    runner = BenchmarkRunner(model_name=model_name)
    
    def executor(task):
        return your_agent_api.evaluate(model_name, task)
    
    runner.run_task_set(ALL_TASKS, executor)
    results[model_name] = runner.get_metrics()

# Compare
for model_name, metrics in results.items():
    print(f"{model_name:15} Pass: {metrics.pass_rate:5.1f}% "
          f"Score: {metrics.average_composite_score:5.1f}")
```

## Extending the System

### Adding New Tasks

```python
from benchmark.tasks import BenchmarkTask, TaskCategory, TaskDifficulty

new_task = BenchmarkTask(
    task_id="custom_task_001",
    title="My Custom Task",
    description="What the agent needs to do",
    category=TaskCategory.IMPLEMENTATION,
    difficulty=TaskDifficulty.MEDIUM,
    objective="What should be accomplished",
    success_criteria=[
        "First criterion",
        "Second criterion",
        "Third criterion"
    ],
    context="Optional background information",
    hints=["First hint", "Second hint"],
    estimated_time_minutes=10,
    max_tool_calls=25,
    tags=["custom", "experimental"]
)

# Add to tasks
from benchmark.tasks import ALL_TASKS
ALL_TASKS.append(new_task)
```

### Custom Executors

```python
async def advanced_executor(task):
    """Advanced executor with real agent API"""
    agent = MyAdvancedAgent()
    
    try:
        result = await asyncio.wait_for(
            agent.execute(task),
            timeout=task.estimated_time_minutes * 60
        )
        
        return (
            result.success,
            result.output,
            result.errors
        )
    except Exception as e:
        return False, "", [str(e)]

runner = BenchmarkRunner(model_name="Advanced-Agent")
runner.run_task_set(ALL_TASKS, advanced_executor)
```

## Use Cases

### 1. Model Evaluation
Compare different AI models on their ability to work with code:
```bash
python -m benchmark.cli run --model "GPT-4" --output gpt4.txt
python -m benchmark.cli run --model "Claude-3" --output claude3.txt
# Compare reports
```

### 2. Capability Assessment
Identify agent strengths and weaknesses:
```bash
python -m benchmark.cli run --category implementation  # Implementation skills
python -m benchmark.cli run --category debugging       # Debugging skills
python -m benchmark.cli run --difficulty hard          # Advanced tasks
```

### 3. Continuous Improvement
Track progress over multiple benchmark runs:
```bash
# Run weekly
python -m benchmark.cli run --model "My-Agent" --json-output week1.json
python -m benchmark.cli run --model "My-Agent" --json-output week2.json
# Track improvement in pass rates
```

### 4. Feature Validation
Test new agent capabilities:
```bash
python -m benchmark.cli run --difficulty expert --model "New-Features"
```

## Test Suite

The benchmark system includes comprehensive tests:

```bash
# Run all benchmark tests
pytest tests/test_benchmark.py -v

# Run specific test class
pytest tests/test_benchmark.py::TestTaskDefinitions -v

# Run with coverage
pytest tests/test_benchmark.py --cov=benchmark
```

### Test Coverage

- ✅ Task definitions (15 tasks validated)
- ✅ Metrics collection (aggregation, scoring)
- ✅ Runner orchestration (execution flow)
- ✅ CLI interface (commands, options)
- ✅ Integration tests (end-to-end workflows)

## File Structure

```
CIE/
├── benchmark/
│   ├── __init__.py              # Package init
│   ├── tasks.py                 # 15 benchmark tasks
│   ├── metrics.py               # Metrics collection & analysis
│   ├── runner.py                # Benchmark orchestration
│   ├── cli.py                   # Command-line interface
│   ├── example_usage.py         # 6 usage examples
│   ├── README.md                # Detailed documentation
│   ├── templates/               # Task templates (future)
│   └── tasks/                   # Individual task files (future)
│
└── tests/
    └── test_benchmark.py         # Comprehensive tests (50+ tests)
```

## Key Concepts

### Success Criteria
Objective, verifiable requirements that must be met. Each task has 3-8 criteria.

### Tool Calls
Any invocation of a tool (read_file, edit_file, grep, etc.). Efficiency = successful calls / total calls.

### Code Quality
Subjective 0-100 score for how well generated code follows project patterns, includes error handling, and is maintainable.

### Autonomy
0-100 score for independent completion. 100 = no hints needed, 0 = required help for every step.

### Composite Score
Weighted combination of success, efficiency, quality, autonomy, and error recovery.

## Troubleshooting

### No tasks found
```bash
python -m benchmark.cli list-tasks
# Should show 15 tasks if system is working
```

### Import errors
```bash
# Ensure benchmark is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/CIE"
```

### CLI not working
```bash
# Try running as module
python -m benchmark.cli --help
# Or install as editable package
pip install -e /path/to/CIE
```

## Contributing

To enhance the benchmark system:

1. **Add Tasks**: Define in `tasks.py` with clear criteria
2. **Improve Metrics**: Extend `metrics.py` with new dimensions
3. **Add Tests**: Expand `test_benchmark.py`
4. **Document**: Update this guide with examples
5. **Submit**: PR with description of additions

## Further Reading

- `benchmark/README.md` - Detailed task descriptions and examples
- `benchmark/tasks.py` - All 15 task definitions
- `benchmark/example_usage.py` - 6 working usage scenarios
- `tests/test_benchmark.py` - 50+ test cases

## Questions?

For questions about:
- **Tasks**: Check `benchmark/tasks.py` for all definitions
- **Metrics**: See `benchmark/metrics.py` for calculation logic
- **Usage**: Review `benchmark/example_usage.py` for examples
- **Tests**: Examine `tests/test_benchmark.py` for patterns
- **CLI**: Run `python -m benchmark.cli --help`

---

**Last Updated**: 2024
**Version**: 1.0
**Status**: Production Ready
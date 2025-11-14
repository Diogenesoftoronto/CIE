# CIE Agent Benchmark System

## Overview

The CIE Agent Benchmark is a comprehensive testing framework designed to measure how well AI agents can use the CIE project tools and environment. It's a **recursive/meta-level evaluation** - testing agents' ability to navigate code, understand systems, make modifications, debug issues, and implement complete workflows.

This is essentially a "Computer Use Recursive Test" where we measure:
- **Navigation**: Can the agent find what it needs?
- **Comprehension**: Does it understand what it reads?
- **Modification**: Can it make targeted changes?
- **Testing**: Does it verify its work?
- **Debugging**: Can it fix problems autonomously?
- **Workflow**: Can it execute complex multi-step tasks?

## Task Structure

### Difficulty Levels

Tasks are organized into 5 difficulty levels:

| Level | Description | Examples |
|-------|-------------|----------|
| **TRIVIAL** | Read files, list directories, basic navigation | List project structure, read a file |
| **EASY** | Find patterns, understand interfaces, trace imports | Find symbol usage, explain optimizer interface |
| **MEDIUM** | Modify config, add metrics, write simple tests | Add configuration parameter, write unit test |
| **HARD** | Implement features, debug complex issues, refactor | Create new evaluator, fix scoring bugs |
| **EXPERT** | Complete workflows, architecture changes, cross-cutting concerns | Full evaluator with tests, add caching layer |

### Task Categories

Tasks are also organized by competency area:

- **Navigation**: Finding files and understanding project structure
- **Comprehension**: Reading and understanding code
- **Modification**: Making targeted code changes
- **Debugging**: Finding and fixing issues
- **Implementation**: Writing new code
- **Testing**: Writing and running tests
- **Refactoring**: Improving existing code
- **Workflow**: Multi-step complex tasks

## Quick Start

### List Available Tasks

```bash
# List all tasks
python -m benchmark.cli list-tasks

# List tasks by difficulty
python -m benchmark.cli list-tasks --difficulty medium

# List tasks by category
python -m benchmark.cli list-tasks --category implementation

# View task statistics
python -m benchmark.cli stats

# Show details for a specific task
python -m benchmark.cli show-task trivial_read_file
```

### Run Benchmarks

```bash
# Run all tasks (mock execution)
python -m benchmark.cli run --model "GPT-4"

# Run specific difficulty level
python -m benchmark.cli run --difficulty hard --model "Claude-3"

# Run specific category
python -m benchmark.cli run --category implementation --model "Llama-2"

# Run single task
python -m benchmark.cli run --task-id hard_implement_feature --model "My-Agent"

# Save report to file
python -m benchmark.cli run --model "Agent" --output report.txt

# Save metrics as JSON
python -m benchmark.cli run --model "Agent" --json-output metrics.json

# Stop on first failure
python -m benchmark.cli run --stop-on-failure
```

## Metrics

The benchmark system collects comprehensive metrics for each task:

### Per-Task Metrics

- **Completion Status**: completed, failed, timeout, abandoned
- **Success**: Whether task met all success criteria
- **Tool Calls**: Total, successful, and failed
- **Duration**: Execution time in seconds
- **Token Usage**: Estimated tokens consumed
- **Error Recovery**: Number of successful error recoveries
- **Code Quality**: 0-100 score for code quality
- **Autonomy**: 0-100 score for autonomous completion
- **Iterations**: Number of attempt cycles

### Aggregate Metrics

- **Pass Rate**: % of tasks successfully completed
- **Completion Rate**: % of tasks that completed
- **Tool Efficiency**: % of tool calls that succeeded
- **Average Code Quality**: Mean quality score
- **Average Autonomy**: Mean autonomy score
- **Total Errors**: Sum of all failed operations
- **Error Recovery Rate**: % of errors successfully recovered
- **Composite Score**: Weighted overall performance score

## Python API

### Running Benchmarks Programmatically

```python
from benchmark.runner import BenchmarkRunner
from benchmark.tasks import TaskDifficulty, TRIVIAL_TASKS

# Create runner
runner = BenchmarkRunner(
    model_name="My-Agent",
    max_retries=2,
    timeout_seconds=300
)

# Define executor function
def execute_task(task):
    """Execute a task and return (success, output, errors)."""
    try:
        # Call your agent/model here
        result = your_agent.execute(task)
        return result.success, result.output, result.errors
    except Exception as e:
        return False, "", [str(e)]

# Run tasks
results = runner.run_task_set(TRIVIAL_TASKS, execute_task)

# Generate report
report = runner.generate_report()
print(report)

# Get metrics
metrics = runner.get_metrics()
print(f"Pass Rate: {metrics.pass_rate:.1f}%")
print(f"Tool Efficiency: {metrics.average_tool_efficiency * 100:.1f}%")
```

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
implementation_tasks = get_tasks_by_category(TaskCategory.IMPLEMENTATION)

# Inspect a task
for task in hard_tasks:
    print(f"ID: {task.task_id}")
    print(f"Title: {task.title}")
    print(f"Objective: {task.objective}")
    print(f"Success Criteria:")
    for criterion in task.success_criteria:
        print(f"  - {criterion}")
    if task.hints:
        print(f"Hints:")
        for hint in task.hints:
            print(f"  - {hint}")
```

### Collecting Metrics

```python
from benchmark.metrics import MetricsCollector, TaskMetrics

# Create collector
collector = MetricsCollector("run_001", model_name="My-Agent")

# Record task metrics
for task_result in results:
    collector.record_task(
        task_id=task_result.task.task_id,
        completion_status="completed",
        success=task_result.success,
        total_tool_calls=task_result.metrics.tool_calls,
        successful_tool_calls=task_result.metrics.successful_calls,
        failed_tool_calls=task_result.metrics.failed_calls,
        error_recovery_count=task_result.metrics.recoveries,
        duration_seconds=task_result.metrics.duration,
        token_count=task_result.metrics.tokens,
        hints_requested=task_result.metrics.hints_requested,
        hints_used=task_result.metrics.hints_used,
        code_quality_score=task_result.metrics.code_quality,
        autonomy_score=task_result.metrics.autonomy,
        iterations=task_result.metrics.iterations
    )

# Finalize and get aggregate metrics
metrics = collector.finalize(configuration={"model": "My-Agent"})
print(metrics.pass_rate)
print(metrics.average_tool_efficiency)
print(metrics.average_composite_score)
```

## Task Examples

### Trivial Level: Read a File

```
Task ID: trivial_read_file
Title: Read and Summarize a File
Description: Read the core/models.py file and provide a summary
Objective: Explain what dataclasses it defines and their purposes
Success Criteria:
  1. Reads core/models.py successfully
  2. Identifies Policy, Trial, and Workload dataclasses
  3. Correctly describes their purposes
Estimated Time: ~2 minutes
Max Tool Calls: 5
```

### Medium Level: Add a Metric

```
Task ID: medium_add_metric
Title: Add New Metric to Scoring
Description: Add 'memory_usage' as a new scorable metric
Objective: Add memory_usage to Trial.metrics and update scoring
Success Criteria:
  1. Modifies Trial dataclass to include memory_usage
  2. Updates scoring functions if needed
  3. Changes follow project patterns
  4. Existing tests still pass
Estimated Time: ~7 minutes
Max Tool Calls: 20
Hints:
  - Check core/models.py for Trial structure
  - Look at how latency_p95 is used in scoring
```

### Expert Level: Complete Workflow

```
Task ID: expert_complete_workflow
Title: Implement Complete Evaluator Plugin
Description: Create a 'performance' evaluator with CPU, memory, latency
Objective: Implement full evaluator with registration, tests, docs
Success Criteria:
  1. Creates evaluators/plugins/performance.py
  2. Implements Evaluator protocol completely
  3. Provides CPU, memory, latency metrics
  4. Registers in plugin system
  5. Includes comprehensive docstrings
  6. Tests validate all metrics
  7. All tests pass
  8. README/docs updated
Estimated Time: ~25 minutes
Max Tool Calls: 50
Hints:
  - Review mock_evaluator.py for structure
  - Check evaluators/__init__.py for registration pattern
  - Plugin system allows drop-in evaluators
  - Include error handling and validation
```

## Scoring and Analysis

### Composite Score Breakdown

The composite score combines multiple metrics with weights:

```
Composite Score = (30% × Success) 
                + (20% × Tool Efficiency)
                + (20% × Code Quality)
                + (15% × Autonomy)
                + (15% × Error Recovery)
```

### Performance Tiers

| Score | Level | Assessment |
|-------|-------|-----------|
| 90-100 | Expert | Excellent autonomous performance |
| 75-90 | Proficient | Good performance with minor issues |
| 60-75 | Competent | Completes tasks with some struggles |
| 40-60 | Developing | Significant struggles but some success |
| 0-40 | Novice | Poor performance, needs significant help |

## Interpreting Results

### High Tool Efficiency (90%+)
- Agent makes targeted, effective tool calls
- Minimal trial-and-error
- Good planning and execution

### High Code Quality (80%+)
- Generated code follows project patterns
- Proper error handling
- Good documentation

### High Autonomy (90%+)
- Completes tasks without hints
- Self-corrects errors
- Doesn't request help unnecessarily

### High Error Recovery (80%+)
- Learns from failures
- Tries alternative approaches
- Recovers gracefully

## Benchmark Reports

### Report Sections

**SUMMARY**
- Total tasks attempted
- Pass/fail breakdown with percentages

**BY DIFFICULTY**
- Results broken down by difficulty level
- Shows progression through difficulty levels

**BY CATEGORY**
- Results broken down by competency area
- Shows strengths and weaknesses

**DETAILED RESULTS**
- Individual task status
- Duration and attempt count
- Error details for failures

**METRICS SUMMARY**
- Aggregate statistics
- Tool efficiency
- Code quality
- Autonomy scores
- Composite scores

### Example Report

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

METRICS SUMMARY
--------------------------------------------------------------------------------
Total Tool Calls: 247
Total Errors: 12
Average Tool Efficiency: 95.1%
Average Code Quality: 82.3/100
Average Autonomy: 88.5/100
Average Composite Score: 85.2/100
```

## Extending the Benchmark

### Adding New Tasks

```python
from benchmark.tasks import BenchmarkTask, TaskCategory, TaskDifficulty

new_task = BenchmarkTask(
    task_id="custom_task_001",
    title="My Custom Task",
    description="Description of what the task involves",
    category=TaskCategory.IMPLEMENTATION,
    difficulty=TaskDifficulty.MEDIUM,
    objective="What should be accomplished",
    success_criteria=[
        "First criterion",
        "Second criterion",
        "Third criterion"
    ],
    context="Optional background information",
    hints=[
        "First hint if agent struggles",
        "Second hint if still struggling"
    ],
    estimated_time_minutes=10,
    max_tool_calls=25,
    tags=["custom", "experimental"]
)

# Add to tasks collection
from benchmark.tasks import ALL_TASKS
ALL_TASKS.append(new_task)
```

### Custom Executors

```python
async def advanced_executor(task):
    """Advanced executor that uses real agent API."""
    agent = MyAdvancedAgent()
    
    try:
        # Execute with timeout
        result = await asyncio.wait_for(
            agent.execute(task),
            timeout=task.estimated_time_minutes * 60
        )
        
        # Extract tool calls and metrics
        tool_calls = len(result.tool_history)
        successful = sum(1 for t in result.tool_history if t.success)
        errors = [t.error for t in result.tool_history if not t.success]
        
        return (
            result.success,
            result.output,
            errors,
            {
                "tool_calls": tool_calls,
                "successful_calls": successful,
                "tokens_used": result.tokens,
                "duration": result.elapsed_seconds
            }
        )
    except Exception as e:
        return False, "", [str(e)]

# Use custom executor
runner = BenchmarkRunner(model_name="Advanced-Agent")
results = runner.run_task_set(ALL_TASKS, advanced_executor)
```

## Best Practices

### For Benchmark Authors

1. **Clear Criteria**: Success criteria should be objective and verifiable
2. **Realistic Scope**: Match estimated time to actual complexity
3. **Progressive Hints**: Provide hints that help without spoiling the solution
4. **Real Examples**: Base tasks on actual project needs
5. **Diverse Coverage**: Include all difficulty and category combinations

### For Agent Evaluation

1. **Start Simple**: Begin with trivial and easy tasks to establish baseline
2. **Track Progression**: Monitor how agents improve with difficulty
3. **Analyze Patterns**: Look for trends in which categories struggle
4. **Compare Models**: Run same tasks across different models for comparison
5. **Document Results**: Save detailed reports for analysis

## Related Work

This benchmark system is inspired by:
- **Computer Use Benchmarks**: Testing AI on computer tasks
- **Code Understanding Tasks**: Evaluating code comprehension
- **Software Engineering Benchmarks**: Multi-step programming tasks
- **Agentic Workflows**: Testing autonomous agent capabilities

## File Structure

```
benchmark/
├── __init__.py          # Package initialization
├── tasks.py             # Task definitions (trivial to expert)
├── metrics.py           # Metrics collection and analysis
├── runner.py            # Benchmark execution orchestration
├── cli.py               # Command-line interface
└── README.md            # This file
```

## Contributing

To add new tasks or improve the benchmark system:

1. Define new tasks in `tasks.py` with clear criteria
2. Add tests in `tests/test_benchmark.py`
3. Update documentation with examples
4. Run full benchmark suite to verify no regressions
5. Submit PR with description of additions

## Questions?

For questions about the benchmark system:
- Check existing task definitions for patterns
- Review test examples in `tests/test_benchmark.py`
- Examine the metrics system in `metrics.py`

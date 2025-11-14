"""Command-line interface for running benchmarks.

This module provides CLI commands for executing benchmark tasks,
viewing results, and generating reports.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from benchmark.metrics import BenchmarkMetrics
from benchmark.runner import BenchmarkRunner, TaskResult
from benchmark.tasks import (
    ALL_TASKS,
    TaskCategory,
    TaskDifficulty,
    get_tasks_by_category,
    get_tasks_by_difficulty,
)


@click.group()
def benchmark_cli():
    """Benchmark suite for measuring agent capability on CIE codebase tasks."""
    pass


@benchmark_cli.command()
@click.option(
    "--difficulty",
    type=click.Choice(["trivial", "easy", "medium", "hard", "expert"]),
    help="Run tasks at specific difficulty level",
)
@click.option(
    "--category",
    type=click.Choice([c.value for c in TaskCategory]),
    help="Run tasks in specific category",
)
@click.option("--task-id", help="Run specific task by ID")
@click.option("--model", default="unknown", help="Name of model/agent being tested")
@click.option("--output", type=click.Path(), help="Save report to file")
@click.option("--json-output", type=click.Path(), help="Save metrics as JSON")
@click.option("--max-retries", default=2, help="Maximum retries per task")
@click.option("--timeout", default=300, help="Timeout per task in seconds")
@click.option("--stop-on-failure", is_flag=True, help="Stop on first task failure")
def run(
    difficulty: Optional[str],
    category: Optional[str],
    task_id: Optional[str],
    model: str,
    output: Optional[str],
    json_output: Optional[str],
    max_retries: int,
    timeout: int,
    stop_on_failure: bool,
):
    """Run benchmark tasks and collect metrics."""

    runner = BenchmarkRunner(
        model_name=model,
        max_retries=max_retries,
        timeout_seconds=timeout,
    )

    # Determine which tasks to run
    if task_id:
        tasks = [t for t in ALL_TASKS if t.task_id == task_id]
        if not tasks:
            click.echo(f"Task not found: {task_id}", err=True)
            sys.exit(1)
    elif difficulty:
        diff_enum = TaskDifficulty(difficulty)
        tasks = get_tasks_by_difficulty(diff_enum)
    elif category:
        cat_enum = TaskCategory(category)
        tasks = get_tasks_by_category(cat_enum)
    else:
        tasks = ALL_TASKS

    click.echo(f"Running {len(tasks)} tasks for model: {model}")
    click.echo(f"Run ID: {runner.run_id}")
    click.echo()

    # Mock executor - in real use, this would be the actual agent
    def mock_executor(task):
        """Mock executor that simulates task completion."""
        # In real implementation, this would actually execute the task with the agent
        success = task.difficulty in [TaskDifficulty.TRIVIAL, TaskDifficulty.EASY]
        output = f"Executed: {task.task_id}"
        errors = [] if success else ["Mock execution error"]
        return success, output, errors

    # Run tasks
    runner.run_task_set(tasks, mock_executor, stop_on_failure=stop_on_failure)

    # Generate and display report
    report = runner.generate_report()
    click.echo(report)

    # Save report if requested
    if output:
        runner.save_report(output)
        click.echo(f"\nReport saved to: {output}")

    # Save metrics as JSON if requested
    if json_output:
        metrics = runner.get_metrics()
        metrics_dict = {
            "run_id": metrics.run_id,
            "model_name": metrics.model_name,
            "start_time": metrics.start_time.isoformat(),
            "end_time": metrics.end_time.isoformat() if metrics.end_time else None,
            "total_duration_seconds": metrics.total_duration_seconds,
            "tasks_completed": metrics.tasks_completed,
            "tasks_passed": metrics.tasks_passed,
            "pass_rate": metrics.pass_rate,
            "average_tool_efficiency": metrics.average_tool_efficiency,
            "average_code_quality": metrics.average_code_quality,
            "average_autonomy": metrics.average_autonomy,
            "total_tool_calls": metrics.total_tool_calls,
            "total_errors": metrics.total_errors,
            "average_composite_score": metrics.average_composite_score,
        }
        with open(json_output, "w") as f:
            json.dump(metrics_dict, f, indent=2)
        click.echo(f"Metrics saved to: {json_output}")


@benchmark_cli.command()
@click.option(
    "--difficulty",
    type=click.Choice(["trivial", "easy", "medium", "hard", "expert"]),
    help="List tasks at specific difficulty",
)
@click.option(
    "--category",
    type=click.Choice([c.value for c in TaskCategory]),
    help="List tasks in specific category",
)
def list_tasks(difficulty: Optional[str], category: Optional[str]):
    """List available benchmark tasks."""

    if difficulty:
        diff_enum = TaskDifficulty(difficulty)
        tasks = get_tasks_by_difficulty(diff_enum)
    elif category:
        cat_enum = TaskCategory(category)
        tasks = get_tasks_by_category(cat_enum)
    else:
        tasks = ALL_TASKS

    click.echo(f"Found {len(tasks)} tasks\n")

    for task in sorted(tasks, key=lambda t: (t.difficulty.value, t.category.value)):
        click.echo(f"[{task.difficulty.value.upper():6}] {task.task_id}")
        click.echo(f"  Title:    {task.title}")
        click.echo(f"  Category: {task.category.value}")
        click.echo(f"  Criteria: {len(task.success_criteria)} success criteria")
        if task.estimated_time_minutes:
            click.echo(f"  Est. Time: ~{task.estimated_time_minutes} min")
        click.echo()


@benchmark_cli.command()
@click.argument("task_id")
def show_task(task_id: str):
    """Show detailed information about a specific task."""

    task = next((t for t in ALL_TASKS if t.task_id == task_id), None)
    if not task:
        click.echo(f"Task not found: {task_id}", err=True)
        sys.exit(1)

    click.echo(f"Task: {task.task_id}")
    click.echo(f"Title: {task.title}")
    click.echo(f"Difficulty: {task.difficulty.value}")
    click.echo(f"Category: {task.category.value}")
    click.echo(f"Estimated Time: ~{task.estimated_time_minutes} minutes")
    click.echo(f"Max Tool Calls: {task.max_tool_calls}")
    click.echo()

    click.echo("DESCRIPTION")
    click.echo("-" * 80)
    click.echo(task.description)
    click.echo()

    if task.context:
        click.echo("CONTEXT")
        click.echo("-" * 80)
        click.echo(task.context)
        click.echo()

    click.echo("OBJECTIVE")
    click.echo("-" * 80)
    click.echo(task.objective)
    click.echo()

    click.echo("SUCCESS CRITERIA")
    click.echo("-" * 80)
    for i, criterion in enumerate(task.success_criteria, 1):
        click.echo(f"{i}. {criterion}")
    click.echo()

    if task.hints:
        click.echo("HINTS")
        click.echo("-" * 80)
        for i, hint in enumerate(task.hints, 1):
            click.echo(f"{i}. {hint}")
        click.echo()

    if task.tags:
        click.echo("TAGS")
        click.echo("-" * 80)
        click.echo(", ".join(task.tags))


@benchmark_cli.command()
def stats():
    """Show statistics about available tasks."""

    by_difficulty = {}
    by_category = {}

    for task in ALL_TASKS:
        diff = task.difficulty.value
        cat = task.category.value

        if diff not in by_difficulty:
            by_difficulty[diff] = 0
        if cat not in by_category:
            by_category[cat] = 0

        by_difficulty[diff] += 1
        by_category[cat] += 1

    click.echo("TASK STATISTICS")
    click.echo("-" * 80)
    click.echo(f"Total Tasks: {len(ALL_TASKS)}")
    click.echo()

    click.echo("BY DIFFICULTY")
    click.echo("-" * 80)
    for difficulty in ["trivial", "easy", "medium", "hard", "expert"]:
        count = by_difficulty.get(difficulty, 0)
        pct = count / len(ALL_TASKS) * 100 if ALL_TASKS else 0
        click.echo(f"  {difficulty:10}: {count:2} tasks ({pct:5.1f}%)")
    click.echo()

    click.echo("BY CATEGORY")
    click.echo("-" * 80)
    for category in sorted(by_category.keys()):
        count = by_category[category]
        pct = count / len(ALL_TASKS) * 100 if ALL_TASKS else 0
        click.echo(f"  {category:20}: {count:2} tasks ({pct:5.1f}%)")


if __name__ == "__main__":
    benchmark_cli()

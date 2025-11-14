"""Benchmark runner orchestration and task execution.

This module provides the core runner that executes benchmark tasks,
collects metrics, and generates reports on agent performance.
"""

import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from benchmark.metrics import MetricsCollector, TaskMetrics
from benchmark.tasks import BenchmarkTask, TaskCategory, TaskDifficulty


@dataclass
class TaskResult:
    """Result of a single task execution.

    Attributes:
        task: The task that was executed
        success: Whether the task completed successfully
        completion_status: 'completed', 'failed', 'timeout', 'abandoned'
        metrics: Metrics collected during execution
        output: Agent's final output or response
        errors: List of errors encountered
        attempts: Number of attempts made
        final_state: Final state description
    """

    task: BenchmarkTask
    success: bool
    completion_status: str
    metrics: TaskMetrics | None
    output: str = ""
    errors: list[str] = None
    attempts: int = 0
    final_state: str = ""

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.errors is None:
            self.errors = []


class BenchmarkRunner:
    """Orchestrates benchmark task execution and metrics collection.

    This class manages the execution of benchmark tasks, tracks metrics,
    handles errors and recovery, and generates reports.
    """

    def __init__(
        self,
        model_name: str = "unknown",
        max_retries: int = 2,
        timeout_seconds: int = 300,
    ):
        """Initialize benchmark runner.

        Args:
            model_name: Name of the model/agent being tested
            max_retries: Maximum retries for failed tasks
            timeout_seconds: Maximum time per task
        """
        self.model_name = model_name
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.run_id = str(uuid.uuid4())[:8]
        self.metrics_collector = MetricsCollector(self.run_id, model_name)
        self.results: list[TaskResult] = []

    def execute_task(
        self,
        task: BenchmarkTask,
        executor: Callable[[BenchmarkTask], tuple[bool, str, list[str]]],
        max_iterations: int = 10,
    ) -> TaskResult:
        """Execute a single benchmark task.

        Args:
            task: Task to execute
            executor: Callable that executes the task. Should return (success, output, errors)
            max_iterations: Maximum iterations for the task

        Returns:
            TaskResult with execution metrics and outcome
        """
        start_time = time.time()
        attempt = 0
        errors: list[str] = []
        output = ""
        success = False

        # Setup task if needed
        if task.setup_fn:
            try:
                task.setup_fn()
            except Exception as e:
                errors.append(f"Setup failed: {str(e)}")
                return TaskResult(
                    task=task,
                    success=False,
                    completion_status="failed",
                    metrics=None,
                    output="",
                    errors=errors,
                    attempts=1,
                )

        # Execute task with retries
        for attempt in range(self.max_retries + 1):
            elapsed = time.time() - start_time
            if elapsed > self.timeout_seconds:
                errors.append("Task timeout exceeded")
                break

            try:
                success, output, task_errors = executor(task)
                errors.extend(task_errors)

                if success:
                    break
            except Exception as e:
                errors.append(f"Execution error: {str(e)}")

        # Determine completion status
        elapsed = time.time() - start_time
        if elapsed > self.timeout_seconds:
            completion_status = "timeout"
        elif success:
            completion_status = "completed"
        else:
            completion_status = "failed"

        # Validate with validation_fn if available
        if success and task.validation_fn:
            try:
                if not task.validation_fn():
                    success = False
                    errors.append("Validation failed")
                    completion_status = "failed"
            except Exception as e:
                success = False
                errors.append(f"Validation error: {str(e)}")
                completion_status = "failed"

        # Record metrics
        task_metrics = self.metrics_collector.record_task(
            task_id=task.task_id,
            completion_status=completion_status,
            success=success,
            total_tool_calls=0,  # Would be tracked by executor
            successful_tool_calls=0,
            failed_tool_calls=len(errors),
            error_recovery_count=max(0, self.max_retries - attempt),
            duration_seconds=elapsed,
            token_count=0,  # Would be tracked by executor
            hints_requested=0,
            hints_used=0,
            code_quality_score=75 if success else 25,
            autonomy_score=100 if not errors else max(0, 100 - len(errors) * 10),
            iterations=attempt + 1,
            final_state=completion_status,
            notes="; ".join(errors) if errors else "Success",
        )

        result = TaskResult(
            task=task,
            success=success,
            completion_status=completion_status,
            metrics=task_metrics,
            output=output,
            errors=errors,
            attempts=attempt + 1,
            final_state=completion_status,
        )

        self.results.append(result)
        return result

    def run_task_set(
        self,
        tasks: list[BenchmarkTask],
        executor: Callable[[BenchmarkTask], tuple[bool, str, list[str]]],
        stop_on_failure: bool = False,
    ) -> list[TaskResult]:
        """Execute a set of benchmark tasks.

        Args:
            tasks: List of tasks to execute
            executor: Callable that executes tasks
            stop_on_failure: Stop execution on first failure

        Returns:
            List of TaskResults
        """
        results = []
        for i, task in enumerate(tasks):
            print(f"[{i + 1}/{len(tasks)}] Executing {task.title}...")
            result = self.execute_task(task, executor)
            results.append(result)

            status = "✓" if result.success else "✗"
            print(f"  {status} {result.completion_status}")

            if stop_on_failure and not result.success:
                print(f"  Stopping on failure")
                break

        return results

    def run_difficulty_level(
        self,
        difficulty: TaskDifficulty,
        executor: Callable[[BenchmarkTask], tuple[bool, str, list[str]]],
        stop_on_failure: bool = False,
    ) -> list[TaskResult]:
        """Execute all tasks at a specific difficulty level.

        Args:
            difficulty: Difficulty level to run
            executor: Callable that executes tasks
            stop_on_failure: Stop on first failure

        Returns:
            List of TaskResults
        """
        from benchmark.tasks import get_tasks_by_difficulty

        tasks = get_tasks_by_difficulty(difficulty)
        return self.run_task_set(tasks, executor, stop_on_failure)

    def run_category(
        self,
        category: TaskCategory,
        executor: Callable[[BenchmarkTask], tuple[bool, str, list[str]]],
        stop_on_failure: bool = False,
    ) -> list[TaskResult]:
        """Execute all tasks in a specific category.

        Args:
            category: Category to run
            executor: Callable that executes tasks
            stop_on_failure: Stop on first failure

        Returns:
            List of TaskResults
        """
        from benchmark.tasks import get_tasks_by_category

        tasks = get_tasks_by_category(category)
        return self.run_task_set(tasks, executor, stop_on_failure)

    def run_all(
        self,
        executor: Callable[[BenchmarkTask], tuple[bool, str, list[str]]],
        stop_on_failure: bool = False,
    ) -> list[TaskResult]:
        """Execute all benchmark tasks.

        Args:
            executor: Callable that executes tasks
            stop_on_failure: Stop on first failure

        Returns:
            List of TaskResults
        """
        from benchmark.tasks import ALL_TASKS

        return self.run_task_set(ALL_TASKS, executor, stop_on_failure)

    def get_metrics(self, configuration: dict[str, Any] | None = None):
        """Get aggregate metrics for the benchmark run.

        Args:
            configuration: Configuration used for the run

        Returns:
            BenchmarkMetrics object
        """
        return self.metrics_collector.finalize(configuration)

    def generate_report(self) -> str:
        """Generate a comprehensive report of benchmark results.

        Returns:
            Formatted report string
        """
        lines = [
            "=" * 80,
            "BENCHMARK REPORT",
            "=" * 80,
            "",
            f"Run ID: {self.run_id}",
            f"Model: {self.model_name}",
            f"Timestamp: {datetime.now().isoformat()}",
            "",
        ]

        if not self.results:
            lines.append("No tasks executed.")
            return "\n".join(lines)

        # Summary statistics
        passed = sum(1 for r in self.results if r.success)
        total = len(self.results)
        lines.extend(
            [
                "SUMMARY",
                "-" * 80,
                f"Total Tasks: {total}",
                f"Passed: {passed}/{total} ({passed / total * 100:.1f}%)",
                f"Failed: {total - passed}/{total} ({(total - passed) / total * 100:.1f}%)",
                "",
            ]
        )

        # Difficulty breakdown
        by_difficulty = {}
        for result in self.results:
            diff = result.task.difficulty.value
            if diff not in by_difficulty:
                by_difficulty[diff] = {"passed": 0, "total": 0}
            by_difficulty[diff]["total"] += 1
            if result.success:
                by_difficulty[diff]["passed"] += 1

        lines.append("BY DIFFICULTY")
        lines.append("-" * 80)
        for difficulty in ["trivial", "easy", "medium", "hard", "expert"]:
            if difficulty in by_difficulty:
                stats = by_difficulty[difficulty]
                rate = stats["passed"] / stats["total"] * 100
                lines.append(
                    f"  {difficulty:10} {stats['passed']:2}/{stats['total']:2} ({rate:5.1f}%)"
                )
        lines.append("")

        # Category breakdown
        by_category = {}
        for result in self.results:
            cat = result.task.category.value
            if cat not in by_category:
                by_category[cat] = {"passed": 0, "total": 0}
            by_category[cat]["total"] += 1
            if result.success:
                by_category[cat]["passed"] += 1

        lines.append("BY CATEGORY")
        lines.append("-" * 80)
        for category in sorted(by_category.keys()):
            stats = by_category[category]
            rate = stats["passed"] / stats["total"] * 100
            lines.append(f"  {category:20} {stats['passed']:2}/{stats['total']:2} ({rate:5.1f}%)")
        lines.append("")

        # Detailed results
        lines.extend(
            [
                "DETAILED RESULTS",
                "-" * 80,
            ]
        )

        for result in self.results:
            status = "✓ PASS" if result.success else "✗ FAIL"
            lines.append(f"{status} | {result.task.task_id}")
            lines.append(f"      {result.task.title}")
            if result.metrics:
                lines.append(
                    f"      Duration: {result.metrics.duration_seconds:.1f}s | "
                    f"Attempts: {result.attempts} | "
                    f"Errors: {len(result.errors)}"
                )
            if result.errors:
                lines.append(f"      Errors: {'; '.join(result.errors[:2])}")
            lines.append("")

        # Metrics summary
        metrics = self.get_metrics()
        lines.extend(
            [
                "METRICS SUMMARY",
                "-" * 80,
                f"Total Tool Calls: {metrics.total_tool_calls}",
                f"Total Errors: {metrics.total_errors}",
                f"Average Tool Efficiency: {metrics.average_tool_efficiency * 100:.1f}%",
                f"Average Code Quality: {metrics.average_code_quality:.1f}/100",
                f"Average Autonomy: {metrics.average_autonomy:.1f}/100",
                f"Average Composite Score: {metrics.average_composite_score:.1f}/100",
                "",
            ]
        )

        lines.extend(
            [
                "=" * 80,
            ]
        )

        return "\n".join(lines)

    def save_report(self, filepath: str) -> None:
        """Save benchmark report to a file.

        Args:
            filepath: Path where report should be saved
        """
        with open(filepath, "w") as f:
            f.write(self.generate_report())

    def get_failed_tasks(self) -> list[TaskResult]:
        """Get all tasks that failed.

        Returns:
            List of failed TaskResults
        """
        return [r for r in self.results if not r.success]

    def get_slow_tasks(self, threshold_seconds: float = 30.0) -> list[TaskResult]:
        """Get tasks that took longer than threshold.

        Args:
            threshold_seconds: Duration threshold

        Returns:
            List of slow TaskResults
        """
        return [
            r for r in self.results if r.metrics and r.metrics.duration_seconds > threshold_seconds
        ]

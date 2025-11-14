"""Metrics collection and analysis for benchmark performance.

This module defines the metrics collected during benchmark task execution
and provides analysis tools to understand agent performance across different
dimensions (speed, efficiency, quality, autonomy).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class TaskMetrics:
    """Metrics collected for a single task execution.

    Attributes:
        task_id: Identifier of the task
        timestamp: When the task was executed
        completion_status: 'completed', 'failed', 'timeout', 'abandoned'
        success: Whether task met all success criteria
        total_tool_calls: Number of tool invocations
        successful_tool_calls: Tool calls that succeeded
        failed_tool_calls: Tool calls that resulted in errors
        error_recovery_count: Number of times agent recovered from errors
        start_time: Epoch timestamp when task started
        end_time: Epoch timestamp when task ended
        duration_seconds: Total execution time
        token_count: Estimated tokens used
        hints_requested: Number of hints agent asked for
        hints_used: Number of hints actually helpful
        code_quality_score: 0-100 score for code quality
        autonomy_score: 0-100 score for autonomous completion (100 = no hints)
        tool_call_efficiency: successful_calls / total_calls ratio
        error_recovery_rate: error_recovery_count / failed_tool_calls (or 0)
        iterations: Number of attempt cycles
        final_state: Description of final state
        notes: Free-form notes about execution
    """

    task_id: str
    timestamp: datetime
    completion_status: str  # completed, failed, timeout, abandoned
    success: bool
    total_tool_calls: int
    successful_tool_calls: int
    failed_tool_calls: int
    error_recovery_count: int
    start_time: float
    end_time: float
    duration_seconds: float
    token_count: int
    hints_requested: int
    hints_used: int
    code_quality_score: int
    autonomy_score: int
    tool_call_efficiency: float
    error_recovery_rate: float
    iterations: int
    final_state: str = ""
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """Task passed if successful and completed."""
        return self.success and self.completion_status == "completed"

    @property
    def tool_efficiency_score(self) -> float:
        """Score for efficient tool usage (0-100)."""
        if self.total_tool_calls == 0:
            return 100.0
        # Penalize excessive tool calls, reward efficiency
        efficiency = self.successful_tool_calls / self.total_tool_calls
        # Normalize to 0-100 but cap based on excessive calls
        return min(100.0, efficiency * 100.0)

    @property
    def recovery_score(self) -> float:
        """Score for error handling and recovery (0-100)."""
        if self.failed_tool_calls == 0:
            return 100.0  # No errors = perfect recovery
        if self.failed_tool_calls == 0:
            return 0.0  # Failed to recover from errors
        return min(100.0, (self.error_recovery_rate * 100.0))

    @property
    def composite_score(self) -> float:
        """Weighted composite score combining multiple metrics."""
        weights = {
            "success": 0.30,
            "tool_efficiency": 0.20,
            "code_quality": 0.20,
            "autonomy": 0.15,
            "recovery": 0.15,
        }

        score = (
            (100.0 if self.success else 0.0) * weights["success"]
            + self.tool_efficiency_score * weights["tool_efficiency"]
            + self.code_quality_score * weights["code_quality"]
            + self.autonomy_score * weights["autonomy"]
            + self.recovery_score * weights["recovery"]
        )
        return score


@dataclass
class BenchmarkMetrics:
    """Aggregate metrics for a complete benchmark run.

    Attributes:
        run_id: Unique identifier for this benchmark run
        start_time: When the benchmark started
        end_time: When the benchmark finished
        total_duration_seconds: Total execution time
        tasks_completed: Number of tasks that completed
        tasks_passed: Number of tasks that passed all criteria
        pass_rate: Percentage of tasks passed
        completion_rate: Percentage of tasks completed
        average_success_rate: Mean success rate across tasks
        average_tool_efficiency: Mean tool call efficiency
        average_code_quality: Mean code quality score
        average_autonomy: Mean autonomy score
        total_tool_calls: Sum of all tool calls
        total_errors: Sum of all failed tool calls
        total_token_usage: Estimated tokens used
        error_recovery_rate: Overall error recovery percentage
        task_results: Individual task metrics
        model_name: Which model/agent was tested
        configuration: Configuration used for the run
    """

    run_id: str
    start_time: datetime
    end_time: datetime | None
    total_duration_seconds: float
    tasks_completed: int
    tasks_passed: int
    pass_rate: float
    completion_rate: float
    average_success_rate: float
    average_tool_efficiency: float
    average_code_quality: float
    average_autonomy: float
    total_tool_calls: int
    total_errors: int
    total_token_usage: int
    error_recovery_rate: float
    task_results: list[TaskMetrics] = field(default_factory=list)
    model_name: str = "unknown"
    configuration: dict[str, Any] = field(default_factory=dict)

    @property
    def average_composite_score(self) -> float:
        """Average composite score across all tasks."""
        if not self.task_results:
            return 0.0
        return sum(t.composite_score for t in self.task_results) / len(self.task_results)

    @property
    def median_duration(self) -> float:
        """Median task duration in seconds."""
        if not self.task_results:
            return 0.0
        durations = sorted([t.duration_seconds for t in self.task_results])
        n = len(durations)
        if n % 2 == 0:
            return (durations[n // 2 - 1] + durations[n // 2]) / 2.0
        return float(durations[n // 2])


class MetricsCollector:
    """Collects and analyzes metrics during benchmark execution.

    This class tracks metrics as tasks are executed and provides
    aggregation and analysis capabilities.
    """

    def __init__(self, run_id: str, model_name: str = "unknown"):
        """Initialize metrics collector.

        Args:
            run_id: Unique identifier for this benchmark run
            model_name: Name of the model/agent being benchmarked
        """
        self.run_id = run_id
        self.model_name = model_name
        self.start_time = datetime.now()
        self.task_metrics: list[TaskMetrics] = []

    def record_task(
        self,
        task_id: str,
        completion_status: str,
        success: bool,
        total_tool_calls: int,
        successful_tool_calls: int,
        failed_tool_calls: int,
        error_recovery_count: int,
        duration_seconds: float,
        token_count: int,
        hints_requested: int,
        hints_used: int,
        code_quality_score: int,
        autonomy_score: int,
        iterations: int,
        final_state: str = "",
        notes: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> TaskMetrics:
        """Record metrics for a completed task.

        Args:
            task_id: Task identifier
            completion_status: 'completed', 'failed', 'timeout', 'abandoned'
            success: Whether task met success criteria
            total_tool_calls: Number of tool calls made
            successful_tool_calls: Tool calls that succeeded
            failed_tool_calls: Tool calls that failed
            error_recovery_count: Times agent recovered from errors
            duration_seconds: Execution time
            token_count: Tokens used
            hints_requested: Number of hints requested
            hints_used: Number of hints that were actually useful
            code_quality_score: Quality score (0-100)
            autonomy_score: Autonomy score (0-100)
            iterations: Number of iteration cycles
            final_state: Final state description
            notes: Additional notes
            metadata: Additional metadata

        Returns:
            TaskMetrics object that was recorded
        """
        if metadata is None:
            metadata = {}

        tool_call_efficiency = (
            successful_tool_calls / total_tool_calls if total_tool_calls > 0 else 0.0
        )

        error_recovery_rate = (
            error_recovery_count / failed_tool_calls if failed_tool_calls > 0 else 0.0
        )

        metrics = TaskMetrics(
            task_id=task_id,
            timestamp=datetime.now(),
            completion_status=completion_status,
            success=success,
            total_tool_calls=total_tool_calls,
            successful_tool_calls=successful_tool_calls,
            failed_tool_calls=failed_tool_calls,
            error_recovery_count=error_recovery_count,
            start_time=datetime.now().timestamp() - duration_seconds,
            end_time=datetime.now().timestamp(),
            duration_seconds=duration_seconds,
            token_count=token_count,
            hints_requested=hints_requested,
            hints_used=hints_used,
            code_quality_score=code_quality_score,
            autonomy_score=autonomy_score,
            tool_call_efficiency=tool_call_efficiency,
            error_recovery_rate=error_recovery_rate,
            iterations=iterations,
            final_state=final_state,
            notes=notes,
            metadata=metadata,
        )

        self.task_metrics.append(metrics)
        return metrics

    def finalize(self, configuration: dict[str, Any] | None = None) -> BenchmarkMetrics:
        """Finalize the benchmark run and return aggregate metrics.

        Args:
            configuration: Configuration used for the run

        Returns:
            BenchmarkMetrics with aggregate statistics
        """
        if configuration is None:
            configuration = {}

        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        tasks_completed = len(self.task_metrics)
        tasks_passed = sum(1 for t in self.task_metrics if t.passed)

        completion_rate = 100.0  # All recorded tasks are completed
        pass_rate = (tasks_passed / tasks_completed * 100.0) if tasks_completed > 0 else 0.0

        average_success_rate = (
            sum(1 for t in self.task_metrics if t.success) / tasks_completed * 100.0
            if tasks_completed > 0
            else 0.0
        )

        average_tool_efficiency = (
            sum(t.tool_call_efficiency for t in self.task_metrics) / tasks_completed
            if tasks_completed > 0
            else 0.0
        )

        average_code_quality = (
            sum(t.code_quality_score for t in self.task_metrics) / tasks_completed
            if tasks_completed > 0
            else 0.0
        )

        average_autonomy = (
            sum(t.autonomy_score for t in self.task_metrics) / tasks_completed
            if tasks_completed > 0
            else 0.0
        )

        total_tool_calls = sum(t.total_tool_calls for t in self.task_metrics)
        total_errors = sum(t.failed_tool_calls for t in self.task_metrics)
        total_token_usage = sum(t.token_count for t in self.task_metrics)

        error_recovery_rate = (
            sum(t.error_recovery_count for t in self.task_metrics) / total_errors * 100.0
            if total_errors > 0
            else 100.0
        )

        return BenchmarkMetrics(
            run_id=self.run_id,
            start_time=self.start_time,
            end_time=end_time,
            total_duration_seconds=total_duration,
            tasks_completed=tasks_completed,
            tasks_passed=tasks_passed,
            pass_rate=pass_rate,
            completion_rate=completion_rate,
            average_success_rate=average_success_rate,
            average_tool_efficiency=average_tool_efficiency,
            average_code_quality=average_code_quality,
            average_autonomy=average_autonomy,
            total_tool_calls=total_tool_calls,
            total_errors=total_errors,
            total_token_usage=total_token_usage,
            error_recovery_rate=error_recovery_rate,
            task_results=self.task_metrics,
            model_name=self.model_name,
            configuration=configuration,
        )

    def summary_report(self) -> str:
        """Generate a human-readable summary report of metrics collected so far.

        Returns:
            Formatted string with summary statistics
        """
        lines = [
            f"Benchmark Run: {self.run_id}",
            f"Model: {self.model_name}",
            f"Tasks: {len(self.task_metrics)}",
            "",
        ]

        if not self.task_metrics:
            lines.append("No tasks recorded yet.")
            return "\n".join(lines)

        passed = sum(1 for t in self.task_metrics if t.passed)
        lines.append(
            f"Pass Rate: {passed}/{len(self.task_metrics)} ({passed / len(self.task_metrics) * 100:.1f}%)"
        )

        avg_duration = sum(t.duration_seconds for t in self.task_metrics) / len(self.task_metrics)
        lines.append(f"Average Duration: {avg_duration:.1f}s")

        total_calls = sum(t.total_tool_calls for t in self.task_metrics)
        total_errors = sum(t.failed_tool_calls for t in self.task_metrics)
        lines.append(f"Tool Calls: {total_calls} ({total_errors} errors)")

        avg_efficiency = sum(t.tool_call_efficiency for t in self.task_metrics) / len(
            self.task_metrics
        )
        lines.append(f"Average Tool Efficiency: {avg_efficiency * 100:.1f}%")

        avg_quality = sum(t.code_quality_score for t in self.task_metrics) / len(self.task_metrics)
        lines.append(f"Average Code Quality: {avg_quality:.1f}/100")

        avg_autonomy = sum(t.autonomy_score for t in self.task_metrics) / len(self.task_metrics)
        lines.append(f"Average Autonomy: {avg_autonomy:.1f}/100")

        return "\n".join(lines)

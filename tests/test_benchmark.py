"""Comprehensive tests for the benchmark system.

This module tests the benchmark framework including task definitions,
metrics collection, and benchmark execution.
"""

import time
from datetime import datetime

import pytest

from benchmark.metrics import BenchmarkMetrics, MetricsCollector, TaskMetrics
from benchmark.runner import BenchmarkRunner, TaskResult
from benchmark.tasks import (
    ALL_TASKS,
    EASY_TASKS,
    EXPERT_TASKS,
    HARD_TASKS,
    MEDIUM_TASKS,
    TRIVIAL_TASKS,
    BenchmarkTask,
    TaskCategory,
    TaskDifficulty,
    get_tasks_by_category,
    get_tasks_by_difficulty,
)


class TestTaskDefinitions:
    """Test benchmark task definitions."""

    def test_trivial_tasks_exist(self):
        """Verify trivial tasks are defined."""
        assert len(TRIVIAL_TASKS) >= 3
        assert all(t.difficulty == TaskDifficulty.TRIVIAL for t in TRIVIAL_TASKS)

    def test_easy_tasks_exist(self):
        """Verify easy tasks are defined."""
        assert len(EASY_TASKS) >= 3
        assert all(t.difficulty == TaskDifficulty.EASY for t in EASY_TASKS)

    def test_medium_tasks_exist(self):
        """Verify medium tasks are defined."""
        assert len(MEDIUM_TASKS) >= 4
        assert all(t.difficulty == TaskDifficulty.MEDIUM for t in MEDIUM_TASKS)

    def test_hard_tasks_exist(self):
        """Verify hard tasks are defined."""
        assert len(HARD_TASKS) >= 3
        assert all(t.difficulty == TaskDifficulty.HARD for t in HARD_TASKS)

    def test_expert_tasks_exist(self):
        """Verify expert tasks are defined."""
        assert len(EXPERT_TASKS) >= 3
        assert all(t.difficulty == TaskDifficulty.EXPERT for t in EXPERT_TASKS)

    def test_all_tasks_collection(self):
        """Verify all tasks are in the collection."""
        total = len(TRIVIAL_TASKS + EASY_TASKS + MEDIUM_TASKS + HARD_TASKS + EXPERT_TASKS)
        assert len(ALL_TASKS) == total

    def test_task_has_required_fields(self):
        """Verify tasks have required fields."""
        for task in ALL_TASKS[:3]:  # Check first 3 tasks
            assert task.task_id
            assert task.title
            assert task.description
            assert task.objective
            assert len(task.success_criteria) > 0
            assert task.category in TaskCategory
            assert task.difficulty in TaskDifficulty

    def test_task_hashable(self):
        """Verify tasks can be hashed and used in sets."""
        task = TRIVIAL_TASKS[0]
        task_set = {task}
        assert task in task_set
        assert hash(task) is not None

    def test_task_equality(self):
        """Verify task equality works."""
        task1 = TRIVIAL_TASKS[0]
        task2 = TRIVIAL_TASKS[0]
        assert task1 == task2

    def test_get_tasks_by_difficulty(self):
        """Verify getting tasks by difficulty."""
        for difficulty in TaskDifficulty:
            tasks = get_tasks_by_difficulty(difficulty)
            assert all(t.difficulty == difficulty for t in tasks)
            assert len(tasks) > 0

    def test_get_tasks_by_category(self):
        """Verify getting tasks by category."""
        for category in TaskCategory:
            tasks = get_tasks_by_category(category)
            if tasks:  # Some categories might be empty
                assert all(t.category == category for t in tasks)


class TestTaskMetrics:
    """Test task metrics collection."""

    def test_task_metrics_creation(self):
        """Verify task metrics can be created."""
        metrics = TaskMetrics(
            task_id="test_task",
            timestamp=datetime.now(),
            completion_status="completed",
            success=True,
            total_tool_calls=10,
            successful_tool_calls=9,
            failed_tool_calls=1,
            error_recovery_count=1,
            start_time=time.time() - 5,
            end_time=time.time(),
            duration_seconds=5.0,
            token_count=1000,
            hints_requested=0,
            hints_used=0,
            code_quality_score=85,
            autonomy_score=95,
            tool_call_efficiency=0.9,
            error_recovery_rate=1.0,
            iterations=1,
        )
        assert metrics.task_id == "test_task"
        assert metrics.success is True
        assert metrics.passed is True

    def test_task_metrics_passed_property(self):
        """Verify passed property works correctly."""
        metrics_passed = TaskMetrics(
            task_id="test",
            timestamp=datetime.now(),
            completion_status="completed",
            success=True,
            total_tool_calls=5,
            successful_tool_calls=5,
            failed_tool_calls=0,
            error_recovery_count=0,
            start_time=time.time(),
            end_time=time.time(),
            duration_seconds=1.0,
            token_count=100,
            hints_requested=0,
            hints_used=0,
            code_quality_score=90,
            autonomy_score=100,
            tool_call_efficiency=1.0,
            error_recovery_rate=0.0,
            iterations=1,
        )
        assert metrics_passed.passed is True

        metrics_failed = TaskMetrics(
            task_id="test",
            timestamp=datetime.now(),
            completion_status="failed",
            success=False,
            total_tool_calls=10,
            successful_tool_calls=5,
            failed_tool_calls=5,
            error_recovery_count=0,
            start_time=time.time(),
            end_time=time.time(),
            duration_seconds=2.0,
            token_count=200,
            hints_requested=1,
            hints_used=0,
            code_quality_score=40,
            autonomy_score=80,
            tool_call_efficiency=0.5,
            error_recovery_rate=0.0,
            iterations=2,
        )
        assert metrics_failed.passed is False

    def test_composite_score_calculation(self):
        """Verify composite score calculation."""
        metrics = TaskMetrics(
            task_id="test",
            timestamp=datetime.now(),
            completion_status="completed",
            success=True,
            total_tool_calls=10,
            successful_tool_calls=10,
            failed_tool_calls=0,
            error_recovery_count=0,
            start_time=time.time(),
            end_time=time.time(),
            duration_seconds=1.0,
            token_count=100,
            hints_requested=0,
            hints_used=0,
            code_quality_score=100,
            autonomy_score=100,
            tool_call_efficiency=1.0,
            error_recovery_rate=0.0,
            iterations=1,
        )
        # Perfect score should be close to 100
        assert metrics.composite_score > 90


class TestMetricsCollector:
    """Test metrics collection functionality."""

    def test_collector_creation(self):
        """Verify metrics collector can be created."""
        collector = MetricsCollector("run_001", "TestModel")
        assert collector.run_id == "run_001"
        assert collector.model_name == "TestModel"
        assert len(collector.task_metrics) == 0

    def test_record_single_task(self):
        """Verify recording a single task."""
        collector = MetricsCollector("run_001", "TestModel")
        metrics = collector.record_task(
            task_id="task_1",
            completion_status="completed",
            success=True,
            total_tool_calls=5,
            successful_tool_calls=5,
            failed_tool_calls=0,
            error_recovery_count=0,
            duration_seconds=2.0,
            token_count=500,
            hints_requested=0,
            hints_used=0,
            code_quality_score=85,
            autonomy_score=100,
            iterations=1,
        )
        assert len(collector.task_metrics) == 1
        assert metrics.task_id == "task_1"
        assert metrics.success is True

    def test_record_multiple_tasks(self):
        """Verify recording multiple tasks."""
        collector = MetricsCollector("run_001", "TestModel")
        for i in range(5):
            collector.record_task(
                task_id=f"task_{i}",
                completion_status="completed",
                success=i < 3,  # First 3 pass
                total_tool_calls=5,
                successful_tool_calls=5 if i < 3 else 3,
                failed_tool_calls=0 if i < 3 else 2,
                error_recovery_count=0,
                duration_seconds=1.0,
                token_count=100,
                hints_requested=0,
                hints_used=0,
                code_quality_score=90 if i < 3 else 50,
                autonomy_score=100 if i < 3 else 70,
                iterations=1 if i < 3 else 2,
            )

        assert len(collector.task_metrics) == 5

    def test_finalize_metrics(self):
        """Verify finalizing metrics."""
        collector = MetricsCollector("run_001", "TestModel")
        for i in range(3):
            collector.record_task(
                task_id=f"task_{i}",
                completion_status="completed",
                success=True,
                total_tool_calls=5,
                successful_tool_calls=5,
                failed_tool_calls=0,
                error_recovery_count=0,
                duration_seconds=1.0,
                token_count=100,
                hints_requested=0,
                hints_used=0,
                code_quality_score=90,
                autonomy_score=100,
                iterations=1,
            )

        metrics = collector.finalize()
        assert isinstance(metrics, BenchmarkMetrics)
        assert metrics.tasks_completed == 3
        assert metrics.tasks_passed == 3
        assert metrics.pass_rate == 100.0

    def test_summary_report_generation(self):
        """Verify summary report generation."""
        collector = MetricsCollector("run_001", "TestModel")
        for i in range(3):
            collector.record_task(
                task_id=f"task_{i}",
                completion_status="completed",
                success=True,
                total_tool_calls=5,
                successful_tool_calls=5,
                failed_tool_calls=0,
                error_recovery_count=0,
                duration_seconds=1.0,
                token_count=100,
                hints_requested=0,
                hints_used=0,
                code_quality_score=90,
                autonomy_score=100,
                iterations=1,
            )

        report = collector.summary_report()
        assert isinstance(report, str)
        assert "run_001" in report
        assert "TestModel" in report
        assert "Pass Rate" in report


class TestBenchmarkRunner:
    """Test benchmark runner functionality."""

    def test_runner_creation(self):
        """Verify runner can be created."""
        runner = BenchmarkRunner(model_name="TestModel")
        assert runner.model_name == "TestModel"
        assert runner.max_retries == 2
        assert runner.timeout_seconds == 300
        assert len(runner.results) == 0

    def test_execute_single_task(self):
        """Verify executing a single task."""
        runner = BenchmarkRunner(model_name="TestModel")

        def mock_executor(task):
            return True, f"Completed {task.task_id}", []

        task = TRIVIAL_TASKS[0]
        result = runner.execute_task(task, mock_executor)

        assert isinstance(result, TaskResult)
        assert result.task == task
        assert result.success is True
        assert len(runner.results) == 1

    def test_execute_task_with_failure(self):
        """Verify task execution with failure."""
        runner = BenchmarkRunner(model_name="TestModel")

        def mock_executor(task):
            return False, "", ["Mock error"]

        task = TRIVIAL_TASKS[0]
        result = runner.execute_task(task, mock_executor)

        assert result.success is False
        assert len(result.errors) > 0

    def test_execute_task_set(self):
        """Verify executing a set of tasks."""
        runner = BenchmarkRunner(model_name="TestModel")

        def mock_executor(task):
            return True, f"Completed {task.task_id}", []

        results = runner.run_task_set(TRIVIAL_TASKS, mock_executor)

        assert len(results) == len(TRIVIAL_TASKS)
        assert all(r.success for r in results)

    def test_run_by_difficulty(self):
        """Verify running tasks by difficulty."""
        runner = BenchmarkRunner(model_name="TestModel")

        def mock_executor(task):
            return True, f"Completed {task.task_id}", []

        results = runner.run_difficulty_level(TaskDifficulty.TRIVIAL, mock_executor)

        assert len(results) == len(TRIVIAL_TASKS)
        assert all(r.task.difficulty == TaskDifficulty.TRIVIAL for r in results)

    def test_run_by_category(self):
        """Verify running tasks by category."""
        runner = BenchmarkRunner(model_name="TestModel")

        def mock_executor(task):
            return True, f"Completed {task.task_id}", []

        results = runner.run_category(TaskCategory.NAVIGATION, mock_executor)

        assert all(r.task.category == TaskCategory.NAVIGATION for r in results)

    def test_get_failed_tasks(self):
        """Verify getting failed tasks."""
        runner = BenchmarkRunner(model_name="TestModel")

        def mock_executor(task):
            # Fail every other task
            return task.task_id != "trivial_list_directory", "", []

        runner.run_task_set(TRIVIAL_TASKS, mock_executor)
        failed = runner.get_failed_tasks()

        assert len(failed) > 0
        assert all(not r.success for r in failed)

    def test_generate_report(self):
        """Verify report generation."""
        runner = BenchmarkRunner(model_name="TestModel")

        def mock_executor(task):
            return True, f"Completed {task.task_id}", []

        runner.run_task_set(TRIVIAL_TASKS, mock_executor)
        report = runner.generate_report()

        assert isinstance(report, str)
        assert "BENCHMARK REPORT" in report
        assert "TestModel" in report
        assert "PASSED" in report or "PASS" in report

    def test_get_slow_tasks(self):
        """Verify identifying slow tasks."""
        runner = BenchmarkRunner(model_name="TestModel")

        def mock_executor(task):
            # Simulate task taking different amounts of time
            return True, f"Completed {task.task_id}", []

        runner.run_task_set(TRIVIAL_TASKS, mock_executor)
        slow_tasks = runner.get_slow_tasks(threshold_seconds=0.1)

        # With mock executor, might have slow tasks
        # This just verifies the method works
        assert isinstance(slow_tasks, list)

    def test_get_metrics(self):
        """Verify getting aggregate metrics."""
        runner = BenchmarkRunner(model_name="TestModel")

        def mock_executor(task):
            return True, f"Completed {task.task_id}", []

        runner.run_task_set(TRIVIAL_TASKS, mock_executor)
        metrics = runner.get_metrics()

        assert isinstance(metrics, BenchmarkMetrics)
        assert metrics.model_name == "TestModel"
        assert metrics.tasks_completed == len(TRIVIAL_TASKS)


class TestBenchmarkIntegration:
    """Integration tests for the benchmark system."""

    def test_end_to_end_benchmark(self):
        """Verify end-to-end benchmark execution."""
        runner = BenchmarkRunner(model_name="IntegrationTest")

        def mock_executor(task):
            # Simple mock: pass easy/trivial, fail hard/expert
            return (
                task.difficulty
                in [
                    TaskDifficulty.TRIVIAL,
                    TaskDifficulty.EASY,
                ],
                "",
                [],
            )

        # Run a subset of tasks
        all_tasks = TRIVIAL_TASKS + EASY_TASKS
        runner.run_task_set(all_tasks, mock_executor)

        report = runner.generate_report()
        assert "TRIVIAL" in report or "trivial" in report
        assert "EASY" in report or "easy" in report

    def test_benchmark_with_retries(self):
        """Verify benchmark handles retries correctly."""
        runner = BenchmarkRunner(model_name="RetryTest", max_retries=2)

        attempt_count = 0

        def mock_executor(task):
            nonlocal attempt_count
            attempt_count += 1
            # Succeed on second attempt
            return attempt_count >= 2, "", [] if attempt_count >= 2 else ["First attempt failed"]

        task = TRIVIAL_TASKS[0]
        result = runner.execute_task(task, mock_executor)

        # Task should eventually succeed due to retries
        assert result.attempts <= runner.max_retries + 1

    def test_task_result_structure(self):
        """Verify TaskResult has correct structure."""
        runner = BenchmarkRunner(model_name="TestModel")

        def mock_executor(task):
            return True, "Test output", []

        result = runner.execute_task(TRIVIAL_TASKS[0], mock_executor)

        assert hasattr(result, "task")
        assert hasattr(result, "success")
        assert hasattr(result, "completion_status")
        assert hasattr(result, "metrics")
        assert hasattr(result, "output")
        assert hasattr(result, "errors")
        assert hasattr(result, "attempts")

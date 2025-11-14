"""Benchmark system for measuring agent capability on CIE codebase tasks.

This module provides a framework for testing how well AI agents can:
- Navigate and understand the codebase
- Read and comprehend code
- Make targeted modifications
- Debug and fix issues
- Implement complete workflows

The benchmark system tracks metrics like task completion rate, tool call
efficiency, error recovery, and code quality to measure agent performance.
"""

from benchmark.metrics import BenchmarkMetrics, MetricsCollector
from benchmark.runner import BenchmarkRunner, TaskResult

from benchmark.tasks import BenchmarkTask, TaskCategory, TaskDifficulty

__all__ = [
    "BenchmarkRunner",
    "BenchmarkTask",
    "TaskDifficulty",
    "TaskCategory",
    "TaskResult",
    "BenchmarkMetrics",
    "MetricsCollector",
]

"""Context-aware benchmark system for CIE.

The suite validates whether agents can:
- Capture and reason about their working context
- Apply compression/reorganization strategies
- Measure context efficiency vs latency/cost guardrails
- Automate end-to-end context workflows

Traditional metrics (tool efficiency, code quality, autonomy) are still collected,
but context-centric metrics (compression ratio, context size, guardrail hits) are
now first-class citizens.
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

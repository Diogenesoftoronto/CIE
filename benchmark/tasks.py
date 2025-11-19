"""Benchmark task definitions and structures.

This module defines the task system for benchmarking agent capabilities.
Tasks are organized by difficulty, category, and success criteria to enable
comprehensive evaluation of agent performance across different competency areas.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class TaskDifficulty(Enum):
    """Task difficulty levels."""

    TRIVIAL = "trivial"  # Read a file, answer a question
    EASY = "easy"  # Find patterns, basic comprehension
    MEDIUM = "medium"  # Make targeted edits, run tests
    HARD = "hard"  # Implement features, debug complex issues
    EXPERT = "expert"  # Complete workflows, architecture changes


class TaskCategory(Enum):
    """Task categories measuring different competencies."""

    CONTEXT_AWARENESS = "context-awareness"  # Capture + summarize working memory
    CONTEXT_OPTIMIZATION = "context-optimization"  # Reorganize / compress context trees
    CONTEXT_PERFORMANCE = "context-performance"  # Measure effect on latency/cost
    CONTEXT_AUTONOMY = "context-autonomy"  # Automate capture + adoption workflows
    WORKFLOW = "workflow"  # Multi-step demo or CLI pipelines


@dataclass
class BenchmarkTask:
    """A single benchmark task for evaluating agent capability.

    Attributes:
        task_id: Unique identifier for the task
        title: Human-readable task title
        description: Detailed task description
        category: Category of the task
        difficulty: Difficulty level
        context: Background information or setup instructions
        objective: What needs to be accomplished
        success_criteria: List of criteria that must be met for success
        hints: Optional hints if agent struggles (revealed progressively)
        setup_fn: Optional function to prepare the task environment
        validation_fn: Optional function to validate task completion
        estimated_time_minutes: Rough estimate for completion
        max_tool_calls: Maximum tool calls before considering task failed
        tags: Additional tags for organization
    """

    task_id: str
    title: str
    description: str
    category: TaskCategory
    difficulty: TaskDifficulty
    objective: str
    success_criteria: list[str]
    context: str = ""
    hints: list[str] = field(default_factory=list)
    setup_fn: Callable[[], Any] | None = None
    validation_fn: Callable[[], bool] | None = None
    estimated_time_minutes: int = 5
    max_tool_calls: int = 50
    tags: list[str] = field(default_factory=list)

    def __hash__(self) -> int:
        """Make task hashable for caching."""
        return hash(self.task_id)

    def __eq__(self, other: object) -> bool:
        """Tasks are equal if they have the same ID."""
        if not isinstance(other, BenchmarkTask):
            return NotImplemented
        return self.task_id == other.task_id


# ============================================================================
# TRIVIAL LEVEL TASKS
# ============================================================================


TASK_READ_FILE = BenchmarkTask(
    task_id="trivial_read_file",
    title="Capture a Context Snapshot",
    description="Use the `[CTX]` panel or context tools modal to capture a snapshot focused on `core/models.py` and describe the resulting tree.",
    category=TaskCategory.CONTEXT_AWARENESS,
    difficulty=TaskDifficulty.TRIVIAL,
    objective="Capture context for `core/models.py`, list top-level nodes (Policy/Trial/Workload), and report node counts plus depth.",
    success_criteria=[
        "Invokes the Capture workflow and stores the snapshot",
        "Reports node/leaf counts and the computed depth metric",
        "Describes Policy, Trial, and Workload using information pulled from the snapshot rather than static file reads",
    ],
    context="Demonstrates the baseline workflow for context introspection before any optimization occurs.",
    estimated_time_minutes=3,
    max_tool_calls=5,
)

TASK_LIST_DIRECTORY = BenchmarkTask(
    task_id="trivial_list_directory",
    title="Map Context Roots",
    description="Enumerate the major directories that feed into context capture (core/, ui/, benchmark/) and tag them with expected context weight.",
    category=TaskCategory.CONTEXT_AWARENESS,
    difficulty=TaskDifficulty.TRIVIAL,
    objective="List the project roots that typically enter the context window and note whether they contain models, UI definitions, or benchmarks.",
    success_criteria=[
        "Lists the root directories and notes why they matter for context",
        "Identifies at least three subdirectories with likely large contexts (ui/, benchmark/, scripts/)",
        "Explains how each directory influences capture/compression decisions",
    ],
    context="Agents should know where large context segments originate before optimizing them.",
    estimated_time_minutes=3,
    max_tool_calls=3,
)

TASK_FIND_PATTERN = BenchmarkTask(
    task_id="trivial_find_pattern",
    title="Identify High-Churn Context Files",
    description="Locate Python files under core/ or ui/ whose size suggests they should be compressed or summarized before entering context.",
    category=TaskCategory.CONTEXT_AWARENESS,
    difficulty=TaskDifficulty.TRIVIAL,
    objective="List candidate files (>200 lines) and capture size metadata used for later compression decisions.",
    success_criteria=[
        "Uses search tools to find large Python files",
        "Reports approximate line counts or file sizes",
        "Explains why each file may require compression or focused capture",
    ],
    estimated_time_minutes=3,
    max_tool_calls=6,
)


# ============================================================================
# EASY LEVEL TASKS
# ============================================================================


TASK_FIND_SYMBOL = BenchmarkTask(
    task_id="easy_find_symbol",
    title="Trace Context Hotspots",
    description="Locate every module that instantiates `ContextNavigator` or triggers context tooling so optimizers know where to focus.",
    category=TaskCategory.CONTEXT_AWARENESS,
    difficulty=TaskDifficulty.EASY,
    objective="Use search utilities to find context-tool usage, then summarize how calls are distributed across panels, modals, and CLI helpers.",
    success_criteria=[
        "Runs grep/ripgrep queries that target ContextNavigator/context tools",
        "Lists at least five call sites with file references",
        "Explains how each call site contributes to capture or optimization workflows",
    ],
    context="Before optimizing context, agents must know where the hooks live.",
    estimated_time_minutes=3,
    max_tool_calls=10,
)

TASK_UNDERSTAND_OPTIMIZER = BenchmarkTask(
    task_id="easy_understand_optimizer",
    title="Understand Context-Aware Optimizers",
    description="Explain how context metadata flows through the Optimizer protocol (propose/observe/state).",
    category=TaskCategory.CONTEXT_OPTIMIZATION,
    difficulty=TaskDifficulty.EASY,
    objective="Describe how `state[\"context\"]` and metadata such as `context_efficiency` are passed to optimizers and how they should respond.",
    success_criteria=[
        "Reads the Optimizer protocol definitions",
        "Identifies how propose(), observe(), get_state(), reset() interact with context metrics",
        "Suggests at least one strategy for adapting proposals based on context efficiency",
    ],
    estimated_time_minutes=6,
    max_tool_calls=10,
)

TASK_TRACE_IMPORTS = BenchmarkTask(
    task_id="easy_trace_imports",
    title="Trace Context Tool Integration",
    description="Identify where context modals are imported/mounted and outline their lifecycle (capture, summary, optimize, export).",
    category=TaskCategory.CONTEXT_AWARENESS,
    difficulty=TaskDifficulty.EASY,
    objective="List the modules responsible for context capture/export and explain how they are triggered (key bindings, toolbar actions, CLI).",
    success_criteria=[
        "Reads ui/app.py and related components successfully",
        "Lists the key imports for ContextNavigator, ContextToolsModal, and related helpers",
        "Explains the trigger path (key binding → action → modal) for each tool",
    ],
    estimated_time_minutes=5,
    max_tool_calls=8,
)


# ============================================================================
# MEDIUM LEVEL TASKS
# ============================================================================


TASK_LOCATE_BUG = BenchmarkTask(
    task_id="medium_locate_bug",
    title="Diagnose Context Drift",
    description="Trace where context snapshots are invalidated or overwritten when optimizers run, and explain how drift is prevented.",
    category=TaskCategory.CONTEXT_PERFORMANCE,
    difficulty=TaskDifficulty.MEDIUM,
    objective="Find the backend logic that guards context snapshots (capture, reset, invalidate) and describe how it reacts when optimizers exceed limits.",
    success_criteria=[
        "Searches backend/optimizer integrations for context-handling code",
        "Identifies guardrails that trigger when context exceeds limits or becomes stale",
        "Explains how the mechanism prevents drift across propose/evaluate cycles",
    ],
    context="Self-aware agents must detect when their working memory diverges between optimization steps.",
    estimated_time_minutes=6,
    max_tool_calls=15,
    hints=[
        "Check backend.py around snapshot management",
        "Inspect optimizer.observe for metadata handling",
    ],
)

TASK_EDIT_CONFIG = BenchmarkTask(
    task_id="medium_edit_config",
    title="Add Context Guard Configuration",
    description="Extend the configuration to include `context_guard.max_nodes` and `context_guard.max_size_kb` so operators can tune when compression triggers.",
    category=TaskCategory.CONTEXT_OPTIMIZATION,
    difficulty=TaskDifficulty.MEDIUM,
    objective="Add the guard parameters to `config/settings.py`, wire them to defaults, and ensure they surface in the CLI/TUI metadata.",
    success_criteria=[
        "Updates the relevant dataclass with the new guard values",
        "Sets sensible defaults aligned with the paper (e.g., 60KB, 2k nodes)",
        "Mirrors the settings into any CLI/TUI surfaces that display guard thresholds",
        "Code follows existing patterns and passes linting",
    ],
    estimated_time_minutes=6,
    max_tool_calls=15,
)

TASK_ADD_METRIC = BenchmarkTask(
    task_id="medium_add_metric",
    title="Add Context Efficiency Metric",
    description="Add `context_efficiency` to Trial metrics and ensure scoring + Pareto labels surface it.",
    category=TaskCategory.CONTEXT_PERFORMANCE,
    difficulty=TaskDifficulty.MEDIUM,
    objective="Extend Trial.metrics with `context_efficiency`, update scoring to weigh it, and make sure the Experiments panel renders the value.",
    success_criteria=[
        "Modifies the Trial dataclass to include the metric",
        "Updates CIEBackend.score and Pareto tagging to consider it",
        "Verifies the UI/CLI display the metric without errors",
        "Existing tests still pass",
    ],
    estimated_time_minutes=8,
    max_tool_calls=20,
    hints=[
        "Check core/models.py for Trial structure",
        "Review how latency_p95 is used in scoring and mimic the wiring",
    ],
)

TASK_WRITE_SIMPLE_TEST = BenchmarkTask(
    task_id="medium_write_test",
    title="Test Context Compression",
    description="Write a unit test that exercises the frequency-based compression strategy and asserts it improves efficiency.",
    category=TaskCategory.CONTEXT_OPTIMIZATION,
    difficulty=TaskDifficulty.MEDIUM,
    objective="Add a test (e.g., test_context_compression_frequency) that builds a fake tree, runs compression, and asserts node depth decreases.",
    success_criteria=[
        "Creates a deterministic context tree fixture",
        "Applies the compression strategy under test",
        "Asserts metrics like depth or size improved",
        "Uses pytest assertions and follows project patterns",
        "Test passes when run",
    ],
    estimated_time_minutes=9,
    max_tool_calls=20,
)


# ============================================================================
# HARD LEVEL TASKS
# ============================================================================


TASK_IMPLEMENT_FEATURE = BenchmarkTask(
    task_id="hard_implement_feature",
    title="Implement Context Efficiency Evaluator",
    description="Create a `context_efficiency` evaluator plugin that measures compression ratio, access latency, and hotspot cache hit-rate.",
    category=TaskCategory.CONTEXT_OPTIMIZATION,
    difficulty=TaskDifficulty.HARD,
    objective=(
        "Create `evaluators/context_efficiency.py` implementing the Evaluator protocol "
        "with metrics compression_ratio, context_size_kb, access_latency_mean."
    ),
    success_criteria=[
        "Implements Evaluator protocol completely",
        "Includes run() method that captures context stats and returns Trial metrics",
        "get_supported_metrics() returns the context-oriented metrics",
        "validate_workload() checks required fields",
        "Registers in evaluators/__init__.py",
        "Code follows project patterns",
        "No import errors",
    ],
    context=(
        "Evaluators implement run() and get_supported_metrics(). Mirror existing plugins but focus on context instrumentation.",
    ),
    estimated_time_minutes=15,
    max_tool_calls=30,
    hints=[
        "Review mock_evaluator.py for baseline structure",
        "Use ContextNavigator utilities to compute metrics",
        "Must implement run() -> Trial",
        "get_supported_metrics() should return list of metric names",
    ],
)

TASK_DEBUG_COMPLEX = BenchmarkTask(
    task_id="hard_debug_complex",
    title="Debug Context Scoring Issue",
    description=(
        "Fix the scoring logic so context_efficiency and compression_ratio weights properly reward improvements "
        "while still penalizing regressions."
    ),
    category=TaskCategory.CONTEXT_PERFORMANCE,
    difficulty=TaskDifficulty.HARD,
    objective="Locate and fix the score() method in backend.py so context metrics respect positive/negative weights and reflect guardrails.",
    success_criteria=[
        "Identifies the score() method in backend.py",
        "Explains how context metrics should influence scores (penalties vs rewards)",
        "Fixes the logic and writes a regression test covering context_efficiency",
        "Test passes",
    ],
    context="Context-aware optimization relies on accurate scoring; this task ensures weights behave as described in the paper.",
    estimated_time_minutes=13,
    max_tool_calls=25,
)

TASK_REFACTOR_MODULE = BenchmarkTask(
    task_id="hard_refactor_module",
    title="Refactor Context Optimizer",
    description=(
        "Refactor the HillClimbOptimizer so context-state handling is extracted into a helper "
        "that can be reused by other optimizers."
    ),
    category=TaskCategory.CONTEXT_OPTIMIZATION,
    difficulty=TaskDifficulty.HARD,
    objective="Extract context state preparation/filtering into `_prepare_context_state()` and ensure propose() uses it consistently.",
    success_criteria=[
        "Reads optimizers/hill_climb.py",
        "Identifies where context metadata is massaged before propose()",
        "Creates `_prepare_context_state()` (or similar) with thorough docstring/tests",
        "Updates propose() to call the helper",
        "All tests still pass",
        "Code is more readable",
    ],
    estimated_time_minutes=12,
    max_tool_calls=30,
)


# ============================================================================
# EXPERT LEVEL TASKS
# ============================================================================


TASK_COMPLETE_WORKFLOW = BenchmarkTask(
    task_id="expert_complete_workflow",
    title="Ship a Context Optimization Workflow",
    description=(
        "Create a complete context-optimization workflow that captures a snapshot, applies compression, runs the evaluator, and exports a report."
    ),
    category=TaskCategory.CONTEXT_AUTONOMY,
    difficulty=TaskDifficulty.EXPERT,
    objective=(
        "Implement a CLI or script under `benchmark/templates/` that ties together capture → optimize → evaluate → export, "
        "register it in docs, and add an integration test that exercises the workflow."
    ),
    success_criteria=[
        "Creates an executable workflow script/template",
        "Orchestrates capture, compression strategy selection, and evaluation",
        "Exports a structured report (JSON/Markdown) summarizing context efficiency gains",
        "Adds documentation describing how to run the workflow",
        "Adds tests validating the orchestration logic",
    ],
    context=(
        "The vision is end-to-end context-aware optimization; this task packages it into a reproducible workflow.",
    ),
    estimated_time_minutes=25,
    max_tool_calls=50,
    hints=[
        "Reuse CLI helpers from `benchmark/example_usage.py`",
        "Leverage ContextNavigator APIs for capture/export",
    ],
)

TASK_ARCHITECTURE_CHANGE = BenchmarkTask(
    task_id="expert_architecture_change",
    title="Architecture: Context Cache Layer",
    description=(
        "Add support for caching context snapshots and derived metrics so repeated optimizations reuse prior analysis safely."
    ),
    category=TaskCategory.CONTEXT_AUTONOMY,
    difficulty=TaskDifficulty.EXPERT,
    objective=(
        "Implement a context cache in CIEBackend with configurable size/TTL, expose cache hits via metrics, and add tests validating eviction + reuse."
    ),
    success_criteria=[
        "Reads core/backend.py and understands current structure",
        "Designs cache interface (store snapshots + derived metrics)",
        "Implements caching with size/TTL guards and metrics (hits/misses)",
        "Backward compatible (no breaking changes)",
        "Comprehensive tests verify caching behavior",
        "All existing tests still pass",
        "Code includes proper documentation",
    ],
    context=(
        "The backend could benefit from caching to avoid rerunning the same evaluations. "
        "Must be transparent and not break existing functionality."
    ),
    estimated_time_minutes=30,
    max_tool_calls=60,
    hints=[
        "Consider leveraging functools.lru_cache or a custom ring buffer",
        "Cache key should include workload + policy + compression strategy",
        "Add cache statistics for monitoring",
        "Make cache configurable via settings",
    ],
)

TASK_CROSS_CUTTING_CONCERN = BenchmarkTask(
    task_id="expert_cross_cutting",
    title="Add Context Telemetry",
    description=(
        "Implement structured telemetry for context capture/optimization so operators can monitor compression ratios, guardrail triggers, and Pareto shifts."
    ),
    category=TaskCategory.CONTEXT_AUTONOMY,
    difficulty=TaskDifficulty.EXPERT,
    objective=(
        "Add telemetry hooks (logging or metrics) across backend/optimizers to record context sizes, compression ratios, guardrail breaches, and publish them via the status panel.",
    ),
    success_criteria=[
        "Creates a telemetry helper (utils/context_telemetry.py or similar)",
        "Integrates telemetry into context capture, compression, and adoption paths",
        "Surfaces metrics in the status panel or CLI output",
        "Error logging with context and stack traces",
        "Configurable via settings (on/off, sinks)",
        "Tests verify telemetry is emitted for key events",
        "No breaking changes to existing code",
        "Documentation explains logging setup",
    ],
    context=(
        "The system needs better visibility into what's happening. "
        "Logging should be comprehensive but non-invasive."
    ),
    estimated_time_minutes=30,
    max_tool_calls=50,
)


# ============================================================================
# TASK COLLECTIONS
# ============================================================================


TRIVIAL_TASKS = [
    TASK_READ_FILE,
    TASK_LIST_DIRECTORY,
    TASK_FIND_PATTERN,
]

EASY_TASKS = [
    TASK_FIND_SYMBOL,
    TASK_UNDERSTAND_OPTIMIZER,
    TASK_TRACE_IMPORTS,
]

MEDIUM_TASKS = [
    TASK_LOCATE_BUG,
    TASK_EDIT_CONFIG,
    TASK_ADD_METRIC,
    TASK_WRITE_SIMPLE_TEST,
]

HARD_TASKS = [
    TASK_IMPLEMENT_FEATURE,
    TASK_DEBUG_COMPLEX,
    TASK_REFACTOR_MODULE,
]

EXPERT_TASKS = [
    TASK_COMPLETE_WORKFLOW,
    TASK_ARCHITECTURE_CHANGE,
    TASK_CROSS_CUTTING_CONCERN,
]

ALL_TASKS = TRIVIAL_TASKS + EASY_TASKS + MEDIUM_TASKS + HARD_TASKS + EXPERT_TASKS


def get_tasks_by_difficulty(difficulty: TaskDifficulty) -> list[BenchmarkTask]:
    """Get all tasks at a specific difficulty level."""
    difficulty_map = {
        TaskDifficulty.TRIVIAL: TRIVIAL_TASKS,
        TaskDifficulty.EASY: EASY_TASKS,
        TaskDifficulty.MEDIUM: MEDIUM_TASKS,
        TaskDifficulty.HARD: HARD_TASKS,
        TaskDifficulty.EXPERT: EXPERT_TASKS,
    }
    return difficulty_map.get(difficulty, [])


def get_tasks_by_category(category: TaskCategory) -> list[BenchmarkTask]:
    """Get all tasks in a specific category."""
    return [task for task in ALL_TASKS if task.category == category]

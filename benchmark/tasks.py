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

    NAVIGATION = "navigation"  # Finding files and understanding structure
    COMPREHENSION = "comprehension"  # Understanding code and design
    MODIFICATION = "modification"  # Making targeted code changes
    DEBUGGING = "debugging"  # Finding and fixing issues
    IMPLEMENTATION = "implementation"  # Writing new code
    WORKFLOW = "workflow"  # Multi-step complex tasks
    TESTING = "testing"  # Writing and running tests
    REFACTORING = "refactoring"  # Improving existing code


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
    title="Read and Summarize a File",
    description="Read the core/models.py file and provide a summary of its contents.",
    category=TaskCategory.NAVIGATION,
    difficulty=TaskDifficulty.TRIVIAL,
    objective="Read core/models.py and explain what dataclasses it defines and their purposes.",
    success_criteria=[
        "Reads core/models.py successfully",
        "Identifies Policy, Trial, and Workload dataclasses",
        "Correctly describes their purposes",
    ],
    context="The CIE project has domain models defined in core/models.py",
    estimated_time_minutes=2,
    max_tool_calls=5,
)

TASK_LIST_DIRECTORY = BenchmarkTask(
    task_id="trivial_list_directory",
    title="List Project Structure",
    description="List the contents of the CIE project root and describe its structure.",
    category=TaskCategory.NAVIGATION,
    difficulty=TaskDifficulty.TRIVIAL,
    objective="List the CIE directory and explain what each subdirectory contains.",
    success_criteria=[
        "Lists CIE root directory successfully",
        "Identifies core/, ui/, optimizers/, evaluators/ directories",
        "Correctly describes their purposes",
    ],
    estimated_time_minutes=2,
    max_tool_calls=3,
)

TASK_FIND_PATTERN = BenchmarkTask(
    task_id="trivial_find_pattern",
    title="Find Python Files",
    description="Find all Python files in the CIE core module.",
    category=TaskCategory.NAVIGATION,
    difficulty=TaskDifficulty.TRIVIAL,
    objective="List all .py files in the core/ directory.",
    success_criteria=[
        "Uses find_path or similar to locate files",
        "Lists all Python files in core/",
        "Includes models.py, backend.py, __init__.py",
    ],
    estimated_time_minutes=2,
    max_tool_calls=5,
)


# ============================================================================
# EASY LEVEL TASKS
# ============================================================================


TASK_FIND_SYMBOL = BenchmarkTask(
    task_id="easy_find_symbol",
    title="Find Symbol Usage",
    description="Find all files that import or use the 'Policy' dataclass.",
    category=TaskCategory.COMPREHENSION,
    difficulty=TaskDifficulty.EASY,
    objective="Use grep to find all references to the Policy class throughout the codebase.",
    success_criteria=[
        "Uses grep with proper regex",
        "Finds at least 5 files using Policy",
        "Includes core/backend.py and test files",
        "Correctly interprets results",
    ],
    context="Policy is defined in core/models.py and used throughout the project.",
    estimated_time_minutes=3,
    max_tool_calls=10,
)

TASK_UNDERSTAND_OPTIMIZER = BenchmarkTask(
    task_id="easy_understand_optimizer",
    title="Understand Optimizer Interface",
    description="Read and explain how the Optimizer protocol works in the codebase.",
    category=TaskCategory.COMPREHENSION,
    difficulty=TaskDifficulty.EASY,
    objective="Explain the Optimizer protocol: what methods it requires and what they do.",
    success_criteria=[
        "Reads core/models.py or optimizers/",
        "Identifies propose(), observe(), get_state(), reset() methods",
        "Explains the purpose of each method",
        "Describes the data flow between methods",
    ],
    estimated_time_minutes=5,
    max_tool_calls=10,
)

TASK_TRACE_IMPORTS = BenchmarkTask(
    task_id="easy_trace_imports",
    title="Trace Import Dependencies",
    description="Identify all imports in ui/app.py and explain what they import.",
    category=TaskCategory.COMPREHENSION,
    difficulty=TaskDifficulty.EASY,
    objective="List all imports in ui/app.py and describe what module/class each one provides.",
    success_criteria=[
        "Reads ui/app.py successfully",
        "Lists at least 10 imports",
        "Correctly identifies source modules for each import",
        "Notes any internal vs external imports",
    ],
    estimated_time_minutes=5,
    max_tool_calls=8,
)


# ============================================================================
# MEDIUM LEVEL TASKS
# ============================================================================


TASK_LOCATE_BUG = BenchmarkTask(
    task_id="medium_locate_bug",
    title="Find a Specific Issue",
    description="Locate where in the code error handling happens for optimizer timeouts.",
    category=TaskCategory.DEBUGGING,
    difficulty=TaskDifficulty.MEDIUM,
    objective="Find code that handles timeout errors from optimizers.",
    success_criteria=[
        "Searches through relevant files",
        "Finds error handling code",
        "Identifies timeout handling mechanism",
        "Can explain how it works",
    ],
    context="Optimizers may time out; find where this is handled.",
    estimated_time_minutes=5,
    max_tool_calls=15,
    hints=[
        "Check backend.py and optimizer implementations",
        "Look for try/except blocks or timeout-related code",
    ],
)

TASK_EDIT_CONFIG = BenchmarkTask(
    task_id="medium_edit_config",
    title="Update Configuration",
    description="Add a new configuration parameter for evaluation timeout.",
    category=TaskCategory.MODIFICATION,
    difficulty=TaskDifficulty.MEDIUM,
    objective="Add 'eval_timeout_seconds' parameter to the configuration system.",
    success_criteria=[
        "Reads config/settings.py",
        "Adds new parameter to appropriate dataclass",
        "Updates default values",
        "Code follows existing patterns",
        "No syntax errors",
    ],
    estimated_time_minutes=5,
    max_tool_calls=15,
)

TASK_ADD_METRIC = BenchmarkTask(
    task_id="medium_add_metric",
    title="Add New Metric to Scoring",
    description="Add 'memory_usage' as a new scorable metric in the Trial dataclass.",
    category=TaskCategory.MODIFICATION,
    difficulty=TaskDifficulty.MEDIUM,
    objective="Add memory_usage to Trial.metrics and update scoring to support it.",
    success_criteria=[
        "Modifies Trial dataclass to include memory_usage",
        "Updates scoring functions if needed",
        "Changes follow project patterns",
        "Existing tests still pass",
    ],
    estimated_time_minutes=7,
    max_tool_calls=20,
    hints=[
        "Check core/models.py for Trial structure",
        "Look at how latency_p95 is used in scoring",
    ],
)

TASK_WRITE_SIMPLE_TEST = BenchmarkTask(
    task_id="medium_write_test",
    title="Write a Unit Test",
    description="Write a test for the Policy dataclass initialization and validation.",
    category=TaskCategory.TESTING,
    difficulty=TaskDifficulty.MEDIUM,
    objective="Create test_policy_creation in tests/test_models.py that validates Policy creation.",
    success_criteria=[
        "Creates test function with proper naming",
        "Tests Policy instantiation with various parameters",
        "Uses pytest assertions",
        "Test passes when run",
        "Follows project test patterns",
    ],
    estimated_time_minutes=8,
    max_tool_calls=20,
)


# ============================================================================
# HARD LEVEL TASKS
# ============================================================================


TASK_IMPLEMENT_FEATURE = BenchmarkTask(
    task_id="hard_implement_feature",
    title="Implement New Evaluator",
    description="Create a new evaluator called 'latency_tester' that measures response time.",
    category=TaskCategory.IMPLEMENTATION,
    difficulty=TaskDifficulty.HARD,
    objective=(
        "Create evaluators/latency_tester.py implementing the Evaluator protocol "
        "with metrics for p50, p95, p99 latency."
    ),
    success_criteria=[
        "Implements Evaluator protocol completely",
        "Includes run() method that returns Trial with latency metrics",
        "get_supported_metrics() returns ['latency_p50', 'latency_p95', 'latency_p99']",
        "validate_workload() checks required fields",
        "Registers in evaluators/__init__.py",
        "Code follows project patterns",
        "No import errors",
    ],
    context=(
        "Evaluators implement the Evaluator protocol with run() and get_supported_metrics() methods. "
        "See mock_evaluator.py or text_match.py for examples."
    ),
    estimated_time_minutes=15,
    max_tool_calls=30,
    hints=[
        "Review mock_evaluator.py for the basic structure",
        "Look at text_match.py for a more complete example",
        "Must implement run() -> Trial",
        "get_supported_metrics() should return list of metric names",
    ],
)

TASK_DEBUG_COMPLEX = BenchmarkTask(
    task_id="hard_debug_complex",
    title="Debug Scoring Issue",
    description=(
        "Fix an issue where negative metric weights don't properly reduce scores. "
        "The scoring function should penalize when metrics are low, reward when high."
    ),
    category=TaskCategory.DEBUGGING,
    difficulty=TaskDifficulty.HARD,
    objective="Locate and fix the scoring logic in backend.py to properly handle negative weights.",
    success_criteria=[
        "Identifies the score() method in backend.py",
        "Understands weight application (positive = penalize, negative = reward)",
        "Fixes any logic errors",
        "Writes test demonstrating the fix",
        "Test passes",
    ],
    context="The scoring system uses weights to combine multiple metrics into a single score.",
    estimated_time_minutes=12,
    max_tool_calls=25,
)

TASK_REFACTOR_MODULE = BenchmarkTask(
    task_id="hard_refactor_module",
    title="Refactor for Clarity",
    description=(
        "Refactor the HillClimbOptimizer to extract the step-size adaptation logic "
        "into a separate method for better testability."
    ),
    category=TaskCategory.REFACTORING,
    difficulty=TaskDifficulty.HARD,
    objective="Extract step size adaptation into _adapt_step_size() method.",
    success_criteria=[
        "Reads optimizers/hill_climb.py",
        "Identifies step size adaptation logic",
        "Creates new _adapt_step_size() method",
        "Updates propose() to use new method",
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
    title="Implement Complete Evaluator Plugin",
    description=(
        "Create a complete 'performance' evaluator that measures CPU, memory, and latency. "
        "Include registration, documentation, and tests."
    ),
    category=TaskCategory.WORKFLOW,
    difficulty=TaskDifficulty.EXPERT,
    objective=(
        "Implement evaluators/plugins/performance.py with CPU, memory, and latency metrics, "
        "register it, add tests, and document it."
    ),
    success_criteria=[
        "Creates evaluators/plugins/performance.py",
        "Implements Evaluator protocol completely",
        "Provides metrics: cpu_percent, memory_mb, latency_ms",
        "Registers in evaluators/__init__.py or plugins/__init__.py",
        "Includes comprehensive docstrings",
        "Tests in tests/ directory validate all metrics",
        "All tests pass",
        "README or docs updated with new evaluator",
    ],
    context=(
        "Evaluators are plugins that implement the Evaluator protocol. "
        "See plugin system in evaluators/__init__.py for registration."
    ),
    estimated_time_minutes=25,
    max_tool_calls=50,
    hints=[
        "Review mock_evaluator.py for structure",
        "Check evaluators/__init__.py for registration pattern",
        "Plugin system allows drop-in evaluators",
        "Include error handling and validation",
    ],
)

TASK_ARCHITECTURE_CHANGE = BenchmarkTask(
    task_id="expert_architecture_change",
    title="Architectural Improvement",
    description=(
        "Add support for caching Trial results to avoid recomputation. "
        "Design and implement a caching layer in the backend."
    ),
    category=TaskCategory.WORKFLOW,
    difficulty=TaskDifficulty.EXPERT,
    objective=(
        "Implement trial result caching in CIEBackend with configurable cache size "
        "and TTL, including tests validating cache behavior."
    ),
    success_criteria=[
        "Reads core/backend.py and understands current structure",
        "Designs cache interface (get, set, invalidate)",
        "Implements caching for trial results",
        "Adds configuration for cache size and TTL",
        "Includes cache hit/miss metrics",
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
        "Consider using functools.lru_cache or implementing custom cache",
        "Cache key should include policy and workload identifiers",
        "Add cache statistics for monitoring",
        "Make cache configurable via settings",
    ],
)

TASK_CROSS_CUTTING_CONCERN = BenchmarkTask(
    task_id="expert_cross_cutting",
    title="Add Cross-Cutting Concern",
    description=(
        "Implement comprehensive logging for all optimization and evaluation operations. "
        "Create a logging system that tracks performance and errors without cluttering code."
    ),
    category=TaskCategory.WORKFLOW,
    difficulty=TaskDifficulty.EXPERT,
    objective=(
        "Add structured logging to backend.py, optimizers, and evaluators with "
        "configurable levels and performance metrics."
    ),
    success_criteria=[
        "Creates utils/logging.py with logging infrastructure",
        "Integrates logging into CIEBackend without polluting code",
        "Logs key operations: policy generation, evaluation, adoption",
        "Includes performance metrics (timing, call counts)",
        "Error logging with context and stack traces",
        "Configurable via settings (log level, format, output)",
        "Tests verify logging behavior",
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

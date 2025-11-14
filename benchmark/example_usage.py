"""Example usage scenarios for the CIE benchmark system.

This module demonstrates various ways to use the benchmark framework,
from simple CLI usage to advanced programmatic scenarios.
"""

from benchmark.runner import BenchmarkRunner
from benchmark.tasks import (
    ALL_TASKS,
    EASY_TASKS,
    EXPERT_TASKS,
    HARD_TASKS,
    MEDIUM_TASKS,
    TRIVIAL_TASKS,
    TaskCategory,
    TaskDifficulty,
    get_tasks_by_category,
    get_tasks_by_difficulty,
)

# ============================================================================
# EXAMPLE 1: Simple Benchmark Run
# ============================================================================


def example_simple_benchmark():
    """Run a simple benchmark with mock executor."""
    print("=" * 80)
    print("EXAMPLE 1: Simple Benchmark Run")
    print("=" * 80)
    print()

    # Create runner
    runner = BenchmarkRunner(
        model_name="GPT-4",
        max_retries=2,
        timeout_seconds=300,
    )

    # Define simple executor
    def simple_executor(task):
        """Mock executor that passes trivial/easy, fails hard/expert."""
        success = task.difficulty in [TaskDifficulty.TRIVIAL, TaskDifficulty.EASY]
        return success, f"Executed: {task.task_id}", []

    # Run trivial level tasks
    print("Running TRIVIAL level tasks...")
    results = runner.run_difficulty_level(TaskDifficulty.TRIVIAL, simple_executor)

    # Show results
    for result in results:
        status = "✓ PASS" if result.success else "✗ FAIL"
        print(f"  {status}: {result.task.title}")

    print()
    print(runner.generate_report())


# ============================================================================
# EXAMPLE 2: Benchmark by Category
# ============================================================================


def example_benchmark_by_category():
    """Benchmark specific competency categories."""
    print("=" * 80)
    print("EXAMPLE 2: Benchmark by Category")
    print("=" * 80)
    print()

    runner = BenchmarkRunner(model_name="Claude-3", max_retries=1)

    def category_executor(task):
        """Different success rates for different categories."""
        category_success_rates = {
            TaskCategory.NAVIGATION: 0.95,
            TaskCategory.COMPREHENSION: 0.90,
            TaskCategory.MODIFICATION: 0.75,
            TaskCategory.DEBUGGING: 0.60,
            TaskCategory.IMPLEMENTATION: 0.70,
        }

        import random

        rate = category_success_rates.get(task.category, 0.5)
        success = random.random() < rate

        return success, f"Category: {task.category.value}", []

    # Run by category and show results
    categories_to_test = [
        TaskCategory.NAVIGATION,
        TaskCategory.COMPREHENSION,
        TaskCategory.MODIFICATION,
    ]

    for category in categories_to_test:
        print(f"Testing {category.value}...")
        results = runner.run_category(category, category_executor)
        passed = sum(1 for r in results if r.success)
        total = len(results)
        print(f"  Result: {passed}/{total} passed ({passed / total * 100:.0f}%)")
        print()


# ============================================================================
# EXAMPLE 3: Progressive Difficulty
# ============================================================================


def example_progressive_difficulty():
    """Test agent across progressive difficulty levels."""
    print("=" * 80)
    print("EXAMPLE 3: Progressive Difficulty")
    print("=" * 80)
    print()

    runner = BenchmarkRunner(model_name="Llama-2-70B")

    def progressive_executor(task):
        """Success rate decreases with difficulty."""
        difficulty_success_rates = {
            TaskDifficulty.TRIVIAL: 0.99,
            TaskDifficulty.EASY: 0.90,
            TaskDifficulty.MEDIUM: 0.70,
            TaskDifficulty.HARD: 0.40,
            TaskDifficulty.EXPERT: 0.10,
        }

        import random

        rate = difficulty_success_rates.get(task.difficulty, 0.5)
        success = random.random() < rate

        return success, f"Difficulty: {task.difficulty.value}", []

    # Test each difficulty level
    for difficulty in [
        TaskDifficulty.TRIVIAL,
        TaskDifficulty.EASY,
        TaskDifficulty.MEDIUM,
        TaskDifficulty.HARD,
        TaskDifficulty.EXPERT,
    ]:
        print(f"\nTesting {difficulty.value.upper()} level...")
        results = runner.run_difficulty_level(difficulty, progressive_executor)
        passed = sum(1 for r in results if r.success)
        total = len(results)
        rate = passed / total * 100 if total > 0 else 0
        print(f"  {passed}/{total} passed ({rate:.0f}%)")

    print()
    print("FINAL REPORT")
    print("-" * 80)
    print(runner.generate_report())


# ============================================================================
# EXAMPLE 4: Comparing Multiple Models
# ============================================================================


def example_compare_models():
    """Compare performance across multiple models."""
    print("=" * 80)
    print("EXAMPLE 4: Comparing Multiple Models")
    print("=" * 80)
    print()

    models = ["GPT-4", "Claude-3", "Llama-2"]
    results_by_model = {}

    # Run benchmark for each model
    for model_name in models:
        print(f"Benchmarking {model_name}...")
        runner = BenchmarkRunner(model_name=model_name)

        def model_executor(task):
            """Simple mock executor."""
            import random

            # Each model has slightly different performance
            base_success = {
                "GPT-4": 0.85,
                "Claude-3": 0.80,
                "Llama-2": 0.60,
            }.get(model_name, 0.5)

            # Harder tasks reduce success rate
            difficulty_factor = {
                TaskDifficulty.TRIVIAL: 1.0,
                TaskDifficulty.EASY: 0.95,
                TaskDifficulty.MEDIUM: 0.85,
                TaskDifficulty.HARD: 0.60,
                TaskDifficulty.EXPERT: 0.30,
            }.get(task.difficulty, 0.5)

            success = random.random() < (base_success * difficulty_factor)
            return success, "", []

        # Run all tasks
        runner.run_task_set(ALL_TASKS[:10], model_executor)  # First 10 tasks
        results_by_model[model_name] = runner

    # Compare results
    print()
    print("COMPARISON")
    print("-" * 80)
    print(f"{'Model':<15} {'Pass Rate':<15} {'Avg Quality':<15} {'Composite':<10}")
    print("-" * 80)

    for model_name, runner in results_by_model.items():
        metrics = runner.get_metrics()
        print(
            f"{model_name:<15} {metrics.pass_rate:<14.1f}% "
            f"{metrics.average_code_quality:<14.1f} {metrics.average_composite_score:<10.1f}"
        )


# ============================================================================
# EXAMPLE 5: Detailed Task Analysis
# ============================================================================


def example_detailed_analysis():
    """Detailed analysis of task performance."""
    print("=" * 80)
    print("EXAMPLE 5: Detailed Task Analysis")
    print("=" * 80)
    print()

    runner = BenchmarkRunner(model_name="AnalysisAgent")

    # Use a more sophisticated executor
    def analysis_executor(task):
        """Executor with different success rates per task."""
        # Some tasks are inherently harder
        task_difficulties = {
            "trivial_read_file": 0.98,
            "trivial_list_directory": 0.96,
            "easy_find_symbol": 0.85,
            "medium_add_metric": 0.60,
            "hard_implement_feature": 0.30,
        }

        import random

        rate = task_difficulties.get(task.task_id, 0.5)
        success = random.random() < rate
        errors = [] if success else ["Task execution failed"]

        return success, "", errors

    # Run all tasks
    runner.run_task_set(ALL_TASKS, analysis_executor)

    # Analyze failures
    print("FAILURE ANALYSIS")
    print("-" * 80)
    failed = runner.get_failed_tasks()
    if failed:
        print(f"Failed tasks: {len(failed)}")
        for result in failed[:5]:  # Show first 5
            print(f"  - {result.task.task_id}: {result.task.title}")
            print(f"    Difficulty: {result.task.difficulty.value}")
            print(f"    Category: {result.task.category.value}")
    else:
        print("No failures!")

    print()
    print("PERFORMANCE BY DIFFICULTY")
    print("-" * 80)
    by_difficulty = {}
    for result in runner.results:
        diff = result.task.difficulty.value
        if diff not in by_difficulty:
            by_difficulty[diff] = {"passed": 0, "total": 0}
        by_difficulty[diff]["total"] += 1
        if result.success:
            by_difficulty[diff]["passed"] += 1

    for difficulty in ["trivial", "easy", "medium", "hard", "expert"]:
        if difficulty in by_difficulty:
            stats = by_difficulty[difficulty]
            rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"  {difficulty:10}: {stats['passed']}/{stats['total']} ({rate:.0f}%)")

    print()
    print("PERFORMANCE BY CATEGORY")
    print("-" * 80)
    by_category = {}
    for result in runner.results:
        cat = result.task.category.value
        if cat not in by_category:
            by_category[cat] = {"passed": 0, "total": 0}
        by_category[cat]["total"] += 1
        if result.success:
            by_category[cat]["passed"] += 1

    for category in sorted(by_category.keys()):
        stats = by_category[category]
        rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {category:20}: {stats['passed']}/{stats['total']} ({rate:.0f}%)")


# ============================================================================
# EXAMPLE 6: Custom Task Subset
# ============================================================================


def example_custom_subset():
    """Run benchmark on custom task subset."""
    print("=" * 80)
    print("EXAMPLE 6: Custom Task Subset")
    print("=" * 80)
    print()

    runner = BenchmarkRunner(model_name="CustomTest")

    # Create custom task subset
    # E.g., focus on implementation and debugging
    custom_tasks = []
    custom_tasks.extend(get_tasks_by_category(TaskCategory.IMPLEMENTATION))
    custom_tasks.extend(get_tasks_by_category(TaskCategory.DEBUGGING))

    print(f"Running {len(custom_tasks)} custom tasks")
    print(f"Categories: Implementation, Debugging")
    print()

    def custom_executor(task):
        """Custom executor."""
        import random

        success = random.random() < 0.65
        return success, "", [] if success else ["Task failed"]

    # Run custom subset
    runner.run_task_set(custom_tasks, custom_executor)

    # Show results
    print(runner.generate_report())


# ============================================================================
# MAIN - Run Examples
# ============================================================================


def main():
    """Run all examples."""
    examples = [
        example_simple_benchmark,
        example_benchmark_by_category,
        example_progressive_difficulty,
        example_compare_models,
        example_detailed_analysis,
        example_custom_subset,
    ]

    for i, example in enumerate(examples, 1):
        try:
            example()
            print()
            print()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
            print()


if __name__ == "__main__":
    # Run specific example or all
    import sys

    if len(sys.argv) > 1:
        example_num = int(sys.argv[1])
        examples = [
            example_simple_benchmark,
            example_benchmark_by_category,
            example_progressive_difficulty,
            example_compare_models,
            example_detailed_analysis,
            example_custom_subset,
        ]
        if 1 <= example_num <= len(examples):
            examples[example_num - 1]()
    else:
        main()

#!/usr/bin/env python3
"""
Example: Context-aware optimization with CIE framework

This example demonstrates how to use the context introspection and
manipulation system to optimize agent performance through better
context management.
"""

import sys
from pathlib import Path

# Add CIE to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cie.core.backend import CIEBackend
from cie.core.models import Workload
from cie.evaluators.context_evaluator import ContextEvaluator
from cie.optimizers.context_optimizer import (
    ContextAwareOptimizer,
    ContextCompressionOptimizer,
    ContextNavigationOptimizer,
)
from cie.tools.context_tools import AgentContextTools


def demonstrate_context_introspection():
    """Demonstrate basic context introspection capabilities."""
    print("=" * 60)
    print("Context Introspection Demo")
    print("=" * 60)

    # Create context tools
    tools = AgentContextTools()

    # Create some complex context to analyze
    large_data = {
        "users": [{"id": i, "name": f"user_{i}", "data": "x" * 1000} for i in range(100)],
        "config": {"setting_" + str(i): f"value_{i}" for i in range(50)},
        "cache": {"cached_" + str(i): list(range(i * 10)) for i in range(20)},
        "metadata": {"created_at": "2024-01-01", "version": "1.0.0", "debug": True},
    }

    # Inject into context for analysis
    tools.inject_into_context("/demo/large_data", large_data)

    # Inspect current context
    print("1. Inspecting context structure...")
    inspection = tools.inspect_context("current", max_depth=4)
    summary = inspection["summary"]

    print(f"   Total nodes: {summary['total_nodes']}")
    print(f"   Total size: {summary['total_size']:,} bytes")
    print(f"   Max depth: {summary['max_depth']}")
    print(f"   Type distribution: {dict(summary['type_distribution'])}")

    # Show hotspots
    hotspots = inspection["hotspots"]
    if hotspots:
        print(f"\n2. Access hotspots:")
        for path, count in hotspots[:5]:
            print(f"   {path}: {count} accesses")

    # Analyze efficiency
    print("\n3. Context analysis...")
    analysis = tools.analyze_context()
    print(f"   Efficiency score: {analysis['efficiency_score']:.2f}")
    print(f"   Optimization potential: {analysis['optimization_potential']:.2f}")

    if analysis["suggestions"]["compression_candidates"]:
        print(
            f"   Compression candidates: {len(analysis['suggestions']['compression_candidates'])}"
        )

    return tools, analysis


def demonstrate_context_compression():
    """Demonstrate context compression strategies."""
    print("\n" + "=" * 60)
    print("Context Compression Demo")
    print("=" * 60)

    tools = AgentContextTools()

    # Create large, compressible data
    large_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 1000
    nested_data = {f"level_{i}": {f"item_{j}": f"data_{j}" for j in range(100)} for i in range(10)}

    tools.inject_into_context("/demo/large_text", large_text)
    tools.inject_into_context("/demo/nested_data", nested_data)

    # Test different compression strategies
    strategies = ["auto", "truncate", "summarize", "hierarchical"]

    print("Testing compression strategies:")
    for strategy in strategies:
        # Create checkpoint before compression
        checkpoint = tools.checkpoint_context(f"before_{strategy}")

        # Apply compression
        result = tools.compress_context(strategy=strategy, threshold=500)

        print(f"\n   Strategy: {strategy}")
        print(f"   Original size: {result['original_size']:,} bytes")
        print(f"   Compressed size: {result['compressed_size']:,} bytes")
        print(f"   Compression ratio: {result['compression_ratio']:.2f}")

        # Calculate space saved
        space_saved = result["original_size"] - result["compressed_size"]
        print(
            f"   Space saved: {space_saved:,} bytes ({(1 - result['compression_ratio']) * 100:.1f}%)"
        )


def demonstrate_context_navigation():
    """Demonstrate context navigation capabilities."""
    print("\n" + "=" * 60)
    print("Context Navigation Demo")
    print("=" * 60)

    tools = AgentContextTools()

    # Create structured data for navigation
    file_system = {
        "documents": {
            "reports": ["report1.txt", "report2.txt", "summary.pdf"],
            "presentations": ["slides.pptx", "demo.pdf"],
        },
        "data": {"raw": ["dataset1.csv", "dataset2.json"], "processed": ["cleaned_data.pkl"]},
        "config": {"settings.json": {"theme": "dark", "auto_save": True}},
    }

    tools.inject_into_context("/filesystem", file_system)

    # Demonstrate navigation commands
    navigation_commands = [
        "pwd",  # Show current directory
        "ls /",  # List root
        "cd /filesystem",  # Change directory
        "ls",  # List current directory
        "find report",  # Find files containing 'report'
        "cd documents",  # Go deeper
        "ls",  # List documents
    ]

    print("Navigation commands demonstration:")
    for cmd in navigation_commands:
        try:
            result = tools.navigate_context(cmd)
            print(f"   {cmd:15} → {result}")
        except Exception as e:
            print(f"   {cmd:15} → Error: {e}")


def run_context_aware_optimization():
    """Run complete context-aware optimization cycle."""
    print("\n" + "=" * 60)
    print("Context-Aware Optimization Cycle")
    print("=" * 60)

    # Initialize components
    backend = CIEBackend()
    context_optimizer = ContextAwareOptimizer()
    compression_optimizer = ContextCompressionOptimizer()
    navigation_optimizer = ContextNavigationOptimizer()
    evaluator = ContextEvaluator()

    # Create test workload
    workload = Workload(
        name="context_optimization_test",
        config={"type": "context", "size": "medium", "complexity": "high"},
    )

    optimizers = [
        ("Context-Aware", context_optimizer),
        ("Compression", compression_optimizer),
        ("Navigation", navigation_optimizer),
    ]

    print("Running optimization cycles...")

    results = []
    for opt_name, optimizer in optimizers:
        print(f"\n--- {opt_name} Optimizer ---")

        # Create some context state for the optimizer
        context_state = {
            "context_size": 50000,
            "context_depth": 8,
            "access_patterns": {"path_1": 15, "path_2": 8, "path_3": 3},
            "large_objects": 5,
            "compression_candidates": 12,
        }

        # Generate policy
        policy = optimizer.propose(context_state)
        print(f"Generated policy: {policy.name}")
        print(f"Policy config: {policy.config}")

        # Evaluate policy
        trial = evaluator.run(policy, workload, optimizer_name=optimizer.name)

        # Display key metrics
        key_metrics = [
            "context_efficiency",
            "context_nodes",
            "context_size",
            "total_execution_time",
        ]

        print(f"Evaluation results:")
        for metric in key_metrics:
            if metric in trial.metrics:
                value = trial.metrics[metric]
                if isinstance(value, float):
                    print(f"  {metric}: {value:.4f}")
                else:
                    print(f"  {metric}: {value}")

        print(f"Overall score: {trial.score:.4f}")

        # Store results
        backend.add_trial(trial)
        optimizer.observe(policy, trial.metrics)
        results.append((opt_name, trial))

        # Show optimizer state
        state = optimizer.get_state()
        print(f"Optimizer state: {state}")

    # Find best result
    best_optimizer, best_trial = max(results, key=lambda x: x[1].score)
    print(f"\n🏆 Best optimizer: {best_optimizer}")
    print(f"   Best score: {best_trial.score:.4f}")
    print(f"   Context efficiency: {best_trial.metrics.get('context_efficiency', 'N/A')}")

    return backend, results


def demonstrate_context_views_and_caching():
    """Demonstrate context views and caching."""
    print("\n" + "=" * 60)
    print("Context Views and Caching Demo")
    print("=" * 60)

    tools = AgentContextTools()

    # Create diverse data for view creation
    project_data = {
        "critical": {"passwords": "secret123", "api_keys": "key456", "tokens": "token789"},
        "user_data": {
            "profiles": [{"id": i, "name": f"user{i}", "active": i % 2 == 0} for i in range(100)]
        },
        "analytics": {"page_views": 15000, "conversions": 450, "bounce_rate": 0.35},
        "temp_cache": {f"temp_{i}": f"temporary_data_{i}" for i in range(200)},
        "config": {"theme": "dark", "debug": False, "version": "2.1.0"},
    }

    tools.inject_into_context("/project", project_data)

    # Create different types of views
    print("Creating context views...")

    # 1. Critical data view
    critical_view = tools.create_context_view(
        "critical_data",
        selector=lambda node: "critical" in node.path or "password" in node.path.lower(),
    )
    print(f"   Critical data view: {critical_view['size']} items")

    # 2. Small objects view
    small_objects = tools.create_context_view(
        "small_objects", selector=lambda node: node.size < 100 and node.depth > 2
    )
    print(f"   Small objects view: {small_objects['size']} items")

    # 3. Cache frequently accessed items
    print("\nTesting caching...")
    # Simulate access patterns
    for i in range(10):
        tools.query_context("critical")  # Access critical data multiple times
        tools.query_context("analytics")  # Access analytics

    # Cache hotspots
    hotspots = tools.introspector.get_hotspots(3)
    cached_count = 0
    for path, access_count in hotspots:
        if tools.cache_context(f"hotspot_{cached_count}", path):
            cached_count += 1
            print(f"   Cached hotspot: {path} ({access_count} accesses)")

    # Show cache contents
    print(f"\nCache summary:")
    for key, value in tools.context_cache.items():
        if isinstance(value, dict):
            print(f"   {key}: {len(value)} items")
        else:
            print(f"   {key}: {type(value).__name__}")


def main():
    """Run all context management demonstrations."""
    print("🚀 CIE Context Management Example")
    print("This example demonstrates context introspection and optimization capabilities.\n")

    try:
        # Run demonstrations
        tools, analysis = demonstrate_context_introspection()
        demonstrate_context_compression()
        demonstrate_context_navigation()
        demonstrate_context_views_and_caching()
        backend, results = run_context_aware_optimization()

        # Summary
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)

        print("✅ Context introspection: Successfully analyzed runtime context")
        print("✅ Context compression: Tested multiple compression strategies")
        print("✅ Context navigation: Demonstrated filesystem-like navigation")
        print("✅ Context caching: Created views and cached hotspots")
        print("✅ Context optimization: Ran complete optimization cycles")

        print(f"\nFinal statistics:")
        print(f"  Total trials run: {len(backend.trials)}")
        print(f"  Best score achieved: {max(trial.score for _, trial in results):.4f}")
        print(f"  Context tools cache: {len(tools.context_cache)} items")

        # Show optimization suggestions
        suggestions = analysis["suggestions"]
        if any(suggestions.values()):
            print(f"\n💡 Optimization opportunities found:")
            if suggestions["large_objects"]:
                print(f"   - {len(suggestions['large_objects'])} large objects to compress")
            if suggestions["deep_nesting"]:
                print(f"   - {len(suggestions['deep_nesting'])} deeply nested structures")
            if suggestions["compression_candidates"]:
                print(f"   - {len(suggestions['compression_candidates'])} compression candidates")

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print(f"\n🎉 Context management demonstration completed successfully!")
    print(f"   Context tools provide powerful introspection capabilities")
    print(f"   for optimizing agent performance through better context management.")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

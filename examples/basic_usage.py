#!/usr/bin/env python3
"""
Basic usage example for CIE optimization framework.

This script demonstrates how to use CIE programmatically
for running optimization experiments.
"""

import time
from pathlib import Path

from cie.config.settings import CIEConfig
from cie.core.backend import CIEBackend


def main():
    """Run a basic optimization experiment."""
    print("🚀 CIE Basic Usage Example")
    print("=" * 50)

    # Create configuration
    config = CIEConfig()
    config.storage.backend = "json"
    config.storage.experiments_dir = str(Path.home() / ".cie" / "examples")
    config.model.provider = "mock"  # Use mock for demo
    config.model.model_name = "mock-model"

    print("📊 Configuration:")
    print(f"  Storage: {config.storage.backend}")
    print(f"  Model: {config.model.provider} ({config.model.model_name})")
    print(f"  Experiments dir: {config.storage.experiments_dir}")
    print()

    # Initialize backend
    print("🔧 Initializing backend...")
    backend = CIEBackend(config)
    print(f"✅ Backend initialized with {len(backend.optimizers)} optimizers")
    print(f"✅ {len(backend.workloads)} workloads available")
    print()

    # Show available optimizers
    print("🎯 Available Optimizers:")
    optimizers = backend.list_optimizers()
    for i, (name, meta) in enumerate(optimizers):
        print(f"  {i}: {name}")
        for key, value in meta.items():
            if value is not None:
                print(f"     {key}: {value}")
    print()

    # Show available workloads
    print("📋 Available Workloads:")
    for i, workload in enumerate(backend.workloads):
        print(f"  {i}: {workload.name} ({workload.items} items)")
        if workload.description:
            print(f"     {workload.description}")
    print()

    # Run optimization experiment
    print("🧪 Running Optimization Experiment")
    print("-" * 40)

    num_iterations = 5
    best_score = float("inf")
    best_trial = None
    best_policy = None

    for i in range(num_iterations):
        print(f"\nIteration {i + 1}/{num_iterations}")

        # Generate policy using first optimizer
        print("  🎲 Generating policy...")
        policy = backend.propose_once(0)
        print(f"  ✅ Policy generated: {policy.name}")
        print(f"  📄 Parameters: {policy.params}")

        # Evaluate policy on first workload
        print("  ⚡ Evaluating policy...")
        trial = backend.eval_policy(policy, 0)
        print("  ✅ Evaluation complete!")
        print(f"  📊 Score: {trial.score:.4f}")
        print("  📈 Metrics:")
        for metric, value in trial.metrics.items():
            print(f"    {metric}: {value}")

        # Track best trial
        if trial.score < best_score:
            best_score = trial.score
            best_trial = trial
            best_policy = policy
            print("  🏆 New best score!")

        # Small delay for readability
        time.sleep(0.5)

    # Show results
    print("\n🎯 Experiment Complete!")
    print("=" * 40)
    print(f"Total trials: {len(backend.trials)}")
    print(f"Best score: {best_score:.4f}")
    print(f"Best trial: #{best_trial.id}")
    print(f"Best policy: {best_policy.name}")
    print()

    # Show Pareto frontier
    print("🏆 Pareto Frontier:")
    if backend.pareto:
        for i, trial in enumerate(backend.pareto[:5]):  # Show top 5
            print(f"  {i + 1}. Trial #{trial.id}: score={trial.score:.4f}")
            print(f"     latency={trial.metrics.get('latency_p95', 0):.1f}ms")
            print(f"     cost=${trial.metrics.get('cost_per_req', 0):.5f}")
            print(f"     success={trial.metrics.get('task_success', 0):.3f}")
    else:
        print("  No Pareto frontier available")
    print()

    # Try to adopt the best policy
    print("🔒 Attempting to adopt best policy...")
    success = backend.adopt_policy(best_trial.id)

    if success:
        print("✅ Policy adopted successfully!")
        print(f"🎯 Active policy: {backend.active_policy.name}")
        print("📋 Actions:")
        for action in backend.active_policy.actions:
            print(f"  - {action}")
    else:
        print("❌ Policy adoption failed (didn't pass guardrails)")
        print("📋 Guardrails check:")
        print(f"  Tool error rate: {best_trial.metrics.get('tool_error_rate', 0):.3f} (max: 0.03)")
        print(f"  Task success rate: {best_trial.metrics.get('task_success', 0):.3f} (min: 0.7)")

    # Show final statistics
    print("\n📈 Final Statistics:")
    stats = backend.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Cleanup
    print("\n🧹 Cleaning up...")
    backend.close()
    print("✅ Done!")


if __name__ == "__main__":
    main()

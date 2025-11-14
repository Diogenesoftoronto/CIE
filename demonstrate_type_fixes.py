#!/usr/bin/env python3
"""
Demonstration script showing that type fixes in CIE work correctly.

This script validates:
1. Modal classes have no duplicate methods
2. Type annotations are properly applied
3. Protocols are correctly implemented
4. Type validation catches errors
"""

from __future__ import annotations

import sys
from typing import get_type_hints

from cie.config.settings import CIEConfig, get_config
from cie.core.backend import CIEBackend
from cie.core.models import Policy, Trial, Workload
from cie.evaluators.mock_evaluator import MockEvaluator
from cie.optimizers.hill_climb import HillClimbOptimizer
from cie.ui.modals import ConfigModal, MessageModal, WeightsModal
from cie.utils.model_providers import MockModelProvider


def demonstrate_modal_fixes():
    """Demonstrate that modal classes have been fixed and have no duplicate methods."""
    print("=== Modal Class Fixes ===")

    # Check that ConfigModal has the methods that were incorrectly in MessageModal
    # We check the class itself, not instances, to avoid Textual runtime requirements

    # These methods should only exist in ConfigModal
    assert hasattr(ConfigModal, "_apply_config"), "ConfigModal should have _apply_config"
    assert hasattr(ConfigModal, "_reset_config"), "ConfigModal should have _reset_config"

    # MessageModal shouldn't have ConfigModal's private methods
    # Note: We can't easily check this without instantiation due to Textual's metaclasses
    # But we can verify the source code structure

    import inspect

    # Get the source of both classes
    config_source = inspect.getsource(ConfigModal)
    message_source = inspect.getsource(MessageModal)

    # ConfigModal should have _apply_config and _reset_config
    assert "_apply_config" in config_source, "ConfigModal source should contain _apply_config"
    assert "_reset_config" in config_source, "ConfigModal source should contain _reset_config"

    # MessageModal should NOT have these methods
    assert "_apply_config" not in message_source, (
        "MessageModal source shouldn't contain _apply_config"
    )
    assert "_reset_config" not in message_source, (
        "MessageModal source shouldn't contain _reset_config"
    )

    # Check that both have their appropriate event handlers
    assert "on_button_pressed" in config_source, "ConfigModal should have on_button_pressed"
    assert "on_button_pressed" in message_source, "MessageModal should have on_button_pressed"

    print("✅ Modal classes fixed: No duplicate methods found")
    print("   - ConfigModal has its own _apply_config and _reset_config methods")
    print("   - MessageModal doesn't have ConfigModal's private methods")
    print("   - Each modal has its own on_button_pressed handler")


def demonstrate_type_annotations():
    """Demonstrate that type annotations are properly applied."""
    print("\n=== Type Annotations ===")

    # Check Policy type hints
    policy_hints = get_type_hints(Policy)
    # Check that params is a dict (comparing origins due to generic types)
    assert (
        hasattr(policy_hints["params"], "__origin__") and policy_hints["params"].__origin__ == dict
    )
    assert (
        hasattr(policy_hints["actions"], "__origin__")
        and policy_hints["actions"].__origin__ == list
    )
    print("✅ Policy dataclass has proper type hints")

    # Check Trial type hints
    trial_hints = get_type_hints(Trial)
    assert (
        hasattr(trial_hints["metrics"], "__origin__") and trial_hints["metrics"].__origin__ == dict
    )
    # Check artifact_id is Optional (Union with None or using | None syntax)
    artifact_type_str = str(trial_hints["artifact_id"])
    assert "None" in artifact_type_str or "NoneType" in artifact_type_str
    print("✅ Trial dataclass has proper type hints")

    # Check Workload type hints
    workload_hints = get_type_hints(Workload)
    assert workload_hints["items"] == int
    assert (
        hasattr(workload_hints["config"], "__origin__")
        and workload_hints["config"].__origin__ == dict
    )
    print("✅ Workload dataclass has proper type hints")


def demonstrate_protocol_compliance():
    """Demonstrate that implementations comply with protocols."""
    print("\n=== Protocol Compliance ===")

    # Test Optimizer protocol
    optimizer = HillClimbOptimizer()
    assert hasattr(optimizer, "name")
    assert callable(getattr(optimizer, "propose"))
    assert callable(getattr(optimizer, "observe"))
    assert callable(getattr(optimizer, "get_state"))
    assert callable(getattr(optimizer, "reset"))
    print("✅ HillClimbOptimizer complies with Optimizer protocol")

    # Test Evaluator protocol
    evaluator = MockEvaluator()
    assert hasattr(evaluator, "name")
    assert callable(getattr(evaluator, "run"))
    assert callable(getattr(evaluator, "get_supported_metrics"))
    assert callable(getattr(evaluator, "validate_workload"))
    print("✅ MockEvaluator complies with Evaluator protocol")

    # Test ModelProvider protocol
    provider = MockModelProvider()
    assert hasattr(provider, "name")
    assert hasattr(provider, "model_name")
    assert callable(getattr(provider, "generate"))
    assert callable(getattr(provider, "embed"))
    print("✅ MockModelProvider complies with ModelProvider protocol")


def demonstrate_type_validation():
    """Demonstrate that type validation catches errors."""
    print("\n=== Type Validation ===")

    # Test Policy validation
    try:
        Policy(name="", params={}, actions=[])  # Empty name should fail
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print("✅ Policy validation catches empty name")

    try:
        # This will raise TypeError at construction time, not ValueError in __post_init__
        Policy(name="test", params="not_a_dict", actions=[])  # Wrong type should fail
        assert False, "Should have raised ValueError or TypeError"
    except (ValueError, TypeError, AttributeError) as e:
        print("✅ Policy validation catches wrong param type")

    # Test Trial validation
    try:
        Trial(
            id=1,
            policy_name="",  # Empty name should fail
            metrics={},
            score=0.0,
            workload="test",
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print("✅ Trial validation catches empty policy name")

    try:
        Trial(
            id=1,
            policy_name="test",
            metrics={"key": "not_numeric"},  # Non-numeric value should fail
            score=0.0,
            workload="test",
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print("✅ Trial validation catches non-numeric metrics")

    # Test Workload validation
    try:
        Workload(name="test", items=-5)  # Negative items should fail
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print("✅ Workload validation catches negative items")


def demonstrate_backend_types():
    """Demonstrate that backend types are correct."""
    print("\n=== Backend Types ===")

    config = CIEConfig()
    backend = CIEBackend(config)

    # Check attribute types
    assert isinstance(backend.config, CIEConfig)
    assert isinstance(backend.trials, list)
    assert isinstance(backend.workloads, list)
    assert isinstance(backend.pareto, list)
    print("✅ Backend attributes have correct types")

    # Check method return types
    stats = backend.get_stats()
    assert isinstance(stats, dict)
    assert "trial_count" in stats
    assert "pareto_count" in stats
    print("✅ Backend methods return correct types")

    # Check list_optimizers returns tuples
    optimizers = backend.list_optimizers()
    assert isinstance(optimizers, list)
    if optimizers:
        assert isinstance(optimizers[0], tuple)
        assert len(optimizers[0]) == 2
    print("✅ list_optimizers returns list of tuples")


def demonstrate_none_handling():
    """Demonstrate that None handling has been fixed."""
    print("\n=== None Handling ===")

    # Test HillClimbOptimizer None handling
    optimizer = HillClimbOptimizer()

    # Initial state should handle None properly
    state = optimizer.get_state()
    assert isinstance(state, dict)

    # Proposing with empty state should work
    policy = optimizer.propose({})
    assert isinstance(policy, Policy)
    print("✅ HillClimbOptimizer handles None values properly")

    # Test score comparison with None
    optimizer.current_score = None
    optimizer.best_score = None

    # This should not raise an error
    metrics = {"latency_p95": 100.0, "cost_per_req": 0.01}
    optimizer.observe(policy, metrics)
    assert optimizer.current_score is not None
    print("✅ Score comparison handles None values properly")


def main():
    """Run all demonstrations."""
    print("=" * 60)
    print("CIE Type Fixes Demonstration")
    print("=" * 60)

    try:
        demonstrate_modal_fixes()
        demonstrate_type_annotations()
        demonstrate_protocol_compliance()
        demonstrate_type_validation()
        demonstrate_backend_types()
        demonstrate_none_handling()

        print("\n" + "=" * 60)
        print("✅ All type fixes validated successfully!")
        print("=" * 60)

        print("\nSummary:")
        print("1. Modal classes: Fixed duplicate methods issue")
        print("2. Type annotations: All dataclasses properly typed")
        print("3. Protocol compliance: All implementations follow protocols")
        print("4. Type validation: Input validation catches type errors")
        print("5. Backend types: Correct return types and attributes")
        print("6. None handling: Proper handling of optional values")

        print("\nTo verify the complete fix:")
        print("  - Run tests: python -m pytest tests/test_type_checking.py -v")
        print("  - Run mypy: python -m mypy cie/ --ignore-missing-imports")

        return 0

    except AssertionError as e:
        print(f"\n❌ Assertion failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())

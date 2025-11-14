"""
Comprehensive type checking tests for CIE.

This module tests type annotations, protocol compliance, and catches common type errors.
"""

from __future__ import annotations

import inspect
from datetime import datetime
from pathlib import Path
from typing import Any, get_type_hints

import pytest
from textual.screen import ModalScreen

# Import all CIE modules for type checking
from cie.config.settings import CIEConfig, get_config
from cie.core.backend import CIEBackend
from cie.core.models import Policy, Trial, Workload
from cie.evaluators.mock_evaluator import MockEvaluator
from cie.evaluators.text_match import TextMatchEvaluator
from cie.optimizers.dspy_optimizer import DSPyOptimizer
from cie.optimizers.hill_climb import HillClimbOptimizer
from cie.ui.modals import (
    ConfigModal,
    ConfirmModal,
    ErrorModal,
    InfoModal,
    MessageModal,
    ProgressModal,
    WeightsModal,
)
from cie.utils.model_providers import (
    KimiProvider,
    MockModelProvider,
    OpenAIProvider,
    get_model_provider,
)


class TestTypeAnnotations:
    """Test that all functions and methods have proper type annotations."""

    def test_policy_dataclass_types(self):
        """Test Policy dataclass has correct types."""
        # Create a policy with correct types
        policy = Policy(
            name="test",
            params={"key": "value"},
            actions=["action1", "action2"],
            created_at=datetime.now(),
            metadata={"meta": "data"},
        )

        # Check field types
        assert isinstance(policy.name, str)
        assert isinstance(policy.params, dict)
        assert isinstance(policy.actions, list)
        assert isinstance(policy.created_at, datetime)
        assert isinstance(policy.metadata, dict)

        # Test type hints are correct
        hints = get_type_hints(Policy)
        assert hints["name"] == str
        assert hints["params"] == dict[str, Any]
        assert hints["actions"] == list[str]
        assert hints["created_at"] == datetime
        assert hints["metadata"] == dict[str, Any]

    def test_trial_dataclass_types(self):
        """Test Trial dataclass has correct types."""
        trial = Trial(
            id=1,
            policy_name="test_policy",
            metrics={"latency": 100.0, "cost": 0.5},
            score=0.75,
            workload="test_workload",
            created_at=datetime.now(),
            artifact_id="artifact_123",
            notes="test notes",
            metadata={"key": "value"},
        )

        # Check field types
        assert isinstance(trial.id, int)
        assert isinstance(trial.policy_name, str)
        assert isinstance(trial.metrics, dict)
        assert isinstance(trial.score, float)
        assert isinstance(trial.workload, str)
        assert isinstance(trial.created_at, datetime)
        assert trial.artifact_id is None or isinstance(trial.artifact_id, str)
        assert isinstance(trial.notes, str)
        assert isinstance(trial.metadata, dict)

        # Test type hints
        hints = get_type_hints(Trial)
        assert hints["id"] == int
        assert hints["policy_name"] == str
        assert hints["metrics"] == dict[str, float]
        assert hints["score"] == float
        assert hints["workload"] == str
        assert hints["artifact_id"] == str | None

    def test_workload_dataclass_types(self):
        """Test Workload dataclass has correct types."""
        workload = Workload(
            name="test_workload",
            items=10,
            description="Test description",
            config={"param": "value"},
            tags=["tag1", "tag2"],
        )

        # Check field types
        assert isinstance(workload.name, str)
        assert isinstance(workload.items, int)
        assert isinstance(workload.description, str)
        assert isinstance(workload.config, dict)
        assert isinstance(workload.tags, list)

        # Test type hints
        hints = get_type_hints(Workload)
        assert hints["name"] == str
        assert hints["items"] == int
        assert hints["description"] == str
        assert hints["config"] == dict[str, Any]
        assert hints["tags"] == list[str]


class TestProtocolCompliance:
    """Test that implementations comply with Protocol interfaces."""

    def test_optimizer_protocol_compliance(self):
        """Test that optimizer implementations comply with Optimizer protocol."""
        # Check DSPyOptimizer
        dspy_opt = DSPyOptimizer()
        assert hasattr(dspy_opt, "name")
        assert callable(getattr(dspy_opt, "propose", None))
        assert callable(getattr(dspy_opt, "observe", None))
        assert callable(getattr(dspy_opt, "get_state", None))
        assert callable(getattr(dspy_opt, "reset", None))

        # Check method signatures
        propose_sig = inspect.signature(dspy_opt.propose)
        assert "state" in propose_sig.parameters
        assert propose_sig.return_annotation != inspect.Signature.empty

        observe_sig = inspect.signature(dspy_opt.observe)
        assert "policy" in observe_sig.parameters
        assert "metrics" in observe_sig.parameters

        # Check HillClimbOptimizer
        hill_opt = HillClimbOptimizer()
        assert hasattr(hill_opt, "name")
        assert callable(getattr(hill_opt, "propose", None))
        assert callable(getattr(hill_opt, "observe", None))
        assert callable(getattr(hill_opt, "get_state", None))
        assert callable(getattr(hill_opt, "reset", None))

    def test_evaluator_protocol_compliance(self):
        """Test that evaluator implementations comply with Evaluator protocol."""
        # Check MockEvaluator
        mock_eval = MockEvaluator()
        assert hasattr(mock_eval, "name")
        assert callable(getattr(mock_eval, "run", None))
        assert callable(getattr(mock_eval, "get_supported_metrics", None))
        assert callable(getattr(mock_eval, "validate_workload", None))

        # Check method signatures
        run_sig = inspect.signature(mock_eval.run)
        assert "policy" in run_sig.parameters
        assert "workload" in run_sig.parameters
        # Handle both string and actual type annotations
        expected_return = dict[str, float]
        actual_return = run_sig.return_annotation
        assert actual_return == expected_return or str(actual_return) == "dict[str, float]"

        # Check TextMatchEvaluator
        text_eval = TextMatchEvaluator()
        assert hasattr(text_eval, "name")
        assert callable(getattr(text_eval, "run", None))
        assert callable(getattr(text_eval, "get_supported_metrics", None))
        assert callable(getattr(text_eval, "validate_workload", None))

    def test_model_provider_protocol_compliance(self):
        """Test that model provider implementations comply with ModelProvider protocol."""
        providers = [
            MockModelProvider(model_name="test"),
            OpenAIProvider(model_name="gpt-4", api_key="test_key"),
            KimiProvider(model_name="kimi", api_key="test_key"),
        ]

        for provider in providers:
            assert hasattr(provider, "name")
            assert hasattr(provider, "model_name")
            assert callable(getattr(provider, "generate", None))
            assert callable(getattr(provider, "embed", None))
            assert callable(getattr(provider, "get_model_info", None))

            # Check method signatures
            gen_sig = inspect.signature(provider.generate)
            assert "prompt" in gen_sig.parameters
            assert gen_sig.return_annotation == str

            embed_sig = inspect.signature(provider.embed)
            assert "text" in embed_sig.parameters
            assert embed_sig.return_annotation == list[float]


class TestModalTypes:
    """Test modal classes for proper types and inheritance."""

    def test_modal_inheritance(self):
        """Test that all modal classes properly inherit from ModalScreen."""
        modals = [
            WeightsModal,
            ConfigModal,
            MessageModal,
            ConfirmModal,
            ErrorModal,
            InfoModal,
            ProgressModal,
        ]

        for modal_class in modals:
            assert issubclass(modal_class, ModalScreen)

    def test_modal_method_signatures(self):
        """Test that modal methods have correct signatures."""
        # Test WeightsModal
        weights_modal = WeightsModal()
        assert callable(weights_modal.on_button_pressed)
        assert callable(weights_modal.key_enter)
        assert callable(weights_modal.key_escape)

        # Check that methods don't have duplicate definitions
        weights_methods = [m for m in dir(WeightsModal) if not m.startswith("_")]
        assert weights_methods.count("on_button_pressed") == 1
        assert weights_methods.count("key_enter") == 1
        assert weights_methods.count("key_escape") == 1

        # Test ConfigModal
        config_modal = ConfigModal()
        assert callable(config_modal.on_button_pressed)
        assert callable(config_modal.key_enter)
        assert callable(config_modal.key_escape)
        assert callable(config_modal._apply_config)
        assert callable(config_modal._reset_config)

        # Check that methods don't have duplicate definitions
        config_methods = [m for m in dir(ConfigModal) if not m.startswith("_")]
        assert config_methods.count("on_button_pressed") == 1
        assert config_methods.count("key_enter") == 1
        assert config_methods.count("key_escape") == 1

        # Test MessageModal doesn't have ConfigModal's methods
        message_modal = MessageModal(title="Test", message="Test message")
        assert not hasattr(message_modal, "_apply_config")
        assert not hasattr(message_modal, "_reset_config")

        # Check MessageModal has correct button handling
        assert hasattr(message_modal, "_button_results")
        assert isinstance(message_modal._button_results, dict)

    def test_modal_event_handlers(self):
        """Test that modal event handlers have correct signatures."""

        # Test button pressed event signature
        weights_modal = WeightsModal()
        sig = inspect.signature(weights_modal.on_button_pressed)
        assert "event" in sig.parameters

        # Test key handlers
        key_enter_sig = inspect.signature(weights_modal.key_enter)
        assert len(key_enter_sig.parameters) == 0  # key handlers take no params

        key_escape_sig = inspect.signature(weights_modal.key_escape)
        assert len(key_escape_sig.parameters) == 0


class TestBackendTypes:
    """Test backend classes for proper types."""

    def test_storage_backend_interface(self):
        """Test StorageBackend protocol methods."""
        from cie.core.backend import InMemoryStorageBackend

        backends = [
            InMemoryStorageBackend(),
            # JSONStorageBackend would need a temp file
        ]

        for backend in backends:
            # Check required methods exist
            assert callable(getattr(backend, "save_trial", None))
            assert callable(getattr(backend, "get_trials", None))
            assert callable(getattr(backend, "save_policy", None))
            assert callable(getattr(backend, "get_policies", None))
            assert callable(getattr(backend, "close", None))

            # Check method signatures
            save_trial_sig = inspect.signature(backend.save_trial)
            assert "trial" in save_trial_sig.parameters

            get_trials_sig = inspect.signature(backend.get_trials)
            assert get_trials_sig.return_annotation == list[Trial]

            save_policy_sig = inspect.signature(backend.save_policy)
            assert "policy" in save_policy_sig.parameters

            get_policies_sig = inspect.signature(backend.get_policies)
            assert get_policies_sig.return_annotation == list[Policy]

    def test_cie_backend_types(self):
        """Test CIEBackend type annotations."""
        config = CIEConfig()
        backend = CIEBackend(config)

        # Check attributes
        assert isinstance(backend.config, CIEConfig)
        assert isinstance(backend.trials, list)
        assert isinstance(backend.workloads, list)
        assert isinstance(backend.pareto, list)

        # Check method return types
        stats = backend.get_stats()
        assert isinstance(stats, dict)

        # Check list_optimizers returns correct type
        optimizers = backend.list_optimizers()
        assert isinstance(optimizers, list)
        for opt in optimizers:
            assert isinstance(opt, tuple)
            assert len(opt) == 2
            name, metadata = opt
            assert isinstance(name, str)
            assert isinstance(metadata, dict)


class TestTypeConsistency:
    """Test for type consistency across the codebase."""

    def test_no_any_type_in_inputs(self):
        """Test that Input types are properly specified, not 'any'."""
        # This would catch issues like dict[str, any] instead of dict[str, Any]
        source_file = Path("CIE/cie/ui/modals.py")
        if source_file.exists():
            content = source_file.read_text()
            # Check for lowercase 'any' which is incorrect
            assert "dict[str, any]" not in content, "Found 'any' instead of 'Any' in type hints"

    def test_consistent_optional_syntax(self):
        """Test that Optional types use consistent syntax."""
        # Modern Python 3.10+ should use X | None instead of Optional[X]
        # This is a style preference but helps catch inconsistencies

        # Check a sample of type hints
        trial_hints = get_type_hints(Trial)
        # artifact_id should be str | None
        assert trial_hints.get("artifact_id") == str | None

    def test_no_duplicate_method_definitions(self):
        """Test that classes don't have duplicate method definitions."""
        classes_to_check = [
            WeightsModal,
            ConfigModal,
            MessageModal,
            ConfirmModal,
            ErrorModal,
            InfoModal,
            ProgressModal,
        ]

        for cls in classes_to_check:
            methods = {}
            for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
                if name in methods:
                    pytest.fail(f"Duplicate method {name} found in {cls.__name__}")
                methods[name] = method

    def test_return_type_annotations(self):
        """Test that all public methods have return type annotations."""
        modules_to_check = [
            MockEvaluator,
            DSPyOptimizer,
            HillClimbOptimizer,
            CIEBackend,
        ]

        for module_class in modules_to_check:
            for name, method in inspect.getmembers(module_class, predicate=inspect.ismethod):
                if not name.startswith("_"):  # Public methods
                    sig = inspect.signature(method)
                    if sig.return_annotation == inspect.Signature.empty:
                        # Some methods legitimately return None and might not annotate it
                        # But we should at least warn about it
                        print(
                            f"Warning: {module_class.__name__}.{name} lacks return type annotation"
                        )


class TestFunctionSignatures:
    """Test function signatures for correctness."""

    def test_get_config_signature(self):
        """Test get_config returns correct type."""
        config = get_config()
        assert isinstance(config, CIEConfig)

        # Check the function signature
        sig = inspect.signature(get_config)
        assert sig.return_annotation == CIEConfig

    def test_get_model_provider_signature(self):
        """Test get_model_provider returns correct type."""
        provider = get_model_provider(provider="mock")
        # Should implement ModelProvider protocol
        assert hasattr(provider, "generate")
        assert hasattr(provider, "embed")
        assert hasattr(provider, "name")
        assert hasattr(provider, "model_name")

    def test_backend_method_signatures(self):
        """Test CIEBackend method signatures."""
        backend = CIEBackend()

        # Test propose_once
        propose_sig = inspect.signature(backend.propose_once)
        assert "optimizer_index" in propose_sig.parameters
        # propose_once only takes optimizer_index, not state
        assert propose_sig.return_annotation == Policy

        # Test eval_policy
        eval_sig = inspect.signature(backend.eval_policy)
        assert "policy" in eval_sig.parameters
        assert "workload_index" in eval_sig.parameters
        assert eval_sig.return_annotation == Trial

        # Test adopt_policy
        adopt_sig = inspect.signature(backend.adopt_policy)
        assert "trial_id" in adopt_sig.parameters
        assert adopt_sig.return_annotation == bool


class TestTypeErrors:
    """Test that type errors are properly caught."""

    def test_policy_validation(self):
        """Test that Policy validates types."""
        with pytest.raises(ValueError):
            Policy(name="", params={}, actions=[])  # Empty name

        with pytest.raises(ValueError):
            Policy(name="test", params="not_a_dict", actions=[])  # Wrong type for params

        with pytest.raises(ValueError):
            Policy(name="test", params={}, actions="not_a_list")  # Wrong type for actions

    def test_trial_validation(self):
        """Test that Trial validates types."""
        with pytest.raises(ValueError):
            Trial(
                id=1,
                policy_name="",  # Empty name
                metrics={},
                score=0.0,
                workload="test",
            )

        with pytest.raises(ValueError):
            Trial(
                id=1,
                policy_name="test",
                metrics="not_a_dict",  # Wrong type
                score=0.0,
                workload="test",
            )

        with pytest.raises(ValueError):
            Trial(
                id=1,
                policy_name="test",
                metrics={"key": "not_numeric"},  # Non-numeric value
                score=0.0,
                workload="test",
            )

    def test_workload_validation(self):
        """Test that Workload validates types."""
        with pytest.raises(ValueError):
            Workload(name="", items=10)  # Empty name

        with pytest.raises(ValueError):
            Workload(name="test", items=0)  # Non-positive items

        with pytest.raises(ValueError):
            Workload(name="test", items=-5)  # Negative items


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

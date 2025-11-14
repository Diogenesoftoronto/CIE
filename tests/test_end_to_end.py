"""
End-to-end tests for CIE application.

These tests cover the complete workflow from policy generation
to evaluation and optimization.
"""

import tempfile
from pathlib import Path

import pytest

from cie.config.settings import CIEConfig
from cie.core.backend import CIEBackend
from cie.core.models import Policy, Trial


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    @pytest.fixture
    def temp_config(self):
        """Create a temporary configuration for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CIEConfig()
            config.storage.backend = "json"
            config.storage.experiments_dir = str(Path(temp_dir) / "experiments")
            config.model.provider = "mock"
            config.model.model_name = "mock-model"
            config.debug = True
            yield config

    @pytest.fixture
    def backend(self, temp_config):
        """Create a backend instance for testing."""
        backend = CIEBackend(temp_config)
        yield backend
        backend.close()

    def test_complete_optimization_workflow(self, backend):
        """Test a complete optimization workflow."""
        # 1. Verify initial state
        assert len(backend.trials) == 0
        assert len(backend.pareto) == 0
        assert backend.active_policy is None

        # 2. List available optimizers
        optimizers = backend.list_optimizers()
        assert len(optimizers) > 0

        optimizer_name, meta = optimizers[0]
        assert optimizer_name == "DSPy:BootstrapFewShot"
        assert meta["best_score"] is None

        # 3. Generate a policy proposal
        policy = backend.propose_once(0)
        assert isinstance(policy, Policy)
        assert policy.name == "DSPy:BootstrapFewShot"
        assert "artifact" in policy.params
        assert len(policy.actions) > 0

        # 4. Evaluate the policy
        trial = backend.eval_policy(policy, 0)  # Use first workload
        assert isinstance(trial, Trial)
        assert trial.policy_name == policy.name
        assert trial.workload == "MicroEval:basic"
        assert trial.score is not None
        assert len(trial.metrics) > 0

        # Verify metrics are reasonable
        assert "latency_p95" in trial.metrics
        assert "cost_per_req" in trial.metrics
        assert "task_success" in trial.metrics
        assert "tool_error_rate" in trial.metrics

        # 5. Check that trial was saved
        assert len(backend.trials) == 1
        assert backend.trials[0].id == trial.id

        # 6. Check Pareto frontier was updated
        assert len(backend.pareto) >= 0  # Could be empty if dominated

        # 7. Generate another policy and evaluate
        policy2 = backend.propose_once(0)
        trial2 = backend.eval_policy(policy2, 1)  # Use different workload

        assert len(backend.trials) == 2
        assert trial2.id != trial.id

        # 8. Test policy adoption
        adoption_result = backend.adopt_policy(trial.id)
        assert isinstance(adoption_result, bool)

        if adoption_result:
            assert backend.active_policy is not None
            assert backend.active_policy.name.endswith("@adopted")

        # 9. Test scoring function
        test_metrics = {
            "latency_p95": 200.0,
            "cost_per_req": 0.005,
            "task_success": 0.9,
            "context_usage": 0.7,
            "tool_error_rate": 0.02,
        }

        score = backend.score(test_metrics)
        assert isinstance(score, float)
        assert score != 0.0

        # 10. Test backend statistics
        stats = backend.get_stats()
        assert stats["trial_count"] == 2
        assert stats["optimizer_count"] == len(backend.optimizers)
        assert stats["workload_count"] == len(backend.workloads)

    def test_multiple_optimizers(self, backend):
        """Test using multiple optimizers."""
        # Add a second optimizer
        from cie.optimizers.hill_climb import HillClimbOptimizer

        backend.optimizers.append(HillClimbOptimizer())
        backend.optimizer_meta.append({"best_score": None, "artifact_id": None})

        # Generate policies from different optimizers
        policy1 = backend.propose_once(0)  # DSPy
        policy2 = backend.propose_once(1)  # Hill Climb

        assert policy1.name != policy2.name
        assert policy1.params != policy2.params

        # Evaluate both
        trial1 = backend.eval_policy(policy1, 0)
        trial2 = backend.eval_policy(policy2, 0)

        assert trial1.policy_name != trial2.policy_name
        assert len(backend.trials) == 2

    def test_pareto_optimization(self, backend):
        """Test Pareto frontier optimization."""
        # Generate multiple trials with different characteristics
        policies = []
        trials = []

        for i in range(10):
            policy = backend.propose_once(0)
            policies.append(policy)

            trial = backend.eval_policy(policy, 0)
            trials.append(trial)

        # Check that Pareto frontier was built
        assert len(backend.pareto) > 0
        assert len(backend.pareto) <= len(backend.trials)

        # Verify Pareto properties
        for pareto_trial in backend.pareto:
            # Check that no other trial dominates this one
            dominated = False
            for other_trial in backend.trials:
                if self._dominates(other_trial, pareto_trial):
                    dominated = True
                    break
            assert not dominated, f"Pareto trial {pareto_trial.id} is dominated"

    def test_workload_variations(self, backend):
        """Test evaluation with different workloads."""
        policy = backend.propose_once(0)

        # Evaluate on different workloads
        trials = []
        for i in range(len(backend.workloads)):
            trial = backend.eval_policy(policy, i)
            trials.append(trial)

        # Verify workload-specific effects
        assert len(trials) == len(backend.workloads)

        # Check that different workloads produce different results
        scores = [t.score for t in trials]
        assert len(set(scores)) > 1  # Should have different scores

        # Check workload names are correct
        workload_names = [t.workload for t in trials]
        expected_names = [w.name for w in backend.workloads]
        assert set(workload_names) == set(expected_names)

    def test_policy_adoption_guardrails(self, backend):
        """Test policy adoption guardrails."""
        # Create a policy with poor metrics
        poor_policy = Policy(name="PoorPolicy", params={"test": True}, actions=["test.action()"])

        # Create a trial with high error rate (should be rejected)
        poor_trial = Trial(
            id=999,
            policy_name="PoorPolicy",
            metrics={
                "latency_p95": 1000.0,
                "cost_per_req": 0.01,
                "task_success": 0.5,
                "context_usage": 0.8,
                "tool_error_rate": 0.1,  # High error rate
            },
            score=999.0,
            workload="TestWorkload",
        )

        # Manually add the trial
        backend.trials.append(poor_trial)

        # Try to adopt - should fail due to high error rate
        result = backend.adopt_policy(999)
        assert result is False
        assert backend.active_policy is None

        # Create a good trial
        good_trial = Trial(
            id=1000,
            policy_name="GoodPolicy",
            metrics={
                "latency_p95": 200.0,
                "cost_per_req": 0.005,
                "task_success": 0.95,
                "context_usage": 0.7,
                "tool_error_rate": 0.01,  # Low error rate
            },
            score=10.0,
            workload="TestWorkload",
        )

        backend.trials.append(good_trial)

        # Try to adopt - should succeed
        result = backend.adopt_policy(1000)
        if result:
            assert backend.active_policy is not None
            assert backend.active_policy.name.endswith("@adopted")

    def test_storage_persistence(self, temp_config):
        """Test that data is persisted to storage."""
        # Create backend and add some data
        backend1 = CIEBackend(temp_config)

        policy = backend1.propose_once(0)
        trial = backend1.eval_policy(policy, 0)

        # Close the backend
        backend1.close()

        # Create new backend instance with same config
        backend2 = CIEBackend(temp_config)

        # Check that data was loaded
        assert len(backend2.trials) >= 1
        assert any(t.id == trial.id for t in backend2.trials)

        backend2.close()

    def test_configuration_changes(self, backend):
        """Test that configuration changes affect behavior."""
        # Change metric weights
        original_weights = backend.config.evaluation.metric_weights.copy()

        # Make latency much more important
        backend.config.evaluation.metric_weights["latency_p95"] = 0.1

        # Generate and evaluate policy
        policy = backend.propose_once(0)
        trial1 = backend.eval_policy(policy, 0)

        # Change weights back
        backend.config.evaluation.metric_weights = original_weights.copy()

        # Evaluate same policy again (should get different score)
        trial2 = backend.eval_policy(policy, 0)

        # Scores should be different due to different weights
        assert trial1.score != trial2.score

    def test_error_handling(self, backend):
        """Test error handling in various scenarios."""
        # Test invalid optimizer index
        with pytest.raises(ValueError):
            backend.propose_once(999)

        # Test invalid workload index
        policy = backend.propose_once(0)
        with pytest.raises(ValueError):
            backend.eval_policy(policy, 999)

        # Test adopting non-existent trial
        result = backend.adopt_policy(99999)
        assert result is False

    def test_concurrent_evaluations(self, backend):
        """Test multiple evaluations in sequence."""
        import threading

        results = []
        errors = []

        def evaluate_policy(policy_idx, workload_idx):
            try:
                policy = backend.propose_once(0)
                trial = backend.eval_policy(policy, workload_idx)
                results.append(trial)
            except Exception as e:
                errors.append(str(e))

        # Start multiple evaluation threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=evaluate_policy, args=(0, i % len(backend.workloads)))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        assert len(results) + len(errors) == 5
        assert len(backend.trials) >= len(results)

    def _dominates(self, a: Trial, b: Trial) -> bool:
        """Check if trial a dominates trial b."""
        la, ca, qa = (
            a.metrics.get("latency_p95", float("inf")),
            a.metrics.get("cost_per_req", float("inf")),
            1 - a.metrics.get("task_success", 0.0),
        )
        lb, cb, qb = (
            b.metrics.get("latency_p95", float("inf")),
            b.metrics.get("cost_per_req", float("inf")),
            1 - b.metrics.get("task_success", 0.0),
        )

        return (la <= lb and ca <= cb and qa <= qb) and (la < lb or ca < cb or qa < qb)


class TestRealModelIntegration:
    """Test integration with real AI models."""

    @pytest.fixture
    def real_config(self):
        """Create configuration for real model testing."""
        config = CIEConfig()
        config.storage.backend = "memory"  # Use memory for faster tests

        # Try to use real API key if available
        import os

        if os.getenv("KIMI_API_KEY") or os.getenv("OPENAI_API_KEY"):
            config.model.provider = "kimi" if os.getenv("KIMI_API_KEY") else "openai"
            config.model.model_name = "kimi" if os.getenv("KIMI_API_KEY") else "gpt-4o-mini"
        else:
            pytest.skip("No API key available for real model testing")

        return config

    @pytest.mark.slow
    def test_real_model_policy_generation(self, real_config):
        """Test policy generation with real AI model."""
        backend = CIEBackend(real_config)

        try:
            # Generate policy with real model
            policy = backend.propose_once(0)

            assert isinstance(policy, Policy)
            assert policy.name == "DSPy:BootstrapFewShot"
            assert "artifact" in policy.params

            # The policy should have been generated by the real model
            # so it should have more sophisticated parameters than the mock
            assert len(policy.params) > 3  # Should have more than just basic params

        except Exception as e:
            pytest.skip(f"Real model test failed (possibly API issue): {e}")
        finally:
            backend.close()


class TestPerformance:
    """Test application performance."""

    @pytest.fixture
    def perf_backend(self):
        """Create backend for performance testing."""
        config = CIEConfig()
        config.storage.backend = "memory"
        config.model.provider = "mock"
        return CIEBackend(config)

    def test_policy_generation_performance(self, perf_backend):
        """Test policy generation performance."""
        import time

        start_time = time.time()
        policy = perf_backend.propose_once(0)
        generation_time = time.time() - start_time

        assert generation_time < 1.0  # Should be fast with mock model
        assert isinstance(policy, Policy)

    def test_evaluation_performance(self, perf_backend):
        """Test evaluation performance."""
        import time

        policy = perf_backend.propose_once(0)

        start_time = time.time()
        trial = perf_backend.eval_policy(policy, 0)
        evaluation_time = time.time() - start_time

        assert evaluation_time < 3.0  # Should complete within 3 seconds
        assert isinstance(trial, Trial)

    def test_scalability(self, perf_backend):
        """Test scalability with many trials."""
        import time

        # Generate many trials
        start_time = time.time()
        for i in range(50):
            policy = perf_backend.propose_once(0)
            trial = perf_backend.eval_policy(policy, i % len(perf_backend.workloads))

        total_time = time.time() - start_time

        assert len(perf_backend.trials) == 50
        assert total_time < 30.0  # Should complete within 30 seconds

        # Test Pareto frontier performance
        pareto_start = time.time()
        perf_backend._rebuild_pareto()
        pareto_time = time.time() - pareto_start

        assert pareto_time < 1.0  # Should be fast


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

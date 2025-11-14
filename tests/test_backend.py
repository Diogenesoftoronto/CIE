"""Backend regression tests for the packaged CIE implementation."""

from cie.config.settings import CIEConfig, set_config
from cie.core.backend import CIEBackend


def make_backend() -> CIEBackend:
    """Construct a backend wired for tests."""
    config = CIEConfig()
    config.storage.backend = "memory"
    config.model.provider = "mock"
    config.model.model_name = "mock-model"
    config.evaluation.default_evaluator = "mock"
    set_config(config)
    return CIEBackend(config)


def test_backend_initialization():
    backend = make_backend()
    try:
        assert backend.optimizers, "Expected at least one optimizer"
        assert backend.workloads and len(backend.workloads) >= 3
        assert backend.evaluator is not None
        assert backend.evaluator_slug == backend.config.evaluation.default_evaluator
        assert backend.trials == []
        assert backend.pareto == []
    finally:
        backend.close()


def test_score_respects_metric_weights():
    backend = make_backend()
    try:
        backend.config.evaluation.metric_weights = {
            "latency_p95": 1.0,
            "task_success": -2.0,
        }
        fast_successful = {"latency_p95": 100.0, "task_success": 0.95}
        slow_failed = {"latency_p95": 500.0, "task_success": 0.20}
        assert backend.score(fast_successful) < backend.score(slow_failed)
    finally:
        backend.close()


def test_policy_proposal_and_evaluation_updates_state():
    backend = make_backend()
    try:
        policy = backend.propose_once(0)
        trial = backend.eval_policy(policy, 0)
        assert backend.trials[-1].id == trial.id
        assert backend.pareto  # at least one point after eval
        stats = backend.get_stats()
        assert stats["trial_count"] >= 1
        assert stats["optimizer_count"] == len(backend.optimizers)
    finally:
        backend.close()


def test_stats_report_active_evaluator():
    backend = make_backend()
    try:
        stats = backend.get_stats()
        assert stats.get("evaluator") == "mock"
    finally:
        backend.close()

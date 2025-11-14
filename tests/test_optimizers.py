"""Unit tests for the shipped optimizer implementations."""

from cie.config.settings import CIEConfig, set_config
from cie.optimizers.dspy_optimizer import DSPyOptimizer
from cie.optimizers.hill_climb import HillClimbOptimizer


def configure_mock_environment() -> None:
    """Ensure optimizers see the mock model provider via global config."""
    config = CIEConfig()
    config.model.provider = "mock"
    config.model.model_name = "mock-model"
    set_config(config)


def test_dspy_optimizer_propose_and_observe():
    configure_mock_environment()
    optimizer = DSPyOptimizer(k_shots=2, model="mock-model")

    policy = optimizer.propose(state={"trials": []})
    assert policy.name == "DSPy:BootstrapFewShot"
    assert policy.params["k_shots"] == 2
    assert "artifact" in policy.params
    assert policy.metadata["engine"] in {"dspy", "prompt"}

    metrics = {"latency_p95": 150.0, "cost_per_req": 0.001, "task_success": 0.92}
    optimizer.observe(policy, metrics)
    state = optimizer.get_state()
    assert state["trial_count"] == 1
    assert state["best_score"] is not None


def test_hill_climb_optimizer_parameter_ranges():
    optimizer = HillClimbOptimizer(step_size=0.2)
    policy = optimizer.propose(state={})
    assert policy.name == "HillClimb"
    assert 0.0 <= policy.params["prune_ratio"] <= 0.8
    assert 1 <= policy.params["batch_size"] <= 32
    assert isinstance(policy.actions, list) and policy.actions


def test_hill_climb_optimizer_observe_updates_state():
    optimizer = HillClimbOptimizer(step_size=0.1, max_stagnation=4)
    policy = optimizer.propose(state={})
    metrics = {"latency_p95": 200.0, "cost_per_req": 0.001, "task_success": 0.85}
    optimizer.observe(policy, metrics)

    state = optimizer.get_state()
    assert state["trial_count"] == 1
    assert state["best_score"] is not None

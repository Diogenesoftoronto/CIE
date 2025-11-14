"""Shared pytest fixtures for the modern CIE package."""

import pytest

from cie.config.settings import CIEConfig, set_config
from cie.core.backend import CIEBackend
from cie.core.models import Policy


@pytest.fixture
def backend_config() -> CIEConfig:
    """Provide a base configuration suitable for tests."""
    config = CIEConfig()
    config.storage.backend = "memory"
    config.model.provider = "mock"
    config.model.model_name = "mock-model"
    config.evaluation.default_evaluator = "mock"
    return config


@pytest.fixture
def backend(backend_config: CIEConfig):
    """Yield an in-memory backend with the mock model provider."""
    set_config(backend_config)
    engine = CIEBackend(backend_config)
    try:
        yield engine
    finally:
        engine.close()


@pytest.fixture
def sample_policy() -> Policy:
    """Provide a sample Policy for testing."""
    return Policy(
        name="TestPolicy", params={"param1": "value1", "param2": 42}, actions=["action1", "action2"]
    )


@pytest.fixture
def sample_metrics() -> dict[str, float]:
    """Provide sample metrics for testing."""
    return {
        "latency_p95": 200.0,
        "cost_per_req": 0.005,
        "task_success": 0.9,
        "context_usage": 0.7,
        "tool_error_rate": 0.02,
    }

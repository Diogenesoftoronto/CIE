"""
Pytest configuration for CIE tests.

This is a placeholder configuration file. Add actual fixtures and configuration as needed.
"""

import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the virtual environment to the path if it exists
venv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.venv')
if os.path.exists(venv_path):
    sys.path.insert(0, os.path.join(venv_path, 'lib', 'python3.13', 'site-packages'))


@pytest.fixture
def backend():
    """Provide a fresh CIEBackend instance for testing."""
    from main import CIEBackend
    return CIEBackend()


@pytest.fixture
def sample_policy():
    """Provide a sample Policy for testing."""
    from main import Policy
    return Policy(
        name="TestPolicy",
        params={"param1": "value1", "param2": 42},
        actions=["action1", "action2"]
    )


@pytest.fixture
def sample_metrics():
    """Provide sample metrics for testing."""
    return {
        "latency_p95": 200.0,
        "cost_per_req": 0.005,
        "task_success": 0.9,
        "context_usage": 0.7,
        "tool_error_rate": 0.02
    }


# Configure pytest to handle async tests if needed
def pytest_configure(config):
    """Configure pytest for the project."""
    # Add any project-specific pytest configuration here
    pass
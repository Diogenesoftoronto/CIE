"""
Core domain models for CIE optimization framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol


@dataclass
class Policy:
    """Configuration for optimization algorithms."""

    name: str
    params: dict[str, Any]
    actions: list[str]
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate policy after creation."""
        if not self.name:
            raise ValueError("Policy name cannot be empty")
        if not isinstance(self.params, dict):
            raise ValueError("Policy params must be a dictionary")
        if not isinstance(self.actions, list):
            raise ValueError("Policy actions must be a list")


@dataclass
class Trial:
    """Individual experiment results."""

    id: int
    policy_name: str
    metrics: dict[str, float]
    score: float
    workload: str
    created_at: datetime = field(default_factory=datetime.now)
    artifact_id: str | None = None
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate trial after creation."""
        if not self.policy_name:
            raise ValueError("Policy name cannot be empty")
        if not isinstance(self.metrics, dict):
            raise ValueError("Trial metrics must be a dictionary")
        if not all(isinstance(v, (int, float)) for v in self.metrics.values()):
            raise ValueError("All metrics values must be numeric")


@dataclass
class Workload:
    """Evaluation workload configuration."""

    name: str
    items: int
    description: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate workload after creation."""
        if not self.name:
            raise ValueError("Workload name cannot be empty")
        if self.items <= 0:
            raise ValueError("Workload items must be positive")


class Optimizer(Protocol):
    """Interface for optimization algorithms."""

    name: str

    def propose(self, state: dict[str, Any]) -> Policy:
        """Propose a new policy based on current state."""
        ...

    def observe(self, policy: Policy, metrics: dict[str, float]) -> None:
        """Observe the results of a policy evaluation."""
        ...

    def get_state(self) -> dict[str, Any]:
        """Get current optimizer state."""
        ...

    def reset(self) -> None:
        """Reset optimizer to initial state."""
        ...


class Evaluator(Protocol):
    """Interface for evaluation systems."""

    name: str

    def run(self, policy: Policy, workload: Workload) -> dict[str, float]:
        """Run evaluation for a policy on a workload."""
        ...

    def get_supported_metrics(self) -> list[str]:
        """Get list of metrics this evaluator can provide."""
        ...

    def validate_workload(self, workload: Workload) -> bool:
        """Validate if workload is compatible with this evaluator."""
        ...


class ModelProvider(Protocol):
    """Interface for AI model providers."""

    name: str
    model_name: str

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using the model."""
        ...

    def embed(self, text: str, **kwargs: Any) -> list[float]:
        """Generate embeddings for text."""
        ...

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the model."""
        ...


@dataclass
class Prompt:
    """Prompt configuration and template."""

    id: str
    content: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate prompt after creation."""
        if not self.id:
            raise ValueError("Prompt ID cannot be empty")
        if not self.content:
            raise ValueError("Prompt content cannot be empty")

"""
Context-aware optimization for agent behavior.
"""

from typing import Any

from cie.core.context import ContextAwareEvaluator, ContextIntrospector
from cie.core.models import Policy
from cie.tools.context_tools import AgentContextTools


class ContextAwareOptimizer:
    """Optimizer that uses context introspection to improve agent performance."""

    def __init__(self) -> None:
        self.name = "Context-Aware Optimizer"
        self.evaluator = ContextAwareEvaluator()
        self.introspector = ContextIntrospector()
        self.tools = AgentContextTools()
        self.optimization_history: list[dict[str, Any]] = []

    def propose(self, state: dict[str, Any]) -> Policy:
        """Propose a new policy based on context analysis."""
        # Capture current context
        import sys

        frame = sys._getframe(1)
        context_tree = self.introspector.capture_context(
            frame.f_locals, frame.f_globals, max_depth=3
        )

        # Analyze context efficiency
        efficiency = self.evaluator.evaluate_context_efficiency(
            {"locals": frame.f_locals, "globals": frame.f_globals}
        )

        # Get improvement suggestions
        improvements = self.evaluator.suggest_improvements()

        # Generate policy based on analysis
        policy_params = {
            "context_efficiency": efficiency,
            "improvements": improvements,
            "hotspots": self.introspector.get_hotspots(5),
            "compression_enabled": efficiency < 0.7,
            "cache_hotspots": len(self.introspector.get_hotspots()) > 10,
            "flatten_deep_structures": any("Flatten" in imp for imp in improvements),
        }

        policy = Policy(
            name=f"context_aware_{len(self.optimization_history)}",
            params=policy_params,
            actions=[
                "analyze_context",
                "cache_hotspots",
                "compress" if efficiency < 0.7 else "noop",
            ],
            metadata={
                "optimizer": self.name,
                "context_score": efficiency,
                "suggested_improvements": improvements,
            },
        )

        return policy

    def observe(self, policy: Policy, metrics: dict[str, float]) -> None:
        """Observe results and update strategy."""
        self.optimization_history.append(
            {
                "policy": policy.name,
                "metrics": metrics,
                "context_efficiency": policy.params.get("context_efficiency", 0),
                "improvements_applied": policy.params.get("improvements", []),
            }
        )

        # Learn from results
        if metrics.get("task_success", 0) > 0.8:
            # This context organization worked well
            self._save_successful_pattern(policy)

    def _save_successful_pattern(self, policy: Policy) -> None:
        """Save successful context organization patterns."""
        # This would save patterns that led to good performance
        pass

    def get_state(self) -> dict[str, Any]:
        """Get current optimizer state."""
        return {
            "name": self.name,
            "optimization_history": self.optimization_history,
            "history_length": len(self.optimization_history),
        }

    def reset(self) -> None:
        """Reset optimizer to initial state."""
        self.optimization_history = []


class ContextCompressionOptimizer:
    """Optimizer focused on reducing context size."""

    def __init__(self) -> None:
        self.name = "Context Compression Optimizer"
        self.evaluator = ContextAwareEvaluator()
        self.compression_history: list[dict[str, Any]] = []

    def propose(self, state: dict[str, Any]) -> Policy:
        """Propose compression-focused policies."""
        # Get current context size
        context_size = state.get("context_size", 1000)

        # Determine compression strategy
        if context_size > 50000:
            strategy = "aggressive"
            target_size = context_size * 0.3
        elif context_size > 10000:
            strategy = "moderate"
            target_size = context_size * 0.6
        else:
            strategy = "light"
            target_size = context_size * 0.8

        policy_params = {
            "compression_strategy": strategy,
            "target_size": target_size,
            "preserve_structure": True,
            "use_sampling": context_size > 20000,
            "cache_before_compression": True,
        }

        policy = Policy(
            name=f"compression_{strategy}_{len(self.compression_history)}",
            params=policy_params,
            actions=["compress", "cache", "validate"],
            metadata={
                "optimizer": self.name,
                "input_size": context_size,
                "target_size": target_size,
            },
        )

        return policy

    def observe(self, policy: Policy, metrics: dict[str, float]) -> None:
        """Observe compression results."""
        self.compression_history.append(
            {
                "policy": policy.name,
                "metrics": metrics,
                "compression_ratio": metrics.get("compression_ratio", 1.0),
            }
        )

    def get_state(self) -> dict[str, Any]:
        """Get current optimizer state."""
        return {
            "name": self.name,
            "compression_history": self.compression_history,
            "history_length": len(self.compression_history),
        }

    def reset(self) -> None:
        """Reset optimizer to initial state."""
        self.compression_history = []


class ContextNavigationOptimizer:
    """Optimizer for improving context access patterns."""

    def __init__(self) -> None:
        self.name = "Context Navigation Optimizer"
        self.evaluator = ContextAwareEvaluator()
        self.navigation_history: list[dict[str, Any]] = []

    def propose(self, state: dict[str, Any]) -> Policy:
        """Propose navigation-optimized policies."""
        # Analyze access patterns
        access_pattern = state.get("access_pattern", "sequential")
        hotspot_count = state.get("hotspot_count", 5)

        # Determine optimization strategy
        if hotspot_count > 20:
            caching_strategy = "aggressive"
        elif hotspot_count > 5:
            caching_strategy = "moderate"
        else:
            caching_strategy = "minimal"

        policy_params = {
            "caching_strategy": caching_strategy,
            "prefetch_enabled": hotspot_count > 10,
            "reorganize_by_access": True,
            "maintain_indices": True,
            "tracking_depth": min(5, max(2, hotspot_count // 5)),
        }

        policy = Policy(
            name=f"navigation_{caching_strategy}_{len(self.navigation_history)}",
            params=policy_params,
            actions=["analyze_access", "reorganize", "prefetch" if hotspot_count > 10 else "noop"],
            metadata={
                "optimizer": self.name,
                "caching_strategy": caching_strategy,
                "hotspot_count": hotspot_count,
            },
        )

        return policy

    def observe(self, policy: Policy, metrics: dict[str, float]) -> None:
        """Observe navigation optimization results."""
        self.navigation_history.append(
            {
                "policy": policy.name,
                "metrics": metrics,
                "access_efficiency": metrics.get("access_efficiency", 0),
            }
        )

    def get_state(self) -> dict[str, Any]:
        """Get current optimizer state."""
        return {
            "name": self.name,
            "navigation_history": self.navigation_history,
            "history_length": len(self.navigation_history),
        }

    def reset(self) -> None:
        """Reset optimizer to initial state."""
        self.navigation_history = []

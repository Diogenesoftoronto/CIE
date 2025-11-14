"""
Hill climbing optimization algorithm for CIE.
"""

import random
import time
from datetime import datetime
from typing import Any

from cie.config.settings import get_config
from cie.core.models import Optimizer, Policy


class HillClimbOptimizer(Optimizer):
    """
    Hill climbing optimizer that iteratively improves policy parameters.
    This optimizer starts with an initial set of parameters and makes
    small incremental changes, keeping changes that improve performance.
    """

    name = "HillClimb"

    def __init__(
        self,
        step_size: float = 0.1,
        max_stagnation: int = 10,
        parameter_ranges: dict[str, tuple[float, float]] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize hill climb optimizer.
        Args:
            step_size: Size of parameter changes (relative to range)
            max_stagnation: Maximum iterations without improvement
            parameter_ranges: Dict mapping parameter names to (min, max) tuples
            **kwargs: Additional arguments
        """
        self.step_size = step_size
        self.max_stagnation = max_stagnation
        self.parameter_ranges = parameter_ranges or self._get_default_ranges()
        self.kwargs = kwargs
        # State tracking
        self.current_params: dict[str, Any] | None = None
        self.current_score: float | None = None
        self.best_params: dict[str, Any] | None = None
        self.best_score: float | None = None
        self.stagnation_count: int = 0
        self.iteration_count: int = 0
        self.trial_history: list[dict[str, Any]] = []
        # Initialize with random parameters
        self._initialize_parameters()

    def _get_default_ranges(self) -> dict[str, tuple[float, float]]:
        """Get default parameter ranges."""
        return {
            "prune_ratio": (0.0, 0.8),
            "batch_size": (1, 32),
            "temperature": (0.1, 1.0),
            "max_tokens": (100, 2000),
            "learning_rate": (0.001, 0.1),
            "dropout_rate": (0.0, 0.5),
            "context_window": (1024, 16384),
        }

    def _initialize_parameters(self) -> None:
        """Initialize parameters with random values."""
        self.current_params = {}
        for param_name, (min_val, max_val) in self.parameter_ranges.items():
            if isinstance(min_val, int) and isinstance(max_val, int):
                # Integer parameter
                self.current_params[param_name] = random.randint(min_val, max_val)
            else:
                # Float parameter
                self.current_params[param_name] = random.uniform(min_val, max_val)
        self.best_params = self.current_params.copy()

    def propose(self, state: dict[str, Any]) -> Policy:
        """
        Propose a new policy by making small changes to current parameters.
        Args:
            state: Current optimization state
        Returns:
            New policy proposal
        """
        # Generate new parameters by perturbing current ones
        new_params = self._perturb_parameters()
        # Create artifact ID
        artifact_id = f"hillclimb-{int(time.time() * 1000)}-{self.iteration_count}"
        # Add metadata
        new_params["artifact"] = artifact_id
        new_params["iteration"] = self.iteration_count
        new_params["step_size"] = self.step_size
        new_params["stagnation_count"] = self.stagnation_count
        # Generate actions based on parameters
        actions = self._generate_actions(new_params)
        policy = Policy(
            name=self.name,
            params=new_params,
            actions=actions,
            metadata={
                "iteration": self.iteration_count,
                "stagnation_count": self.stagnation_count,
                "created_at": datetime.now().isoformat(),
                "parameter_ranges": self.parameter_ranges,
            },
        )
        return policy

    def observe(self, policy: Policy, metrics: dict[str, float]) -> None:
        """
        Observe the results of a policy evaluation.
        Args:
            policy: The policy that was evaluated
            metrics: Evaluation metrics
        """
        # Calculate score based on metrics
        score = self._calculate_score(metrics)
        # Store trial history
        trial_record = {
            "policy": policy,
            "metrics": metrics,
            "score": score,
            "iteration": self.iteration_count,
            "timestamp": datetime.now().isoformat(),
        }
        self.trial_history.append(trial_record)
        # Update current state
        self.current_params = policy.params.copy()
        self.current_score = score
        # Check if this is the best so far
        if self.best_score is None or score < self.best_score:
            self.best_score = score
            self.best_params = self.current_params.copy()
            self.stagnation_count = 0
        else:
            self.stagnation_count += 1
            # If we've stagnated too long, increase step size
            if self.stagnation_count > self.max_stagnation // 2:
                self.step_size = min(self.step_size * 1.5, 0.5)
        self.iteration_count += 1
        # Reset parameters if we've stagnated too long
        if self.stagnation_count >= self.max_stagnation:
            self._restart_from_best()

    def get_state(self) -> dict[str, Any]:
        """Get current optimizer state."""
        return {
            "name": self.name,
            "step_size": self.step_size,
            "max_stagnation": self.max_stagnation,
            "iteration_count": self.iteration_count,
            "stagnation_count": self.stagnation_count,
            "current_score": self.current_score,
            "best_score": self.best_score,
            "trial_count": len(self.trial_history),
            "parameter_count": len(self.parameter_ranges),
        }

    def reset(self) -> None:
        """Reset optimizer to initial state."""
        self.current_params = None
        self.current_score = None
        self.best_params = None
        self.best_score = None
        self.stagnation_count = 0
        self.iteration_count = 0
        self.trial_history.clear()
        self._initialize_parameters()

    def _perturb_parameters(self) -> dict[str, Any]:
        """Perturb current parameters to generate new ones."""
        if self.current_params is None:
            self._initialize_parameters()
            if self.current_params is None:  # Still None after initialization
                raise ValueError("Failed to initialize parameters")
        new_params = self.current_params.copy()
        # Select a subset of parameters to perturb
        param_names = list(self.parameter_ranges.keys())
        num_to_perturb = max(1, random.randint(1, len(param_names) // 2 + 1))
        params_to_perturb = random.sample(param_names, num_to_perturb)
        for param_name in params_to_perturb:
            min_val, max_val = self.parameter_ranges[param_name]
            current_val = new_params.get(param_name, (min_val + max_val) / 2)
            # Calculate perturbation amount
            range_size = max_val - min_val
            perturbation = self.step_size * range_size * random.gauss(0, 0.5)
            # Apply perturbation
            new_val = current_val + perturbation
            # Ensure within bounds
            if isinstance(min_val, int) and isinstance(max_val, int):
                new_val = int(max(min_val, min(max_val, new_val)))
            else:
                new_val = max(min_val, min(max_val, new_val))
            new_params[param_name] = new_val
        return new_params

    def _generate_actions(self, params: dict[str, Any], **kwargs: Any) -> list[str]:
        """Generate actions based on policy parameters."""
        actions = []
        if "prune_ratio" in params:
            actions.append(f"context.prune(ratio={params['prune_ratio']:.2f})")
        if "batch_size" in params:
            actions.append(f"batch.set_size({params['batch_size']})")
        if "temperature" in params:
            actions.append(f"model.set_temperature({params['temperature']:.2f})")
        if "max_tokens" in params:
            actions.append(f"model.set_max_tokens({params['max_tokens']})")
        if "learning_rate" in params:
            actions.append(f"optimizer.set_lr({params['learning_rate']:.4f})")
        if "dropout_rate" in params:
            actions.append(f"model.set_dropout({params['dropout_rate']:.2f})")
        if "context_window" in params:
            actions.append(f"context.set_window({params['context_window']})")
        # Add default actions if none generated
        if not actions:
            actions = [
                f"hillclimb.apply(iteration={params.get('iteration', 0)})",
                "parameters.optimize()",
                "metrics.track()",
            ]
        return actions

    def _calculate_score(self, metrics: dict[str, float], **kwargs: Any) -> float:
        """Calculate a composite score from metrics."""
        config = get_config()
        weights = config.evaluation.metric_weights
        score = 0.0
        for metric, weight in weights.items():
            value = metrics.get(metric, 0.0)
            score += weight * value
        return -score  # Negative because lower is better in our scoring system

    def _restart_from_best(self) -> None:
        """Restart from the best known parameters."""
        if self.best_params is not None:
            self.current_params = self.best_params.copy()
            self.current_score = self.best_score
        else:
            self._initialize_parameters()
        # Reset stagnation and increase exploration
        self.stagnation_count = 0
        self.step_size = min(self.step_size * 2.0, 0.5)
        # Add some randomness to restart
        if self.current_params is not None:
            for param_name in self.current_params:
                if random.random() < 0.3:  # 30% chance to randomize each parameter
                    min_val, max_val = self.parameter_ranges[param_name]
                    if isinstance(min_val, int) and isinstance(max_val, int):
                        self.current_params[param_name] = random.randint(min_val, max_val)
                    else:
                        self.current_params[param_name] = random.uniform(min_val, max_val)


class AdaptiveHillClimbOptimizer(HillClimbOptimizer):
    """
    Adaptive hill climbing optimizer that adjusts step size based on progress.
    """

    name = "AdaptiveHillClimb"

    def __init__(
        self,
        step_size: float = 0.1,
        max_stagnation: int = 10,
        adaptation_rate: float = 0.9,
        **kwargs,
    ):
        """
        Initialize adaptive hill climb optimizer.
        Args:
            step_size: Initial step size
            max_stagnation: Maximum iterations without improvement
            adaptation_rate: Rate at which to adapt step size
            **kwargs: Additional arguments
        """
        super().__init__(step_size, max_stagnation, **kwargs)
        self.adaptation_rate = adaptation_rate
        self.improvement_history: list[bool] = []

    def observe(self, policy: Policy, metrics: dict[str, float]) -> None:
        """
        Observe results and adapt step size.
        Args:
            policy: The policy that was evaluated
            metrics: Evaluation metrics
        """
        old_score = self.current_score
        super().observe(policy, metrics)
        new_score = self.current_score
        # Track improvement
        improved = old_score is None or (new_score is not None and new_score < old_score)
        self.improvement_history.append(improved)
        # Keep only recent history
        if len(self.improvement_history) > 20:
            self.improvement_history.pop(0)
        # Adapt step size based on improvement rate
        if len(self.improvement_history) >= 5:
            improvement_rate = sum(self.improvement_history[-5:]) / 5
            if improvement_rate > 0.6:
                # Good improvement rate, decrease step size for fine-tuning
                self.step_size *= self.adaptation_rate
            elif improvement_rate < 0.2:
                # Poor improvement rate, increase step size for exploration
                self.step_size = min(self.step_size / self.adaptation_rate, 0.5)

    def get_state(self) -> dict[str, Any]:
        """Get current optimizer state."""
        state = super().get_state()
        state.update(
            {
                "adaptation_rate": self.adaptation_rate,
                "recent_improvement_rate": (
                    sum(self.improvement_history[-5:]) / min(5, len(self.improvement_history))
                    if self.improvement_history
                    else 0.0
                ),
            }
        )
        return state

"""Mock evaluator for testing and development."""

from __future__ import annotations

import time
from random import Random

from cie.config.settings import CIEConfig
from cie.core.models import Evaluator, Policy, Workload


class MockEvaluator(Evaluator):
    """
    Mock evaluator that generates realistic metrics for testing.
    This evaluator simulates different evaluation scenarios based on
    policy parameters and workload characteristics.
    """

    name = "MockEvaluator"

    def __init__(self, seed: int = 42, config: CIEConfig | None = None, **_: object):
        """Initialize mock evaluator.

        Args:
            seed: Random seed for reproducible results.
            config: Optional configuration passed by the backend.
        """
        self.config = config
        self.random = Random(seed)
        self.call_count = 0

    def run(self, policy: Policy, workload: Workload) -> dict[str, float]:
        """
        Run mock evaluation and generate metrics.
        Args:
            policy: Policy to evaluate
            workload: Workload to run evaluation on
        Returns:
            Dictionary of evaluation metrics
        """
        self.call_count += 1
        # Simulate processing time but keep unit tests fast.
        processing_time = self._calculate_processing_time(policy, workload)
        time.sleep(min(processing_time, 0.05))
        # Generate base metrics
        base_metrics = self._generate_base_metrics(workload)
        # Apply policy effects
        adjusted_metrics = self._apply_policy_effects(base_metrics, policy)
        # Add some randomness
        final_metrics = self._add_randomness(adjusted_metrics)
        # Ensure metrics are within reasonable bounds
        final_metrics = self._apply_bounds(final_metrics)
        return final_metrics

    def get_supported_metrics(self) -> list[str]:
        """Get list of metrics this evaluator can provide."""
        return [
            "latency_p95",
            "cost_per_req",
            "task_success",
            "context_usage",
            "tool_error_rate",
            "throughput",
            "memory_usage",
            "cpu_usage",
        ]

    def validate_workload(self, workload: Workload) -> bool:
        """Validate if workload is compatible with this evaluator."""
        # Mock evaluator accepts all workloads
        return True

    def _calculate_processing_time(self, policy: Policy, workload: Workload) -> float:
        """Calculate simulated processing time."""
        base_time = 0.1
        # Add time based on workload size
        base_time += workload.items * 0.01
        # Add time based on policy complexity
        if "k_shots" in policy.params:
            base_time += policy.params["k_shots"] * 0.02
        if "max_tokens" in policy.params:
            base_time += policy.params["max_tokens"] * 0.0001
        # Add some randomness
        base_time *= self.random.uniform(0.8, 1.2)
        return min(base_time, 2.0)  # Cap at 2 seconds

    def _generate_base_metrics(self, workload: Workload) -> dict[str, float]:
        """Generate base metrics based on workload."""
        # Base values vary by workload type
        if "micro" in workload.name.lower():
            base_latency = self.random.uniform(50, 200)
            base_cost = self.random.uniform(0.0001, 0.001)
            base_success = self.random.uniform(0.85, 0.98)
            base_throughput = self.random.uniform(100, 500)
        elif "macro" in workload.name.lower():
            base_latency = self.random.uniform(200, 1000)
            base_cost = self.random.uniform(0.001, 0.01)
            base_success = self.random.uniform(0.75, 0.95)
            base_throughput = self.random.uniform(10, 100)
        elif "synthetic" in workload.name.lower():
            base_latency = self.random.uniform(100, 500)
            base_cost = self.random.uniform(0.0005, 0.005)
            base_success = self.random.uniform(0.8, 0.99)
            base_throughput = self.random.uniform(50, 200)
        else:
            # Default values
            base_latency = self.random.uniform(100, 700)
            base_cost = self.random.uniform(0.001, 0.01)
            base_success = self.random.uniform(0.7, 0.98)
            base_throughput = self.random.uniform(20, 150)
        return {
            "latency_p95": base_latency,
            "cost_per_req": base_cost,
            "task_success": base_success,
            "throughput": base_throughput,
            "context_usage": self.random.uniform(0.45, 0.92),
            "tool_error_rate": self.random.uniform(0.0, 0.05),
            "memory_usage": self.random.uniform(0.3, 0.8),
            "cpu_usage": self.random.uniform(0.2, 0.9),
        }

    def _apply_policy_effects(self, metrics: dict[str, float], policy: Policy) -> dict[str, float]:
        """Apply policy-specific effects to metrics."""
        adjusted = metrics.copy()
        # DSPy policy effects
        if "k_shots" in policy.params:
            k_shots = policy.params["k_shots"]
            # More shots generally improve success but increase cost and latency
            success_boost = min(0.02 * (k_shots / 4), 0.06)
            cost_increase = 0.0003 * (k_shots / 4)
            latency_increase = 1.05 ** (k_shots / 4)  # Exponential increase
            adjusted["task_success"] += success_boost
            adjusted["cost_per_req"] += cost_increase
            adjusted["latency_p95"] *= latency_increase
        if "temperature" in policy.params:
            temp = policy.params["temperature"]
            # Lower temperature generally improves consistency but may reduce creativity
            if temp < 0.5:
                adjusted["task_success"] += 0.02
                adjusted["tool_error_rate"] -= 0.005
            else:
                adjusted["task_success"] -= 0.01
                adjusted["tool_error_rate"] += 0.005
        if "max_tokens" in policy.params:
            max_tokens = policy.params["max_tokens"]
            # More tokens can improve quality but increase cost and latency
            token_factor = max_tokens / 1000
            adjusted["cost_per_req"] += 0.0001 * token_factor
            adjusted["latency_p95"] *= 1 + 0.01 * token_factor
            adjusted["task_success"] += min(0.01 * token_factor, 0.05)
        # Hill climbing policy effects
        if "prune_ratio" in policy.params:
            prune_ratio = policy.params["prune_ratio"]
            # Pruning reduces latency but may hurt success rate
            adjusted["latency_p95"] *= 1.0 - 0.1 * prune_ratio
            adjusted["task_success"] -= 0.05 * prune_ratio
            adjusted["context_usage"] *= 1.0 - 0.2 * prune_ratio
        if "batch_size" in policy.params:
            batch_size = policy.params["batch_size"]
            # Larger batches can improve throughput but increase latency
            throughput_boost = 1 + 0.1 * (batch_size / 8)
            latency_increase = 1 + 0.05 * (batch_size / 8)
            adjusted["throughput"] *= throughput_boost
            adjusted["latency_p95"] *= latency_increase
        # Bandit policy effects
        if "arm" in policy.params:
            arm = policy.params["arm"]
            # Different arms have different characteristics
            if arm == "A":
                # Arm A: Balanced approach
                pass
            elif arm == "B":
                # Arm B: More aggressive, higher risk/reward
                adjusted["task_success"] += self.random.uniform(-0.1, 0.15)
                adjusted["tool_error_rate"] += self.random.uniform(-0.01, 0.02)
                adjusted["latency_p95"] *= self.random.uniform(0.8, 1.2)
        return adjusted

    def _add_randomness(self, metrics: dict[str, float]) -> dict[str, float]:
        """Add realistic randomness to metrics."""
        noisy = metrics.copy()
        # Add Gaussian noise to each metric
        for key, value in noisy.items():
            if key == "task_success":
                # Success rate gets small noise
                noise = self.random.gauss(0, 0.02)
                noisy[key] = max(0.0, min(1.0, value + noise))
            elif key == "tool_error_rate":
                # Error rate gets small noise
                noise = self.random.gauss(0, 0.005)
                noisy[key] = max(0.0, min(1.0, value + noise))
            elif "latency" in key:
                # Latency gets multiplicative noise
                noise = self.random.gauss(1.0, 0.1)
                noisy[key] = max(1.0, value * noise)
            elif "cost" in key:
                # Cost gets multiplicative noise
                noise = self.random.gauss(1.0, 0.05)
                noisy[key] = max(0.0001, value * noise)
            elif "usage" in key or "rate" in key:
                # Usage and rates get additive noise
                noise = self.random.gauss(0, 0.02)
                noisy[key] = max(0.0, min(1.0, value + noise))
            else:
                # Other metrics get moderate noise
                noise = self.random.gauss(0, 0.05)
                noisy[key] = max(0.0, value + noise)
        return noisy

    def _apply_bounds(self, metrics: dict[str, float]) -> dict[str, float]:
        """Apply reasonable bounds to metrics."""
        bounded = metrics.copy()
        # Latency bounds (1ms to 10s)
        if "latency_p95" in bounded:
            bounded["latency_p95"] = max(1.0, min(10000.0, bounded["latency_p95"]))
        # Cost bounds ($0.00001 to $1.0 per request)
        if "cost_per_req" in bounded:
            bounded["cost_per_req"] = max(0.00001, min(1.0, bounded["cost_per_req"]))
        # Success rate bounds (0% to 100%)
        if "task_success" in bounded:
            bounded["task_success"] = max(0.0, min(1.0, bounded["task_success"]))
        # Usage bounds (0% to 100%)
        for key in ["context_usage", "memory_usage", "cpu_usage"]:
            if key in bounded:
                bounded[key] = max(0.0, min(1.0, bounded[key]))
        # Error rate bounds (0% to 100%)
        if "tool_error_rate" in bounded:
            bounded["tool_error_rate"] = max(0.0, min(1.0, bounded["tool_error_rate"]))
        # Throughput bounds (1 to 1000 req/s)
        if "throughput" in bounded:
            bounded["throughput"] = max(1.0, min(1000.0, bounded["throughput"]))
        # Round values for consistency
        bounded["latency_p95"] = round(bounded["latency_p95"], 2)
        bounded["cost_per_req"] = round(bounded["cost_per_req"], 5)
        bounded["task_success"] = round(bounded["task_success"], 3)
        bounded["context_usage"] = round(bounded["context_usage"], 2)
        bounded["tool_error_rate"] = round(bounded["tool_error_rate"], 3)
        bounded["throughput"] = round(bounded["throughput"], 1)
        bounded["memory_usage"] = round(bounded["memory_usage"], 2)
        bounded["cpu_usage"] = round(bounded["cpu_usage"], 2)
        return bounded

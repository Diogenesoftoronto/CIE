"""
Context-aware evaluator for agent performance.
"""

import time
from typing import Dict, List

from cie.core.models import Policy, Trial, Workload
from cie.tools.context_tools import AgentContextTools


class ContextEvaluator:
    """Evaluator that measures context manipulation efficiency."""

    def __init__(self):
        self.name = "context"
        self.tools = AgentContextTools()

    def run(self, policy: Policy, workload: Workload, **kwargs) -> Trial:
        """Run evaluation of context manipulation efficiency."""
        metrics = {}
        start_time = time.perf_counter()

        # Test context inspection
        inspection_start = time.perf_counter()
        inspection_result = self.tools.inspect_context("current", max_depth=3)
        inspection_time = time.perf_counter() - inspection_start

        metrics["inspection_time"] = inspection_time
        metrics["context_nodes"] = inspection_result["summary"]["total_nodes"]
        metrics["context_size"] = inspection_result["summary"]["total_size"]
        metrics["context_depth"] = inspection_result["summary"]["max_depth"]

        # Test compression if enabled
        if policy.params.get("compression_enabled"):
            compression_start = time.perf_counter()
            compression_result = self.tools.compress_context(
                strategy=policy.params.get("compression_strategy", "auto"),
                threshold=policy.params.get("compression_threshold", 1000),
            )
            compression_time = time.perf_counter() - compression_start

            metrics["compression_ratio"] = compression_result["compression_ratio"]
            metrics["context_loss"] = 1.0 - compression_result["compression_ratio"]
            metrics["compression_time"] = compression_time

        # Test reorganization if enabled
        if policy.params.get("reorganize_context"):
            reorg_start = time.perf_counter()
            reorg_result = self.tools.reorganize_context(
                method=policy.params.get("reorganization_method", "by_access")
            )
            reorg_time = time.perf_counter() - reorg_start

            metrics["reorganization_time"] = reorg_time
            metrics["reorganization_method"] = policy.params.get("reorganization_method")

        # Test caching if enabled
        if policy.params.get("cache_hotspots"):
            cache_start = time.perf_counter()
            hotspots = inspection_result["hotspots"]
            cached_count = 0
            for path, count in hotspots[:5]:
                if self.tools.cache_context(f"hotspot:{path}", None):
                    cached_count += 1
            cache_time = time.perf_counter() - cache_start

            metrics["cached_paths"] = cached_count
            metrics["cache_time"] = cache_time

        # Test navigation if enabled
        if policy.params.get("navigation_strategy"):
            nav_start = time.perf_counter()
            # Test various navigation commands
            nav_results = []
            nav_results.append(self.tools.navigate_context("pwd"))
            nav_results.append(self.tools.navigate_context("ls /"))
            nav_results.append(self.tools.navigate_context("find policy"))
            nav_time = time.perf_counter() - nav_start

            metrics["navigation_time"] = nav_time
            metrics["navigation_commands"] = len(nav_results)

        # Analyze context efficiency
        analysis_start = time.perf_counter()
        analysis = self.tools.analyze_context()
        analysis_time = time.perf_counter() - analysis_start

        metrics["context_efficiency"] = analysis["efficiency_score"]
        metrics["optimization_potential"] = analysis["optimization_potential"]
        metrics["analysis_time"] = analysis_time

        # Test query performance
        query_start = time.perf_counter()
        query_results = self.tools.query_context("test", return_values=False)
        query_time = time.perf_counter() - query_start

        metrics["query_time"] = query_time
        metrics["query_results"] = len(query_results)

        # Test checkpoint/restore if enabled
        if policy.params.get("checkpoint_enabled"):
            checkpoint_start = time.perf_counter()
            checkpoint_name = self.tools.checkpoint_context("test_checkpoint")
            checkpoint_time = time.perf_counter() - checkpoint_start

            metrics["checkpoint_time"] = checkpoint_time
            metrics["checkpoint_created"] = 1 if checkpoint_name else 0

        # Measure memory usage
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            metrics["memory_usage"] = memory_info.rss / 1024 / 1024  # MB
        except ImportError:
            metrics["memory_usage"] = 0

        # Calculate access pattern efficiency
        if self.tools.introspector.access_patterns:
            total_accesses = sum(self.tools.introspector.access_patterns.values())
            unique_paths = len(self.tools.introspector.access_patterns)
            metrics["access_pattern_efficiency"] = (
                unique_paths / total_accesses if total_accesses > 0 else 0
            )
            metrics["total_context_accesses"] = total_accesses
            metrics["unique_context_paths"] = unique_paths
        else:
            metrics["access_pattern_efficiency"] = 0
            metrics["total_context_accesses"] = 0
            metrics["unique_context_paths"] = 0

        # Test view creation if enabled
        if policy.params.get("create_views"):
            view_start = time.perf_counter()
            view_result = self.tools.create_context_view(
                "test_view", selector=lambda node: node.size < 1000
            )
            view_time = time.perf_counter() - view_start

            metrics["view_creation_time"] = view_time
            metrics["view_size"] = view_result["size"]

        # Calculate overall execution time
        total_time = time.perf_counter() - start_time
        metrics["total_execution_time"] = total_time

        # Calculate overall score
        score = self._calculate_score(metrics, policy)

        return Trial(
            id=len(kwargs.get("trials", [])) + 1,
            policy=policy,
            metrics=metrics,
            score=score,
            optimizer_name=kwargs.get("optimizer_name", "unknown"),
            workload_name=workload.name,
        )

    def _calculate_score(self, metrics: Dict[str, float], policy: Policy) -> float:
        """Calculate overall score from metrics."""
        score = metrics.get("context_efficiency", 0.5)

        # Bonus for good compression
        if "compression_ratio" in metrics:
            compression_ratio = metrics["compression_ratio"]
            if compression_ratio < 0.5:  # Good compression
                score += 0.1
            elif compression_ratio > 0.9:  # Poor compression
                score -= 0.05

        # Bonus for effective caching
        if metrics.get("cached_paths", 0) > 0:
            cache_bonus = min(metrics["cached_paths"] / 10, 0.2)
            score += cache_bonus

        # Penalty for high optimization potential (means current state is inefficient)
        optimization_penalty = metrics.get("optimization_potential", 0) * 0.3
        score -= optimization_penalty

        # Bonus for fast operations
        total_time = metrics.get("total_execution_time", 1.0)
        if total_time < 0.1:  # Very fast
            score += 0.1
        elif total_time > 1.0:  # Slow
            score -= 0.1

        # Bonus for good access patterns
        access_efficiency = metrics.get("access_pattern_efficiency", 0)
        score += access_efficiency * 0.2

        # Penalty for high memory usage
        memory_usage = metrics.get("memory_usage", 0)
        if memory_usage > 100:  # > 100MB
            score -= 0.05

        # Bonus for successful navigation
        if metrics.get("navigation_commands", 0) > 0:
            nav_time = metrics.get("navigation_time", 1.0)
            if nav_time < 0.01:  # Fast navigation
                score += 0.05

        # Bonus for successful view creation
        if metrics.get("view_size", 0) > 0:
            score += 0.05

        # Apply policy-specific adjustments
        if policy.params.get("compression_enabled") and "compression_ratio" in metrics:
            # Reward policies that successfully use compression
            score += 0.1

        if policy.params.get("cache_hotspots") and metrics.get("cached_paths", 0) > 0:
            # Reward policies that successfully cache hotspots
            score += 0.1

        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))

    def get_supported_metrics(self) -> List[str]:
        """Get list of supported metrics."""
        return [
            "context_efficiency",
            "context_nodes",
            "context_size",
            "context_depth",
            "compression_ratio",
            "context_loss",
            "compression_time",
            "reorganization_time",
            "cached_paths",
            "cache_time",
            "navigation_time",
            "navigation_commands",
            "optimization_potential",
            "analysis_time",
            "query_time",
            "query_results",
            "checkpoint_time",
            "checkpoint_created",
            "memory_usage",
            "access_pattern_efficiency",
            "total_context_accesses",
            "unique_context_paths",
            "view_creation_time",
            "view_size",
            "total_execution_time",
            "inspection_time",
        ]

    def validate_workload(self, workload: Workload) -> bool:
        """Validate if workload is suitable for this evaluator."""
        # Context evaluation works for any workload as it measures
        # the efficiency of context management during execution
        return True

    def describe(self) -> str:
        """Describe what this evaluator measures."""
        return (
            "Measures context management efficiency including inspection, "
            "compression, reorganization, caching, and navigation performance"
        )

    def get_evaluation_categories(self) -> Dict[str, List[str]]:
        """Get categories of metrics this evaluator provides."""
        return {
            "Performance": [
                "inspection_time",
                "compression_time",
                "reorganization_time",
                "cache_time",
                "navigation_time",
                "analysis_time",
                "query_time",
                "total_execution_time",
            ],
            "Efficiency": [
                "context_efficiency",
                "compression_ratio",
                "access_pattern_efficiency",
                "optimization_potential",
            ],
            "Structure": [
                "context_nodes",
                "context_size",
                "context_depth",
                "cached_paths",
                "query_results",
                "view_size",
            ],
            "Resource Usage": [
                "memory_usage",
                "context_loss",
                "total_context_accesses",
                "unique_context_paths",
            ],
        }

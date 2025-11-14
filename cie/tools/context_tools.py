"""
Tools for agents to manipulate and navigate their context.
"""

import json
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

from cie.core.context import ContextIntrospector, ContextManipulator, ContextNode, ContextOptimizer


class AgentContextTools:
    """Collection of context manipulation tools for agents."""

    def __init__(self):
        self.introspector = ContextIntrospector()
        self.manipulator = ContextManipulator(self.introspector)
        self.optimizer = ContextOptimizer(self.introspector, self.manipulator)
        self.context_cache = {}
        self.tool_registry = self._register_tools()
        self.current_path = "/"

    def _register_tools(self) -> Dict[str, Callable]:
        """Register available tools."""
        return {
            "inspect": self.inspect_context,
            "query": self.query_context,
            "compress": self.compress_context,
            "reorganize": self.reorganize_context,
            "create_view": self.create_context_view,
            "summarize": self.summarize_context,
            "cache": self.cache_context,
            "extract": self.extract_from_context,
            "inject": self.inject_into_context,
            "navigate": self.navigate_context,
            "analyze": self.analyze_context,
            "optimize": self.optimize_context,
            "checkpoint": self.checkpoint_context,
            "diff": self.diff_context,
            "merge": self.merge_contexts,
        }

    def inspect_context(self, target: str = "current", max_depth: int = 5) -> Dict:
        """
        Inspect context at different levels.

        Args:
            target: 'current', 'parent', 'global', or specific path
            max_depth: Maximum depth to traverse

        Returns:
            Context inspection results
        """
        import sys

        if target == "current":
            frame = sys._getframe(1)
        elif target == "parent":
            frame = sys._getframe(2)
        elif target == "global":
            frame = sys._getframe()
            while frame.f_back:
                frame = frame.f_back
        else:
            # Specific path query
            return self.query_context(target)

        context_tree = self.introspector.capture_context(
            frame.f_locals, frame.f_globals, max_depth=max_depth
        )

        return {
            "tree": context_tree.to_dict(),
            "summary": self.manipulator.create_summary(),
            "hotspots": self.introspector.get_hotspots(5),
        }

    def query_context(self, query: str, return_values: bool = False) -> List[Dict]:
        """
        Query context with path patterns.

        Args:
            query: Path pattern to search for
            return_values: Whether to include actual values

        Returns:
            List of matching context nodes
        """
        nodes = self.introspector.query_context(query)

        results = []
        for node in nodes:
            result = {
                "path": node.path,
                "name": node.name,
                "type": node.type,
                "size": node.size,
                "depth": node.depth,
            }

            if return_values and node.size < 1000:
                result["value"] = node.value

            results.append(result)

        return results

    def compress_context(
        self, strategy: str = "auto", threshold: int = 1000, preserve_paths: List[str] = None
    ) -> Dict:
        """
        Compress context using specified strategy.

        Args:
            strategy: 'auto', 'truncate', 'summarize', 'hierarchical'
            threshold: Size threshold for compression
            preserve_paths: Paths to preserve uncompressed

        Returns:
            Compression results
        """
        preserve_paths = preserve_paths or []

        # Get current context
        compressed_tree = self.manipulator.compress_context(strategy, threshold)

        # Preserve specified paths
        for path in preserve_paths:
            nodes = self.introspector.query_context(path)
            # Mark as preserved in metadata
            for node in nodes:
                node.metadata["preserved"] = True

        original_summary = self.manipulator.create_summary()

        # Apply compression
        self.introspector.context_tree = compressed_tree
        compressed_summary = self.manipulator.create_summary()

        return {
            "strategy": strategy,
            "original_size": original_summary["total_size"],
            "compressed_size": compressed_summary["total_size"],
            "compression_ratio": compressed_summary["total_size"] / original_summary["total_size"]
            if original_summary["total_size"] > 0
            else 0,
            "preserved_paths": preserve_paths,
        }

    def reorganize_context(self, method: str = "by_access") -> Dict:
        """
        Reorganize context structure.

        Args:
            method: 'by_access', 'by_type', 'by_size', 'flatten'

        Returns:
            Reorganization results
        """
        if method == "by_access":
            result = self.manipulator.reorganize_by_access()
        elif method == "by_type":
            result = self._reorganize_by_type()
        elif method == "by_size":
            result = self._reorganize_by_size()
        elif method == "flatten":
            result = self._flatten_context()
        else:
            raise ValueError(f"Unknown reorganization method: {method}")

        return {
            "method": method,
            "result": result,
            "new_structure": self.manipulator.create_summary(),
        }

    def create_context_view(
        self, name: str, selector: Callable[[ContextNode], bool] = None, paths: List[str] = None
    ) -> Dict:
        """
        Create a view of the context.

        Args:
            name: View name
            selector: Function to select nodes
            paths: Specific paths to include

        Returns:
            Created view
        """
        if paths:
            selector = lambda node: node.path in paths
        elif not selector:
            # Default: select frequently accessed
            hotspots = [path for path, _ in self.introspector.get_hotspots(10)]
            selector = lambda node: node.path in hotspots

        view = self.manipulator.create_view(name, selector)

        # Cache the view
        self.context_cache[name] = view

        return {"name": name, "size": len(view), "paths": list(view.keys())}

    def summarize_context(self, format: str = "json") -> Any:
        """
        Create a summary of the current context.

        Args:
            format: 'json', 'text', 'tree', 'metrics'

        Returns:
            Context summary in requested format
        """
        summary = self.manipulator.create_summary()

        if format == "json":
            return summary
        elif format == "text":
            return self._format_summary_text(summary)
        elif format == "tree":
            return self._format_summary_tree(summary)
        elif format == "metrics":
            return self._format_summary_metrics(summary)
        else:
            return summary

    def cache_context(self, key: str, value: Any = None) -> bool:
        """
        Cache context or value.

        Args:
            key: Cache key
            value: Value to cache (if None, caches current context)

        Returns:
            Success status
        """
        if value is None:
            # Cache current context
            value = (
                self.introspector.context_tree.to_dict() if self.introspector.context_tree else {}
            )

        self.context_cache[key] = value
        return True

    def extract_from_context(self, path: str, default: Any = None) -> Any:
        """
        Extract value from context by path.

        Args:
            path: Context path
            default: Default value if not found

        Returns:
            Extracted value or default
        """
        # Check synthetic context first
        if (
            hasattr(self.manipulator, "synthetic_context")
            and path in self.manipulator.synthetic_context
        ):
            return self.manipulator.synthetic_context[path]

        # Fall back to introspector query
        nodes = self.introspector.query_context(path)
        if nodes:
            return nodes[0].value
        return default

    def inject_into_context(self, path: str, value: Any) -> bool:
        """
        Inject value into context.

        Args:
            path: Target path
            value: Value to inject

        Returns:
            Success status
        """
        # Parse path
        parts = path.strip("/").split("/")

        # Create synthetic entry
        self.manipulator.synthetic_context[path] = value

        # If it's a tool/function, register it
        if callable(value):
            self.manipulator.inject_tool(parts[-1], value)

        return True

    def navigate_context(self, command: str) -> Any:
        """
        Navigate context with commands.

        Args:
            command: Navigation command (cd, ls, pwd, find, etc.)

        Returns:
            Command result
        """
        parts = command.split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        if cmd == "ls":
            # List current level
            path = args[0] if args else "/"
            nodes = self.introspector.query_context(path)
            return [{"name": n.name, "type": n.type, "size": n.size} for n in nodes]

        elif cmd == "cd":
            # Change context focus
            path = args[0] if args else "/"
            self.current_path = path
            return f"Changed to {path}"

        elif cmd == "pwd":
            # Current path
            return getattr(self, "current_path", "/")

        elif cmd == "find":
            # Find in context
            pattern = args[0] if args else ""
            return self.query_context(pattern)

        else:
            return f"Unknown command: {cmd}"

    def analyze_context(self) -> Dict:
        """
        Perform deep analysis of context.

        Returns:
            Analysis results
        """
        suggestions = self.introspector.suggest_reorganization()
        efficiency = 1.0

        # Calculate efficiency score
        if suggestions["deep_nesting"]:
            efficiency -= 0.1 * len(suggestions["deep_nesting"])
        if suggestions["large_objects"]:
            efficiency -= 0.05 * len(suggestions["large_objects"])
        if suggestions["compression_candidates"]:
            efficiency -= 0.02 * len(suggestions["compression_candidates"])

        efficiency = max(0.0, efficiency)

        # Get access patterns
        access_analysis = {
            "total_accesses": sum(self.introspector.access_patterns.values()),
            "unique_paths": len(self.introspector.access_patterns),
            "access_distribution": self._analyze_access_distribution(),
            "access_efficiency": self._calculate_access_efficiency(),
        }

        return {
            "efficiency_score": efficiency,
            "suggestions": suggestions,
            "access_analysis": access_analysis,
            "optimization_potential": 1.0 - efficiency,
        }

    def optimize_context(self) -> Dict:
        """
        Run full context optimization.

        Returns:
            Optimization results
        """
        return self.optimizer.optimize()

    def checkpoint_context(self, name: str = None) -> str:
        """
        Create a checkpoint of current context.

        Args:
            name: Checkpoint name (auto-generated if None)

        Returns:
            Checkpoint ID
        """
        import time

        if not name:
            name = f"checkpoint_{int(time.time())}"

        checkpoint = self.manipulator.create_checkpoint()
        self.context_cache[f"checkpoint:{name}"] = checkpoint

        return name

    def diff_context(self, checkpoint1: str, checkpoint2: str = "current") -> Dict:
        """
        Diff two context states.

        Args:
            checkpoint1: First checkpoint name
            checkpoint2: Second checkpoint name or 'current'

        Returns:
            Differences between contexts
        """
        # Get first checkpoint
        cp1 = self.context_cache.get(f"checkpoint:{checkpoint1}")
        if not cp1:
            return {"error": f"Checkpoint {checkpoint1} not found"}

        # Get second checkpoint or current
        if checkpoint2 == "current":
            cp2 = self.manipulator.create_checkpoint()
        else:
            cp2 = self.context_cache.get(f"checkpoint:{checkpoint2}")
            if not cp2:
                return {"error": f"Checkpoint {checkpoint2} not found"}

        # Compare
        differences = {
            "added_paths": [],
            "removed_paths": [],
            "changed_values": [],
            "size_changes": [],
        }

        # This would do actual diffing logic
        return differences

    def merge_contexts(self, contexts: List[str], strategy: str = "union") -> Dict:
        """
        Merge multiple contexts.

        Args:
            contexts: List of context names/checkpoints
            strategy: 'union', 'intersection', 'latest'

        Returns:
            Merged context
        """
        merged = {}

        for ctx_name in contexts:
            ctx = self.context_cache.get(ctx_name, {})
            if strategy == "union":
                merged.update(ctx)
            elif strategy == "intersection":
                if not merged:
                    merged = ctx.copy()
                else:
                    merged = {k: v for k, v in merged.items() if k in ctx}
            elif strategy == "latest":
                merged = ctx

        return merged

    # Helper methods
    def _reorganize_by_type(self) -> Dict:
        """Reorganize context by type."""
        result = defaultdict(list)

        def categorize(node: ContextNode):
            result[node.type].append({"path": node.path, "name": node.name, "size": node.size})
            for child in node.children:
                categorize(child)

        if self.introspector.context_tree:
            categorize(self.introspector.context_tree)

        return dict(result)

    def _reorganize_by_size(self) -> Dict:
        """Reorganize context by size."""
        result = {
            "large": [],  # > 10KB
            "medium": [],  # 1KB - 10KB
            "small": [],  # < 1KB
        }

        def categorize(node: ContextNode):
            if node.size > 10000:
                category = "large"
            elif node.size > 1000:
                category = "medium"
            else:
                category = "small"

            result[category].append(
                {"path": node.path, "name": node.name, "size": node.size, "type": node.type}
            )

            for child in node.children:
                categorize(child)

        if self.introspector.context_tree:
            categorize(self.introspector.context_tree)

        return result

    def _flatten_context(self) -> Dict:
        """Flatten context structure."""
        flattened = {}

        def flatten(node: ContextNode, prefix: str = ""):
            key = f"{prefix}{node.name}" if prefix else node.name
            flattened[key] = {
                "value": node.value if node.size < 100 else f"<{node.type}>",
                "type": node.type,
                "size": node.size,
            }

            for child in node.children:
                flatten(child, f"{key}.")

        if self.introspector.context_tree:
            flatten(self.introspector.context_tree)

        return flattened

    def _format_summary_text(self, summary: Dict) -> str:
        """Format summary as text."""
        lines = [
            "=== Context Summary ===",
            f"Total Nodes: {summary['total_nodes']}",
            f"Total Size: {summary['total_size']:,} bytes",
            f"Max Depth: {summary['max_depth']}",
            "",
            "Type Distribution:",
        ]

        for type_name, count in summary["type_distribution"].items():
            lines.append(f"  {type_name}: {count}")

        lines.extend(
            [
                "",
                "Access Statistics:",
                f"  Total Accesses: {summary['access_statistics']['total_accesses']}",
                f"  Unique Paths: {summary['access_statistics']['unique_paths']}",
                f"  Hottest Path: {summary['access_statistics']['hottest_path']}",
            ]
        )

        return "\n".join(lines)

    def _format_summary_tree(self, summary: Dict) -> str:
        """Format summary as tree."""
        # This would create an ASCII tree representation
        return "Tree format not implemented"

    def _format_summary_metrics(self, summary: Dict) -> Dict:
        """Format summary as metrics."""
        return {
            "nodes": summary["total_nodes"],
            "bytes": summary["total_size"],
            "depth": summary["max_depth"],
            "types": len(summary["type_distribution"]),
            "accesses": summary["access_statistics"]["total_accesses"],
            "paths": summary["access_statistics"]["unique_paths"],
        }

    def _analyze_access_distribution(self) -> Dict:
        """Analyze access pattern distribution."""
        patterns = self.introspector.access_patterns
        if not patterns:
            return {}

        values = list(patterns.values())
        return {
            "mean": sum(values) / len(values),
            "max": max(values),
            "min": min(values),
            "std": self._calculate_std(values),
        }

    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if not values:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance**0.5

    def _calculate_access_efficiency(self) -> float:
        """Calculate access efficiency score."""
        patterns = self.introspector.access_patterns
        if not patterns:
            return 0.0

        total = sum(patterns.values())
        unique = len(patterns)

        # Higher score for more distributed access
        distribution_score = unique / total if total > 0 else 0

        # Penalize very deep paths
        depth_penalty = 0
        for path in patterns.keys():
            depth = path.count("/")
            if depth > 5:
                depth_penalty += 0.01 * (depth - 5)

        return max(0.0, distribution_score - depth_penalty)

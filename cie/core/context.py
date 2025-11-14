"""
Context introspection and manipulation system for agent optimization.
"""

import ast
import inspect
import json
import sys
import types
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import numpy as np


@dataclass
class ContextNode:
    """Represents a node in the context tree."""

    name: str
    value: Any
    type: str
    size: int
    depth: int
    path: str
    children: List["ContextNode"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compress(self) -> "ContextNode":
        """Compress this node to reduce size."""
        if self.type == "string" and self.size > 1000:
            # Compress long strings
            compressed_value = (
                self.value[:500] + f"...[{self.size - 1000} chars]..." + self.value[-500:]
            )
            return ContextNode(
                name=self.name,
                value=compressed_value,
                type=self.type,
                size=1000,
                depth=self.depth,
                path=self.path,
                metadata={"compressed": True, "original_size": self.size},
            )
        elif self.type == "list" and self.size > 100:
            # Compress long lists
            compressed_value = self.value[:50] + ["..."] + self.value[-50:]
            return ContextNode(
                name=self.name,
                value=compressed_value,
                type=self.type,
                size=101,
                depth=self.depth,
                path=self.path,
                metadata={"compressed": True, "original_size": self.size},
            )
        return self

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type,
            "size": self.size,
            "depth": self.depth,
            "path": self.path,
            "metadata": self.metadata,
            "children": [c.to_dict() for c in self.children],
        }


class ContextIntrospector:
    """Tool for introspecting and analyzing context."""

    def __init__(self):
        self.context_tree: Optional[ContextNode] = None
        self.context_map: Dict[str, Any] = {}
        self.access_patterns: Dict[str, int] = defaultdict(int)
        self.context_history: List[Dict[str, Any]] = []

    def capture_context(
        self, locals_dict: Dict[str, Any], globals_dict: Dict[str, Any], max_depth: int = 5
    ) -> ContextNode:
        """Capture current context into a tree structure."""
        root = ContextNode(name="root", value=None, type="context", size=0, depth=0, path="/")

        # Capture locals
        locals_node = self._build_context_tree(
            "locals", locals_dict, depth=1, max_depth=max_depth, path="/locals"
        )
        root.children.append(locals_node)

        # Capture globals (filtered)
        filtered_globals = {
            k: v
            for k, v in globals_dict.items()
            if not k.startswith("__") and not inspect.ismodule(v)
        }
        globals_node = self._build_context_tree(
            "globals", filtered_globals, depth=1, max_depth=max_depth, path="/globals"
        )
        root.children.append(globals_node)

        # Capture call stack
        stack_node = self._capture_call_stack()
        root.children.append(stack_node)

        self.context_tree = root
        self.context_history.append(root.to_dict())
        return root

    def _build_context_tree(
        self, name: str, obj: Any, depth: int, max_depth: int, path: str
    ) -> ContextNode:
        """Build context tree recursively."""
        if depth > max_depth:
            return ContextNode(
                name=name, value="<max_depth>", type="truncated", size=0, depth=depth, path=path
            )

        obj_type = type(obj).__name__
        obj_size = self._get_size(obj)

        node = ContextNode(
            name=name, value=obj, type=obj_type, size=obj_size, depth=depth, path=path
        )

        # Track access
        self.access_patterns[path] += 1

        # Add children for complex types
        if isinstance(obj, dict) and depth < max_depth:
            for key, value in obj.items():
                child_path = f"{path}/{key}"
                child = self._build_context_tree(str(key), value, depth + 1, max_depth, child_path)
                node.children.append(child)

        elif isinstance(obj, (list, tuple)) and depth < max_depth:
            for i, item in enumerate(obj[:10]):  # Limit to first 10 items
                child_path = f"{path}[{i}]"
                child = self._build_context_tree(f"[{i}]", item, depth + 1, max_depth, child_path)
                node.children.append(child)

        elif hasattr(obj, "__dict__") and depth < max_depth:
            for attr_name, attr_value in obj.__dict__.items():
                if not attr_name.startswith("_"):
                    child_path = f"{path}.{attr_name}"
                    child = self._build_context_tree(
                        attr_name, attr_value, depth + 1, max_depth, child_path
                    )
                    node.children.append(child)

        return node

    def _capture_call_stack(self) -> ContextNode:
        """Capture the current call stack."""
        stack_node = ContextNode(
            name="call_stack", value=None, type="stack", size=0, depth=1, path="/call_stack"
        )

        frames = inspect.stack()[2:7]  # Skip this method and caller
        for i, frame in enumerate(frames):
            frame_node = ContextNode(
                name=f"frame_{i}",
                value={
                    "function": frame.function,
                    "filename": frame.filename,
                    "lineno": frame.lineno,
                    "code": frame.code_context[0].strip() if frame.code_context else None,
                },
                type="frame",
                size=0,
                depth=2,
                path=f"/call_stack/frame_{i}",
            )
            stack_node.children.append(frame_node)

        return stack_node

    def _get_size(self, obj: Any) -> int:
        """Get approximate size of object."""
        try:
            if isinstance(obj, (str, bytes)):
                return len(obj)
            elif isinstance(obj, (list, tuple, set)):
                return len(obj)
            elif isinstance(obj, dict):
                return len(obj)
            else:
                return sys.getsizeof(obj)
        except:
            return 0

    def query_context(self, query: str) -> List[ContextNode]:
        """Query context tree with path-like syntax."""
        if not self.context_tree:
            return []

        results = []

        def search(node: ContextNode, pattern: str):
            if pattern in node.path or pattern in node.name:
                results.append(node)
            for child in node.children:
                search(child, pattern)

        search(self.context_tree, query)
        return results

    def get_hotspots(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently accessed context paths."""
        sorted_patterns = sorted(self.access_patterns.items(), key=lambda x: x[1], reverse=True)
        return sorted_patterns[:top_n]

    def suggest_reorganization(self) -> Dict[str, Any]:
        """Suggest context reorganization based on access patterns."""
        suggestions = {
            "hotspots": self.get_hotspots(),
            "deep_nesting": [],
            "large_objects": [],
            "redundant_data": [],
            "compression_candidates": [],
        }

        def analyze(node: ContextNode):
            # Check for deep nesting
            if node.depth > 5:
                suggestions["deep_nesting"].append(node.path)

            # Check for large objects
            if node.size > 10000:
                suggestions["large_objects"].append(
                    {"path": node.path, "size": node.size, "type": node.type}
                )

            # Check for compression candidates
            if node.size > 1000 and node.type in ["string", "list", "dict"]:
                suggestions["compression_candidates"].append(node.path)

            for child in node.children:
                analyze(child)

        if self.context_tree:
            analyze(self.context_tree)

        return suggestions


class ContextManipulator:
    """Tool for manipulating and reorganizing context."""

    def __init__(self, introspector: ContextIntrospector):
        self.introspector = introspector
        self.transforms: List[Callable] = []
        self.synthetic_context: Dict[str, Any] = {}

    def create_view(self, name: str, selector: Callable) -> Dict[str, Any]:
        """Create a view of the context based on selector function."""
        view = {}

        def extract(node: ContextNode):
            if selector(node):
                view[node.path] = {"value": node.value, "type": node.type, "size": node.size}
            for child in node.children:
                extract(child)

        if self.introspector.context_tree:
            extract(self.introspector.context_tree)

        self.synthetic_context[name] = view
        return view

    def compress_context(self, strategy: str = "auto", threshold: int = 1000) -> ContextNode:
        """Compress context using specified strategy."""
        if not self.introspector.context_tree:
            return None

        def compress_recursive(node: ContextNode) -> ContextNode:
            compressed_node = node.compress() if node.size > threshold else node
            compressed_node.children = [compress_recursive(child) for child in node.children]
            return compressed_node

        compressed_tree = compress_recursive(self.introspector.context_tree)
        return compressed_tree

    def reorganize_by_access(self) -> Dict[str, Any]:
        """Reorganize context based on access patterns."""
        hotspots = self.introspector.get_hotspots()

        reorganized = {"frequently_accessed": {}, "rarely_accessed": {}, "never_accessed": {}}

        def categorize(node: ContextNode):
            access_count = self.introspector.access_patterns.get(node.path, 0)

            if access_count > 10:
                category = "frequently_accessed"
            elif access_count > 0:
                category = "rarely_accessed"
            else:
                category = "never_accessed"

            reorganized[category][node.path] = {
                "value": node.value if node.size < 100 else f"<large_{node.type}>",
                "type": node.type,
                "access_count": access_count,
            }

            for child in node.children:
                categorize(child)

        if self.introspector.context_tree:
            categorize(self.introspector.context_tree)

        return reorganized

    def create_summary(self) -> Dict[str, Any]:
        """Create a summary of the current context."""
        if not self.introspector.context_tree:
            return {}

        summary = {
            "total_nodes": 0,
            "total_size": 0,
            "max_depth": 0,
            "type_distribution": defaultdict(int),
            "largest_objects": [],
            "access_statistics": {
                "total_accesses": sum(self.introspector.access_patterns.values()),
                "unique_paths": len(self.introspector.access_patterns),
                "hottest_path": max(self.introspector.access_patterns.items(), key=lambda x: x[1])[
                    0
                ]
                if self.introspector.access_patterns
                else None,
            },
        }

        def analyze(node: ContextNode):
            summary["total_nodes"] += 1
            summary["total_size"] += node.size
            summary["max_depth"] = max(summary["max_depth"], node.depth)
            summary["type_distribution"][node.type] += 1

            if node.size > 1000:
                summary["largest_objects"].append(
                    {"path": node.path, "size": node.size, "type": node.type}
                )

            for child in node.children:
                analyze(child)

        analyze(self.introspector.context_tree)

        # Sort largest objects
        summary["largest_objects"] = sorted(
            summary["largest_objects"], key=lambda x: x["size"], reverse=True
        )[:10]

        return summary

    def inject_tool(self, name: str, func: Callable) -> None:
        """Inject a new tool/function into the context."""
        self.synthetic_context[name] = func

    def create_checkpoint(self) -> Dict[str, Any]:
        """Create a checkpoint of the current context state."""
        import time

        return {
            "timestamp": str(int(time.time())),
            "context_tree": self.introspector.context_tree.to_dict()
            if self.introspector.context_tree
            else None,
            "access_patterns": dict(self.introspector.access_patterns),
            "synthetic_context": {k: str(v) for k, v in self.synthetic_context.items()},
        }

    def restore_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """Restore context from checkpoint."""
        # This would restore the context state
        if "access_patterns" in checkpoint:
            self.introspector.access_patterns = defaultdict(int, checkpoint["access_patterns"])


class ContextOptimizer:
    """Optimizer for context organization and access patterns."""

    def __init__(self, introspector: ContextIntrospector, manipulator: ContextManipulator):
        self.introspector = introspector
        self.manipulator = manipulator
        self.optimization_history: List[Dict[str, Any]] = []

    def optimize(self) -> Dict[str, Any]:
        """Run optimization pass on context."""
        suggestions = self.introspector.suggest_reorganization()

        optimization = {
            "timestamp": str(int(__import__("time").time())),
            "suggestions": suggestions,
            "actions": [],
        }

        # Compress large objects
        for path in suggestions["compression_candidates"]:
            nodes = self.introspector.query_context(path)
            if nodes:
                compressed = nodes[0].compress()
                optimization["actions"].append(
                    {
                        "type": "compress",
                        "path": path,
                        "original_size": nodes[0].size,
                        "compressed_size": compressed.size,
                    }
                )

        # Create views for frequently accessed data
        if suggestions["hotspots"]:
            hot_paths = [path for path, _ in suggestions["hotspots"][:5]]
            view = self.manipulator.create_view("hotspot_view", lambda node: node.path in hot_paths)
            optimization["actions"].append(
                {"type": "create_view", "name": "hotspot_view", "paths": hot_paths}
            )

        # Flatten deep nesting
        for path in suggestions["deep_nesting"]:
            optimization["actions"].append(
                {"type": "flatten_suggestion", "path": path, "reason": "deep_nesting"}
            )

        self.optimization_history.append(optimization)
        return optimization

    def benchmark_access(self, access_pattern: List[str]) -> Dict[str, float]:
        """Benchmark access time for given pattern."""
        import time

        results = {}
        for path in access_pattern:
            start = time.perf_counter()
            nodes = self.introspector.query_context(path)
            end = time.perf_counter()
            results[path] = end - start

        return results


# Integration with CIE evaluators
class ContextAwareEvaluator:
    """Evaluator that uses context introspection."""

    def __init__(self):
        self.introspector = ContextIntrospector()
        self.manipulator = ContextManipulator(self.introspector)
        self.optimizer = ContextOptimizer(self.introspector, self.manipulator)

    def evaluate_context_efficiency(self, context: Dict[str, Any]) -> float:
        """Evaluate how efficiently context is organized."""
        # Capture context
        root = self.introspector.capture_context(
            context.get("locals", {}), context.get("globals", {}), max_depth=5
        )

        # Get summary
        summary = self.manipulator.create_summary()

        # Calculate efficiency score
        score = 1.0

        # Penalize deep nesting
        if summary["max_depth"] > 5:
            score -= 0.1 * (summary["max_depth"] - 5)

        # Penalize large objects
        total_large = sum(1 for obj in summary["largest_objects"] if obj["size"] > 10000)
        score -= 0.05 * total_large

        # Reward good access patterns
        if summary["access_statistics"]["total_accesses"] > 0:
            access_efficiency = (
                summary["access_statistics"]["unique_paths"]
                / summary["access_statistics"]["total_accesses"]
            )
            score += 0.2 * access_efficiency

        return max(0.0, min(1.0, score))

    def suggest_improvements(self) -> List[str]:
        """Suggest improvements for context organization."""
        suggestions = self.introspector.suggest_reorganization()
        improvements = []

        if suggestions["deep_nesting"]:
            improvements.append(
                f"Flatten {len(suggestions['deep_nesting'])} deeply nested structures"
            )

        if suggestions["large_objects"]:
            improvements.append(f"Compress {len(suggestions['large_objects'])} large objects")

        if suggestions["compression_candidates"]:
            improvements.append(
                f"Consider compressing {len(suggestions['compression_candidates'])} objects"
            )

        hotspots = self.introspector.get_hotspots(5)
        if hotspots:
            improvements.append(
                f"Cache frequently accessed paths: {', '.join(path for path, _ in hotspots[:3])}"
            )

        return improvements

"""
UI component for navigating and manipulating context.
"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Label, TextArea, Tree

from cie.core.context import ContextIntrospector, ContextManipulator, ContextOptimizer


class ContextNavigator(Vertical):
    """Interactive context navigator widget."""

    BINDINGS = [
        Binding("c", "capture", "Capture"),
        Binding("r", "reorganize", "Reorganize"),
        Binding("o", "optimize", "Optimize"),
        Binding("s", "summary", "Summary"),
        Binding("/", "search", "Search"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.introspector = ContextIntrospector()
        self.manipulator = ContextManipulator(self.introspector)
        self.optimizer = ContextOptimizer(self.introspector, self.manipulator)

    def compose(self) -> ComposeResult:
        """Compose the context navigator."""
        with Horizontal(classes="context-header"):
            yield Label("🔍 Context Navigator", classes="header-title")
            yield Button("Capture", id="capture_btn")
            yield Button("Optimize", id="optimize_btn")
            yield Button("Export", id="export_btn")

        with Horizontal(classes="context-main"):
            # Left: Tree view
            with Vertical(classes="context-tree-panel"):
                yield Label("Context Tree", classes="panel-header")
                yield Tree("Context", id="context_tree")

            # Middle: Details
            with Vertical(classes="context-details-panel"):
                yield Label("Details", classes="panel-header")
                yield TextArea("", id="context_details", read_only=True)

            # Right: Metrics
            with Vertical(classes="context-metrics-panel"):
                yield Label("Metrics", classes="panel-header")
                yield DataTable(id="context_metrics")

        # Bottom: Actions and suggestions
        with Horizontal(classes="context-actions"):
            yield TextArea("", id="suggestions", read_only=True)

    def action_capture(self) -> None:
        """Capture current context."""
        import sys

        # Capture actual runtime context
        frame = sys._getframe(1)
        context_tree = self.introspector.capture_context(
            frame.f_locals, frame.f_globals, max_depth=5
        )

        # Update tree view
        self._update_tree(context_tree)

        # Update metrics
        self._update_metrics()

        # Show suggestions
        self._show_suggestions()

    def _update_tree(self, node, tree_node=None):
        """Update tree widget with context structure."""
        tree = self.query_one("#context_tree", Tree)

        if tree_node is None:
            tree.clear()
            tree_node = tree.root

        for child in node.children:
            label = f"{child.name} ({child.type}) [{child.size}]"
            child_tree_node = tree_node.add(label, expand=False)

            # Add metadata
            child_tree_node.data = {
                "path": child.path,
                "value": child.value,
                "type": child.type,
                "size": child.size,
            }

            # Recursively add children
            if child.children:
                self._update_tree(child, child_tree_node)

    def _update_metrics(self):
        """Update metrics table."""
        table = self.query_one("#context_metrics", DataTable)
        table.clear(columns=True)

        table.add_columns("Metric", "Value")

        summary = self.manipulator.create_summary()

        table.add_row("Total Nodes", str(summary["total_nodes"]))
        table.add_row("Total Size", f"{summary['total_size']:,} bytes")
        table.add_row("Max Depth", str(summary["max_depth"]))
        table.add_row("Total Accesses", str(summary["access_statistics"]["total_accesses"]))
        table.add_row("Unique Paths", str(summary["access_statistics"]["unique_paths"]))

        # Type distribution
        for type_name, count in summary["type_distribution"].items():
            table.add_row(f"Type: {type_name}", str(count))

    def _show_suggestions(self):
        """Show optimization suggestions."""
        suggestions = self.introspector.suggest_reorganization()
        text_area = self.query_one("#suggestions", TextArea)

        output = "=== Optimization Suggestions ===\n\n"

        if suggestions["hotspots"]:
            output += "Hotspots (frequently accessed):\n"
            for path, count in suggestions["hotspots"][:5]:
                output += f"  • {path}: {count} accesses\n"
            output += "\n"

        if suggestions["large_objects"]:
            output += "Large Objects:\n"
            for obj in suggestions["large_objects"][:5]:
                output += f"  • {obj['path']}: {obj['size']:,} bytes ({obj['type']})\n"
            output += "\n"

        if suggestions["compression_candidates"]:
            output += (
                f"Compression Candidates: {len(suggestions['compression_candidates'])} objects\n\n"
            )

        if suggestions["deep_nesting"]:
            output += f"Deep Nesting Issues: {len(suggestions['deep_nesting'])} paths\n\n"

        text_area.text = output

    def action_reorganize(self):
        """Reorganize context by access patterns."""
        reorganized = self.manipulator.reorganize_by_access()

        details = self.query_one("#context_details", TextArea)

        output = "=== Reorganized Context ===\n\n"

        for category, items in reorganized.items():
            output += f"{category.replace('_', ' ').title()}:\n"
            for path, info in list(items.items())[:10]:
                output += f"  • {path} ({info['type']}): {info.get('access_count', 0)} accesses\n"
            output += "\n"

        details.text = output

    def action_optimize(self):
        """Run optimization."""
        result = self.optimizer.optimize()

        details = self.query_one("#context_details", TextArea)

        output = "=== Optimization Results ===\n\n"
        output += f"Timestamp: {result['timestamp']}\n\n"

        output += "Actions Taken:\n"
        for action in result["actions"]:
            if action["type"] == "compress":
                output += f"  • Compressed {action['path']}: {action['original_size']} → {action['compressed_size']}\n"
            elif action["type"] == "create_view":
                output += f"  • Created view '{action['name']}' with {len(action['paths'])} paths\n"
            elif action["type"] == "flatten_suggestion":
                output += f"  • Suggest flattening {action['path']} (reason: {action['reason']})\n"

        details.text = output

    def action_summary(self):
        """Show context summary."""
        summary = self.manipulator.create_summary()
        details = self.query_one("#context_details", TextArea)

        output = "=== Context Summary ===\n\n"
        output += f"Total Nodes: {summary['total_nodes']}\n"
        output += f"Total Size: {summary['total_size']:,} bytes\n"
        output += f"Max Depth: {summary['max_depth']}\n\n"

        output += "Type Distribution:\n"
        for type_name, count in summary["type_distribution"].items():
            output += f"  • {type_name}: {count}\n"

        output += "\nAccess Statistics:\n"
        output += f"  • Total Accesses: {summary['access_statistics']['total_accesses']}\n"
        output += f"  • Unique Paths: {summary['access_statistics']['unique_paths']}\n"
        if summary["access_statistics"]["hottest_path"]:
            output += f"  • Hottest Path: {summary['access_statistics']['hottest_path']}\n"

        if summary["largest_objects"]:
            output += "\nLargest Objects:\n"
            for obj in summary["largest_objects"][:5]:
                output += f"  • {obj['path']}: {obj['size']:,} bytes ({obj['type']})\n"

        details.text = output

    def action_search(self):
        """Search context (placeholder for search functionality)."""
        # This would open a search dialog
        details = self.query_one("#context_details", TextArea)
        details.text = (
            "Search functionality not yet implemented.\nPress 'c' to capture context first."
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "capture_btn":
            self.action_capture()
        elif event.button.id == "optimize_btn":
            self.action_optimize()
        elif event.button.id == "export_btn":
            self._export_context()

    def _export_context(self):
        """Export context data."""
        import json
        from pathlib import Path

        try:
            if not self.introspector.context_tree:
                self.query_one("#context_details", TextArea).text = "No context captured to export."
                return

            # Create export data
            export_data = {
                "context_tree": self.introspector.context_tree.to_dict(),
                "access_patterns": dict(self.introspector.access_patterns),
                "summary": self.manipulator.create_summary(),
                "suggestions": self.introspector.suggest_reorganization(),
            }

            # Save to file
            export_path = Path.home() / ".cie" / "context_export.json"
            export_path.parent.mkdir(parents=True, exist_ok=True)

            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)

            details = self.query_one("#context_details", TextArea)
            details.text = f"Context exported to: {export_path}"

        except Exception as e:
            details = self.query_one("#context_details", TextArea)
            details.text = f"Export failed: {str(e)}"

    def on_tree_node_selected(self, event) -> None:
        """Handle tree node selection."""
        if hasattr(event.node, "data") and event.node.data:
            details = self.query_one("#context_details", TextArea)
            data = event.node.data

            output = f"=== Node Details ===\n\n"
            output += f"Path: {data['path']}\n"
            output += f"Type: {data['type']}\n"
            output += f"Size: {data['size']} bytes\n\n"

            if data["size"] < 1000 and data["value"] is not None:
                output += f"Value:\n{str(data['value'])[:500]}"
                if len(str(data["value"])) > 500:
                    output += "\n... (truncated)"
            else:
                output += "Value: <too large to display>"

            details.text = output

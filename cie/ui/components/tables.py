"""
Enhanced table components with sorting, filtering, and inline actions.
"""

from typing import Any, Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import DataTable, Input, Label, Select, Static


class EnhancedDataTable(Static):
    """Data table with sorting, filtering, and actions."""

    BINDINGS = [
        Binding("s", "sort", "Sort"),
        Binding("f", "filter", "Filter"),
        Binding("enter", "select", "Select"),
        Binding("space", "toggle", "Toggle"),
    ]

    show_filter: reactive[bool] = reactive(False)

    def __init__(
        self,
        *,
        show_row_labels: bool = True,
        fixed_rows: int = 0,
        fixed_columns: int = 0,
        zebra_stripes: bool = True,
        header_height: int = 1,
        show_cursor: bool = True,
        cursor_type: str = "row",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.table_options = {
            "show_row_labels": show_row_labels,
            "fixed_rows": fixed_rows,
            "fixed_columns": fixed_columns,
            "zebra_stripes": zebra_stripes,
            "header_height": header_height,
            "show_cursor": show_cursor,
            "cursor_type": cursor_type,
        }
        self.original_data: list[tuple] = []
        self.filtered_data: list[tuple] = []
        self.sort_column: int | None = None
        self.sort_reverse: bool = False

    def compose(self) -> ComposeResult:
        """Compose the enhanced table."""
        with Vertical(classes="enhanced-table-container"):
            # Filter bar
            with Horizontal(id="filter_bar", classes="filter-bar", display=self.show_filter):
                yield Input(placeholder="Filter...", id="filter_input", classes="filter-input")
                yield Select([("All columns", -1)], id="filter_column", classes="filter-column")

            # Main table
            self.table = DataTable(id="data_table", classes="data-table", **self.table_options)
            yield self.table

            # Action bar
            with Horizontal(id="action_bar", classes="table-actions"):
                yield Label("Actions:", classes="action-label")
                self.action_container = Horizontal(id="action_buttons", classes="action-buttons")
                yield self.action_container

    def add_columns(self, *labels: str) -> None:
        """Add columns to the table."""
        self.table.add_columns(*labels)

        # Update filter column selector
        select = self.query_one("#filter_column", Select)
        options = [("All columns", -1)]
        for i, label in enumerate(labels):
            options.append((label, i))
        select.set_options(options)

    def add_rows(self, rows: list[tuple]) -> None:
        """Add rows to the table."""
        self.original_data = rows
        self.filtered_data = rows
        self._refresh_table()

    def _refresh_table(self) -> None:
        """Refresh table with current data."""
        self.table.clear()
        for row in self.filtered_data:
            self.table.add_row(*row)

    def action_filter(self) -> None:
        """Toggle filter bar."""
        self.show_filter = not self.show_filter
        filter_bar = self.query_one("#filter_bar")
        filter_bar.display = self.show_filter

        if self.show_filter:
            self.query_one("#filter_input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle filter input changes."""
        if event.input.id != "filter_input":
            return

        filter_text = event.value.lower()
        column = self.query_one("#filter_column", Select).value

        if not filter_text:
            self.filtered_data = self.original_data
        else:
            self.filtered_data = []
            for row in self.original_data:
                # Check if filter matches
                if column == -1:  # All columns
                    if any(filter_text in str(cell).lower() for cell in row):
                        self.filtered_data.append(row)
                else:  # Specific column
                    if column < len(row) and filter_text in str(row[column]).lower():
                        self.filtered_data.append(row)

        self._refresh_table()

    def action_sort(self) -> None:
        """Sort by current column."""
        cursor_row, cursor_column = self.table.cursor_coordinate

        if cursor_column != self.sort_column:
            self.sort_column = cursor_column
            self.sort_reverse = False
        else:
            self.sort_reverse = not self.sort_reverse

        def sort_key(row):
            if cursor_column < len(row):
                value = row[cursor_column]
                # Try to convert to number for better sorting
                try:
                    return float(str(value).replace(",", "").replace("%", ""))
                except (ValueError, AttributeError):
                    return str(value)
            return ""

        self.filtered_data.sort(key=sort_key, reverse=self.sort_reverse)
        self._refresh_table()

    def add_action(self, label: str, action: Callable) -> None:
        """Add an action button."""
        from textual.widgets import Button

        button = Button(label, classes="table-action")
        button.action = action
        self.action_container.mount(button)

    def on_button_pressed(self, event) -> None:
        """Handle action button presses."""
        if hasattr(event.button, "action"):
            event.button.action()


class SelectableTable(EnhancedDataTable):
    """Table with row selection capabilities."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_rows: set[int] = set()

    def compose(self) -> ComposeResult:
        """Compose with selection column."""
        with Vertical(classes="selectable-table-container"):
            # Selection bar
            with Horizontal(id="selection_bar", classes="selection-bar"):
                yield Label("Selected: 0", id="selection_count")
                yield Button("Select All", id="select_all")
                yield Button("Clear Selection", id="clear_selection")

            # Use parent's compose for the table
            yield from super().compose()

    def add_columns(self, *labels: str) -> None:
        """Add columns with selection column."""
        super().add_columns("✓", *labels)

    def add_rows(self, rows: list[tuple]) -> None:
        """Add rows with selection state."""
        rows_with_selection = []
        for i, row in enumerate(rows):
            selection = "☑" if i in self.selected_rows else "☐"
            rows_with_selection.append((selection,) + row)
        super().add_rows(rows_with_selection)

    def action_toggle(self) -> None:
        """Toggle row selection."""
        cursor_row, _ = self.table.cursor_coordinate

        if cursor_row in self.selected_rows:
            self.selected_rows.remove(cursor_row)
        else:
            self.selected_rows.add(cursor_row)

        self._update_selection_display()

    def _update_selection_display(self) -> None:
        """Update selection checkboxes and count."""
        # Update checkboxes in table
        for i in range(self.table.row_count):
            if i in self.selected_rows:
                self.table.update_cell(i, 0, "☑")
            else:
                self.table.update_cell(i, 0, "☐")

        # Update count
        count_label = self.query_one("#selection_count", Label)
        count_label.update(f"Selected: {len(self.selected_rows)}")

    def on_button_pressed(self, event) -> None:
        """Handle selection buttons."""
        if event.button.id == "select_all":
            self.selected_rows = set(range(self.table.row_count))
            self._update_selection_display()
        elif event.button.id == "clear_selection":
            self.selected_rows.clear()
            self._update_selection_display()
        else:
            super().on_button_pressed(event)

    def get_selected_data(self) -> list[tuple]:
        """Get data for selected rows."""
        selected = []
        for i in self.selected_rows:
            # Skip selection column when returning data
            row_data = []
            for col in range(1, self.table.column_count):
                try:
                    cell_value = self.table.get_cell(i, col)
                    row_data.append(cell_value)
                except:
                    # Handle cases where get_cell might not be available
                    row_data.append(self.filtered_data[i][col])
            selected.append(tuple(row_data))
        return selected


class TrialTable(EnhancedDataTable):
    """Specialized table for displaying trial data."""

    def __init__(self, **kwargs):
        super().__init__(show_row_labels=False, cursor_type="row", zebra_stripes=True, **kwargs)
        self.add_columns("ID", "Policy", "Score", "Success", "Latency", "Cost", "Pareto", "Status")

    def add_trial_data(self, trials: list) -> None:
        """Add trial data to the table."""
        rows = []
        for trial in trials:
            # Format trial data for display
            row = (
                str(trial.id),
                trial.policy.name[:20],  # Truncate long names
                f"{trial.score:.4f}",
                f"{trial.metrics.get('task_success', 0):.1%}",
                f"{trial.metrics.get('latency_p95', 0):.2f}s",
                f"${trial.metrics.get('cost_per_req', 0):.3f}",
                "⭐" if getattr(trial, "is_pareto", False) else "",
                self._get_trial_status(trial),
            )
            rows.append(row)

        self.add_rows(rows)

    def _get_trial_status(self, trial) -> str:
        """Get status indicator for trial."""
        # Check guardrails and performance
        if trial.metrics.get("tool_error_rate", 0) > 0.03:
            return "[red]⚠ High Errors[/]"
        elif trial.metrics.get("task_success", 0) < 0.7:
            return "[yellow]⚠ Low Success[/]"
        elif trial.metrics.get("latency_p95", 0) > 5.0:
            return "[yellow]⚠ Slow[/]"
        else:
            return "[green]✓ Good[/]"


class OptimizerTable(EnhancedDataTable):
    """Specialized table for displaying optimizer information."""

    def __init__(self, **kwargs):
        super().__init__(show_row_labels=False, cursor_type="row", **kwargs)
        self.add_columns("Name", "Type", "Model", "K-Shots", "Best Score", "Trials", "Status")

    def add_optimizer_data(self, optimizers: list) -> None:
        """Add optimizer data to the table."""
        rows = []
        for name, meta in optimizers:
            row = (
                name,
                meta.get("type", "Unknown"),
                meta.get("model", "N/A"),
                str(meta.get("k_shots", "-")),
                f"{meta.get('best_score', 0):.3f}" if meta.get("best_score") else "-",
                str(meta.get("trial_count", 0)),
                self._get_optimizer_status(meta.get("status", "ready")),
            )
            rows.append(row)

        self.add_rows(rows)

    def _get_optimizer_status(self, status: str) -> str:
        """Get status indicator with color."""
        indicators = {
            "ready": "[green]● Ready[/]",
            "running": "[yellow]⟳ Running[/]",
            "error": "[red]✗ Error[/]",
            "success": "[green]✓ Success[/]",
            "idle": "[dim]○ Idle[/]",
        }
        return indicators.get(status, "[dim]○ Unknown[/]")


class WorkloadTable(EnhancedDataTable):
    """Specialized table for displaying workload information."""

    def __init__(self, **kwargs):
        super().__init__(show_row_labels=False, cursor_type="row", **kwargs)
        self.add_columns("Name", "Type", "Size", "Difficulty", "Evaluator", "Last Used")

    def add_workload_data(self, workloads: list) -> None:
        """Add workload data to the table."""
        rows = []
        for name, config in workloads:
            row = (
                name,
                config.get("type", "Unknown"),
                str(config.get("size", "N/A")),
                config.get("difficulty", "Medium"),
                config.get("evaluator", "Default"),
                config.get("last_used", "Never"),
            )
            rows.append(row)

        self.add_rows(rows)

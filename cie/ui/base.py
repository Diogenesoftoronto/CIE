"""
Base UI components for CIE.
"""

from collections.abc import Callable

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, DataTable, Label, Static


class BasePanel(Static):
    """Base panel with shared header/footer chrome and toolbar support."""

    is_minimized: reactive[bool] = reactive(False)
    can_minimize: reactive[bool] = reactive(True)

    def __init__(self, title: str, icon: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.panel_title = title
        self.panel_icon = icon
        self.original_height = None
        self.title_label: Label | None = None
        self.subtitle_label: Label | None = None
        self.badge_label: Label | None = None
        self.toolbar: Horizontal | None = None
        self.content_container: Vertical | None = None
        self.status_label: Label | None = None
        self._toolbar_actions: dict[str, str | Callable[[], None]] = {}
        self._pending_toolbar_actions: list[tuple[str, Callable[[], None] | None, str | None, str | None, str | None]] = []

    def compose(self) -> ComposeResult:
        """Compose the panel layout."""
        with Horizontal(id=f"{self.id}_header", classes="panel-header"):
            with Vertical(classes="panel-heading"):
                title = self._format_title(self.panel_title, self.panel_icon)
                self.title_label = Label(title, id=f"{self.id}_title", classes="panel-title")
                yield self.title_label
                self.subtitle_label = Label("", classes="panel-subtitle")
                self.subtitle_label.display = False
                yield self.subtitle_label
            self.badge_label = Label("", classes="panel-badge")
            self.badge_label.display = False
            yield self.badge_label
            self.toolbar = Horizontal(classes="panel-toolbar")
            yield self.toolbar

        with Vertical(id=f"{self.id}_content", classes="panel-content") as content:
            self.content_container = content
            yield from self.compose_content()

        self.status_label = Label("", id=f"{self.id}_status", classes="panel-status")
        yield self.status_label

    def compose_content(self) -> ComposeResult:
        """Override this to add panel-specific content."""
        yield Label("Override compose_content() in subclass")

    def on_mount(self) -> None:
        """Mount any toolbar actions queued before compose completed."""
        for args in self._pending_toolbar_actions:
            self._create_toolbar_button(*args)
        self._pending_toolbar_actions.clear()

    def watch_is_minimized(self, old_value: bool, new_value: bool) -> None:
        """React to minimize state changes."""
        content = self.content_container
        status = self.status_label
        if not content or not status:
            return
        if new_value:
            if self.original_height is None:
                self.original_height = self.styles.height
            self.styles.height = "auto"
            content.display = False
            status.display = False
        else:
            if self.original_height:
                self.styles.height = self.original_height
            content.display = True
            status.display = True

    def set_title(self, title: str, icon: str | None = None) -> None:
        """Update the panel title and optional icon."""
        self.panel_title = title
        if icon is not None:
            self.panel_icon = icon
        if self.title_label:
            self.title_label.update(self._format_title(self.panel_title, self.panel_icon))

    def set_subtitle(self, subtitle: str | None) -> None:
        """Set or clear the subtitle beneath the title."""
        if not self.subtitle_label:
            return
        if subtitle:
            self.subtitle_label.update(subtitle)
            self.subtitle_label.display = True
        else:
            self.subtitle_label.display = False

    def set_badge(self, text: str, level: str = "info") -> None:
        """Show a badge next to the title."""
        if not self.badge_label:
            return
        color_map = {"info": "cyan", "success": "green", "warning": "yellow", "error": "red"}
        color = color_map.get(level, "cyan")
        self.badge_label.update(f"[{color}]{text}[/{color}]")
        self.badge_label.display = True

    def clear_badge(self) -> None:
        """Hide the badge element."""
        if self.badge_label:
            self.badge_label.display = False

    def add_toolbar_action(
        self,
        label: str,
        callback: Callable[[], None] | None = None,
        *,
        action_name: str | None = None,
        button_id: str | None = None,
        tooltip: str | None = None,
    ) -> None:
        """Add a toolbar action button aligned to the right of the header."""

        if button_id is None:
            button_id = f"{self.id}_tool_{len(self._toolbar_actions)}"
        record = (label, callback, action_name, button_id, tooltip)
        if self.toolbar is None:
            self._pending_toolbar_actions.append(record)
        else:
            self._create_toolbar_button(*record)

    def clear_toolbar(self) -> None:
        """Remove all toolbar buttons."""
        self._toolbar_actions.clear()
        if self.toolbar:
            self.toolbar.remove_children()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dispatch toolbar button presses."""
        action = self._toolbar_actions.get(event.button.id)
        if callable(action):
            action()
            event.stop()
            return
        if isinstance(action, str) and hasattr(self, action):
            getattr(self, action)()
            event.stop()

    def action_maximize(self) -> None:
        """Maximize this panel (implementation in main app)."""
        self.post_message(PanelMaximize(self))

    def toggle_minimize(self) -> None:
        """Toggle minimized state."""
        self.is_minimized = not self.is_minimized

    def action_minimize(self) -> None:
        """Minimize this panel."""
        self.is_minimized = True

    def update_status(self, message: str, level: str = "info") -> None:
        """Update status message in the footer."""
        if not self.status_label:
            return
        color_map = {"info": "white", "success": "green", "warning": "yellow", "error": "red"}
        color = color_map.get(level, "white")
        self.status_label.update(f"[{color}]{message}[/{color}]")

    def _create_toolbar_button(
        self,
        label: str,
        callback: Callable[[], None] | None,
        action_name: str | None,
        button_id: str | None,
        tooltip: str | None,
    ) -> None:
        if not self.toolbar or button_id is None:
            return
        button = Button(
            label,
            id=button_id,
            classes="panel-toolbar-button",
            tooltip=tooltip or "",
        )
        self.toolbar.mount(button)
        self._toolbar_actions[button_id] = callback or action_name or ""

    @staticmethod
    def _format_title(title: str, icon: str | None) -> str:
        return f"{icon} {title}" if icon else title


class DataTablePanel(BasePanel):
    """Base panel with a primary DataTable and cursor helpers."""

    selected_row: reactive[int | None] = reactive(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.primary_table: DataTable | None = None

    def register_table(self, table: DataTable) -> DataTable:
        """Designate the table used for default cursor actions."""
        self.primary_table = table
        return table

    def action_cursor_down(self) -> None:
        if self.primary_table:
            self.primary_table.action_cursor_down()

    def action_cursor_up(self) -> None:
        if self.primary_table:
            self.primary_table.action_cursor_up()

    def clear_selection(self) -> None:
        """Reset cached selection state."""
        self.selected_row = None

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Track row selection for the primary table."""
        if self.primary_table and event.control is self.primary_table:
            self.selected_row = event.cursor_row


class PanelMaximize(Message):
    """Message sent when a panel requests to be maximized."""

    def __init__(self, panel: BasePanel) -> None:
        self.panel = panel
        super().__init__()


class StatusBar(Static):
    """Status bar component."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_message = "Ready"
        self.status_level = "info"

    def compose(self) -> Horizontal:
        """Compose the status bar."""
        with Horizontal(classes="status-bar"):
            self.message_label = Label(self.status_message, id="status_message")
            yield self.message_label
            self.stats_label = Label("", id="status_stats")
            yield self.stats_label

    def update_status(self, message: str, level: str = "info") -> None:
        """Update status message."""
        self.status_message = message
        self.status_level = level
        # Add color based on level
        color_map = {"info": "white", "success": "green", "warning": "yellow", "error": "red"}
        color = color_map.get(level, "white")
        self.message_label.update(f"[{color}]{message}[/{color}]")

    def update_stats(self, stats: dict) -> None:
        """Update statistics display."""
        stats_text = (
            f"Trials: {stats.get('trials', 0)} | "
            f"Pareto: {stats.get('pareto', 0)} | "
            f"Score: {stats.get('best_score', 'N/A')}"
        )
        self.stats_label.update(stats_text)


class ProgressBar(Static):
    """Progress bar component."""

    def __init__(self, total: int = 100, **kwargs):
        super().__init__(**kwargs)
        self.total = total
        self.current = 0

    def compose(self) -> Horizontal:
        """Compose the progress bar."""
        with Horizontal(classes="progress-container"):
            self.bar = Static("", id="progress_bar", classes="progress-bar")
            yield self.bar
            self.label = Label("0%", id="progress_label", classes="progress-label")
            yield self.label

    def update_progress(self, current: int, total: int | None = None) -> None:
        """Update progress."""
        if total is not None:
            self.total = total
        self.current = current
        percentage = min(100, max(0, int((current / self.total) * 100)))
        # Update bar
        filled_width = int(percentage / 2)  # Scale to bar width
        bar_text = "█" * filled_width + "░" * (50 - filled_width)
        self.bar.update(bar_text)
        # Update label
        self.label.update(f"{percentage}% ({current}/{self.total})")

    def reset(self) -> None:
        """Reset progress bar."""
        self.update_progress(0)


class MetricDisplay(Static):
    """Metric display component."""

    def __init__(self, name: str, value: float, unit: str = "", **kwargs):
        super().__init__(**kwargs)
        self.metric_name = name
        self.metric_value = value
        self.metric_unit = unit

    def compose(self) -> Horizontal:
        """Compose the metric display."""
        with Horizontal(classes="metric-container"):
            self.name_label = Label(f"{self.metric_name}:", classes="metric-name")
            yield self.name_label
            self.value_label = Label(
                f"{self.metric_value:.3f}{self.metric_unit}", classes="metric-value"
            )
            yield self.value_label

    def update_value(self, value: float) -> None:
        """Update metric value."""
        self.metric_value = value
        self.value_label.update(f"{value:.3f}{self.metric_unit}")
        # Update color based on value
        if "latency" in self.metric_name.lower() or "cost" in self.metric_name.lower():
            # Lower is better
            if value < 0.5:
                self.value_label.styles.color = "green"
            elif value < 0.8:
                self.value_label.styles.color = "yellow"
            else:
                self.value_label.styles.color = "red"
        else:
            # Higher is better (like success rate)
            if value > 0.8:
                self.value_label.styles.color = "green"
            elif value > 0.5:
                self.value_label.styles.color = "yellow"
            else:
                self.value_label.styles.color = "red"


class Chart(Static):
    """Simple chart component for displaying metrics over time."""

    def __init__(self, title: str = "Chart", **kwargs):
        super().__init__(**kwargs)
        self.chart_title = title
        self.data_points = []
        self.max_points = 50

    def compose(self) -> Vertical:
        """Compose the chart."""
        with Vertical(classes="chart-container"):
            self.title_label = Label(self.chart_title, classes="chart-title")
            yield self.title_label
            self.chart_area = Static("", id="chart_area", classes="chart-area")
            yield self.chart_area

    def add_data_point(self, value: float, label: str = "") -> None:
        """Add a data point to the chart."""
        self.data_points.append((value, label))
        # Keep only recent points
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        self._render_chart()

    def _render_chart(self) -> None:
        """Render the chart with current data."""
        if not self.data_points:
            self.chart_area.update("No data")
            return
        # Simple ASCII chart
        max_value = max(point[0] for point in self.data_points)
        min_value = min(point[0] for point in self.data_points)
        if max_value == min_value:
            max_value = min_value + 1
        chart_lines = []
        height = 10
        for i in range(height, 0, -1):
            line = ""
            threshold = min_value + (max_value - min_value) * (i / height)
            for value, _ in self.data_points:
                if value >= threshold:
                    line += "█"
                else:
                    line += " "
            chart_lines.append(line)
        chart_text = "\n".join(chart_lines)
        self.chart_area.update(chart_text)

    def clear(self) -> None:
        """Clear all data points."""
        self.data_points.clear()
        self.chart_area.update("No data")


# CSS for base components
BASE_CSS = """
/* Status Bar */
.status-bar {
    height: 1;
    background: $surface;
    color: $text;
    dock: bottom;
    padding: 0 1;
    border-top: solid $border;
    layout: horizontal;
}
#status_message {
    width: 1fr;
    content-align: left middle;
}
#status_stats {
    width: auto;
    content-align: right middle;
    color: $text-muted;
}
/* Progress Bar */
.progress-container {
    height: 3;
    padding: 1;
    background: $surface;
    border: solid $border;
}
.progress-bar {
    height: 1;
    background: $primary;
    color: $text;
    content-align: center middle;
}
.progress-label {
    height: 1;
    color: $text-muted;
    content-align: center middle;
    margin-top: 1;
}
/* Metric Display */
.metric-container {
    height: 1;
    padding: 0 1;
    background: $surface;
    border: solid $border;
    margin: 1 0;
}
.metric-name {
    width: 1fr;
    color: $text-muted;
    content-align: left middle;
}
.metric-value {
    width: auto;
    color: $text;
    content-align: right middle;
    text-style: bold;
}
/* Chart */
.chart-container {
    height: auto;
    padding: 1;
    background: $surface;
    border: solid $border;
    margin: 1 0;
}
.chart-title {
    height: 1;
    color: $text;
    text-style: bold;
    content-align: center middle;
    margin-bottom: 1;
}
.chart-area {
    height: 10;
    color: $accent;
    background: $background;
    border: solid $border;
    font-family: monospace;
    content-align: center middle;
}
"""

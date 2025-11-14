"""
Base UI components for CIE.
"""

from typing import Callable

from textual import events
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label, Static


class BasePanel(Static):
    """Base panel with minimize/maximize functionality."""

    is_minimized: reactive[bool] = reactive(False)
    can_minimize: reactive[bool] = reactive(True)

    def __init__(self, title: str, icon: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.panel_title = title
        self.panel_icon = icon
        self.original_height = None
        self._min_control: PanelHeaderControl | None = None
        self._max_control: PanelHeaderControl | None = None

    def compose(self) -> Horizontal:
        """Compose the panel with title bar and controls."""
        with Horizontal(id=f"{self.id}_header", classes="panel-header"):
            self._min_control = PanelHeaderControl("▁", self.toggle_minimize, f"{self.id}_minimize")
            yield self._min_control
            self._max_control = PanelHeaderControl("▢", self.action_maximize, f"{self.id}_maximize")
            yield self._max_control
            title = self.panel_title
            if self.panel_icon:
                title = f"{self.panel_icon} {title}"
            yield Label(title, id=f"{self.id}_title", classes="panel-title")
        with Vertical(id=f"{self.id}_content", classes="panel-content"):
            yield from self.compose_content()
        yield Label("", id=f"{self.id}_status", classes="panel-status")

    def compose_content(self) -> Vertical:
        """Override this to add panel-specific content."""
        yield Label("Override compose_content() in subclass")

    def watch_is_minimized(self, old_value: bool, new_value: bool) -> None:
        """React to minimize state changes."""
        if new_value:
            # Store original height before minimizing
            if self.original_height is None:
                self.original_height = self.styles.height
            # Minimize - show only header
            self.styles.height = "auto"
            content = self.query_one(f"#{self.id}_content")
            status = self.query_one(f"#{self.id}_status")
            content.display = False
            status.display = False
            # Update minimize button
            if self._min_control:
                self._min_control.update("▣")
        else:
            # Restore original height and show all content
            if self.original_height:
                self.styles.height = self.original_height
            # Show all content
            content = self.query_one(f"#{self.id}_content")
            status = self.query_one(f"#{self.id}_status")
            content.display = True
            status.display = True
            # Update minimize button
            if self._min_control:
                self._min_control.update("▁")


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
        """Update status message."""
        status = self.query_one(f"#{self.id}_status", Label)
        # Add color based on level
        color_map = {"info": "white", "success": "green", "warning": "yellow", "error": "red"}
        color = color_map.get(level, "white")
        status.update(f"[{color}]{message}[/{color}]")


class PanelHeaderControl(Static):
    """Clickable control used in panel headers."""

    def __init__(self, label: str, callback: Callable[[], None], control_id: str):
        super().__init__(label, id=control_id, classes="panel-control")
        self._callback = callback

    def on_click(self, event: events.Click) -> None:  # type: ignore[override]
        event.stop()
        if self._callback:
            self._callback()


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

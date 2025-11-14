"""
Chart and visualization components for metrics display.
"""

from collections import deque
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Label, Static


class SparklineChart(Static):
    """Simple sparkline chart for inline metric display."""

    def __init__(self, max_points: int = 20, height: int = 3, **kwargs):
        super().__init__(**kwargs)
        self.data_points = deque(maxlen=max_points)
        self.chart_height = height

    def add_point(self, value: float) -> None:
        """Add a data point to the sparkline."""
        self.data_points.append(value)
        self.refresh()

    def render_sparkline(self) -> str:
        """Render the sparkline as ASCII art."""
        if not self.data_points:
            return "─" * 20

        # Normalize values
        min_val = min(self.data_points)
        max_val = max(self.data_points)

        if max_val == min_val:
            return "─" * len(self.data_points)

        # Use block characters for smoother visualization
        blocks = " ▁▂▃▄▅▆▇█"

        sparkline = ""
        for value in self.data_points:
            normalized = (value - min_val) / (max_val - min_val)
            index = int(normalized * (len(blocks) - 1))
            sparkline += blocks[index]

        return sparkline

    def render(self) -> str:
        """Render the sparkline."""
        return self.render_sparkline()


class ChartWidget(Static):
    """Base chart widget with title and axes."""

    chart_title: reactive[str] = reactive("Chart")

    def __init__(self, title: str = "Chart", width: int = 40, height: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.chart_title = title
        self.chart_width = width
        self.chart_height = height
        self.data_series: dict[str, list[float]] = {}

    def compose(self) -> ComposeResult:
        """Compose the chart widget."""
        with Vertical(classes="chart-widget"):
            yield Label(self.chart_title, classes="chart-title")
            yield Static("", id="chart_canvas", classes="chart-canvas")
            yield Label("", id="chart_legend", classes="chart-legend")

    def add_series(self, name: str, data: list[float]) -> None:
        """Add or update a data series."""
        self.data_series[name] = data
        self.update_chart()

    def update_chart(self) -> None:
        """Update the chart display."""
        canvas = self.query_one("#chart_canvas", Static)
        legend = self.query_one("#chart_legend", Label)

        if not self.data_series:
            canvas.update("No data")
            return

        # Simple ASCII bar chart
        chart_lines = self.render_chart()
        canvas.update("\n".join(chart_lines))

        # Update legend
        legend_text = " | ".join(
            f"[{self.get_series_color(name)}]● {name}[/]" for name in self.data_series.keys()
        )
        legend.update(legend_text)

    def render_chart(self) -> list[str]:
        """Render the chart as ASCII art."""
        lines = []

        if not self.data_series:
            return ["No data"]

        # Get all values for scaling
        all_values = [v for series in self.data_series.values() for v in series]
        if not all_values:
            return ["No data"]

        min_val = min(all_values)
        max_val = max(all_values)

        if max_val == min_val:
            max_val = min_val + 1

        # Create chart grid
        for row in range(self.chart_height, 0, -1):
            line = ""
            threshold = min_val + (max_val - min_val) * (row / self.chart_height)

            for col in range(self.chart_width):
                char = " "
                for series_name, values in self.data_series.items():
                    if col < len(values):
                        if values[col] >= threshold:
                            char = self.get_series_char(series_name)
                            break
                line += char
            lines.append(line)

        # Add axis
        lines.append("─" * self.chart_width)

        return lines

    def get_series_char(self, series_name: str) -> str:
        """Get the character for a series."""
        chars = "█▓▒░"
        index = list(self.data_series.keys()).index(series_name)
        return chars[index % len(chars)]

    def get_series_color(self, series_name: str) -> str:
        """Get the color for a series."""
        colors = ["cyan", "green", "yellow", "magenta", "blue"]
        index = list(self.data_series.keys()).index(series_name)
        return colors[index % len(colors)]


class MetricsChart(ChartWidget):
    """Specialized chart for displaying metrics over time."""

    def __init__(self, **kwargs):
        super().__init__(title="Metrics History", **kwargs)
        self.metric_history: dict[str, deque] = {}
        self.max_history = 50

    def add_metrics(self, metrics: dict[str, float]) -> None:
        """Add a set of metrics to the history."""
        for metric, value in metrics.items():
            if metric not in self.metric_history:
                self.metric_history[metric] = deque(maxlen=self.max_history)
            self.metric_history[metric].append(value)

        # Update chart with latest data
        for metric, history in self.metric_history.items():
            self.add_series(metric, list(history))

    def render_chart(self) -> list[str]:
        """Render metrics with specialized formatting."""
        lines = super().render_chart()

        # Add metric-specific annotations
        if self.metric_history:
            # Add current values
            current_line = "Current: "
            for metric, history in self.metric_history.items():
                if history:
                    color = self.get_metric_color(metric, history[-1])
                    current_line += f"[{color}]{metric}: {history[-1]:.3f}[/] "
            lines.append(current_line)

        return lines

    def get_metric_color(self, metric: str, value: float) -> str:
        """Get color based on metric type and value."""
        # Metrics where lower is better
        if any(x in metric.lower() for x in ["latency", "cost", "error"]):
            if value < 0.3:
                return "green"
            elif value < 0.7:
                return "yellow"
            else:
                return "red"
        # Metrics where higher is better
        else:
            if value > 0.7:
                return "green"
            elif value > 0.3:
                return "yellow"
            else:
                return "red"


class ParetoChart(Static):
    """Chart for displaying Pareto frontier."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pareto_points: list[tuple[float, float, int]] = []
        self.all_points: list[tuple[float, float, int]] = []

    def compose(self) -> ComposeResult:
        """Compose the Pareto chart."""
        with Vertical(classes="pareto-chart"):
            yield Label("Pareto Frontier", classes="chart-title")
            yield Static("", id="pareto_canvas", classes="chart-canvas")
            yield Label("X: Objective 1 | Y: Objective 2", classes="chart-axes")

    def update_points(
        self,
        all_points: list[tuple[float, float, int]],
        pareto_points: list[tuple[float, float, int]],
    ) -> None:
        """Update the chart with new points."""
        self.all_points = all_points
        self.pareto_points = pareto_points
        self.render_pareto()

    def render_pareto(self) -> None:
        """Render the Pareto frontier."""
        canvas = self.query_one("#pareto_canvas", Static)

        if not self.all_points:
            canvas.update("No data")
            return

        width = 40
        height = 15

        # Get bounds
        x_values = [p[0] for p in self.all_points]
        y_values = [p[1] for p in self.all_points]

        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)

        if x_max == x_min:
            x_max = x_min + 1
        if y_max == y_min:
            y_max = y_min + 1

        # Create grid
        grid = [[" " for _ in range(width)] for _ in range(height)]

        # Plot all points
        for x, y, trial_id in self.all_points:
            col = int((x - x_min) / (x_max - x_min) * (width - 1))
            row = height - 1 - int((y - y_min) / (y_max - y_min) * (height - 1))

            if 0 <= col < width and 0 <= row < height:
                if (x, y, trial_id) in self.pareto_points:
                    grid[row][col] = "●"  # Pareto point
                else:
                    grid[row][col] = "·"  # Regular point

        # Connect Pareto points with line
        if len(self.pareto_points) > 1:
            sorted_pareto = sorted(self.pareto_points, key=lambda p: p[0])
            for i in range(len(sorted_pareto) - 1):
                x1, y1, _ = sorted_pareto[i]
                x2, y2, _ = sorted_pareto[i + 1]

                col1 = int((x1 - x_min) / (x_max - x_min) * (width - 1))
                row1 = height - 1 - int((y1 - y_min) / (y_max - y_min) * (height - 1))
                col2 = int((x2 - x_min) / (x_max - x_min) * (width - 1))
                row2 = height - 1 - int((y2 - y_min) / (y_max - y_min) * (height - 1))

                # Simple line drawing
                steps = max(abs(col2 - col1), abs(row2 - row1))
                if steps > 0:
                    for step in range(steps + 1):
                        t = step / steps
                        col = int(col1 + t * (col2 - col1))
                        row = int(row1 + t * (row2 - row1))

                        if 0 <= col < width and 0 <= row < height:
                            if grid[row][col] == " ":
                                grid[row][col] = "-"

        # Convert grid to string
        chart_text = "\n".join("".join(row) for row in grid)
        canvas.update(f"[cyan]{chart_text}[/cyan]")

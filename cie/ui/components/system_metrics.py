"""
System metrics inspired by W&B beta leet sidebars.
"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Static

from cie.ui.components.charts import SparklineChart


class SystemMetricRow(Static):
    """Displays a metric label with a tiny sparkline."""

    def __init__(self, name: str, unit: str = "", icon: str = "●", **kwargs) -> None:
        super().__init__(classes="system-metric-row", **kwargs)
        self.metric_name = name
        self.unit = unit
        self.icon = icon
        self.sparkline = SparklineChart(max_points=30, height=1)

    def compose(self) -> ComposeResult:
        with Vertical(classes="system-metric-body"):
            self.value_label = Label(
                f"{self.icon} {self.metric_name}: -", classes="system-metric-title"
            )
            yield self.value_label
            yield self.sparkline

    def add_sample(self, value: float) -> None:
        self.sparkline.add_point(value)
        display = f"{value:.3f}{self.unit}".rstrip()
        self.value_label.update(f"{self.icon} {self.metric_name}: {display}")


class SystemMetricsPanel(Static):
    """Collection of system metric rows with easy updates."""

    def __init__(self, metrics: dict[str, dict[str, Any]], **kwargs) -> None:
        super().__init__(classes="system-metrics-panel", **kwargs)
        self.metric_specs = metrics
        self.rows: dict[str, SystemMetricRow] = {}

    def compose(self) -> ComposeResult:
        with Vertical(classes="system-metrics-body"):
            for name, spec in self.metric_specs.items():
                row = SystemMetricRow(
                    name,
                    unit=spec.get("unit", ""),
                    icon=spec.get("icon", "●"),
                )
                self.rows[name] = row
                yield row

    def push_sample(self, values: dict[str, float]) -> None:
        for name, value in values.items():
            row = self.rows.get(name)
            if row is None:
                continue
            row.add_sample(value)

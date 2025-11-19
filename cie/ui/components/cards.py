"""
Metric card components inspired by Dolphie and W&B LEET dashboards.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.reactive import reactive
from textual.widgets import Label, Static


class MetricCard(Static):
    """Displays a single metric with title, value, and delta."""

    value_display: reactive[str] = reactive("-")
    delta_display: reactive[str] = reactive("")
    status: reactive[str] = reactive("info")

    def __init__(
        self,
        title: str,
        *,
        icon: str = "●",
        unit: str = "",
        formatter: Callable[[float], str] | None = None,
        classes: str = "",
    ) -> None:
        super().__init__(classes=f"metric-card {classes}".strip())
        self.title = title
        self.icon = icon
        self.unit = unit
        self.formatter = formatter

    def compose(self) -> ComposeResult:
        with Vertical(classes="metric-card-body"):
            yield Label(f"{self.icon} {self.title}", classes="metric-card-title")
            self.value_label = Label(self.value_display, classes="metric-card-value")
            yield self.value_label
            self.delta_label = Label(self.delta_display, classes="metric-card-delta")
            yield self.delta_label

    def update_value(
        self,
        value: float | str,
        *,
        delta: float | None = None,
        status: str = "info",
        unit: str | None = None,
    ) -> None:
        """Update the card value and optional delta."""
        self.status = status
        unit = unit if unit is not None else self.unit

        if isinstance(value, float) and self.formatter:
            rendered = self.formatter(value)
        elif isinstance(value, float):
            rendered = f"{value:.3f}"
        else:
            rendered = str(value)

        if unit and not rendered.endswith(unit):
            rendered = f"{rendered}{unit}"

        self.value_display = rendered
        color = self._status_color(status)
        self.value_label.update(f"[{color}]{self.value_display}[/{color}]")

        if delta is None:
            self.delta_label.update("")
            return

        arrow = "▲" if delta > 0 else "▼" if delta < 0 else "→"
        delta_color = "green" if delta > 0 else "red" if delta < 0 else "yellow"
        self.delta_display = f"{arrow} {delta:+.3f}{unit}".strip()
        self.delta_label.update(f"[{delta_color}]{self.delta_display}[/{delta_color}]")

    @staticmethod
    def _status_color(status: str) -> str:
        return {
            "good": "green",
            "warn": "yellow",
            "bad": "red",
            "info": "cyan",
        }.get(status, "white")

    def clear(self) -> None:
        """Reset card to its default state."""
        self.value_display = "-"
        self.delta_display = ""
        self.value_label.update("-")
        self.delta_label.update("")


class MetricGrid(Static):
    """Container for displaying multiple MetricCard widgets in a grid."""

    def __init__(self, metrics: dict[str, dict[str, Any]] | None = None, **kwargs) -> None:
        super().__init__(classes="metric-grid", **kwargs)
        self.metric_specs = metrics or {}
        self.cards: dict[str, MetricCard] = {}

    def compose(self) -> ComposeResult:
        with Grid(classes="metric-grid-body"):
            for name, spec in self.metric_specs.items():
                card = MetricCard(
                    name,
                    icon=spec.get("icon", "●"),
                    unit=spec.get("unit", ""),
                    formatter=spec.get("formatter"),
                )
                self.cards[name] = card
                yield card

    def update_metrics(self, metrics: dict[str, dict[str, Any]]) -> None:
        """Update multiple cards at once."""
        for name, payload in metrics.items():
            card = self.cards.get(name)
            if not card:
                continue
            card.update_value(
                payload.get("value", "-"),
                delta=payload.get("delta"),
                status=payload.get("status", "info"),
                unit=payload.get("unit"),
            )

    def clear(self) -> None:
        for card in self.cards.values():
            card.clear()

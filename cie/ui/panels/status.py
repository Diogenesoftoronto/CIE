"""Status panel providing session telemetry akin to W&B system sidebar."""

from __future__ import annotations

from textual.containers import Vertical
from textual.timer import Timer
from textual.widgets import DataTable, Label

from cie.core.backend import CIEBackend, get_backend
from cie.ui.base import BasePanel


class StatusPanel(BasePanel):
    """Status panel showing backend statistics."""

    def __init__(self, backend: CIEBackend | None = None) -> None:
        super().__init__(title="Session Status", icon="[SYS]", id="status_panel", classes="panel")
        self.backend = backend or get_backend()
        self.stats_table: DataTable | None = None
        self.activity_label: Label | None = None
        self._timer: Timer | None = None

    def compose_content(self):
        with Vertical(classes="panel-content status-panel-content"):
            self.stats_table = DataTable(id="status_stats_table", classes="data-table")
            self.stats_table.cursor_type = None
            self.stats_table.add_columns("Metric", "Value")
            yield self.stats_table
            self.activity_label = Label("Ready", id="status_activity", classes="panel-status")
            yield self.activity_label

    def on_mount(self) -> None:
        self.set_subtitle("Backend health & guardrails")
        self.add_toolbar_action("Refresh", self.update_stats, button_id="stat_refresh")
        self.update_stats()
        self._timer = self.set_interval(5.0, self.update_stats)

    def on_unmount(self) -> None:
        if self._timer:
            self._timer.stop()

    def update_stats(self) -> None:
        if not self.stats_table:
            return
        stats = self.backend.get_stats()
        rows = [
            ("Trials", str(stats["trial_count"])),
            ("Pareto", str(stats["pareto_count"])),
            ("Optimizers", str(stats["optimizer_count"])),
            ("Workloads", str(stats["workload_count"])),
            ("Storage", stats["storage_type"].upper()),
            ("Evaluator", stats.get("evaluator", "n/a")),
            ("Recent Trials", str(stats.get("recent_trials", 0))),
            ("Active Policy", "yes" if stats.get("active_policy") else "no"),
        ]
        if stats["best_score"] is not None:
            rows.append(("Best Score", f"{stats['best_score']:.4f}"))
        self.stats_table.clear()
        for name, value in rows:
            self.stats_table.add_row(name, value)

    def update_status(self, message: str, level: str = "info") -> None:
        if not self.activity_label:
            return
        color_map = {"info": "cyan", "success": "green", "warning": "yellow", "error": "red"}
        color = color_map.get(level, "white")
        icon_map = {"info": "•", "success": "✓", "warning": "!", "error": "✗"}
        icon = icon_map.get(level, "•")
        self.activity_label.update(f"{icon} [{color}]{message}[/{color}]")

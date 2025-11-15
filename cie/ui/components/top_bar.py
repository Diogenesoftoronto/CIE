"""
Top bar component modeled after Dolphie's compact header.
"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Label


class CITopBar(Container):
    """Displays session metadata, mode, and keybindings at the top of the TUI."""

    message: reactive[str] = reactive("")
    stats_text: reactive[str] = reactive("")

    def __init__(
        self,
        *,
        version: str,
        mode_label: str = "LIVE",
        help_text: str = "press ? for help",
    ) -> None:
        super().__init__(id="cie_topbar", classes="top-bar")
        self.version = version
        self.mode_label = mode_label
        self.help_text = help_text

    def compose(self) -> ComposeResult:
        self.title_label = Label(
            f"🧪 [b]CIE[/b] v{self.version}",
            id="topbar_title",
            classes="topbar-title",
        )
        self.status_label = Label("", id="topbar_status", classes="topbar-status")
        self.help_label = Label(self.help_text, id="topbar_help", classes="topbar-help")

        yield self.title_label
        yield self.status_label
        yield self.help_label

    def update_message(self, message: str, level: str = "info") -> None:
        """Update contextual message displayed in the center segment."""
        color = {
            "info": "cyan",
            "success": "green",
            "warning": "yellow",
            "error": "red",
        }.get(level, "white")
        self.message = message
        self.status_label.update(f"[{color}]{message}[/{color}]")

    def update_from_stats(
        self,
        stats: dict[str, Any],
        *,
        message: str | None = None,
        level: str = "info",
    ) -> None:
        """Update title (mode) and stats summary."""
        trial_count = stats.get("trial_count", 0)
        pareto = stats.get("pareto_count", 0)
        storage = stats.get("storage_type", "N/A").upper()
        workloads = stats.get("workload_count", 0)
        best_score = stats.get("best_score")

        parts = [
            f"{self.mode_label}",
            f"storage {storage}",
            f"{trial_count} trials",
            f"{workloads} workloads",
            f"{pareto} pareto",
        ]
        if best_score is not None:
            parts.append(f"best {best_score:.4f}")

        stats_text = " • ".join(parts)
        self.title_label.update(
            f"🧪 [b]CIE[/b] v{self.version} · [i]{stats_text}[/i]"
        )
        if message:
            self.update_message(message, level)

    def set_help_text(self, text: str) -> None:
        self.help_text = text
        self.help_label.update(text)

"""
Enhanced status bar component with real-time information display.
"""

from datetime import datetime
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.timer import Timer
from textual.widgets import Label, ProgressBar, Static

from cie.core.backend import get_backend


class StatusIndicator(Static):
    """A single status indicator with icon and value."""

    def __init__(
        self, name: str, icon: str = "●", initial_value: str = "-", classes: str = "", **kwargs
    ):
        super().__init__(classes=f"status-indicator {classes}", **kwargs)
        self.indicator_name = name
        self.icon = icon
        self.value = initial_value

    def compose(self) -> ComposeResult:
        """Compose the indicator."""
        yield Label(
            f"{self.icon} {self.indicator_name}: {self.value}",
            id=f"indicator_{self.indicator_name.lower()}",
        )

    def update_value(self, value: Any, status: str = "normal") -> None:
        """Update the indicator value and status."""
        self.value = str(value)
        label = self.query_one(Label)

        # Update color based on status
        color_map = {
            "normal": "white",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "info": "cyan",
        }
        color = color_map.get(status, "white")
        label.update(f"{self.icon} [{color}]{self.indicator_name}: {self.value}[/{color}]")


class StatusBar(Static):
    """Enhanced status bar with multiple indicators and real-time updates."""

    # Reactive properties
    message: reactive[str] = reactive("Ready")
    level: reactive[str] = reactive("info")

    def __init__(self, **kwargs):
        super().__init__(id="status_bar", classes="status-bar", **kwargs)
        self.backend = get_backend()
        self.update_timer: Timer | None = None
        self.indicators: dict[str, StatusIndicator] = {}

    def compose(self) -> ComposeResult:
        """Compose the status bar."""
        with Horizontal(classes="status-bar-content"):
            # Left side - main message
            yield Label(self.message, id="status_message", classes="status-message")

            # Center - indicators
            with Horizontal(id="status_indicators", classes="status-indicators"):
                self.indicators["trials"] = StatusIndicator("Trials", "📊", "0")
                yield self.indicators["trials"]

                self.indicators["score"] = StatusIndicator("Best", "🏆", "N/A")
                yield self.indicators["score"]

                self.indicators["pareto"] = StatusIndicator("Pareto", "📈", "0")
                yield self.indicators["pareto"]

                self.indicators["backend"] = StatusIndicator("Backend", "💾", "N/A")
                yield self.indicators["backend"]

                self.indicators["eval"] = StatusIndicator("Evaluator", "🔬", "N/A")
                yield self.indicators["eval"]

            # Right side - time and progress
            with Horizontal(id="status_right", classes="status-right"):
                self.progress = ProgressBar(
                    total=100,
                    show_eta=False,
                    show_percentage=True,
                    id="status_progress",
                    classes="status-progress",
                )
                self.progress.display = False
                yield self.progress

                self.time_label = Label(
                    datetime.now().strftime("%H:%M:%S"), id="status_time", classes="status-time"
                )
                yield self.time_label

    def on_mount(self) -> None:
        """Start the update timer when mounted."""
        self.update_timer = self.set_interval(1.0, self.update_time)
        self.update_stats()

    def on_unmount(self) -> None:
        """Stop the update timer when unmounted."""
        if self.update_timer:
            self.update_timer.stop()

    def update_time(self) -> None:
        """Update the time display."""
        self.time_label.update(datetime.now().strftime("%H:%M:%S"))

    @work(thread=True)
    def update_stats(self) -> None:
        """Update statistics from backend."""
        try:
            stats = self.backend.get_stats()

            # Update indicators
            self.indicators["trials"].update_value(
                stats.get("trial_count", 0),
                "success" if stats.get("trial_count", 0) > 0 else "normal",
            )

            best_score = stats.get("best_score")
            if best_score is not None:
                self.indicators["score"].update_value(
                    f"{best_score:.4f}",
                    "success" if best_score > 0.8 else "warning" if best_score > 0.5 else "error",
                )
            else:
                self.indicators["score"].update_value("N/A", "normal")

            self.indicators["pareto"].update_value(
                stats.get("pareto_count", 0),
                "info" if stats.get("pareto_count", 0) > 0 else "normal",
            )

            self.indicators["backend"].update_value(
                stats.get("storage_type", "N/A").upper(), "success"
            )

            self.indicators["eval"].update_value(stats.get("evaluator", "N/A"), "info")

        except Exception as e:
            self.update_message(f"Error updating stats: {e}", "error")

    def update_message(self, message: str, level: str = "info") -> None:
        """Update the main status message."""
        self.message = message
        self.level = level

        # Update message with color
        color_map = {"info": "cyan", "success": "green", "warning": "yellow", "error": "red"}
        color = color_map.get(level, "white")

        icon_map = {"info": "ℹ", "success": "✓", "warning": "⚠", "error": "✗"}
        icon = icon_map.get(level, "●")

        self.query_one("#status_message", Label).update(f"{icon} [{color}]{message}[/{color}]")

    def show_progress(self, current: int = 0, total: int = 100, label: str = "") -> None:
        """Show progress bar with current status."""
        self.progress.total = total
        self.progress.progress = current
        self.progress.display = True

        if label:
            self.update_message(label, "info")

    def hide_progress(self) -> None:
        """Hide the progress bar."""
        self.progress.display = False
        self.progress.progress = 0

    def pulse(self) -> None:
        """Pulse the status bar for attention."""
        self.add_class("pulse")
        self.set_timer(0.5, lambda: self.remove_class("pulse"))

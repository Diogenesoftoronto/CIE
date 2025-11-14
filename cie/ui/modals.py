"""
Modal dialogs for CIE application.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static, ListView, ListItem

from cie.config.settings import get_config
from cie.core.backend import get_backend


class WeightsModal(ModalScreen):
    """Modal for editing objective weights."""

    class Applied(Message):
        """Message sent when weights are applied."""

        def __init__(self):
            super().__init__()

    def __init__(self):
        super().__init__()
        self.backend = get_backend()
        self.config = get_config()
        self.inputs: dict[str, Input] = {}

    def compose(self) -> Vertical:
        """Compose the modal content."""
        with Vertical():
            yield Label("Edit Objective Weights", id="wm_title")
            # Create input fields for each weight
            for metric, weight in self.config.evaluation.metric_weights.items():
                with Horizontal(classes="weight-row"):
                    yield Label(f"{metric}:", classes="weight-label")
                    inp = Input(str(weight), classes="weight-input", id=f"weight_{metric}")
                    self.inputs[metric] = inp
                    yield inp
            yield Label(
                "Tip: weights are coefficients in the scalar objective. "
                "Positive penalizes the metric; negative rewards it. "
                "Enter to apply • Esc to cancel • Use numbers like 0.5 or -1.0",
                id="wm_help",
            )
            with Horizontal(classes="modal-buttons"):
                yield Button("Apply", id="apply_weights", classes="modal-button")
                yield Button("Cancel", id="cancel_weights", classes="modal-button")
                yield Button("Reset to Defaults", id="reset_weights", classes="modal-button")

    def on_mount(self) -> None:
        """Handle modal mount."""
        # Focus first field
        if self.inputs:
            first_input = next(iter(self.inputs.values()))
            self.set_focus(first_input)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        # Validate input format
        if not re.match(r"^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$", event.value):
            event.input.styles.border = ("heavy", "red")
        else:
            event.input.styles.border = ("solid", "white")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "apply_weights":
            self._apply_weights()
        elif event.button.id == "cancel_weights":
            self.dismiss()
        elif event.button.id == "reset_weights":
            self._reset_to_defaults()

    def key_enter(self) -> None:
        """Handle Enter key."""
        self._apply_weights()

    def key_escape(self) -> None:
        """Handle Escape key."""
        self.dismiss()

    def _apply_weights(self) -> None:
        """Apply the new weights."""
        # Validate all inputs
        new_weights = {}
        for metric, inp in self.inputs.items():
            value = inp.value.strip()
            if not re.match(r"^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$", value):
                inp.styles.border = ("heavy", "red")
                return
            new_weights[metric] = float(value)
        # Apply weights
        self.config.evaluation.metric_weights = new_weights
        # Re-score existing trials
        for trial in self.backend.trials:
            trial.score = self.backend.score(trial.metrics)
        # Rebuild Pareto frontier
        self.backend._rebuild_pareto()
        # Dismiss and notify
        self.dismiss()
        self.post_message(self.Applied())

    def _reset_to_defaults(self) -> None:
        """Reset weights to default values."""
        defaults = {
            "latency_p95": 0.001,
            "cost_per_req": 0.5,
            "task_success": -1.0,
            "context_usage": 0.2,
            "tool_error_rate": 0.8,
        }
        for metric, default_value in defaults.items():
            if metric in self.inputs:
                self.inputs[metric].value = str(default_value)
                self.inputs[metric].styles.border = ("solid", "white")


class ConfigModal(ModalScreen):
    """Modal for editing configuration."""

    class Applied(Message):
        """Message sent when configuration is applied."""

        def __init__(self):
            super().__init__()

    def __init__(self):
        super().__init__()
        self.backend = get_backend()
        self.config = get_config()
        self.inputs: dict[str, Any] = {}  # Can be Input or other widgets

    def compose(self) -> Vertical:
        """Compose the modal content."""
        with Vertical():
            yield Label("Edit Configuration", id="cm_title")
            # Model Configuration
            with Vertical(classes="config-section"):
                yield Label("Model Configuration", classes="config-section-title")
                with Horizontal(classes="config-row"):
                    yield Label("Provider:", classes="config-label")
                    provider_input = Input(
                        self.config.model.provider, classes="config-input", id="config_provider"
                    )
                    self.inputs["provider"] = provider_input
                    yield provider_input
                with Horizontal(classes="config-row"):
                    yield Label("Model Name:", classes="config-label")
                    model_input = Input(
                        self.config.model.model_name, classes="config-input", id="config_model_name"
                    )
                    self.inputs["model_name"] = model_input
                    yield model_input
                with Horizontal(classes="config-row"):
                    yield Label("Temperature:", classes="config-label")
                    temp_input = Input(
                        str(self.config.model.temperature),
                        classes="config-input",
                        id="config_temperature",
                    )
                    self.inputs["temperature"] = temp_input
                    yield temp_input
                with Horizontal(classes="config-row"):
                    yield Label("Max Tokens:", classes="config-label")
                    tokens_input = Input(
                        str(self.config.model.max_tokens),
                        classes="config-input",
                        id="config_max_tokens",
                    )
                    self.inputs["max_tokens"] = tokens_input
                    yield tokens_input
            # Storage Configuration
            with Vertical(classes="config-section"):
                yield Label("Storage Configuration", classes="config-section-title")
                with Horizontal(classes="config-row"):
                    yield Label("Backend:", classes="config-label")
                    storage_input = Input(
                        self.config.storage.backend,
                        classes="config-input",
                        id="config_storage_backend",
                    )
                    self.inputs["storage_backend"] = storage_input
                    yield storage_input
                with Horizontal(classes="config-row"):
                    yield Label("Experiments Directory:", classes="config-label")
                    dir_input = Input(
                        self.config.storage.experiments_dir,
                        classes="config-input",
                        id="config_experiments_dir",
                    )
                    self.inputs["experiments_dir"] = dir_input
                    yield dir_input
            # Optimization Configuration
            with Vertical(classes="config-section"):
                yield Label("Optimization Configuration", classes="config-section-title")
                with Horizontal(classes="config-row"):
                    yield Label("Max Iterations:", classes="config-label")
                    iter_input = Input(
                        str(self.config.optimization.max_iterations),
                        classes="config-input",
                        id="config_max_iterations",
                    )
                    self.inputs["max_iterations"] = iter_input
                    yield iter_input
                with Horizontal(classes="config-row"):
                    yield Label("Population Size:", classes="config-label")
                    pop_input = Input(
                        str(self.config.optimization.population_size),
                        classes="config-input",
                        id="config_population_size",
                    )
                    self.inputs["population_size"] = pop_input
                    yield pop_input
            yield Label(
                "Changes will take effect immediately. Some changes may require restart.",
                id="cm_help",
            )
            with Horizontal(classes="modal-buttons"):
                yield Button("Apply", id="apply_config", classes="modal-button")
                yield Button("Cancel", id="cancel_config", classes="modal-button")
                yield Button("Reset", id="reset_config", classes="modal-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "apply_config":
            self._apply_config()
        elif event.button.id == "cancel_config":
            self.dismiss()
        elif event.button.id == "reset_config":
            self._reset_config()

    def key_enter(self) -> None:
        """Handle Enter key."""
        self._apply_config()

    def key_escape(self) -> None:
        """Handle Escape key."""
        self.dismiss()

    def _apply_config(self) -> None:
        """Apply the new configuration."""
        try:
            # Model configuration
            if "provider" in self.inputs:
                self.config.model.provider = self.inputs["provider"].value
            if "model_name" in self.inputs:
                self.config.model.model_name = self.inputs["model_name"].value
            if "temperature" in self.inputs:
                self.config.model.temperature = float(self.inputs["temperature"].value)
            if "max_tokens" in self.inputs:
                self.config.model.max_tokens = int(self.inputs["max_tokens"].value)
            # Storage configuration
            if "storage_backend" in self.inputs:
                self.config.storage.backend = self.inputs["storage_backend"].value
            if "experiments_dir" in self.inputs:
                self.config.storage.experiments_dir = self.inputs["experiments_dir"].value
            # Optimization configuration
            if "max_iterations" in self.inputs:
                self.config.optimization.max_iterations = int(self.inputs["max_iterations"].value)
            if "population_size" in self.inputs:
                self.config.optimization.population_size = int(self.inputs["population_size"].value)
            # Dismiss and notify
            self.dismiss()
            self.post_message(self.Applied())
        except ValueError as e:
            # Show error for invalid input
            self.notify(f"Invalid input: {e}", severity="error")

    def _reset_config(self) -> None:
        """Reset configuration to defaults."""
        # Reset to default values
        defaults = {
            "provider": "openai",
            "model_name": "gpt-4o-mini",
            "temperature": "0.7",
            "max_tokens": "4096",
            "storage_backend": "json",
            "experiments_dir": "~/.cie/experiments",
            "max_iterations": "100",
            "population_size": "20",
        }
        for key, default_value in defaults.items():
            if key in self.inputs:
                self.inputs[key].value = default_value


class MessageModal(ModalScreen[Any]):
    """Generic dialog modal with shared layout."""

    def __init__(
        self,
        title: str,
        message: str,
        *,
        tone: str = "info",
        buttons: Iterable[tuple[str, str, Any]] | None = None,
        detail: str | None = None,
    ):
        super().__init__()
        self.dialog_title = title
        self.dialog_message = message
        self.dialog_detail = detail
        self.tone = tone
        self._buttons = list(buttons or [("dialog_ok", "OK", True)])
        self._button_results = {btn_id: result for btn_id, _, result in self._buttons}

    def compose(self) -> Vertical:
        """Compose dialog content."""
        with Vertical():
            yield Label(
                self.dialog_title,
                classes=f"dialog-title dialog-title--{self.tone}",
            )
            if self.dialog_message:
                yield Label(self.dialog_message, classes="dialog-message")
            if self.dialog_detail:
                yield Label(self.dialog_detail, classes="dialog-detail")
            if self._buttons:
                with Horizontal(classes="modal-buttons"):
                    for btn_id, label, _ in self._buttons:
                        yield Button(label, id=btn_id, classes="modal-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Return the mapped result when a button is pressed."""
        if event.button.id in self._button_results:
            self.dismiss(self._button_results[event.button.id])

    def key_enter(self) -> None:
        """Default Enter handling uses the first button."""
        if self._buttons:
            first_id = self._buttons[0][0]
            self.dismiss(self._button_results.get(first_id))

    def key_escape(self) -> None:
        """Default Escape handling uses the last button."""
        if self._buttons:
            last_id = self._buttons[-1][0]
            self.dismiss(self._button_results.get(last_id))


class ConfirmModal(MessageModal):
    """Modal for confirmation dialogs."""

    def __init__(
        self, title: str, message: str, confirm_text: str = "Confirm", cancel_text: str = "Cancel"
    ):
        buttons = [
            ("confirm_yes", confirm_text, True),
            ("confirm_no", cancel_text, False),
        ]
        super().__init__(title, message, tone="warning", buttons=buttons)


class ErrorModal(MessageModal):
    """Modal for error messages."""

    def __init__(self, title: str, message: str, details: str = ""):
        buttons = [("error_ok", "OK", True)]
        if details:
            buttons.append(("error_copy", "Copy Details", None))
        super().__init__(title, message, tone="error", buttons=buttons, detail=details or None)
        self.details = details

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "error_copy":
            try:
                import pyperclip

                pyperclip.copy(self.details)
                self.notify("Details copied to clipboard")
            except ImportError:
                self.notify("pyperclip not available for clipboard operations", severity="warning")
            return
        super().on_button_pressed(event)


class InfoModal(MessageModal):
    """Modal for informational messages."""

    def __init__(self, title: str, message: str):
        super().__init__(title, message, tone="info", buttons=[("info_ok", "OK", True)])


class ProgressModal(ModalScreen):
    """Modal for showing progress."""

    def __init__(self, title: str, message: str = "", cancellable: bool = False):
        super().__init__()
        self.title = title
        self.message = message
        self.cancellable = cancellable
        self.current = 0
        self.total = 100

    def compose(self) -> Vertical:
        """Compose the modal content."""
        with Vertical():
            yield Label(self.title, id="progress_title")
            if self.message:
                yield Label(self.message, id="progress_message")
            self.progress_bar = Static(
                "░" * 50,  # Empty progress bar
                id="progress_bar",
            )
            yield self.progress_bar
            self.progress_label = Label("0% (0/100)", id="progress_label")
            yield self.progress_label
            if self.cancellable:
                with Horizontal(classes="modal-buttons"):
                    yield Button("Cancel", id="progress_cancel", classes="modal-button")

    def update_progress(
        self, current: int, total: int | None = None, message: str | None = None
    ) -> None:
        """Update progress."""
        if total is not None:
            self.total = total
        self.current = current
        percentage = min(100, max(0, int((current / self.total) * 100)))
        # Update progress bar
        filled_width = int(percentage / 2)  # Scale to bar width
        bar_text = "█" * filled_width + "░" * (50 - filled_width)
        self.progress_bar.update(bar_text)
        # Update label
        self.progress_label.update(f"{percentage}% ({current}/{self.total})")
        # Update message if provided
        if message:
            self.message = message
            message_label = self.query_one("#progress_message", Label)
            message_label.update(message)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "progress_cancel":
            self.dismiss(False)

    def key_escape(self) -> None:
        """Handle Escape key."""
        if self.cancellable:
            self.dismiss(False)

    def complete(self, message: str = "Complete!") -> None:
        """Mark progress as complete."""
        self.update_progress(self.total, message=message)
        # Change button to OK
        if self.cancellable:
            cancel_button = self.query_one("#progress_cancel", Button)
            cancel_button.label = "OK"
            cancel_button.id = "progress_ok"

    def key_enter(self) -> None:
        """Handle Enter key."""
        self.dismiss(True)


class HelpModal(ModalScreen):
    """Modal that displays keyboard help."""

    help_text = """CIE - Optimization & Evaluation

Navigation:
  Tab/Shift+Tab : Move between controls
  Ctrl+R        : Refresh data
  Ctrl+W        : Edit objective weights
  Ctrl+O        : Edit configuration
  Ctrl+T        : Toggle status panel
  F1            : Help (this screen)
  Ctrl+C        : Quit app

Panel Shortcuts:
  Optimizers : O run • W weights
  Evals      : E run eval • B baseline
  Experiments: P pareto • A adopt • N new study
"""

    def compose(self) -> Vertical:
        with Vertical(id="help-modal"):
            yield Label("Keyboard Reference", id="help_title")
            yield Static(self.help_text, classes="help-text")
            with Horizontal(classes="modal-buttons"):
                yield Button("Close", id="help_close", classes="modal-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "help_close":
            self.dismiss()

    def key_escape(self) -> None:
        self.dismiss()

    def key_enter(self) -> None:
        self.dismiss()


class TutorModal(ModalScreen):
    """Guided tips for using the application."""

    def compose(self) -> Vertical:
        with Vertical(id="tutor-modal"):
            yield Label("Quick Tutor", id="tutor_title")
            tips = """1. Start on the Optimizers tab: press O to propose a policy.
2. Switch tabs with H/L or Ctrl+Tab to reach Evaluations.
3. In Evaluations, select a workload (j/k) and press E to run.
4. Jump to Experiments (M or Tab) to inspect trials and adopt.
5. Use Ctrl+Shift+P for the command palette at any time.
"""
            yield Static(tips, classes="help-text")
            with Horizontal(classes="modal-buttons"):
                yield Button("Close", id="tutor_close", classes="modal-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "tutor_close":
            self.dismiss()

    def key_escape(self) -> None:
        self.dismiss()

    def key_enter(self) -> None:
        self.dismiss()


class CommandPaletteModal(ModalScreen):
    """Simple command palette for quick actions."""

    def __init__(self, commands: list[tuple[str, str]]):
        super().__init__()
        self.all_commands = commands
        self.filtered = list(commands)

    def compose(self) -> Vertical:
        with Vertical(id="command-palette"):
            self.input = Input(placeholder="Type a command…", id="command_input")
            yield self.input
            self.list_view = ListView(id="command_list")
            yield self.list_view

    def on_mount(self) -> None:
        self.set_focus(self.input)
        self._refresh_list(self.filtered)

    def _refresh_list(self, commands: list[tuple[str, str]]) -> None:
        self.list_view.clear()
        for label, action in commands:
            item = ListItem(Label(label), name=action)
            self.list_view.append(item)
        if self.list_view.children:
            self.list_view.index = 0

    def filter_commands(self, query: str) -> None:
        self.filtered = [cmd for cmd in self.all_commands if query.lower() in cmd[0].lower()]
        self._refresh_list(self.filtered)

    def on_input_changed(self, event: Input.Changed) -> None:
        self.filter_commands(event.value)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self._invoke_selected()
        event.stop()

    def on_key(self, event) -> None:
        if event.key == "enter":
            self._invoke_selected()
            event.stop()
        elif event.key == "escape":
            self.dismiss()
            event.stop()

    def _invoke_selected(self) -> None:
        index = self.list_view.index
        if 0 <= index < len(self.filtered):
            action = self.filtered[index][1]
            self._execute(action)

    def _execute(self, action: str) -> None:
        handler = getattr(self.app, f"action_{action}", None)
        if callable(handler):
            handler()
        self.dismiss()

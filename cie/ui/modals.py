"""
Modal dialogs for CIE application.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static, ListView, ListItem

from cie.config.settings import get_config
from cie.core.backend import get_backend
from cie.ui.components.context_navigator import ContextNavigator


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
                    inp = self._weight_input(metric, weight)
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
        try:
            float(event.value.strip())
        except ValueError:
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
            try:
                new_weights[metric] = float(value)
            except ValueError:
                inp.styles.border = ("heavy", "red")
                return
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

    def _weight_input(self, metric: str, value: float) -> Input:
        """Create a numeric input tailored for weight editing."""
        return Input(
            str(value),
            placeholder="0.0",
            id=f"weight_{metric}",
            classes="weight-input",
            type="number",
            restrict=r"[-0-9\.]",
            tooltip=f"Weight applied to {metric}",
            compact=True,
        )


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
                    provider_input = self._config_input(
                        "provider",
                        self.config.model.provider,
                        placeholder="openai",
                        tooltip="Model provider identifier",
                    )
                    yield provider_input
                with Horizontal(classes="config-row"):
                    yield Label("Model Name:", classes="config-label")
                    model_input = self._config_input(
                        "model_name",
                        self.config.model.model_name,
                        placeholder="gpt-4o-mini",
                        tooltip="Model name/sku",
                    )
                    yield model_input
                with Horizontal(classes="config-row"):
                    yield Label("Temperature:", classes="config-label")
                    temp_input = self._config_input(
                        "temperature",
                        str(self.config.model.temperature),
                        placeholder="0.7",
                        tooltip="Sampling temperature (0-2)",
                        input_type="number",
                        restrict=r"[-0-9\.]",
                        classes="config-input numeric-input",
                    )
                    yield temp_input
                with Horizontal(classes="config-row"):
                    yield Label("Max Tokens:", classes="config-label")
                    tokens_input = self._config_input(
                        "max_tokens",
                        str(self.config.model.max_tokens),
                        placeholder="4096",
                        tooltip="Maximum completion tokens",
                        input_type="number",
                        restrict=r"[0-9]",
                        classes="config-input numeric-input",
                    )
                    yield tokens_input
            # Storage Configuration
            with Vertical(classes="config-section"):
                yield Label("Storage Configuration", classes="config-section-title")
                with Horizontal(classes="config-row"):
                    yield Label("Backend:", classes="config-label")
                    storage_input = self._config_input(
                        "storage_backend",
                        self.config.storage.backend,
                        placeholder="sqlite/json/memory",
                        tooltip="Storage backend",
                    )
                    yield storage_input
                with Horizontal(classes="config-row"):
                    yield Label("Experiments Directory:", classes="config-label")
                    dir_input = self._config_input(
                        "experiments_dir",
                        self.config.storage.experiments_dir,
                        placeholder="~/.cie/experiments",
                        tooltip="Directory to store experiment data",
                    )
                    yield dir_input
            # Optimization Configuration
            with Vertical(classes="config-section"):
                yield Label("Optimization Configuration", classes="config-section-title")
                with Horizontal(classes="config-row"):
                    yield Label("Max Iterations:", classes="config-label")
                    iter_input = self._config_input(
                        "max_iterations",
                        str(self.config.optimization.max_iterations),
                        placeholder="100",
                        tooltip="Maximum iterations per run",
                        input_type="number",
                        restrict=r"[0-9]",
                        classes="config-input numeric-input",
                    )
                    yield iter_input
                with Horizontal(classes="config-row"):
                    yield Label("Population Size:", classes="config-label")
                    pop_input = self._config_input(
                        "population_size",
                        str(self.config.optimization.population_size),
                        placeholder="20",
                        tooltip="Population size for optimizers",
                        input_type="number",
                        restrict=r"[0-9]",
                        classes="config-input numeric-input",
                    )
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
                self.config.model.provider = self._require_value("provider")
            if "model_name" in self.inputs:
                self.config.model.model_name = self._require_value("model_name")
            if "temperature" in self.inputs:
                self.config.model.temperature = float(self._require_value("temperature"))
            if "max_tokens" in self.inputs:
                self.config.model.max_tokens = int(self._require_value("max_tokens"))
            # Storage configuration
            if "storage_backend" in self.inputs:
                self.config.storage.backend = self._require_value("storage_backend")
            if "experiments_dir" in self.inputs:
                self.config.storage.experiments_dir = self._require_value("experiments_dir")
            # Optimization configuration
            if "max_iterations" in self.inputs:
                self.config.optimization.max_iterations = int(
                    self._require_value("max_iterations")
                )
            if "population_size" in self.inputs:
                self.config.optimization.population_size = int(
                    self._require_value("population_size")
                )
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

    def _config_input(
        self,
        key: str,
        value: str,
        *,
        placeholder: str = "",
        tooltip: str = "",
        input_type: str = "text",
        restrict: str | None = None,
        classes: str = "config-input",
    ) -> Input:
        field = Input(
            value,
            placeholder=placeholder,
            tooltip=tooltip,
            id=f"config_{key}",
            classes=classes,
            type=input_type,
            restrict=restrict,
            compact=True,
        )
        self.inputs[key] = field
        return field

    def _require_value(self, key: str) -> str:
        value = self.inputs[key].value.strip()
        if not value:
            raise ValueError(f"{key.replace('_', ' ').title()} cannot be empty")
        return value


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
  Ctrl+/        : Open context tools
  F1            : Help (this screen)
  Ctrl+C        : Quit app
  Ctrl+Shift+O  : Onboarding tour

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
5. Use the Prompts panel to manage DSPy signatures and templates.
6. Use Ctrl+Shift+P for the command palette at any time.
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


class ContextToolsModal(ModalScreen):
    """Full-screen modal hosting the context navigator."""

    def compose(self) -> Vertical:
        with Vertical(id="context-tools-modal"):
            yield Label("Context Tools", id="context_tools_title")
            yield Label(
                "Capture live context, reorganize, and export snapshots.",
                id="context_tools_subtitle",
            )
            yield ContextNavigator(id="context_navigator")
            yield Label("Press Esc to close • Use header buttons for actions", id="context_tools_hint")

    def key_escape(self) -> None:
        self.dismiss()


class PromptModal(ModalScreen):
    """Modal for creating or editing a prompt."""

    class Applied(Message):
        """Message sent when prompt is saved."""

        def __init__(self):
            super().__init__()

    def __init__(self, prompt_id: str | None = None):
        super().__init__()
        self.backend = get_backend()
        self.prompt_id = prompt_id
        self.inputs: dict[str, Any] = {}

    def compose(self) -> Vertical:
        """Compose the modal content."""
        title = "Edit Prompt" if self.prompt_id else "New Prompt"
        with Vertical(id="prompt-modal"):
            yield Label(title, id="pm_title")
            
            # ID Field
            yield Label("ID (Signature Name):", classes="pm-label")
            self.inputs["id"] = Input(
                self.prompt_id or "",
                placeholder="e.g. dspy.Signature",
                id="pm_id",
                disabled=bool(self.prompt_id),
            )
            yield self.inputs["id"]

            # Description Field
            yield Label("Description:", classes="pm-label")
            self.inputs["description"] = Input(
                placeholder="Brief description of what this prompt does",
                id="pm_description",
            )
            yield self.inputs["description"]

            # Tags Field
            yield Label("Tags (comma separated):", classes="pm-label")
            self.inputs["tags"] = Input(
                placeholder="rag, classification, v1",
                id="pm_tags",
            )
            yield self.inputs["tags"]

            # Content Field
            yield Label("Template / Content:", classes="pm-label")
            from textual.widgets import TextArea
            self.inputs["content"] = TextArea.code_editor(
                "", language="python", id="pm_content"
            )
            yield self.inputs["content"]

            with Horizontal(classes="modal-buttons"):
                yield Button("Save", id="pm_save", classes="modal-button")
                yield Button("Cancel", id="pm_cancel", classes="modal-button")

    def on_mount(self) -> None:
        """Load data if editing."""
        if self.prompt_id:
            # Find prompt
            prompt = next((p for p in self.backend.list_prompts() if p.id == self.prompt_id), None)
            if prompt:
                self.inputs["description"].value = prompt.description
                self.inputs["tags"].value = ", ".join(prompt.tags)
                self.inputs["content"].text = prompt.content
        
        if not self.prompt_id:
            self.set_focus(self.inputs["id"])
        else:
            self.set_focus(self.inputs["content"])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "pm_save":
            self._save_prompt()
        elif event.button.id == "pm_cancel":
            self.dismiss()

    def _save_prompt(self) -> None:
        """Save the prompt."""
        p_id = self.inputs["id"].value.strip()
        content = self.inputs["content"].text
        description = self.inputs["description"].value.strip()
        tags = [t.strip() for t in self.inputs["tags"].value.split(",") if t.strip()]

        if not p_id:
            self.notify("Prompt ID is required", severity="error")
            return
        if not content:
            self.notify("Content is required", severity="error")
            return

        try:
            self.backend.save_prompt(
                id=p_id,
                content=content,
                description=description,
                tags=tags,
            )
            self.dismiss(True)
            self.notify(f"Prompt '{p_id}' saved", severity="info")
        except Exception as e:
            self.notify(f"Error saving prompt: {e}", severity="error")

"""Optimizers panel inspired by Dolphie's modular panels."""

from __future__ import annotations

from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import DataTable

from cie.core.backend import CIEBackend, get_backend
from cie.ui.base import DataTablePanel
from cie.ui.messages import OptimizerRunMessage


class OptimizersPanel(DataTablePanel):
    """Panel for managing optimization algorithms."""

    BINDINGS = [
        Binding("o", "run_once", "Run (O)"),
        Binding("O", "configure", "Configure (O)"),
        Binding("W", "show_weights", "Weights (W)"),
        Binding("j", "cursor_down", "Down (j)", show=False),
        Binding("k", "cursor_up", "Up (k)", show=False),
        Binding("m", "minimize", "Minimize (m)"),
        Binding("M", "maximize", "Maximize (M)"),
    ]

    def __init__(self, backend: CIEBackend | None = None, **kwargs) -> None:
        kwargs.setdefault("id", "optimizers")
        kwargs.setdefault("classes", "panel")
        super().__init__(title="Optimizers", icon="[OPT]", **kwargs)
        self.backend = backend or get_backend()
        self.table: DataTable | None = None

    def compose_content(self):
        with Vertical(classes="panel-content"):
            self.table = self.register_table(
                DataTable(id="optimizers_table", cursor_type="row", classes="data-table")
            )
            self.table.add_columns("Name", "Model", "k-shots", "Best Score", "Artifact", "Trials")
            yield self.table

    def on_mount(self) -> None:
        self.set_subtitle("Generate and inspect policy proposals")
        self.add_toolbar_action("Run", self.action_run_once, button_id="opt_run")
        self.add_toolbar_action("Configure", self.action_configure, button_id="opt_config")
        self.add_toolbar_action("Weights", self.action_show_weights, button_id="opt_weights")
        self.update_status("Select an optimizer and press O to run.")
        self.refresh_table()

    def refresh_table(self) -> None:
        if not self.table:
            return
        self.table.clear()
        optimizers = self.backend.list_optimizers()
        for name, meta in optimizers:
            self.table.add_row(
                name,
                str(meta.get("model", "-")),
                str(meta.get("k_shots", "-")),
                "-" if meta.get("best_score") is None else f"{meta['best_score']:.4f}",
                meta.get("artifact") or "-",
                str(meta.get("trial_count", "0")),
            )
        if self.table.row_count > 0:
            self.table.cursor_coordinate = (0, 0)
            self.selected_row = 0
        else:
            self.clear_selection()

    def action_run_once(self) -> None:
        if self.selected_row is None:
            self.update_status("No optimizer selected", "warning")
            return
        try:
            policy = self.backend.propose_once(self.selected_row)
            self.update_status(f"Proposed policy: {policy.name}", "info")
            self.post_message(OptimizerRunMessage(policy))
        except Exception as exc:
            self.update_status(f"Error: {exc}", "error")

    def action_configure(self) -> None:
        if self.selected_row is None:
            self.update_status("No optimizer selected", "warning")
            return

        from cie.optimizers.dspy_optimizer import DSPyOptimizer

        try:
            optimizer = self.backend.optimizers[self.selected_row]
            if isinstance(optimizer, DSPyOptimizer):
                old_k_shots = optimizer.k_shots
                optimizer.k_shots = 12 if old_k_shots == 8 else 8
                self.update_status(f"{optimizer.name}: k_shots → {optimizer.k_shots}")
                self.refresh_table()
            else:
                self.update_status("Configuration not available for this optimizer", "warning")
        except Exception as exc:
            self.update_status(f"Error: {exc}", "error")

    def action_show_weights(self) -> None:
        app = self.app
        if app and hasattr(app, "action_show_weights"):
            app.action_show_weights()
        else:
            from cie.ui.modals import WeightsModal

            self.mount(WeightsModal())

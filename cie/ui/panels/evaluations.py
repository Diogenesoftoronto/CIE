"""Evaluations panel matching dolphie-like modular structure."""

from __future__ import annotations

from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import DataTable

from cie.core.backend import CIEBackend, get_backend
from cie.core.models import Policy
from cie.ui.base import DataTablePanel
from cie.ui.messages import EvalRunMessage


class EvalsPanel(DataTablePanel):
    """Panel for running evaluations."""

    BINDINGS = [
        Binding("e", "run_eval", "Run Eval (E)"),
        Binding("b", "set_baseline", "Set Baseline (B)"),
        Binding("j", "cursor_down", "Down (j)", show=False),
        Binding("k", "cursor_up", "Up (k)", show=False),
        Binding("m", "minimize", "Minimize (m)"),
        Binding("M", "maximize", "Maximize (M)"),
    ]

    def __init__(self, backend: CIEBackend | None = None, **kwargs) -> None:
        kwargs.setdefault("id", "evals")
        kwargs.setdefault("classes", "panel")
        super().__init__(title="Evaluations", icon="[EVAL]", **kwargs)
        self.backend = backend or get_backend()
        self.current_policy: Policy | None = None
        self.table: DataTable | None = None

    def compose_content(self):
        with Vertical(classes="panel-content"):
            self.table = self.register_table(
                DataTable(id="evals_table", cursor_type="row", classes="data-table")
            )
            self.table.add_columns("Workload", "Items", "Description", "Last Score")
            yield self.table

    def on_mount(self) -> None:
        self.set_subtitle("Select a workload then evaluate the staged policy")
        self.set_badge("Policy needed", "warning")
        self.add_toolbar_action("Run Eval", self.action_run_eval, button_id="eval_run")
        self.add_toolbar_action("Set Baseline", self.action_set_baseline, button_id="eval_baseline")
        self.update_status("No policy selected yet (run an optimizer first)")
        self.refresh_table()

    def refresh_table(self) -> None:
        if not self.table:
            return
        self.table.clear()
        for workload in self.backend.workloads:
            last_score = "-"
            if workload.name in [t.workload for t in self.backend.trials[-10:]]:
                recent_trials = [t for t in self.backend.trials if t.workload == workload.name]
                if recent_trials:
                    last_trial = max(recent_trials, key=lambda t: t.created_at)
                    last_score = f"{last_trial.score:.4f}"
            self.table.add_row(
                workload.name, str(workload.items), workload.description or "-", last_score
            )
        if self.table.row_count > 0:
            self.table.cursor_coordinate = (0, 0)
            self.selected_row = 0
        else:
            self.clear_selection()

    def set_policy(self, policy: Policy) -> None:
        self.current_policy = policy
        self.clear_badge()
        self.update_status(f"Policy staged for eval: {policy.name}", "info")

    def action_run_eval(self) -> None:
        if self.selected_row is None:
            self.update_status("No workload selected", "warning")
            return
        if self.current_policy is None:
            self.update_status("No policy selected (run an optimizer first)", "warning")
            return
        try:
            trial = self.backend.eval_policy(self.current_policy, self.selected_row)
            m = trial.metrics
            status_msg = (
                f"{self.backend.workloads[self.selected_row].name} → "
                f"score={trial.score:.4f} | "
                f"p95={m['latency_p95']:.1f}ms "
                f"cost=${m['cost_per_req']:.5f} "
                f"succ={m['task_success']:.3f} | "
                f"ctx={m['context_usage']:.2f} "
                f"err={m['tool_error_rate']:.3f}"
            )
            self.update_status(status_msg)
            self.refresh_table()
            self.post_message(EvalRunMessage(trial))
        except Exception as exc:
            self.update_status(f"Error: {exc}", "error")

    def action_set_baseline(self) -> None:
        if self.selected_row is None:
            self.update_status("No workload selected", "warning")
            return
        workload = self.backend.workloads[self.selected_row]
        self.update_status(f"Baseline set: {workload.name} (feature not implemented)")

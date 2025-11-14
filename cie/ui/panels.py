"""
UI panels for CIE application.
"""

from textual.binding import Binding
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import DataTable, Label, Static

from cie.core.backend import get_backend
from cie.core.models import Policy
from cie.ui.base import BasePanel, PanelMaximize
from cie.ui.messages import EvalRunMessage, OptimizerRunMessage, PolicyAdoptedMessage


class OptimizersPanel(BasePanel):
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
    selected_index: reactive[int | None] = reactive(None)

    def __init__(self):
        super().__init__(title="Optimizers", icon='[OPT]', id="optimizers", classes="panel")
        self.backend = get_backend()

    def compose_content(self) -> Vertical:
        """Compose the panel content."""
        with Vertical(classes="panel-content"):
            self.table = DataTable(id="optimizers_table", cursor_type="row", classes="data-table")
            self.table.add_columns("Name", "Model", "k-shots", "Best Score", "Artifact", "Trials")
            yield self.table
            self.status = Label(
                "Select an optimizer and press 'O' to run",
                id="optimizers_status",
                classes="panel-status",
            )
            yield self.status

    def on_mount(self) -> None:
        """Handle panel mount."""
        self.refresh_table()

    def refresh_table(self) -> None:
        """Refresh the optimizers table."""
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
            self.selected_index = 0

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle row selection."""
        self.selected_index = event.cursor_row

    def action_run_once(self) -> None:
        """Run the selected optimizer."""
        if self.selected_index is None:
            self.status.update("No optimizer selected")
            return
        try:
            policy = self.backend.propose_once(self.selected_index)
            self.status.update(f"Proposed policy: {policy.name}")
            self.post_message(OptimizerRunMessage(policy))
        except Exception as e:
            self.status.update(f"Error: {str(e)}", "error")

    def action_configure(self) -> None:
        """Configure the selected optimizer."""
        if self.selected_index is None:
            self.status.update("No optimizer selected")
            return
        # Toggle k_shots for DSPy optimizer as an example
        from cie.optimizers.dspy_optimizer import DSPyOptimizer

        try:
            optimizer = self.backend.optimizers[self.selected_index]
            if isinstance(optimizer, DSPyOptimizer):
                old_k_shots = optimizer.k_shots
                optimizer.k_shots = 12 if old_k_shots == 8 else 8
                self.status.update(f"{optimizer.name}: k_shots → {optimizer.k_shots}")
                self.refresh_table()
            else:
                self.status.update("Configuration not available for this optimizer")
        except Exception as e:
            self.status.update(f"Error: {str(e)}", "error")

    def action_show_weights(self) -> None:
        """Show weights modal."""
        app = self.app
        if app and hasattr(app, "action_show_weights"):
            app.action_show_weights()
        else:  # Fallback for safety
            from cie.ui.modals import WeightsModal

            self.mount(WeightsModal())

    def action_minimize(self) -> None:
        """Minimize the panel."""
        self.is_minimized = True

    def action_maximize(self) -> None:
        """Maximize the panel."""
        self.post_message(PanelMaximize(self))

    def action_cursor_down(self) -> None:
        if hasattr(self, 'table'):
            self.table.action_cursor_down()

    def action_cursor_up(self) -> None:
        if hasattr(self, 'table'):
            self.table.action_cursor_up()


class EvalsPanel(BasePanel):
    """Panel for running evaluations."""

    BINDINGS = [
        Binding("e", "run_eval", "Run Eval (E)"),
        Binding("b", "set_baseline", "Set Baseline (B)"),
        Binding("j", "cursor_down", "Down (j)", show=False),
        Binding("k", "cursor_up", "Up (k)", show=False),
        Binding("m", "minimize", "Minimize (m)"),
        Binding("M", "maximize", "Maximize (M)"),
    ]
    selected_index: reactive[int | None] = reactive(None)
    current_policy: Policy | None = None

    def __init__(self):
        super().__init__(title="Evaluations", icon='[EVAL]', id="evals", classes="panel")
        self.backend = get_backend()

    def compose_content(self) -> Vertical:
        """Compose the panel content."""
        with Vertical(classes="panel-content"):
            self.table = DataTable(id="evals_table", cursor_type="row", classes="data-table")
            self.table.add_columns("Workload", "Items", "Description", "Last Score")
            yield self.table
            self.status = Label(
                "No policy selected yet (run an optimizer first)",
                id="evals_status",
                classes="panel-status",
            )
            yield self.status

    def on_mount(self) -> None:
        """Handle panel mount."""
        self.refresh_table()

    def refresh_table(self) -> None:
        """Refresh the evaluations table."""
        self.table.clear()
        for workload in self.backend.workloads:
            last_score = "-"
            if workload.name in [t.workload for t in self.backend.trials[-10:]]:
                # Find most recent trial for this workload
                recent_trials = [t for t in self.backend.trials if t.workload == workload.name]
                if recent_trials:
                    last_trial = max(recent_trials, key=lambda t: t.created_at)
                    last_score = f"{last_trial.score:.4f}"
            self.table.add_row(
                workload.name, str(workload.items), workload.description or "-", last_score
            )
        if self.table.row_count > 0:
            self.table.cursor_coordinate = (0, 0)
            self.selected_index = 0

    def set_policy(self, policy: Policy) -> None:
        """Set the current policy for evaluation."""
        self.current_policy = policy
        self.status.update(f"Policy staged for eval: {policy.name}")

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle row selection."""
        self.selected_index = event.cursor_row

    def action_run_eval(self) -> None:
        """Run evaluation with the current policy."""
        if self.selected_index is None:
            self.status.update("No workload selected")
            return
        if self.current_policy is None:
            self.status.update("No policy selected (run an optimizer first)")
            return
        try:
            trial = self.backend.eval_policy(self.current_policy, self.selected_index)
            # Update status with detailed metrics
            m = trial.metrics
            status_msg = (
                f"{self.backend.workloads[self.selected_index].name} → "
                f"score={trial.score:.4f} | "
                f"p95={m['latency_p95']:.1f}ms "
                f"cost=${m['cost_per_req']:.5f} "
                f"succ={m['task_success']:.3f} | "
                f"ctx={m['context_usage']:.2f} "
                f"err={m['tool_error_rate']:.3f}"
            )
            self.status.update(status_msg)
            # Refresh table to show new score
            self.refresh_table()
            # Notify experiments panel
            self.post_message(EvalRunMessage(trial))
        except Exception as e:
            self.status.update(f"Error: {str(e)}", "error")

    def action_set_baseline(self) -> None:
        """Set baseline for the selected workload."""
        if self.selected_index is None:
            self.status.update("No workload selected")
            return
        workload = self.backend.workloads[self.selected_index]
        self.status.update(f"Baseline set: {workload.name} (feature not implemented)")

    def action_minimize(self) -> None:
        """Minimize the panel."""
        self.is_minimized = True

    def action_maximize(self) -> None:
        """Maximize the panel."""
        self.post_message(PanelMaximize(self))

    def action_cursor_down(self) -> None:
        if hasattr(self, 'table'):
            self.table.action_cursor_down()

    def action_cursor_up(self) -> None:
        if hasattr(self, 'table'):
            self.table.action_cursor_up()


class ExperimentsPanel(BasePanel):
    """Panel for viewing and managing experiments."""

    BINDINGS = [
        Binding("p", "toggle_pareto", "Pareto (P)"),
        Binding("A", "adopt", "Adopt Best (A)"),
        Binding("r", "resume", "Resume (R)"),
        Binding("n", "new_study", "New Study (N)"),
        Binding("k", "kill", "Kill Run (K)"),
        Binding("j", "cursor_down", "Down (j)", show=False),
        Binding("k", "cursor_up", "Up (k)", show=False),
        Binding("m", "minimize", "Minimize (m)"),
        Binding("M", "maximize", "Maximize (M)"),
    ]
    show_pareto: reactive[bool] = reactive(False)
    selected_trial_id: reactive[int | None] = reactive(None)

    def __init__(self):
        super().__init__(title="Experiments", icon='[EXP]', id="experiments", classes="panel")
        self.backend = get_backend()

    def compose_content(self) -> Vertical:
        """Compose the panel content."""
        with Vertical(classes="panel-content"):
            self.trials_table = DataTable(
                id="trials_table", cursor_type="row", classes="data-table"
            )
            self.trials_table.add_columns(
                "Trial",
                "Policy",
                "Score",
                "Latency",
                "Cost",
                "Success",
                "Context",
                "Error",
                "Artifact",
            )
            yield self.trials_table
            self.pareto_table = DataTable(id="pareto_table", cursor_type=None, classes="data-table")
            self.pareto_table.add_columns("Trial", "Latency", "Cost", "Success")
            yield self.pareto_table
            self.status = Label("", id="experiments_status", classes="panel-status")
            yield self.status

    def on_mount(self) -> None:
        """Handle panel mount."""
        self.refresh_tables()

    def refresh_tables(self) -> None:
        """Refresh the experiments tables."""
        # Refresh trials table
        self.trials_table.clear()
        # Show recent trials (limit to avoid performance issues)
        recent_trials = self.backend.trials[-200:]
        for trial in recent_trials:
            m = trial.metrics
            self.trials_table.add_row(
                str(trial.id),
                trial.policy_name,
                f"{trial.score:.4f}",
                f"{m.get('latency_p95', 0):.1f}",
                f"{m.get('cost_per_req', 0):.5f}",
                f"{m.get('task_success', 0):.3f}",
                f"{m.get('context_usage', 0):.2f}",
                f"{m.get('tool_error_rate', 0):.3f}",
                trial.artifact_id or "-",
            )
        if self.trials_table.row_count > 0:
            last_index = self.trials_table.row_count - 1
            self.trials_table.cursor_coordinate = (last_index, 0)
            last_row = self.trials_table.get_row_at(last_index)
            self.selected_trial_id = int(last_row[0])
        # Refresh Pareto table
        self.pareto_table.clear()
        for trial in self.backend.pareto:
            self.pareto_table.add_row(
                str(trial.id),
                f"{trial.metrics.get('latency_p95', 0):.1f}",
                f"{trial.metrics.get('cost_per_req', 0):.5f}",
                f"{trial.metrics.get('task_success', 0):.3f}",
            )
        self.pareto_table.display = self.show_pareto

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle row selection."""
        # Only handle events from the trials table
        if event.control == self.trials_table:
            try:
                row = self.trials_table.get_row(event.row_key)
                self.selected_trial_id = int(row[0])
            except (IndexError, ValueError):
                pass

    def action_toggle_pareto(self) -> None:
        """Toggle Pareto frontier view."""
        self.show_pareto = not self.show_pareto
        self.pareto_table.display = self.show_pareto
        self.status.update(f"Pareto: {'ON' if self.show_pareto else 'OFF'}")
        self.refresh_tables()

    def action_adopt(self) -> None:
        """Adopt the selected trial's policy."""
        if self.selected_trial_id is None:
            self.status.update("No trial selected")
            return
        try:
            success = self.backend.adopt_policy(self.selected_trial_id)
            if success:
                self.status.update(
                    f"Adopted trial #{self.selected_trial_id}. Rollback armed.", "success"
                )
            else:
                self.status.update(
                    f"Refused adoption for trial #{self.selected_trial_id} (guardrails).", "warning"
                )
            # Notify other components
            self.post_message(PolicyAdoptedMessage(self.selected_trial_id, success))
        except Exception as e:
            self.status.update(f"Error: {str(e)}", "error")

    def action_resume(self) -> None:
        """Resume experiment (placeholder)."""
        self.status.update("Resume requested (not implemented)")

    def action_new_study(self) -> None:
        """Start new study (placeholder)."""
        self.status.update("New study initialized (not implemented)")

    def action_kill(self) -> None:
        """Kill active run (placeholder)."""
        self.status.update("Kill signal sent to active run (not implemented)")

    def action_minimize(self) -> None:
        """Minimize the panel."""
        self.is_minimized = True

    def action_maximize(self) -> None:
        """Maximize the panel."""
        self.post_message(PanelMaximize(self))

    def action_cursor_down(self) -> None:
        self.trials_table.action_cursor_down()

    def action_cursor_up(self) -> None:
        self.trials_table.action_cursor_up()


class StatusPanel(Static):
    """Status panel showing backend statistics."""

    def __init__(self):
        super().__init__(id="status_panel", classes="panel")
        self.backend = get_backend()

    def compose(self) -> Vertical:
        """Compose the status panel."""
        with Vertical(classes="panel-content"):
            self.stats_label = Label("Loading statistics...", id="stats_label")
            yield self.stats_label
            self.status_label = Label("Ready", id="status_label")
            yield self.status_label

    def on_mount(self) -> None:
        """Handle panel mount."""
        self.update_stats()

    def update_stats(self) -> None:
        """Update statistics display."""
        stats = self.backend.get_stats()
        stats_text = (
            f"Trials: {stats['trial_count']} | "
            f"Pareto: {stats['pareto_count']} | "
            f"Optimizers: {stats['optimizer_count']} | "
            f"Workloads: {stats['workload_count']} | "
            f"Storage: {stats['storage_type']} | "
            f"Eval: {stats.get('evaluator', 'n/a')}"
        )
        if stats["best_score"] is not None:
            stats_text += f" | Best: {stats['best_score']:.4f}"
        self.stats_label.update(stats_text)

    def update_status(self, message: str, level: str = "info") -> None:
        """Update status message."""
        # Add color based on level
        color_map = {"info": "cyan", "success": "green", "warning": "yellow", "error": "red"}
        icon_map = {"info": "[i]", "success": "[ok]", "warning": "[!]", "error": "[x]"}
        color = color_map.get(level, "white")
        icon = icon_map.get(level, "[ ]")
        self.status_label.update(f"{icon} [{color}]{message}[/{color}]")

"""Experiments panel with LEET-inspired run overview."""

from __future__ import annotations

from collections.abc import Iterable

from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import DataTable, Select
from textual.widgets._data_table import RowDoesNotExist

from cie.core.backend import CIEBackend, get_backend
from cie.core.models import Trial
from cie.ui.base import BasePanel
from cie.ui.components import MetricGrid, MetricsChart, ParetoChart, SystemMetricsPanel
from cie.ui.messages import PolicyAdoptedMessage
from cie.utils.wandb_import import resolve_wandb_run_path


class ExperimentsPanel(BasePanel):
    """Panel for viewing and managing experiments."""

    BINDINGS = [
        Binding("p", "toggle_pareto", "Pareto (P)"),
        Binding("A", "adopt", "Adopt Best (A)"),
        Binding("r", "resume", "Resume (R)"),
        Binding("n", "new_study", "New Study (N)"),
        Binding("K", "kill", "Kill Run (K)"),
        Binding("S", "sync_wandb", "Sync W&B (S)"),
        Binding("j", "cursor_down", "Down (j)", show=False),
        Binding("k", "cursor_up", "Up (k)", show=False),
        Binding("m", "minimize", "Minimize (m)"),
        Binding("M", "maximize", "Maximize (M)"),
    ]

    show_pareto: reactive[bool] = reactive(False)
    selected_trial_id: reactive[int | None] = reactive(None)

    def __init__(self, backend: CIEBackend | None = None, **kwargs) -> None:
        kwargs.setdefault("id", "experiments")
        kwargs.setdefault("classes", "panel")
        super().__init__(title="Experiments", icon="[EXP]", **kwargs)
        self.backend = backend or get_backend()
        self.trials_table: DataTable | None = None
        self.pareto_table: DataTable | None = None
        self.workload_filter: Select[str] | None = None
        self.active_filter: str = "all"
        self.metrics_chart: MetricsChart | None = None
        self.pareto_chart: ParetoChart | None = None
        self.metric_grid = MetricGrid(
            {
                "Score": {"icon": "🏆"},
                "Success": {"icon": "✅"},
                "Latency": {"icon": "⏱", "unit": "ms", "formatter": lambda v: f"{v:.0f}"},
                "Cost": {"icon": "💰", "unit": "$", "formatter": lambda v: f"{v:.5f}"},
            }
        )
        self.system_metrics = SystemMetricsPanel(
            {
                "Latency p95": {"icon": "⏱", "unit": "ms"},
                "Cost / req": {"icon": "💰", "unit": "$"},
                "Success": {"icon": "✅"},
            }
        )

    def compose_content(self):
        with Vertical(classes="panel-content experiments-panel"):
            with Horizontal(classes="experiments-body"):
                with Vertical(classes="trials-column"):
                    self.workload_filter = Select(
                        prompt="Filter workloads",
                        id="workload_filter",
                        allow_blank=False,
                        options=[("All workloads", "all")],
                    )
                    yield self.workload_filter
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
                with Vertical(classes="insights-column"):
                    yield self.metric_grid
                    self.metrics_chart = MetricsChart(id="metrics_chart", width=36, height=10)
                    yield self.metrics_chart
                    yield self.system_metrics
                    self.pareto_chart = ParetoChart(id="pareto_chart")
                    yield self.pareto_chart
                    self.pareto_table = DataTable(
                        id="pareto_table", cursor_type=None, classes="data-table"
                    )
                    self.pareto_table.add_columns("Trial", "Latency", "Cost", "Success")
                    yield self.pareto_table

    def on_mount(self) -> None:
        self.set_subtitle("Review trials, Pareto frontier, and adoption status")
        self.add_toolbar_action("Pareto", self.action_toggle_pareto, button_id="exp_pareto")
        self.add_toolbar_action("Adopt Best", self.action_adopt, button_id="exp_adopt")
        self.add_toolbar_action("New Study", self.action_new_study, button_id="exp_new")
        self.add_toolbar_action(
            "Sync W&B",
            self.action_sync_wandb,
            button_id="exp_wandb",
            tooltip="Import wandb/latest-run metrics",
        )
        self._populate_workload_filter()
        self.refresh_tables()

    def _populate_workload_filter(self) -> None:
        if not self.workload_filter:
            return
        options = [("All workloads", "all")]
        options.extend((w.name, w.name) for w in self.backend.workloads)
        self.workload_filter.set_options(options)
        self.workload_filter.value = "all"

    def on_select_changed(self, event: Select.Changed) -> None:
        if self.workload_filter and event.select is self.workload_filter:
            self.active_filter = event.value or "all"
            self.refresh_tables()

    def refresh_tables(self) -> None:
        if not self.trials_table:
            return
        recent_trials = self.backend.trials[-200:]
        if self.active_filter != "all":
            recent_trials = [t for t in recent_trials if t.workload == self.active_filter]

        self.trials_table.clear()
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
            try:
                self.selected_trial_id = int(last_row[0])
            except (IndexError, ValueError):
                self.selected_trial_id = None
        else:
            self.selected_trial_id = None

        self._refresh_metric_views(recent_trials)
        self._refresh_pareto()

    def _refresh_metric_views(self, trials: Iterable[Trial]) -> None:
        trials = list(trials)
        if self.metrics_chart:
            self.metrics_chart.metric_history.clear()
            recent_for_chart = trials[-self.metrics_chart.max_history :]
            for trial in recent_for_chart:
                metrics = {
                    "Score": trial.score,
                    "Success": trial.metrics.get("task_success", 0.0),
                    "Latency (scaled)": min(trial.metrics.get("latency_p95", 0.0) / 5000.0, 1.5),
                    "Cost (scaled)": min(trial.metrics.get("cost_per_req", 0.0) * 600.0, 1.5),
                }
                self.metrics_chart.add_metrics(metrics)

        if self.system_metrics and trials:
            latest = trials[-1]
            values = {
                "Latency p95": latest.metrics.get("latency_p95", 0.0),
                "Cost / req": latest.metrics.get("cost_per_req", 0.0),
                "Success": latest.metrics.get("task_success", 0.0),
            }
            self.system_metrics.push_sample(values)

        last = trials[-1] if trials else None
        prev = trials[-2] if len(trials) > 1 else None
        self._update_run_overview(last, prev)

    def _refresh_pareto(self) -> None:
        if self.pareto_chart:
            all_points = [
                (
                    trial.metrics.get("latency_p95", 0.0),
                    trial.metrics.get("task_success", 0.0),
                    trial.id,
                )
                for trial in self.backend.trials
            ]
            pareto_points = [
                (
                    trial.metrics.get("latency_p95", 0.0),
                    trial.metrics.get("task_success", 0.0),
                    trial.id,
                )
                for trial in self.backend.pareto
            ]
            self.pareto_chart.update_points(all_points, pareto_points)

        if self.pareto_table:
            self.pareto_table.clear()
            for trial in self.backend.pareto:
                self.pareto_table.add_row(
                    str(trial.id),
                    f"{trial.metrics.get('latency_p95', 0):.1f}",
                    f"{trial.metrics.get('cost_per_req', 0):.5f}",
                    f"{trial.metrics.get('task_success', 0):.3f}",
                )
            self.pareto_table.display = self.show_pareto
        if self.pareto_chart:
            self.pareto_chart.display = True

    def _update_run_overview(self, trial: Trial | None, prev: Trial | None) -> None:
        if not trial:
            self.metric_grid.clear()
            return
        prev_metrics = prev.metrics if prev else {}
        data = {
            "Score": {
                "value": trial.score,
                "delta": (trial.score - prev.score) if prev else None,
                "status": self._status_for_score(trial.score),
            },
            "Success": {
                "value": trial.metrics.get("task_success", 0.0),
                "delta": (
                    trial.metrics.get("task_success", 0.0)
                    - prev_metrics.get("task_success", 0.0)
                    if prev
                    else None
                ),
                "status": self._status_for_success(trial.metrics.get("task_success", 0.0)),
            },
            "Latency": {
                "value": trial.metrics.get("latency_p95", 0.0),
                "delta": (
                    trial.metrics.get("latency_p95", 0.0)
                    - prev_metrics.get("latency_p95", 0.0)
                    if prev
                    else None
                ),
                "status": self._status_for_latency(trial.metrics.get("latency_p95", 0.0)),
                "unit": "ms",
            },
            "Cost": {
                "value": trial.metrics.get("cost_per_req", 0.0),
                "delta": (
                    trial.metrics.get("cost_per_req", 0.0)
                    - prev_metrics.get("cost_per_req", 0.0)
                    if prev
                    else None
                ),
                "status": self._status_for_cost(trial.metrics.get("cost_per_req", 0.0)),
                "unit": "$",
            },
        }
        self.metric_grid.update_metrics(data)

    @staticmethod
    def _status_for_score(score: float) -> str:
        if score >= 0.8:
            return "good"
        if score >= 0.5:
            return "warn"
        return "bad"

    @staticmethod
    def _status_for_success(success: float) -> str:
        if success >= 0.8:
            return "good"
        if success >= 0.6:
            return "warn"
        return "bad"

    @staticmethod
    def _status_for_latency(latency: float) -> str:
        if latency <= 1500:
            return "good"
        if latency <= 3000:
            return "warn"
        return "bad"

    @staticmethod
    def _status_for_cost(cost: float) -> str:
        if cost <= 0.01:
            return "good"
        if cost <= 0.05:
            return "warn"
        return "bad"

    def action_toggle_pareto(self) -> None:
        self.show_pareto = not self.show_pareto
        if self.pareto_table:
            self.pareto_table.display = self.show_pareto
        state = "ON" if self.show_pareto else "OFF"
        self.update_status(f"Pareto: {state}")

    def action_adopt(self) -> None:
        if self.selected_trial_id is None:
            self.update_status("No trial selected", "warning")
            return
        try:
            success = self.backend.adopt_policy(self.selected_trial_id)
            if success:
                self.update_status(
                    f"Adopted trial #{self.selected_trial_id}. Rollback armed.", "success"
                )
            else:
                self.update_status(
                    f"Refused adoption for trial #{self.selected_trial_id} (guardrails).",
                    "warning",
                )
            self.post_message(PolicyAdoptedMessage(self.selected_trial_id, success))
        except Exception as exc:
            self.update_status(f"Error: {exc}", "error")

    def action_resume(self) -> None:
        self.update_status("Resume requested (not implemented)")

    def action_new_study(self) -> None:
        self.update_status("New study initialized (not implemented)")

    def action_kill(self) -> None:
        self.update_status("Kill signal sent to active run (not implemented)")

    def action_sync_wandb(self) -> None:
        """Import trials from the latest W&B run directory."""
        try:
            run_path = resolve_wandb_run_path()
        except FileNotFoundError as exc:
            self.update_status(str(exc), "error")
            return

        imported = self.backend.ingest_wandb_run(run_path)
        if not imported:
            self.update_status("No new W&B metrics found to ingest", "warning")
            return

        self.refresh_tables()
        message = f"Ingested {len(imported)} W&B steps from {run_path.name}"
        self.update_status(message, "success")

        app = self.app
        if app and getattr(app, "status_panel", None):
            app.status_panel.update_stats()
        if app and getattr(app, "status_bar", None):
            app.status_bar.update_message(message, "info")
            app.status_bar.update_stats()
        if app and hasattr(app, "_update_top_bar"):
            app._update_top_bar(message, "info")

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.control is self.trials_table:
            try:
                row = self.trials_table.get_row(event.row_key)
                self.selected_trial_id = int(row[0])
            except (IndexError, ValueError):
                self.selected_trial_id = None
            except RowDoesNotExist:
                return

    def action_cursor_down(self) -> None:
        if self.trials_table:
            self.trials_table.action_cursor_down()

    def action_cursor_up(self) -> None:
        if self.trials_table:
            self.trials_table.action_cursor_up()

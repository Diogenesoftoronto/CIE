# cie_tui.py
# Textual panels + weights modal + integration hooks
# pip install "textual>=0.47"
from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Tuple

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import DataTable, Footer, Header, Input, Label, Static
from textual.screen import ModalScreen as Modal

# =========================
# Core domain contracts
# =========================


@dataclass
class Policy:
    name: str
    params: Dict[str, Any]
    actions: List[str]


@dataclass
class Trial:
    id: int
    policy_name: str
    metrics: Dict[str, float]
    score: float
    artifact_id: Optional[str] = None
    notes: str = ""


class Optimizer(Protocol):
    name: str

    def propose(self, state: Dict[str, Any]) -> Policy: ...
    def observe(self, policy: Policy, metrics: Dict[str, float]) -> None: ...


class Evaluator(Protocol):
    name: str

    def run(self, policy: Policy, workload: str) -> Dict[str, float]: ...


# =========================
# Hook adapters (swap these)
# =========================


class MockDspyOptimizer:
    """Replace with Real DSPy optimizer to compile and return an artifact-backed Policy."""

    name = "DSPy:BootstrapFewShot"

    def __init__(self, k_shots: int = 8, model="gpt-4.1-mini"):
        self.k_shots = k_shots
        self.model = model
        self.best_score: Optional[float] = None
        self.best_artifact: Optional[str] = None

    def propose(self, state: Dict[str, Any]) -> Policy:
        ks = self.k_shots
        art = f"art-{int(time.time())}-{ks}"
        return Policy(
            name=self.name,
            params={"artifact": art, "k_shots": ks, "model": self.model},
            actions=[f"dspy.use(artifact='{art}')"],
        )

    def observe(self, policy: Policy, metrics: Dict[str, float]) -> None:
        # When wired: update best based on evaluation score
        pass


class MockHillClimb:
    name = "HillClimb"

    def propose(self, state: Dict[str, Any]) -> Policy:
        pr = random.choice([0.0, 0.2, 0.4, 0.6])
        bs = random.choice([2, 4, 8, 12, 16])
        return Policy(
            name=self.name,
            params={"prune_ratio": pr, "batch_size": bs},
            actions=[f"context.prune(ratio={pr})", f"batch.set_size({bs})"],
        )

    def observe(self, policy: Policy, metrics: Dict[str, float]) -> None:
        pass


class MockBandit:
    name = "TwoArmBandit"

    def propose(self, state: Dict[str, Any]) -> Policy:
        arm = random.choice(["A", "B"])
        return Policy(
            name=self.name, params={"arm": arm}, actions=[f"dispatch.arm('{arm}')"]
        )

    def observe(self, policy: Policy, metrics: Dict[str, float]) -> None:
        pass


class MockEvaluator:
    """Replace with real Micro/Macro evaluators. Returns metrics for scoring."""

    name = "MockEvaluator"

    def run(self, policy: Policy, workload: str) -> Dict[str, float]:
        base_latency = random.uniform(250, 700)
        base_cost = random.uniform(0.001, 0.01)
        base_success = random.uniform(0.7, 0.98)

        if "prune_ratio" in policy.params:
            pr = policy.params["prune_ratio"]
            base_latency *= 1.0 - 0.1 * pr
            base_success -= 0.05 * pr
        if "k_shots" in policy.params:
            ks = policy.params["k_shots"]
            base_success += min(0.02 * (ks / 4), 0.06)
            base_cost += 0.0003 * (ks / 4)

        return {
            "latency_p95": round(max(120.0, base_latency), 2),
            "cost_per_req": round(max(0.0005, base_cost), 5),
            "task_success": round(min(0.995, max(0.0, base_success)), 3),
            "context_usage": round(random.uniform(0.45, 0.92), 2),
            "tool_error_rate": round(random.uniform(0.0, 0.05), 3),
        }


# =========================
# Backend state + scoring
# =========================


class CIEBackend:
    def __init__(self):
        # Objective weights: positive -> penalize; negative -> reward
        self.objective_weights: Dict[str, float] = {
            "latency_p95": 0.001,
            "cost_per_req": 0.5,
            "task_success": -1.0,
            "context_usage": 0.2,
            "tool_error_rate": 0.8,
        }
        # Registered optimizers (swap mocks for real)
        self.optimizers: List[Optimizer] = [
            MockDspyOptimizer(k_shots=8, model="gpt-4.1-mini"),
            MockHillClimb(),
            MockBandit(),
        ]
        self.optimizer_meta: List[Dict[str, Any]] = [
            {"best_score": None, "artifact_id": None} for _ in self.optimizers
        ]
        # Workloads
        self.workloads = [
            {"name": "MicroEval:basic", "items": 50, "last_score": None},
            {"name": "MacroEval:rag-xl", "items": 10, "last_score": None},
            {"name": "SyntheticLoad:cpu80", "items": 1, "last_score": None},
        ]
        # Evaluator (swap for real)
        self.evaluator: Evaluator = MockEvaluator()

        self.trials: List[Trial] = []
        self._trial_id = 0
        self.pareto: List[Trial] = []
        self.active_policy: Optional[Policy] = None

    # ---- Objective scoring (edit here to change the scalarization) ----
    def score(self, metrics: Dict[str, float]) -> float:
        w = self.objective_weights
        # Missing metrics default to zero to stay robust if a runner omits some
        return sum(w.get(k, 0.0) * float(metrics.get(k, 0.0)) for k in w.keys())

    # ---- Pareto maintenance (3D: latency, cost, 1-success) ----
    @staticmethod
    def _dominates(a: Trial, b: Trial) -> bool:
        la, ca, qa = (
            a.metrics["latency_p95"],
            a.metrics["cost_per_req"],
            1 - a.metrics["task_success"],
        )
        lb, cb, qb = (
            b.metrics["latency_p95"],
            b.metrics["cost_per_req"],
            1 - b.metrics["task_success"],
        )
        return (la <= lb and ca <= cb and qa <= qb) and (la < lb or ca < cb or qa < qb)

    def _rebuild_pareto(self) -> None:
        pts: List[Trial] = []
        for t in self.trials:
            dominated = False
            for u in self.trials:
                if t is not u and self._dominates(u, t):
                    dominated = True
                    break
            if not dominated:
                pts.append(t)
        # Deduplicate by id & sort by latency
        seen = set()
        dedup = []
        for t in sorted(pts, key=lambda x: x.metrics["latency_p95"]):
            if t.id not in seen:
                seen.add(t.id)
                dedup.append(t)
        self.pareto = dedup

    # ---- Public operations used by UI ----
    def list_optimizers(self) -> List[Tuple[str, Dict[str, Any]]]:
        out = []
        for opt, meta in zip(self.optimizers, self.optimizer_meta):
            row = {"best_score": meta["best_score"], "artifact": meta["artifact_id"]}
            # attach common metadata if present
            if isinstance(opt, MockDspyOptimizer):
                row |= {"model": opt.model, "k_shots": opt.k_shots}
            out.append((opt.name, row))
        return out

    def propose_once(self, index: int) -> Policy:
        opt = self.optimizers[index]
        # State can carry live system stats if needed
        return opt.propose(state={})

    def eval_policy(self, policy: Policy, workload_index: int) -> Trial:
        workload = self.workloads[workload_index]["name"]
        metrics = self.evaluator.run(policy, workload)
        score = round(self.score(metrics), 6)
        self._trial_id += 1
        trial = Trial(
            id=self._trial_id,
            policy_name=policy.name,
            metrics=metrics,
            score=score,
            artifact_id=policy.params.get("artifact"),
        )
        self.trials.append(trial)
        # Update workload last score
        self.workloads[workload_index]["last_score"] = score
        # Update optimizer meta (best score)
        name_to_idx = {opt.name: i for i, opt in enumerate(self.optimizers)}
        if policy.name in name_to_idx:
            oi = name_to_idx[policy.name]
            best = self.optimizer_meta[oi]["best_score"]
            if best is None or score < best:
                self.optimizer_meta[oi]["best_score"] = score
                self.optimizer_meta[oi]["artifact_id"] = policy.params.get("artifact")
        # Pareto
        self._rebuild_pareto()
        # Notify optimizer
        self.optimizers[name_to_idx.get(policy.name, 0)].observe(policy, metrics)
        return trial

    def adopt_policy(self, trial_id: int) -> bool:
        t = next((x for x in self.trials if x.id == trial_id), None)
        if not t:
            return False
        # Guardrails example
        if t.metrics.get("tool_error_rate", 0.0) > 0.03:
            return False
        self.active_policy = Policy(
            name=f"{t.policy_name}@adopted",
            params={"adopted_from_trial": t.id, "artifact": t.artifact_id},
            actions=["apply.diff(...)", "enable.cache(...)", "limit.tools(5)"],
        )
        return True


BACKEND = CIEBackend()

# =========================
# Weights Modal
# =========================


class WeightsModal(Modal):
    """Tiny modal to edit objective weights in BACKEND.objective_weights."""

    CSS = """
    WeightsModal {
        width: 64;
        height: auto;
        border: heavy $accent;
        padding: 1;
        background: $panel;
    }
    #wm_title { content-align: center middle; }
    .row { height: 3; }
    .label { width: 28; }
    .input { width: 20; }
    #wm_help { height: auto; color: $text-muted; }
    """

    class Applied(Message):
        def __init__(self):
            super().__init__()

    def __init__(self):
        super().__init__()
        self.inputs: Dict[str, Input] = {}

    def compose(self) -> ComposeResult:
        yield Label("Objective Weights", id="wm_title")
        for k in BACKEND.objective_weights.keys():
            with Horizontal(classes="row"):
                yield Label(f"{k:>16}:", classes="label")
                inp = Input(str(BACKEND.objective_weights[k]), classes="input")
                self.inputs[k] = inp
                yield inp
        yield Label(
            "Tip: weights are coefficients in the scalar objective. "
            "Positive penalizes the metric; negative rewards it. "
            "Enter to apply • Esc to cancel • Use numbers like 0.5 or -1.0",
            id="wm_help",
        )

    def on_mount(self) -> None:
        # Focus first field
        first = next(iter(self.inputs.values()))
        self.set_focus(first)

    def key_enter(self) -> None:
        # Validate & apply
        new_weights = {}
        for k, inp in self.inputs.items():
            txt = inp.value.strip()
            if not re.match(r"^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$", txt):
                inp.styles.border = ("heavy", "red")
                return
            new_weights[k] = float(txt)
        BACKEND.objective_weights = new_weights
        BACKEND._rebuild_pareto()  # since scalarization preference changed
        self.dismiss()
        self.post_message(self.Applied())

    def key_escape(self) -> None:
        self.dismiss()


# =========================
# Panels (UI)
# =========================


class OptimizersPanel(Static):
    BINDINGS = [
        Binding("o", "run_once", "Run (o)"),
        Binding("O", "configure", "Configure (O)"),
        Binding("W", "weights", "Weights (W)"),
    ]
    selected_index: reactive[int | None] = reactive(None)

    class OptimizerRun(Message):
        def __init__(self, policy: Policy) -> None:
            self.policy = policy
            super().__init__()

    class OpenWeights(Message):
        pass

    def compose(self) -> ComposeResult:
        yield Label("Optimizers", id="opti_title")
        self.table = DataTable(id="opti_table", cursor_type="row")
        self.table.add_columns("Name", "Model", "k-shots", "Best Score", "Artifact")
        yield self.table
        self.status = Label("", id="opti_status")
        yield self.status

    def on_mount(self) -> None:
        self.refresh_table()

    def refresh_table(self) -> None:
        self.table.clear()
        for name, meta in BACKEND.list_optimizers():
            self.table.add_row(
                name,
                str(meta.get("model", "-")),
                str(meta.get("k_shots", "-")),
                "-" if meta.get("best_score") is None else f"{meta['best_score']:.4f}",
                meta.get("artifact") or "-",
            )
        if self.table.row_count:
            self.table.cursor_coordinate = (0, 0)
            self.selected_index = 0

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self.selected_index = event.cursor_row

    def action_run_once(self) -> None:
        if self.selected_index is None:
            return
        policy = BACKEND.propose_once(self.selected_index)
        self.status.update(f"Proposed policy: {policy.name} {policy.params}")
        self.post_message(self.OptimizerRun(policy))

    def action_configure(self) -> None:
        if self.selected_index is None:
            return
        # Example: toggle k_shots for DSPy mock
        opt = BACKEND.optimizers[self.selected_index]
        if isinstance(opt, MockDspyOptimizer):
            opt.k_shots = 12 if opt.k_shots == 8 else 8
            self.status.update(f"{opt.name}: k_shots → {opt.k_shots}")
            self.refresh_table()

    def action_weights(self) -> None:
        self.post_message(self.OpenWeights())


class EvalsPanel(Static):
    BINDINGS = [
        Binding("e", "run_eval", "Run Eval (e)"),
        Binding("b", "set_baseline", "Set Baseline (b)"),
    ]
    selected_index: reactive[int | None] = reactive(None)
    current_policy: Optional[Policy] = None

    class EvalRun(Message):
        def __init__(self, trial: Trial) -> None:
            self.trial = trial
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Label("Evals", id="evals_title")
        self.table = DataTable(id="evals_table", cursor_type="row")
        self.table.add_columns("Workload", "Items", "Last Score")
        yield self.table
        self.status = Label(
            "No policy selected yet (press 'o' in Optimizers, then 'e' here).",
            id="evals_status",
        )
        yield self.status

    def on_mount(self) -> None:
        self.refresh_table()

    def refresh_table(self) -> None:
        self.table.clear()
        for w in BACKEND.workloads:
            last = "-" if w["last_score"] is None else f"{w['last_score']:.4f}"
            self.table.add_row(w["name"], str(w["items"]), last)
        if self.table.row_count:
            self.table.cursor_coordinate = (0, 0)
            self.selected_index = 0

    def set_policy(self, policy: Policy) -> None:
        self.current_policy = policy
        self.status.update(f"Policy staged for eval: {policy.name}")

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self.selected_index = event.cursor_row

    def action_run_eval(self) -> None:
        if self.selected_index is None or self.current_policy is None:
            return
        trial = BACKEND.eval_policy(self.current_policy, self.selected_index)
        m = trial.metrics
        self.status.update(
            f"{BACKEND.workloads[self.selected_index]['name']} → score={trial.score:.4f} "
            f"| p95={m['latency_p95']}ms cost=${m['cost_per_req']} succ={m['task_success']} "
            f"| ctx={m['context_usage']} err={m['tool_error_rate']}"
        )
        self.refresh_table()
        self.post_message(self.EvalRun(trial))

    def action_set_baseline(self) -> None:
        if self.selected_index is None:
            return
        w = BACKEND.workloads[self.selected_index]
        self.status.update(f"Baseline set: {w['name']} (UI stub)")


class ExperimentsPanel(Static):
    BINDINGS = [
        Binding("p", "toggle_pareto", "Pareto (p)"),
        Binding("A", "adopt", "Adopt Best (A)"),
        Binding("r", "resume", "Resume (r)"),
        Binding("n", "new_study", "New Study (n)"),
        Binding("k", "kill", "Kill Run (k)"),
    ]
    show_pareto: reactive[bool] = reactive(False)
    selected_trial_id: reactive[int | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Label("Experiments", id="exp_title")
        self.trials_table = DataTable(id="trials_table", cursor_type="row")
        self.trials_table.add_columns(
            "Trial",
            "Policy",
            "Score",
            "lat_p95",
            "cost",
            "success",
            "ctx",
            "err",
            "artifact",
        )
        yield self.trials_table
        self.pareto_table = DataTable(id="pareto_table", cursor_type=None)
        self.pareto_table.add_columns("Trial", "lat_p95", "cost", "success")
        yield self.pareto_table
        self.status = Label("", id="exp_status")
        yield self.status

    def on_mount(self) -> None:
        self.refresh_tables()

    def refresh_tables(self) -> None:
        self.trials_table.clear()
        for t in BACKEND.trials[-200:]:
            m = t.metrics
            self.trials_table.add_row(
                str(t.id),
                t.policy_name,
                f"{t.score:.4f}",
                str(m["latency_p95"]),
                str(m["cost_per_req"]),
                str(m["task_success"]),
                str(m["context_usage"]),
                str(m["tool_error_rate"]),
                t.artifact_id or "-",
            )
        if self.trials_table.row_count:
            self.trials_table.cursor_coordinate = (self.trials_table.row_count - 1, 0)
            self.selected_trial_id = int(
                self.trials_table.get_row(self.trials_table.row_count - 1)[0]
            )

        self.pareto_table.clear()
        for t in BACKEND.pareto:
            self.pareto_table.add_row(
                str(t.id),
                str(t.metrics["latency_p95"]),
                str(t.metrics["cost_per_req"]),
                str(t.metrics["task_success"]),
            )
        self.pareto_table.display = self.show_pareto

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        # Check if this event is from the trials table by verifying cursor_row is valid
        if event.cursor_row >= 0 and event.cursor_row < self.trials_table.row_count:
            row = self.trials_table.get_row(event.cursor_row)
            self.selected_trial_id = int(row[0])

    def action_toggle_pareto(self) -> None:
        self.show_pareto = not self.show_pareto
        self.pareto_table.display = self.show_pareto
        self.status.update("Pareto: ON" if self.show_pareto else "Pareto: OFF")
        self.refresh_tables()

    def action_adopt(self) -> None:
        if self.selected_trial_id is None:
            return
        ok = BACKEND.adopt_policy(self.selected_trial_id)
        if ok:
            self.status.update(
                f"Adopted trial #{self.selected_trial_id}. Rollback armed."
            )
        else:
            self.status.update(
                f"Refused adoption for trial #{self.selected_trial_id} (guardrails)."
            )

    def action_resume(self) -> None:
        self.status.update("Resume requested (stub).")

    def action_new_study(self) -> None:
        self.status.update("New study initialized (stub).")

    def action_kill(self) -> None:
        self.status.update("Kill signal sent to active run (stub).")


# =========================
# App shell + modal wiring
# =========================


class CIEOptimEvalsApp(App):
    CSS = """
    Screen { layout: vertical; }
    #row { height: 1fr; }
    #opti, #evals, #exper { border: tall $accent; padding: 1; }
    #opti_title, #evals_title, #exp_title { content-align: center middle; height: 1; }
    #opti_status, #evals_status, #exp_status { height: 1; color: $text; }
    #opti_table, #evals_table, #trials_table, #pareto_table { height: 1fr; }
    """
    BINDINGS = [
        Binding("ctrl+r", "refresh_all", "Refresh"),
        Binding("tab", "focus_next", "Next"),
        Binding("shift+tab", "focus_previous", "Prev"),
        Binding("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="row"):
            with Vertical(id="opti"):
                self.opti = OptimizersPanel()
                yield self.opti
            with Vertical(id="evals"):
                self.evals = EvalsPanel()
                yield self.evals
            with Vertical(id="exper"):
                self.exper = ExperimentsPanel()
                yield self.exper
        yield Footer()

    # --- Events from Optimizers ---
    def on_optimizers_panel_optimizer_run(
        self, msg: OptimizersPanel.OptimizerRun
    ) -> None:
        self.evals.set_policy(msg.policy)

    def on_optimizers_panel_open_weights(self, _: OptimizersPanel.OpenWeights) -> None:
        modal = WeightsModal()
        self.mount(modal)

    # --- Modal applied ---
    def on_weights_modal_applied(self, _: WeightsModal.Applied) -> None:
        # Re-score existing trials with new weights and rebuild Pareto
        for t in BACKEND.trials:
            t.score = round(BACKEND.score(t.metrics), 6)
        BACKEND._rebuild_pareto()
        self.action_refresh_all()

    # --- Evals finished ---
    def on_evals_panel_eval_run(self, _: EvalsPanel.EvalRun) -> None:
        self.exper.refresh_tables()

    # --- Global refresh ---
    def action_refresh_all(self) -> None:
        self.opti.refresh_table()
        self.evals.refresh_table()
        self.exper.refresh_tables()


if __name__ == "__main__":
    CIEOptimEvalsApp().run()

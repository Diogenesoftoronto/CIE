"""
Main TUI application for CIE.
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, TabbedContent, TabPane

from cie.config.settings import CIEConfig
from cie.core.backend import get_backend
from cie.ui.base import PanelMaximize
from cie.ui.messages import EvalRunMessage, OptimizerRunMessage, PolicyAdoptedMessage
from cie.ui.modals import CommandPaletteModal, ConfigModal, HelpModal, TutorModal, WeightsModal
from cie.ui.panels import EvalsPanel, ExperimentsPanel, OptimizersPanel, StatusPanel


class CIEOptimEvalsApp(App):
    """Main CIE TUI application."""

    CSS_PATH = [Path(__file__).with_name("theme.tcss")]
    BINDINGS = [
        Binding("ctrl+r", "refresh_all", "Refresh"),
        Binding("tab", "focus_next", "Next Panel"),
        Binding("shift+tab", "focus_previous", "Prev Panel"),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+w", "show_weights", "Weights"),
        Binding("ctrl+o", "show_config", "Config"),
        Binding("ctrl+t", "toggle_status", "Status"),
        Binding("ctrl+shift+p", "show_command_palette", "Command Palette"),
        Binding("ctrl+shift+t", "show_tutor", "Tutor"),
        Binding("h", "tab_prev", "Tab ←", show=False),
        Binding("l", "tab_next", "Tab →", show=False),
        Binding("f1", "help", "Help"),
        Binding("f5", "refresh_all", "Refresh"),
    ]

    def __init__(self, config: CIEConfig | None = None):
        super().__init__()
        self.config = config
        self.backend = get_backend(config)
        self.show_status = True
        self.status_panel: StatusPanel | None = None
        self.footer: Footer | None = None
        self.tabbed: TabbedContent | None = None
        self.command_palette_entries = [
            ("Show Tutor", "show_tutor"),
            ("Show Command Palette", "show_command_palette"),
            ("Toggle Status", "toggle_status"),
            ("Refresh All", "refresh_all"),
            ("Show Weights", "show_weights"),
            ("Show Config", "show_config"),
        ]

    def _tab_order(self) -> list[str]:
        return ["optimizers", "evals", "experiments"]

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()
        with TabbedContent(initial="optimizers", id="main-tabs") as tabbed:
            self.tabbed = tabbed
            with TabPane("[OPT] Optimizers", id="optimizers"):
                self.optimizers_panel = OptimizersPanel()
                yield self.optimizers_panel
            with TabPane("[EVAL] Evaluations", id="evals"):
                self.evals_panel = EvalsPanel()
                yield self.evals_panel
            with TabPane("[EXP] Experiments", id="experiments"):
                self.experiments_panel = ExperimentsPanel()
                yield self.experiments_panel
        if self.show_status:
            self.status_panel = StatusPanel()
            yield self.status_panel
        footer = Footer()
        self.footer = footer
        yield footer

    def on_mount(self) -> None:
        """Handle application mount."""
        self.title = "CIE - Optimization & Evaluation"
        self.sub_title = "AI-Powered Optimization Framework"
        self.optimizers_panel.focus()

    # --- Message Handlers ---
    def on_optimizer_run_message(self, message: OptimizerRunMessage) -> None:
        self.evals_panel.set_policy(message.policy)
        if self.status_panel:
            self.status_panel.update_status(f"Policy proposed: {message.policy.name}")

    def on_eval_run_message(self, message: EvalRunMessage) -> None:
        self.experiments_panel.refresh_tables()
        if self.status_panel:
            trial = message.trial
            status_msg = (
                f"Evaluation complete: Trial #{trial.id} "
                f"score={trial.score:.4f} "
                f"success={trial.metrics.get('task_success', 0):.3f}"
            )
            self.status_panel.update_status(status_msg)

    def on_policy_adopted_message(self, message: PolicyAdoptedMessage) -> None:
        if not self.status_panel:
            return
        if message.success:
            self.status_panel.update_status(
                f"Policy adopted from trial #{message.trial_id}", "success"
            )
        else:
            self.status_panel.update_status(
                f"Policy adoption failed for trial #{message.trial_id}", "error"
            )

    def on_weights_modal_applied(self, message: WeightsModal.Applied) -> None:
        self.action_refresh_all()
        if self.status_panel:
            self.status_panel.update_status("Objective weights updated", "info")

    def on_config_modal_applied(self, message: ConfigModal.Applied) -> None:
        self.action_refresh_all()
        if self.status_panel:
            self.status_panel.update_status("Configuration updated", "info")

    # --- Actions ---
    def action_refresh_all(self) -> None:
        self.optimizers_panel.refresh_table()
        self.evals_panel.refresh_table()
        self.experiments_panel.refresh_tables()
        if self.status_panel:
            self.status_panel.update_stats()

    def action_show_weights(self) -> None:
        self.push_screen(WeightsModal())

    def action_show_config(self) -> None:
        self.push_screen(ConfigModal())

    def action_toggle_status(self) -> None:
        self.show_status = not self.show_status
        if self.show_status:
            if not self.status_panel or not self.status_panel.is_attached:
                self.status_panel = StatusPanel()
                if self.footer and self.footer.is_attached:
                    self.mount(self.status_panel, before=self.footer)
                else:
                    self.mount(self.status_panel)
        else:
            if self.status_panel and self.status_panel.is_attached:
                self.status_panel.remove()

    def action_help(self) -> None:
        self.push_screen(HelpModal())

    def action_show_tutor(self) -> None:
        self.push_screen(TutorModal())

    def action_show_command_palette(self) -> None:
        palette = CommandPaletteModal(self.command_palette_entries)
        self.push_screen(palette)

    def action_tab_next(self) -> None:
        if not self.tabbed:
            return
        order = self._tab_order()
        try:
            index = order.index(self.tabbed.active)
        except ValueError:
            return
        self.tabbed.active = order[(index + 1) % len(order)]

    def action_tab_prev(self) -> None:
        if not self.tabbed:
            return
        order = self._tab_order()
        try:
            index = order.index(self.tabbed.active)
        except ValueError:
            return
        self.tabbed.active = order[(index - 1) % len(order)]

    def on_panel_maximize(self, message: PanelMaximize) -> None:
        if not self.tabbed:
            return
        panel_map = {
            self.optimizers_panel: "optimizers",
            self.evals_panel: "evals",
            self.experiments_panel: "experiments",
        }
        tab_id = panel_map.get(message.panel)
        if tab_id:
            self.tabbed.active = tab_id
            message.panel.focus()

    def on_unmount(self) -> None:
        if self.backend:
            self.backend.close()


def main(config: CIEConfig | None = None):
    """Main entry point for the TUI application."""
    app = CIEOptimEvalsApp(config)
    app.run()


if __name__ == "__main__":
    main()

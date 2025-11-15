"""
Main TUI application for CIE.
"""

from importlib import metadata
from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import ContentSwitcher, Label, ListItem, ListView

from cie.config.settings import CIEConfig
from cie.core.backend import get_backend
from cie.ui.base import PanelMaximize
from cie.ui.components import (
    CITopBar,
    CommandPalette,
    CommandRegistry,
    StatusBar as EnhancedStatusBar,
    create_default_registry,
)
from cie.ui.components.onboarding import OnboardingWizard, TutorModal
from cie.ui.messages import EvalRunMessage, OptimizerRunMessage, PolicyAdoptedMessage
from cie.ui.modals import ConfigModal, ContextToolsModal, HelpModal, WeightsModal
from cie.ui.panels import (
    ContextPanel,
    EvalsPanel,
    ExperimentsPanel,
    OptimizersPanel,
    PromptsPanel,
    StatusPanel,
)


def _resolve_version() -> str:
    """Best effort package version lookup."""
    try:
        return metadata.version("cie")
    except metadata.PackageNotFoundError:  # type: ignore[attr-defined]
        return "dev"


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
        Binding("ctrl+/", "show_context_tools", "Context"),
        Binding("ctrl+shift+p", "show_command_palette", "Command Palette"),
        Binding("ctrl+shift+t", "show_tutor", "Tutor"),
        Binding("ctrl+shift+o", "show_onboarding", "Onboarding"),
        Binding("ctrl+shift+w", "sync_wandb", "Sync W&B"),
        Binding("h", "sidebar_prev", "Sidebar ↑", show=False),
        Binding("l", "sidebar_next", "Sidebar ↓", show=False),
        Binding("f1", "help", "Help"),
        Binding("f5", "refresh_all", "Refresh"),
    ]

    def __init__(
        self,
        config: CIEConfig | None = None,
        *,
        demo_mode: bool = False,
        demo_metadata: dict[str, Any] | None = None,
    ):
        super().__init__()
        self.config = config
        self.backend = get_backend(config)
        self.app_version = _resolve_version()
        self.show_status = True
        self.status_panel: StatusPanel | None = None
        self.status_bar: EnhancedStatusBar | None = None
        self.sidebar: ListView | None = None
        self.content_switcher: ContentSwitcher | None = None
        self.context_panel: ContextPanel | None = None
        self.top_bar: CITopBar | None = None
        self.command_registry: CommandRegistry = create_default_registry(self)
        self._register_app_commands()
        self._onboarding_flag = Path.home() / ".cie" / ".onboarding_shown"
        self.demo_mode = demo_mode
        self.demo_metadata = demo_metadata or {}

    def _sidebar_items(self) -> list[tuple[str, str]]:
        """Return list of (id, label) for sidebar."""
        return [
            ("optimizers", "Optimizers"),
            ("evals", "Evaluations"),
            ("experiments", "Experiments"),
            ("prompts", "Prompts"),
            ("context", "Context"),
        ]

    def _register_app_commands(self) -> None:
        """Register domain-specific commands with the palette."""
        registry = self.command_registry
        registry.register(
            "Show Weights", self.action_show_weights, "Edit objective weights", "Ctrl+W", "Actions"
        )
        registry.register(
            "Show Config", self.action_show_config, "Edit configuration", "Ctrl+O", "Actions"
        )
        registry.register(
            "Show Tutor", self.action_show_tutor, "Contextual tips", "Ctrl+Shift+T", "Help"
        )
        registry.register(
            "Onboarding Tour",
            self.action_show_onboarding,
            "Interactive walkthrough",
            "Ctrl+Shift+O",
            "Help",
        )
        registry.register(
            "Context Navigator",
            self.action_show_context_tools,
            "Inspect runtime context",
            "Ctrl+/",
            "Tools",
        )
        registry.register(
            "Sync W&B Run",
            self.action_sync_wandb,
            "Import wandb/latest-run history",
            "Ctrl+Shift+W",
            "Integrations",
        )

    def _update_top_bar(self, message: str | None = None, level: str = "info") -> None:
        if not self.top_bar:
            return
        stats = self.backend.get_stats()
        status_text = message or self.sub_title
        self.top_bar.update_from_stats(stats, message=status_text, level=level)

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        mode_label = "DEMO" if self.demo_mode else "LIVE"
        help_text = "Ctrl+Shift+P commands · F1 help"
        self.top_bar = CITopBar(version=self.app_version, mode_label=mode_label, help_text=help_text)
        yield self.top_bar

        with Horizontal(id="app-grid"):
            # Sidebar
            with Vertical(id="sidebar"):
                sidebar_items = [
                    ListItem(Label(label), id=f"nav-{panel_id}")
                    for panel_id, label in self._sidebar_items()
                ]
                self.sidebar = ListView(*sidebar_items, id="sidebar-list")
                yield self.sidebar

            # Main Content
            with Vertical(id="content-area"):
                with ContentSwitcher(initial="optimizers", id="content-switcher") as switcher:
                    self.content_switcher = switcher
                    
                    self.optimizers_panel = OptimizersPanel(self.backend, id="optimizers")
                    yield self.optimizers_panel
                    
                    self.evals_panel = EvalsPanel(self.backend, id="evals")
                    yield self.evals_panel
                    
                    self.experiments_panel = ExperimentsPanel(self.backend, id="experiments")
                    yield self.experiments_panel
                    
                    self.prompts_panel = PromptsPanel(self.backend, id="prompts")
                    yield self.prompts_panel

                    self.context_panel = ContextPanel(
                        demo_metadata=self.demo_metadata if self.demo_mode else None,
                        id="context"
                    )
                    yield self.context_panel

                if self.show_status:
                    self.status_panel = StatusPanel(self.backend)
                    yield self.status_panel

        self.status_bar = EnhancedStatusBar()
        yield self.status_bar

    def on_mount(self) -> None:
        """Handle application mount."""
        base_title = "CIE - Optimization & Evaluation"
        self.title = f"{base_title} [Demo]" if self.demo_mode else base_title
        if self.demo_mode and self.demo_metadata.get("description"):
            self.sub_title = self.demo_metadata["description"]
        else:
            self.sub_title = "AI-Powered Optimization Framework"
        
        # Select first item in sidebar
        if self.sidebar:
            self.sidebar.index = 0
            self.optimizers_panel.focus()

        if self.status_bar:
            self.status_bar.update_stats()
        if not self._onboarding_flag.exists():
            self.set_timer(0.6, self.action_show_onboarding)
        if self.demo_mode and self.demo_metadata:
            banner = self.demo_metadata.get("status_message", "Demo mode enabled.")
            if self.status_panel:
                self.status_panel.update_status(banner, "info")
            if self.status_bar:
                self.status_bar.update_message(banner, "info")
        self._update_top_bar("Ready", "info")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle sidebar selection."""
        if not event.item or not self.content_switcher:
            return
        
        # Extract panel_id from nav-{panel_id}
        panel_id = event.item.id.replace("nav-", "")
        self.content_switcher.current = panel_id
        
        # Focus the active panel
        panel_map = {
            "optimizers": self.optimizers_panel,
            "evals": self.evals_panel,
            "experiments": self.experiments_panel,
            "prompts": self.prompts_panel,
            "context": self.context_panel,
        }
        if panel := panel_map.get(panel_id):
            panel.focus()

    # --- Message Handlers ---
    def on_optimizer_run_message(self, message: OptimizerRunMessage) -> None:
        self.evals_panel.set_policy(message.policy)
        if self.status_panel:
            self.status_panel.update_status(f"Policy proposed: {message.policy.name}")
        if self.status_bar:
            self.status_bar.update_message(f"Policy proposed: {message.policy.name}", "info")
            self.status_bar.update_stats()
        self._update_top_bar(f"Policy proposed: {message.policy.name}", "info")

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
        if self.status_bar:
            self.status_bar.update_message("Evaluation complete", "success")
            self.status_bar.update_stats()
        self._update_top_bar("Evaluation complete", "success")

    def on_policy_adopted_message(self, message: PolicyAdoptedMessage) -> None:
        if self.status_panel:
            if message.success:
                self.status_panel.update_status(
                    f"Policy adopted from trial #{message.trial_id}", "success"
                )
            else:
                self.status_panel.update_status(
                    f"Policy adoption failed for trial #{message.trial_id}", "error"
                )
        if self.status_bar:
            if message.success:
                self.status_bar.update_message(f"Adopted trial #{message.trial_id}", "success")
            else:
                self.status_bar.update_message(
                    f"Adoption failed for trial #{message.trial_id}", "error"
                )
        level = "success" if message.success else "error"
        text = (
            f"Adopted trial #{message.trial_id}"
            if message.success
            else f"Adoption failed for trial #{message.trial_id}"
        )
        self._update_top_bar(text, level)

    def on_weights_modal_applied(self, message: WeightsModal.Applied) -> None:
        self.action_refresh_all()
        if self.status_panel:
            self.status_panel.update_status("Objective weights updated", "info")
        if self.status_bar:
            self.status_bar.update_message("Objective weights updated", "info")
            self.status_bar.update_stats()
        self._update_top_bar("Objective weights updated", "info")

    def on_config_modal_applied(self, message: ConfigModal.Applied) -> None:
        self.action_refresh_all()
        if self.status_panel:
            self.status_panel.update_status("Configuration updated", "info")
        if self.status_bar:
            self.status_bar.update_message("Configuration updated", "info")
            self.status_bar.update_stats()
        self._update_top_bar("Configuration updated", "info")

    # --- Actions ---
    def action_refresh_all(self) -> None:
        self.optimizers_panel.refresh_table()
        self.evals_panel.refresh_table()
        self.experiments_panel.refresh_tables()
        self.prompts_panel.refresh_table()
        if self.status_panel:
            self.status_panel.update_stats()
        if self.status_bar:
            self.status_bar.update_stats()
            self.status_bar.update_message("Refreshed all panels", "info")
        self._update_top_bar("Refreshed all panels", "info")

    def action_show_weights(self) -> None:
        self.push_screen(WeightsModal())

    def action_show_config(self) -> None:
        self.push_screen(ConfigModal())

    def action_toggle_status(self) -> None:
        self.show_status = not self.show_status
        if self.show_status:
            if not self.status_panel or not self.status_panel.is_attached:
                self.status_panel = StatusPanel(self.backend)
                # Mount before status bar if possible, otherwise just mount
                # Note: In new layout, status panel is inside content-area vertical container
                # This logic needs adjustment for the new layout
                content_area = self.query_one("#content-area", Vertical)
                content_area.mount(self.status_panel)
        else:
            if self.status_panel and self.status_panel.is_attached:
                self.status_panel.remove()
        self._update_top_bar(
            "Status panel {}".format("shown" if self.show_status else "hidden"),
            "info",
        )

    def action_help(self) -> None:
        self.push_screen(HelpModal())

    def action_show_tutor(self) -> None:
        self.push_screen(TutorModal())

    def action_show_command_palette(self) -> None:
        palette = CommandPalette(self.command_registry)
        self.push_screen(palette)

    def action_show_context_tools(self) -> None:
        self.push_screen(ContextToolsModal())

    def action_show_onboarding(self) -> None:
        self.push_screen(OnboardingWizard())
        self._mark_onboarding_shown()

    def action_sync_wandb(self) -> None:
        if self.experiments_panel:
            self.experiments_panel.action_sync_wandb()

    def action_sidebar_next(self) -> None:
        if self.sidebar:
            self.sidebar.action_cursor_down()

    def action_sidebar_prev(self) -> None:
        if self.sidebar:
            self.sidebar.action_cursor_up()

    def action_focus_context(self) -> None:
        """Bring the context panel to the foreground."""
        if self.sidebar:
            # Find index of context item
            for i, item in enumerate(self.sidebar.children):
                if item.id == "nav-context":
                    self.sidebar.index = i
                    break

    def on_panel_maximize(self, message: PanelMaximize) -> None:
        if not self.sidebar:
            return
        
        panel_map = {
            self.optimizers_panel: "optimizers",
            self.evals_panel: "evals",
            self.experiments_panel: "experiments",
            self.prompts_panel: "prompts",
        }
        if hasattr(self, "context_panel"):
            panel_map[self.context_panel] = "context"
            
        target_id = panel_map.get(message.panel)
        if target_id:
            # Find index in sidebar
            for i, item in enumerate(self.sidebar.children):
                if item.id == f"nav-{target_id}":
                    self.sidebar.index = i
                    message.panel.focus()
                    break

    def on_unmount(self) -> None:
        if self.backend:
            self.backend.close()
        if self.status_bar and self.status_bar.is_attached:
            self.status_bar.update_message("Shutting down", "warning")

    def _mark_onboarding_shown(self) -> None:
        """Persist onboarding completion flag."""
        try:
            self._onboarding_flag.parent.mkdir(parents=True, exist_ok=True)
            self._onboarding_flag.write_text("shown")
        except OSError:
            pass


def main(
    config: CIEConfig | None = None,
    *,
    demo_mode: bool = False,
    demo_metadata: dict[str, Any] | None = None,
):
    """Main entry point for the TUI application."""
    app = CIEOptimEvalsApp(config, demo_mode=demo_mode, demo_metadata=demo_metadata)
    app.run()


if __name__ == "__main__":
    main()

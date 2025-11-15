"""Context tools panel."""

from __future__ import annotations

from typing import Any

from textual.binding import Binding
from textual.containers import Vertical

from cie.ui.base import BasePanel
from cie.ui.components import ContextNavigator


class ContextPanel(BasePanel):
    """Panel providing embedded context navigation tools."""

    BINDINGS = [
        Binding("c", "capture_context", "Capture (C)"),
        Binding("o", "optimize_context", "Optimize (O)"),
        Binding("r", "show_summary", "Summary (R)"),
        Binding("m", "minimize", "Minimize (m)"),
        Binding("M", "maximize", "Maximize (M)"),
    ]

    def __init__(self, demo_metadata: dict[str, Any] | None = None, **kwargs) -> None:
        kwargs.setdefault("id", "context")
        kwargs.setdefault("classes", "panel")
        super().__init__(title="Context Tools", icon="[CTX]", **kwargs)
        self.navigator: ContextNavigator | None = None
        self.demo_metadata = demo_metadata or {}

    def compose_content(self):
        with Vertical(classes="context-panel-body"):
            self.navigator = ContextNavigator(
                id="context_panel_navigator",
                show_header=not self.demo_metadata,
                compact=bool(self.demo_metadata),
            )
            yield self.navigator

    def on_mount(self) -> None:
        subtitle = "Inspect runtime context and metrics"
        if self.demo_metadata:
            self.set_badge("DEMO", "info")
            if self.demo_metadata.get("name"):
                subtitle = f"{self.demo_metadata['name']} · context snapshot"
            intro = self.demo_metadata.get("context_intro")
            if intro and self.navigator:
                self.call_after_refresh(lambda: self.navigator.load_intro_text(intro))
        self.set_subtitle(subtitle)
        self.add_toolbar_action("Capture", self.action_capture_context, button_id="ctx_capture")
        self.add_toolbar_action("Summary", self.action_show_summary, button_id="ctx_summary")
        self.add_toolbar_action("Optimize", self.action_optimize_context, button_id="ctx_optimize")
        self.add_toolbar_action("Export", self.action_export_context, button_id="ctx_export")
        self.update_status("Context navigator ready.")

    def action_capture_context(self) -> None:
        if self.navigator:
            self.navigator.action_capture()
            self.update_status("Captured runtime context", "info")

    def action_optimize_context(self) -> None:
        if self.navigator:
            self.navigator.action_optimize()
            self.update_status("Optimization run complete", "info")

    def action_show_summary(self) -> None:
        if self.navigator:
            self.navigator.action_summary()
            self.update_status("Summary generated", "info")

    def action_export_context(self) -> None:
        if self.navigator:
            self.navigator.action_export()
            self.update_status("Context export generated", "info")

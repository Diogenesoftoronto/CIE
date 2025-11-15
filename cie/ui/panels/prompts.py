"""
Prompts panel for managing DSPy signatures and prompts.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable
from textual.widgets._data_table import RowDoesNotExist

from cie.core.backend import CIEBackend, get_backend
from cie.ui.base import BasePanel
from cie.ui.modals import ConfirmModal, PromptModal


class PromptsPanel(BasePanel):
    """Panel for managing prompts and signatures."""

    BINDINGS = [
        Binding("n", "new_prompt", "New (n)"),
        Binding("e", "edit_prompt", "Edit (e)"),
        Binding("d", "delete_prompt", "Delete (d)"),
        Binding("j", "cursor_down", "Down (j)", show=False),
        Binding("k", "cursor_up", "Up (k)", show=False),
    ]

    def __init__(self, backend: CIEBackend | None = None, **kwargs) -> None:
        kwargs.setdefault("id", "prompts")
        kwargs.setdefault("classes", "panel")
        super().__init__(title="Prompts", icon="[PRM]", **kwargs)
        self.backend = backend or get_backend()
        self.table: DataTable | None = None
        self.selected_prompt_id: str | None = None

    def compose_content(self) -> ComposeResult:
        """Compose the prompts panel content."""
        self.table = DataTable(id="prompts_table", cursor_type="row", classes="data-table")
        self.table.add_columns("ID", "Description", "Tags", "Updated")
        yield self.table

    def on_mount(self) -> None:
        """Initialize the panel."""
        self.set_subtitle("Manage DSPy signatures and prompt templates")
        self.add_toolbar_action("New", self.action_new_prompt, button_id="prm_new")
        self.add_toolbar_action("Edit", self.action_edit_prompt, button_id="prm_edit")
        self.add_toolbar_action("Delete", self.action_delete_prompt, button_id="prm_delete")
        self.refresh_table()

    def refresh_table(self) -> None:
        """Refresh the prompts table."""
        if not self.table:
            return
        
        self.table.clear()
        prompts = self.backend.list_prompts()
        
        for p in prompts:
            self.table.add_row(
                p.id,
                p.description,
                ", ".join(p.tags),
                p.updated_at.strftime("%Y-%m-%d %H:%M"),
                key=p.id
            )
        
        if self.table.row_count > 0:
            self.table.cursor_coordinate = (0, 0)
            self._update_selection()
        else:
            self.selected_prompt_id = None

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle row selection."""
        if event.control is self.table:
            self._update_selection()

    def _update_selection(self) -> None:
        """Update selected prompt ID from table cursor."""
        if not self.table:
            return
        try:
            row_key = self.table.coordinate_to_cell_key(self.table.cursor_coordinate).row_key
            self.selected_prompt_id = row_key.value
        except (RowDoesNotExist, ValueError):
            self.selected_prompt_id = None

    def action_new_prompt(self) -> None:
        """Create a new prompt."""
        self.app.push_screen(PromptModal(), self._handle_modal_result)

    def action_edit_prompt(self) -> None:
        """Edit the selected prompt."""
        if not self.selected_prompt_id:
            self.update_status("No prompt selected", "warning")
            return
        self.app.push_screen(PromptModal(self.selected_prompt_id), self._handle_modal_result)

    def action_delete_prompt(self) -> None:
        """Delete the selected prompt."""
        if not self.selected_prompt_id:
            self.update_status("No prompt selected", "warning")
            return
        
        def _do_delete(confirmed: bool) -> None:
            if confirmed and self.selected_prompt_id:
                self.backend.delete_prompt(self.selected_prompt_id)
                self.refresh_table()
                self.update_status(f"Deleted prompt '{self.selected_prompt_id}'", "info")

        self.app.push_screen(
            ConfirmModal(
                "Delete Prompt",
                f"Are you sure you want to delete '{self.selected_prompt_id}'?",
                confirm_text="Delete",
            ),
            _do_delete,
        )

    def _handle_modal_result(self, result: Any) -> None:
        """Handle modal result (refresh table)."""
        if result:
            self.refresh_table()

    def action_cursor_down(self) -> None:
        if self.table:
            self.table.action_cursor_down()

    def action_cursor_up(self) -> None:
        if self.table:
            self.table.action_cursor_up()

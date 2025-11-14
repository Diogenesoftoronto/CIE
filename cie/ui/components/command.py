"""
Command palette with fuzzy search and keyboard navigation.
"""

from typing import Any, Callable

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListItem, ListView


class CommandRegistry:
    """Registry for available commands."""

    def __init__(self):
        self.commands: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        action: Callable,
        description: str = "",
        shortcut: str = "",
        category: str = "General",
    ) -> None:
        """Register a command."""
        self.commands[name] = {
            "action": action,
            "description": description,
            "shortcut": shortcut,
            "category": category,
            "name": name,
        }

    def get_commands(self, category: str | None = None) -> list[dict[str, Any]]:
        """Get commands, optionally filtered by category."""
        commands = list(self.commands.values())
        if category:
            commands = [c for c in commands if c["category"] == category]
        return commands

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search commands with fuzzy matching."""
        query = query.lower()
        results = []

        for cmd in self.commands.values():
            score = 0
            name_lower = cmd["name"].lower()
            desc_lower = cmd["description"].lower()

            # Exact match in name
            if query == name_lower:
                score = 100
            # Starts with query
            elif name_lower.startswith(query):
                score = 80
            # Contains query in name
            elif query in name_lower:
                score = 60
            # Contains query in description
            elif query in desc_lower:
                score = 40
            # Fuzzy match
            else:
                # Simple fuzzy scoring
                matches = sum(1 for c in query if c in name_lower)
                if matches > len(query) / 2:
                    score = 20

            if score > 0:
                results.append((score, cmd))

        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        return [cmd for _, cmd in results]


class CommandPalette(ModalScreen):
    """Command palette modal with search and selection."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("down,j", "next_item", "Next", show=False),
        Binding("up,k", "prev_item", "Previous", show=False),
        Binding("enter", "execute", "Execute"),
        Binding("tab", "complete", "Complete", show=False),
    ]

    CSS = """
    CommandPalette {
        align: center middle;
    }

    #command_palette_container {
        width: 60;
        height: 20;
        background: $panel;
        border: solid $accent;
        padding: 1;
    }

    #command_search {
        margin-bottom: 1;
        border: solid $border;
    }

    #command_list {
        height: 1fr;
        border: solid $border;
        background: $surface;
    }

    .command-item {
        padding: 0 1;
    }

    .command-item.--highlighted {
        background: $accent;
        color: $background;
    }

    .command-shortcut {
        float: right;
        color: $text-muted;
    }

    .command-category {
        color: $text-muted;
        text-style: italic;
    }
    """

    def __init__(self, registry: CommandRegistry | None = None):
        super().__init__()
        self.registry = registry or CommandRegistry()
        self.filtered_commands: list[dict[str, Any]] = []
        self.selected_index = 0

    def compose(self) -> ComposeResult:
        """Compose the command palette."""
        with Vertical(id="command_palette_container"):
            yield Label("Command Palette", classes="title")
            yield Input(placeholder="Type to search commands...", id="command_search")
            yield ListView(id="command_list")

    def on_mount(self) -> None:
        """Initialize when mounted."""
        self.filtered_commands = self.registry.get_commands()
        self.update_list()
        self.query_one("#command_search", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        query = event.value.strip()

        if query:
            self.filtered_commands = self.registry.search(query)
        else:
            self.filtered_commands = self.registry.get_commands()

        self.selected_index = 0
        self.update_list()

    def update_list(self) -> None:
        """Update the command list display."""
        list_view = self.query_one("#command_list", ListView)
        list_view.clear()

        if not self.filtered_commands:
            list_view.append(ListItem(Label("No commands found")))
            return

        current_category = None
        for i, cmd in enumerate(self.filtered_commands):
            # Add category header if changed
            if cmd["category"] != current_category:
                current_category = cmd["category"]
                list_view.append(
                    ListItem(Label(f"── {current_category} ──", classes="command-category"))
                )

            # Create command item
            item_text = cmd["name"]
            if cmd["description"]:
                item_text += f" - {cmd['description']}"

            item = ListItem(Label(item_text), classes="command-item")

            # Add shortcut if present
            if cmd["shortcut"]:
                shortcut = Label(cmd["shortcut"], classes="command-shortcut")
                item.compose_add_child(shortcut)

            list_view.append(item)

            # Highlight selected item
            if i == self.selected_index:
                item.add_class("--highlighted")

    def action_next_item(self) -> None:
        """Select next item."""
        if self.filtered_commands:
            self.selected_index = (self.selected_index + 1) % len(self.filtered_commands)
            self.update_list()

    def action_prev_item(self) -> None:
        """Select previous item."""
        if self.filtered_commands:
            self.selected_index = (self.selected_index - 1) % len(self.filtered_commands)
            self.update_list()

    def action_execute(self) -> None:
        """Execute selected command."""
        if self.filtered_commands and 0 <= self.selected_index < len(self.filtered_commands):
            cmd = self.filtered_commands[self.selected_index]
            self.dismiss()

            # Execute the command action
            if cmd["action"]:
                try:
                    cmd["action"]()
                except Exception as e:
                    self.app.notify(f"Error executing command: {e}", severity="error")

    def action_complete(self) -> None:
        """Auto-complete the search."""
        if self.filtered_commands:
            cmd = self.filtered_commands[0]
            search_input = self.query_one("#command_search", Input)
            search_input.value = cmd["name"]
            search_input.cursor_position = len(cmd["name"])

    def key_escape(self) -> None:
        """Close the palette."""
        self.dismiss()


def create_default_registry(app) -> CommandRegistry:
    """Create default command registry with common commands."""
    registry = CommandRegistry()

    # File commands
    registry.register("Quit", app.action_quit, "Quit application", "Ctrl+C", "File")
    registry.register(
        "Save", lambda: app.notify("Save not implemented"), "Save current state", "Ctrl+S", "File"
    )

    # View commands
    registry.register("Refresh All", app.action_refresh_all, "Refresh all panels", "Ctrl+R", "View")
    if hasattr(app, "action_toggle_status"):
        registry.register(
            "Toggle Status", app.action_toggle_status, "Toggle status bar", "Ctrl+T", "View"
        )

    # Navigation
    if hasattr(app, "action_tab_next"):
        registry.register("Next Tab", app.action_tab_next, "Go to next tab", "Tab", "Navigation")
    if hasattr(app, "action_tab_prev"):
        registry.register(
            "Previous Tab", app.action_tab_prev, "Go to previous tab", "Shift+Tab", "Navigation"
        )

    # Help
    if hasattr(app, "action_help"):
        registry.register("Show Help", app.action_help, "Show help", "F1", "Help")
    if hasattr(app, "action_show_tutor"):
        registry.register(
            "Show Tutor", app.action_show_tutor, "Show tutorial", "Ctrl+Shift+T", "Help"
        )

    return registry

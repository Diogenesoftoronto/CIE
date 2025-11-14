# Textual Framework - Comprehensive Guide

## Overview

**Textual** is a Python framework for building rich Text User Interfaces (TUI). This project uses Textual ≥0.47 to create an interactive terminal-based application for optimization and evaluation workflows.

**⚠️ Version Note**: The CIE project uses Textual ≥0.47 API patterns. The actual imports in `main.py` show:
```python
from textual.screen import ModalScreen as Modal  # Older API pattern
```

This documentation covers both the older patterns used in CIE and modern equivalents where applicable.

## CIE-Specific Textual Patterns

### Version Compatibility
CIE uses Textual ≥0.47 with these specific patterns:

```python
# Modal import (older pattern)
from textual.screen import ModalScreen as Modal

# Modern equivalent would be:
# from textual.screen import ModalScreen

# Usage in CIE:
class WeightsModal(Modal):  # Modal is alias for ModalScreen
    pass
```

### Actual CIE Imports
The project uses these Textual components:
```python
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import DataTable, Footer, Header, Input, Label, Static
from textual.screen import ModalScreen as Modal
```

## Core Concepts

### 1. Application Architecture

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static

class MyApp(App):
    def compose(self) -> ComposeResult:
        # Return widgets to mount
        yield Header()
        yield Footer()
        yield YourWidget()

    def on_mount(self) -> None:
        # Called when app starts
        pass

if __name__ == "__main__":
    MyApp().run()
```

### 2. Widgets

Widgets are the building blocks of Textual UIs. Common widgets used in CIE:

#### Layout Widgets
```python
from textual.containers import Horizontal, Vertical, Container

# Horizontal layout
with Horizontal():
    yield WidgetA()
    yield WidgetB()

# Vertical layout
with Vertical():
    yield WidgetA()
    yield WidgetB()
```

#### Display Widgets
```python
from textual.widgets import Label, Static, Button

# Simple text display
Label("Text", id="my_label")

# Stylable text
Static("Formatted text", classes="highlight")

# Interactive button
Button("Click me", id="my_button")
```

#### Data Display
```python
from textual.widgets import DataTable, ListView, Tree

# Tabular data with sorting/selection
table = DataTable()
table.add_columns("Name", "Value", "Status")

# List with items
list_view = ListView()
list_view.append(ListItem(Label("Item 1")))

# Hierarchical data
tree = Tree()
root = tree.root.add("Root")
child = root.add("Child")
```

#### Input Widgets
```python
from textual.widgets import Input, TextArea, Select

# Text input
Input(placeholder="Enter text", id="text_input")

# Multi-line text
TextArea(text="Multiple\nlines", id="text_area")

# Dropdown selection
Select([("Option 1", "value1"), ("Option 2", "value2")])
```

### 3. Event Handling

Textual uses a message-based event system:

```python
from textual.message import Message
from textual.widgets import Button

class MyWidget(Static):
    class Clicked(Message):
        def __init__(self, button_id: str):
            self.button_id = button_id
            super().__init__()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Handle button press
        self.post_message(self.Clicked(event.button.id))

class MyApp(App):
    def on_my_widget_clicked(self, event: MyWidget.Clicked) -> None:
        # Handle custom message
        print(f"Clicked: {event.button_id}")
```

### 4. CSS Styling

Textual uses CSS-like styling:

```python
CSS = """
Screen {
    layout: vertical;
}

Widget {
    border: solid $primary;
    padding: 1;
}

Button {
    background: $primary;
    color: $text;
}

Button:hover {
    background: $accent;
}
"""
```

## CIE Project Implementation Patterns

**Note**: CIE uses Textual ≥0.47 API patterns. Some examples may show newer syntax but the core concepts remain the same.

### 1. Panel Architecture

Each panel in CIE follows a consistent pattern:

```python
class OptimizersPanel(Static):
    BINDINGS = [
        Binding("o", "run_once", "Run (o)"),
        Binding("O", "configure", "Configure (O)"),
        Binding("W", "weights", "Weights (W)"),
    ]

    def compose(self) -> ComposeResult:
        yield Label("Optimizers", id="opti_title")
        self.table = DataTable(id="opti_table")
        yield self.table
        yield Label("", id="status")

    def on_mount(self) -> None:
        self.refresh_table()

    def action_run_once(self) -> None:
        # Handle action
        pass
```

### 2. Modal Screens

Modals are used for configuration dialogs:

```python
from textual.screen import ModalScreen as Modal

class WeightsModal(Modal):
    CSS = """
    WeightsModal {
        width: 64;
        height: auto;
        border: heavy $accent;
        background: $panel;
        padding: 1;
    }
    """

    class Applied(Message):
        pass

    def compose(self) -> ComposeResult:
        yield Label("Objective Weights")

    def key_escape(self) -> None:
        self.dismiss()

    def key_enter(self) -> None:
        self.apply_weights()
        self.dismiss()
        self.post_message(self.Applied())
```

### 3. Message-Based Communication

Panels communicate via messages:

```python
# Panel A sends message
class PanelA(Static):
    class UpdateRequest(Message):
        def __init__(self, data: Any):
            self.data = data
            super().__init__()

    def action_update(self) -> None:
        self.post_message(self.UpdateRequest(new_data))

# App receives and routes message
class MyApp(App):
    def on_panel_a_update_request(self, event: PanelA.UpdateRequest) -> None:
        # Route to other panels
        self.panel_b.update_data(event.data)
```

### 4. Reactive Properties

Widgets can have reactive properties:

```python
from textual.reactive import reactive

class MyWidget(Static):
    selected_index: reactive[int | None] = reactive(None)

    def watch_selected_index(self, old_value: int | None, value: int | None) -> None:
        # Called when selected_index changes
        self.update_display()
```

## DataTable Usage in CIE

### Basic Setup
```python
def compose(self) -> ComposeResult:
    table = DataTable(id="data_table", cursor_type="row")
    table.add_columns("Column1", "Column2", "Column3")
    yield table

def on_mount(self) -> None:
    self.populate_table()

def populate_table(self) -> None:
    self.table.clear()
    for item in data:
        self.table.add_row(item.col1, item.col2, item.col3)
    if self.table.row_count:
        self.table.cursor_coordinate = (0, 0)
```

### Selection Handling
```python
def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
    self.selected_index = event.cursor_row

def get_selected_row(self) -> List[str] | None:
    if self.selected_index is not None:
        return self.table.get_row(self.selected_index)
    return None
```

### Dynamic Updates
```python
def update_table(self, new_data: List[Any]) -> None:
    self.table.clear()
    for item in new_data:
        self.table.add_row(str(item.id), item.name, f"{item.score:.2f}")

    # Maintain selection if possible
    if self.table.row_count and self.selected_index is not None:
        if self.selected_index < self.table.row_count:
            self.table.cursor_coordinate = (self.selected_index, 0)
```

## Styling Patterns

### Panel Styling
```python
CSS = """
PanelWidget {
    border: tall $accent;
    padding: 1;
}

.title {
    content-align: center middle;
    height: 1;
    background: $primary;
}

.status {
    height: 1;
    color: $text-muted;
}
"""
```

### Modal Styling
```python
CSS = """
ModalScreen {
    background: rgba(0, 0, 0, 0.8);
}

ModalWidget {
    width: 60;
    height: auto;
    border: heavy $accent;
    background: $panel;
    padding: 1;
}
"""
```

### DataTable Styling
```python
CSS = """
DataTable {
    height: 1fr;
}

DataTable > .datatable--cursor {
    background: $primary;
    color: $text;
}
"""
```

## Advanced Features

### 1. Screen Management

```python
class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield MainContent()
        yield Footer()

    def action_show_modal(self) -> None:
        modal = MyModal()
        self.push_screen(modal)

class MyModal(ModalScreen):
    pass
```

### 2. Bindings and Keyboard Navigation

```python
class MyWidget(Static):
    BINDINGS = [
        Binding("enter", "activate", "Activate"),
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+r", "refresh", "Refresh"),
    ]

    def action_activate(self) -> None:
        # Handle activation
        pass
```

### 3. Message Routing

```python
# Automatic message routing by name
class MyApp(App):
    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Handles all button presses
        pass

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        # Handles all DataTable selections
        pass
```

## Common Patterns in CIE

### 1. Panel State Management
```python
class PanelWidget(Static):
    selected_index: reactive[int | None] = reactive(None)
    data_cache: List[Any] = []

    def on_mount(self) -> None:
        self.load_data()
        self.refresh_display()

    def load_data(self) -> None:
        # Load from backend
        self.data_cache = BACKEND.get_data()

    def refresh_display(self) -> None:
        # Update UI with cached data
        self.update_table(self.data_cache)

    def watch_selected_index(self, old_value: int | None, value: int | None) -> None:
        # React to selection changes
        if value is not None:
            self.highlight_selection()
```

### 2. Backend Integration
```python
class BackendConnectedWidget(Static):
    def action_refresh(self) -> None:
        try:
            # Fetch fresh data
            new_data = BACKEND.fetch_data()
            self.update_display(new_data)
            self.set_status("Data refreshed", "success")
        except Exception as e:
            self.set_status(f"Error: {e}", "error")

    def set_status(self, message: str, type: str = "info") -> None:
        status_widget = self.query_one("#status", Label)
        status_widget.update(message)

        # Apply styling based on type
        if type == "error":
            status_widget.styles.color = "red"
        elif type == "success":
            status_widget.styles.color = "green"
        else:
            status_widget.styles.color = "white"
```

### 3. Multi-Panel Coordination
```python
class MainApp(App):
    def on_panel_action_request(self, event: Panel.ActionRequest) -> None:
        # Central coordination
        if event.action_type == "policy_selected":
            self.other_panel.update_policy(event.policy)
        elif event.action_type == "data_changed":
            self.refresh_all_panels()
```

## Performance Considerations

### 1. Efficient Data Updates
```python
def update_large_table(self, data: List[Item]) -> None:
    # Clear all at once instead of incremental updates
    self.table.clear()

    # Batch add rows
    rows = [[str(item.id), item.name, f"{item.score:.4f}"] for item in data]
    for row in rows:
        self.table.add_row(*row)
```

### 2. Lazy Loading
```python
class LargeDataWidget(Static):
    def on_mount(self) -> None:
        # Load data in background
        self.set_timer(0.1, self.load_data_async)

    def load_data_async(self) -> None:
        # Use thread pool for heavy data loading
        with ThreadPoolExecutor() as executor:
            future = executor.submit(self.fetch_large_dataset)
            data = future.result()
            self.update_display(data)
```

### 3. Debouncing Updates
```python
class ResponsiveWidget(Static):
    def on_input_changed(self, event: Input.Changed) -> None:
        # Cancel previous timer
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()

        # Start new timer
        self.update_timer = self.set_timer(0.5, self.perform_update)
```

## Debugging Tips

### 1. Logging
```python
import logging

class DebugWidget(Static):
    def action_debug(self) -> None:
        logging.debug(f"Selected index: {self.selected_index}")
        logging.debug(f"Data cache size: {len(self.data_cache)}")

        # Log current table state
        for row_idx in range(self.table.row_count):
            row = self.table.get_row(row_idx)
            logging.debug(f"Row {row_idx}: {row}")
```

### 2. Visual Debugging
```python
CSS = """
/* Debug styles */
.debug-highlight {
    background: red;
    border: solid yellow;
}
"""

def toggle_debug_mode(self) -> None:
    for widget in self.query("Widget"):
        widget.toggle_class("debug-highlight")
```

### 3. Console Output
```python
def debug_layout(self) -> None:
    print("=== Widget Hierarchy ===")
    for widget in self.walk_children():
        print(f"{widget.__class__.__name__} (id={widget.id}, classes={widget.classes})")
```

## Testing Textual Apps

**Note**: CIE currently has no test infrastructure. The following shows how testing would work when added.

### Unit Testing Widgets (Future Implementation)
```python
from textual.app import App
from textual.testing import AppTest

async def test_widget_behavior():
    app = AppTest(MyApp())
    async with app.run_test() as pilot:
        # Test widget interactions
        await pilot.click("#my_button")
        await pilot.press("o")
        
        # Assert state
        status_widget = app.query_one("#status", Label)
        assert "expected" in status_widget.renderable.lower()
```

### Testing User Flows (Future Implementation)
```python
async def test_complete_workflow():
    app = AppTest(MyApp())
    async with app.run_test() as pilot:
        # Simulate complete user workflow
        await pilot.click("#opti_table")
        await pilot.press("o")  # Run optimization
        
        # Verify policy was proposed
        evals_panel = app.query_one("#evals", EvalsPanel)
        assert evals_panel.current_policy is not None
```

## Resources and References

### Official Documentation
- [Textual Documentation](https://textual.textualize.dev/)
- [Textual GitHub Repository](https://github.com/Textualize/textual)
- [Textual Widget Reference](https://textual.textualize.dev/widgets/)

### CIE-Specific Implementation Notes

**Current Status**:
- Uses Textual ≥0.47 API (older but stable)
- Single-file architecture (`main.py` ≈650 lines)
- Mock implementations ready for replacement
- No test infrastructure yet

**Key Patterns Used**:
- **App Composition**: `compose()` method for widget setup
- **Message System**: Custom messages for panel communication
- **Reactive Properties**: Automatic UI updates on state changes
- **CSS Styling**: Consistent visual design
- **Screen Management**: Modal dialogs for configuration (using `ModalScreen as Modal`)
- **Event Handling**: Keyboard shortcuts and mouse interactions
- **Data Display**: DataTable for tabular data presentation

**Best Practices from CIE Implementation**:
- **Consistent Panel Pattern**: Each panel has compose(), on_mount(), action_*() methods
- **Message-Based Architecture**: Decoupled components communicate via messages
- **Centralized State**: Single backend instance manages all data
- **Reactive Updates**: UI automatically reflects backend changes
- **Keyboard-First Design**: Full functionality accessible via keyboard
- **Clear Visual Hierarchy**: Consistent styling and layout patterns

### Migration Notes
When upgrading to newer Textual versions:
- Update import paths (e.g., `ModalScreen` → `ModalScreen` without alias)
- Review API changes in event handling
- Test CSS styling compatibility
- Update testing patterns if adding test infrastructure

This guide covers the Textual patterns and techniques used throughout the CIE project. Understanding these concepts is essential for effective development and maintenance of the application.
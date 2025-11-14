"""
Onboarding wizard and tutorial system.
"""

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ProgressBar, Static


class OnboardingStep:
    """A single step in the onboarding process."""

    def __init__(
        self,
        title: str,
        content: str,
        action: str | None = None,
        action_label: str = "Try it",
        validation: Any = None,
    ):
        self.title = title
        self.content = content
        self.action = action
        self.action_label = action_label
        self.validation = validation


class OnboardingWizard(ModalScreen):
    """First-run onboarding wizard."""

    BINDINGS = [
        Binding("escape", "skip", "Skip"),
        Binding("right,l", "next_step", "Next"),
        Binding("left,h", "prev_step", "Previous"),
        Binding("enter", "action", "Continue"),
    ]

    def __init__(self):
        super().__init__(classes="onboarding-wizard")
        self.current_step = 0
        self.steps = self._create_steps()

    def _create_steps(self) -> list[OnboardingStep]:
        """Create onboarding steps."""
        return [
            OnboardingStep(
                "Welcome to CIE",
                """Welcome to the CIE Optimization & Evaluation Framework!

CIE helps you optimize AI model parameters using various algorithms
and evaluate their performance across different workloads.

This quick tour will help you get started with the key features.""",
                None,
                "Get Started",
            ),
            OnboardingStep(
                "Setting Up Your Backend",
                """First, let's configure your backend settings.

CIE supports multiple storage backends:
• SQLite - Best for production use
• JSON - Human-readable, great for development
• Memory - Fast, for testing only

You can also configure your AI model provider:
• OpenAI - GPT models
• Kimi - Kimi AI models
• Mock - For testing without API calls""",
                "show_config",
                "Open Config",
            ),
            OnboardingStep(
                "Understanding Optimizers",
                """Optimizers generate new policies to test.

Available optimizers:
• DSPy - Uses few-shot learning for optimization
• Hill Climbing - Iterative improvement algorithm
• Context-Aware - Optimizes based on context analysis

Select an optimizer in the Optimizers tab and press 'O' to run.""",
                "focus_optimizers",
                "View Optimizers",
            ),
            OnboardingStep(
                "Running Evaluations",
                """Evaluations test policies against workloads.

After generating a policy:
1. Go to the Evaluations tab
2. Select a workload
3. Press 'E' to run evaluation

Metrics include latency, cost, success rate, and more.""",
                "focus_evaluations",
                "View Evaluations",
            ),
            OnboardingStep(
                "Analyzing Experiments",
                """The Experiments tab shows all your trials.

Key features:
• View all trial results
• Toggle Pareto frontier view (press 'P')
• Adopt successful policies (press 'A')
• Export results for analysis

Pareto frontier shows non-dominated solutions.""",
                "focus_experiments",
                "View Experiments",
            ),
            OnboardingStep(
                "Context Management",
                """CIE includes powerful context management tools.

Features:
• Inspect runtime context structure
• Compress large contexts
• Create views of important data
• Navigate context like a filesystem

Use Ctrl+/ to open the context navigator.""",
                "show_context_navigator",
                "Open Context Tools",
            ),
            OnboardingStep(
                "Keyboard Shortcuts",
                """Master these shortcuts for efficiency:

Global:
• Ctrl+R - Refresh all panels
• Tab/Shift+Tab - Navigate panels
• Ctrl+C - Quit
• F1 - Help
• Ctrl+Shift+P - Command palette

Panel-specific:
• O - Run optimizer
• E - Run evaluation
• A - Adopt policy
• P - Toggle Pareto view

Press Ctrl+Shift+P for command palette.""",
                None,
                "Practice",
            ),
            OnboardingStep(
                "You're Ready!",
                """You now know the basics of CIE!

Next steps:
1. Configure your API keys in settings
2. Run your first optimization
3. Evaluate different workloads
4. Analyze results in Experiments

Access this tutorial anytime with Ctrl+Shift+T.

Happy optimizing!""",
                None,
                "Start Using CIE",
            ),
        ]

    def compose(self) -> ComposeResult:
        """Compose the onboarding wizard."""
        with Center(id="onboarding_center"):
            with Vertical(id="onboarding_container"):
                # Header
                yield Label("CIE Onboarding", id="onboarding_header")

                # Progress
                self.progress = ProgressBar(
                    total=len(self.steps),
                    show_eta=False,
                    show_percentage=True,
                    id="onboarding_progress",
                )
                yield self.progress

                # Content area
                with Vertical(id="onboarding_content"):
                    self.step_title = Label("", id="step_title")
                    yield self.step_title

                    self.step_content = Static("", id="step_content")
                    yield self.step_content

                # Navigation
                with Horizontal(id="onboarding_nav"):
                    self.prev_button = Button("← Previous", id="prev_button")
                    yield self.prev_button

                    self.action_button = Button("", id="action_button")
                    yield self.action_button

                    self.next_button = Button("Next →", id="next_button")
                    yield self.next_button

                    self.skip_button = Button("Skip Tour", id="skip_button")
                    yield self.skip_button

    def on_mount(self) -> None:
        """Initialize when mounted."""
        self.show_step(0)

    def show_step(self, index: int) -> None:
        """Show a specific step."""
        if 0 <= index < len(self.steps):
            self.current_step = index
            step = self.steps[index]

            # Update content
            self.step_title.update(f"Step {index + 1}/{len(self.steps)}: {step.title}")
            self.step_content.update(step.content)

            # Update progress
            self.progress.progress = index + 1

            # Update buttons
            self.prev_button.disabled = index == 0
            self.next_button.disabled = index == len(self.steps) - 1

            if step.action:
                self.action_button.label = step.action_label
                self.action_button.display = True
            else:
                self.action_button.display = False

            # Update navigation label for last step
            if index == len(self.steps) - 1:
                self.next_button.label = "Finish"

    def action_next_step(self) -> None:
        """Go to next step."""
        if self.current_step < len(self.steps) - 1:
            self.show_step(self.current_step + 1)
        else:
            self.dismiss()

    def action_prev_step(self) -> None:
        """Go to previous step."""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def action_action(self) -> None:
        """Execute step action."""
        step = self.steps[self.current_step]
        if step.action:
            # Execute action on app
            if hasattr(self.app, f"action_{step.action}"):
                getattr(self.app, f"action_{step.action}")()

    def action_skip(self) -> None:
        """Skip the tour."""
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "next_button":
            self.action_next_step()
        elif button_id == "prev_button":
            self.action_prev_step()
        elif button_id == "action_button":
            self.action_action()
        elif button_id == "skip_button":
            self.action_skip()


class TutorModal(ModalScreen):
    """Interactive tutor with contextual tips."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("?", "show_tips", "Tips"),
    ]

    def __init__(self, context: str = "general"):
        super().__init__(classes="tutor-modal")
        self.context = context
        self.tips = self._get_contextual_tips()

    def _get_contextual_tips(self) -> list[dict[str, str]]:
        """Get tips based on context."""
        tips = {
            "general": [
                {
                    "title": "Quick Navigation",
                    "content": "Use Tab/Shift+Tab to move between panels",
                },
                {
                    "title": "Command Palette",
                    "content": "Press Ctrl+Shift+P to access all commands",
                },
                {"title": "Refresh Data", "content": "Press Ctrl+R to refresh all panels"},
            ],
            "optimizers": [
                {
                    "title": "Run Optimizer",
                    "content": "Select an optimizer and press 'O' to generate a policy",
                },
                {
                    "title": "Configure",
                    "content": "Press Shift+O to configure the selected optimizer",
                },
                {"title": "View Details", "content": "Press Enter to see optimizer details"},
            ],
            "evaluations": [
                {"title": "Run Evaluation", "content": "Press 'E' to evaluate current policy"},
                {
                    "title": "Change Workload",
                    "content": "Use arrow keys to select different workloads",
                },
                {"title": "Baseline", "content": "Press 'B' to set current as baseline"},
            ],
            "experiments": [
                {"title": "Pareto View", "content": "Press 'P' to toggle Pareto frontier view"},
                {
                    "title": "Adopt Policy",
                    "content": "Select a trial and press 'A' to adopt its policy",
                },
                {"title": "Export", "content": "Press 'X' to export results"},
            ],
            "context": [
                {
                    "title": "Capture Context",
                    "content": "Press 'C' to capture current runtime context",
                },
                {
                    "title": "Navigate",
                    "content": "Use 'ls', 'cd', 'pwd' commands to navigate context",
                },
                {"title": "Optimize", "content": "Press 'O' to run context optimization"},
            ],
        }

        return tips.get(self.context, tips["general"])

    def compose(self) -> ComposeResult:
        """Compose the tutor modal."""
        with Center():
            with Vertical(id="tutor_container"):
                yield Label(f"💡 Tips: {self.context.title()}", id="tutor_header")

                with Vertical(id="tips_list"):
                    for tip in self.tips:
                        with Horizontal(classes="tip_item"):
                            yield Label(f"• {tip['title']}:", classes="tip_title")
                            yield Label(tip["content"], classes="tip_content")

                yield Label("Press '?' for more tips • ESC to close", id="tutor_footer")

                with Horizontal(id="tutor_buttons"):
                    yield Button("Got it!", id="close_tutor")
                    yield Button("Full Tutorial", id="full_tutorial")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close_tutor":
            self.dismiss()
        elif event.button.id == "full_tutorial":
            self.dismiss()
            self.app.push_screen(OnboardingWizard())

    def action_show_tips(self) -> None:
        """Show additional tips."""
        # Cycle through different tip categories
        categories = ["general", "optimizers", "evaluations", "experiments", "context"]
        current_index = categories.index(self.context) if self.context in categories else 0
        next_context = categories[(current_index + 1) % len(categories)]

        self.context = next_context
        self.tips = self._get_contextual_tips()

        # Update display
        header = self.query_one("#tutor_header", Label)
        header.update(f"💡 Tips: {self.context.title()}")

        # Clear and rebuild tips list
        tips_list = self.query_one("#tips_list")
        tips_list.remove_children()

        for tip in self.tips:
            with Horizontal(classes="tip_item"):
                tips_list.mount(Label(f"• {tip['title']}:", classes="tip_title"))
                tips_list.mount(Label(tip["content"], classes="tip_content"))

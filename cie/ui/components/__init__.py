"""
CIE UI Components - Modular UI building blocks.
"""

from cie.ui.components.charts import ChartWidget, MetricsChart, ParetoChart, SparklineChart
from cie.ui.components.command import CommandPalette, CommandRegistry, create_default_registry
from cie.ui.components.context_navigator import ContextNavigator
from cie.ui.components.onboarding import OnboardingWizard, TutorModal
from cie.ui.components.status import StatusBar, StatusIndicator
from cie.ui.components.tables import EnhancedDataTable, SelectableTable

__all__ = [
    # Status components
    "StatusBar",
    "StatusIndicator",
    # Chart components
    "ChartWidget",
    "SparklineChart",
    "MetricsChart",
    "ParetoChart",
    # Command system
    "CommandPalette",
    "CommandRegistry",
    "create_default_registry",
    # Table components
    "EnhancedDataTable",
    "SelectableTable",
    # Context tools
    "ContextNavigator",
    # Onboarding system
    "OnboardingWizard",
    "TutorModal",
]

# Version info
__version__ = "0.2.0"
__author__ = "CIE Team"

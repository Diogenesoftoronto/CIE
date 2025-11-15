"""
CIE UI Components - Modular UI building blocks.
"""

from cie.ui.components.cards import MetricCard, MetricGrid
from cie.ui.components.charts import ChartWidget, MetricsChart, ParetoChart, SparklineChart
from cie.ui.components.command import CommandPalette, CommandRegistry, create_default_registry
from cie.ui.components.context_navigator import ContextNavigator
from cie.ui.components.onboarding import OnboardingWizard, TutorModal
from cie.ui.components.status import StatusBar, StatusIndicator
from cie.ui.components.system_metrics import SystemMetricsPanel
from cie.ui.components.top_bar import CITopBar
from cie.ui.components.tables import EnhancedDataTable, SelectableTable

__all__ = [
    # Status components
    "StatusBar",
    "StatusIndicator",
    "CITopBar",
    # Chart components
    "ChartWidget",
    "SparklineChart",
    "MetricsChart",
    "ParetoChart",
    # Metric cards
    "MetricCard",
    "MetricGrid",
    "SystemMetricsPanel",
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

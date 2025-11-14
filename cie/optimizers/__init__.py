"""Optimization algorithms for CIE."""

from cie.optimizers.context_optimizer import (
    ContextAwareOptimizer,
    ContextCompressionOptimizer,
    ContextNavigationOptimizer,
)
from cie.optimizers.dspy_optimizer import DSPyOptimizer
from cie.optimizers.hill_climb import HillClimbOptimizer

__all__ = [
    # Traditional optimizers
    "DSPyOptimizer",
    "HillClimbOptimizer",
    # Context-aware optimizers
    "ContextAwareOptimizer",
    "ContextCompressionOptimizer",
    "ContextNavigationOptimizer",
]

# Version info
__version__ = "0.2.0"
__author__ = "CIE Team"

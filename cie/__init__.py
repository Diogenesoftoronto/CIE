"""
CIE (Optimization & Evaluation) - A Python TUI for running optimization experiments.
This package provides an interactive interface for running optimization experiments
using different algorithms and evaluating their performance across various workloads.
"""

__version__ = "0.2.0"
__author__ = "CIE Team"
__description__ = "Optimization & Evaluation TUI Application"
from cie.core.backend import CIEBackend
from cie.core.models import Policy, Trial

__all__ = ["Policy", "Trial", "CIEBackend"]

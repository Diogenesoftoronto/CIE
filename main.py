"""Legacy entrypoint that proxies to the package implementation."""

from cie.core.backend import CIEBackend
from cie.core.models import Policy, Trial
from cie.ui.app import main as run_tui_app

__all__ = ["CIEBackend", "Policy", "Trial", "main"]


def main() -> None:
    """Launch the CIE Textual application."""
    run_tui_app()


if __name__ == "__main__":
    main()

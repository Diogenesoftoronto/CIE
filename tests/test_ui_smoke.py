"""Smoke test for the Textual TUI to catch CSS regressions."""

from __future__ import annotations

import pytest

from cie.config.settings import CIEConfig
from cie.ui.app import CIEOptimEvalsApp


@pytest.mark.asyncio
async def test_tui_smoke() -> None:
    """Run the app in Textual's test harness to ensure it composes."""

    app = CIEOptimEvalsApp(CIEConfig())
    async with app.run_test() as pilot:
        await pilot.pause()

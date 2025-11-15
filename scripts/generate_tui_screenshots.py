#!/usr/bin/env python3
"""Generate reusable CIE TUI screenshots for the paper."""

from __future__ import annotations

import asyncio
import io
import os
from pathlib import Path
from typing import Iterable

try:  # Optional dependency used for bitmap exports
    import cairosvg
except ImportError:  # pragma: no cover - runtime optional
    cairosvg = None

try:  # Optional dependency for JPEG conversion
    from PIL import Image
except ImportError:  # pragma: no cover - runtime optional
    Image = None

from cie.config.settings import get_config
from cie.core.backend import set_backend
from cie.demo import create_demo_backend
from cie.ui.app import CIEOptimEvalsApp


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "papers" / "assets"
MAIN_SCREENSHOT = OUTPUT_DIR / "tui-main.svg"
CONTEXT_SCREENSHOT = OUTPUT_DIR / "tui-context.svg"
WEIGHTS_SCREENSHOT = OUTPUT_DIR / "tui-weights.svg"
CONFIG_SCREENSHOT = OUTPUT_DIR / "tui-config.svg"
CONTEXT_TOOLS_SCREENSHOT = OUTPUT_DIR / "tui-context-tools.svg"
TUTOR_SCREENSHOT = OUTPUT_DIR / "tui-tutor.svg"
ONBOARDING_SCREENSHOT = OUTPUT_DIR / "tui-onboarding.svg"
BITMAP_FORMATS = ("png", "jpg")
TERMINAL_SIZE = (160, 48)


def _convert_svg(svg_path: Path, formats: Iterable[str] = BITMAP_FORMATS) -> None:
    """Convert SVG screenshots into easier-to-share bitmap formats."""
    if cairosvg is None:  # pragma: no cover - optional tool
        print(
            "[screenshots] CairoSVG not installed; skipping PNG/JPG export. "
            "Run `pip install cairosvg pillow` to enable bitmap output."
        )
        return

    svg_url = str(svg_path)
    for fmt in formats:
        suffix = ".jpeg" if fmt.lower() in {"jpeg", "jpg"} else ".png"
        out_path = svg_path.with_suffix(suffix)

        if fmt.lower() == "png":
            cairosvg.svg2png(url=svg_url, write_to=str(out_path))
            print(f"[screenshots] → {out_path.name}")
            continue

        if fmt.lower() in {"jpg", "jpeg"}:
            if Image is None:  # pragma: no cover
                print(
                    "[screenshots] Pillow not installed; skipping JPEG export "
                    "(install pillow for JPG support)."
                )
                continue
            buffer = io.BytesIO()
            cairosvg.svg2png(url=svg_url, write_to=buffer)
            buffer.seek(0)
            with Image.open(buffer) as image:
                if image.mode in {"RGBA", "LA"}:
                    background = Image.new("RGB", image.size, "#111417")
                    background.paste(image, mask=image.split()[-1])
                    image = background
                image.save(out_path, format="JPEG", quality=92, optimize=True)
            print(f"[screenshots] → {out_path.name}")


async def _capture() -> None:
    """Launch the demo TUI headlessly and export SVG + bitmap screenshots."""
    config = get_config()
    backend, demo_metadata = create_demo_backend(config)
    set_backend(backend)
    app = CIEOptimEvalsApp(backend.config, demo_mode=True, demo_metadata=demo_metadata)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[screenshots] starting headless session")
    async with app.run_test(headless=True, size=TERMINAL_SIZE) as pilot:
        print("[screenshots] pilot ready")
        await pilot.pause(1.2)
        app.save_screenshot(str(MAIN_SCREENSHOT))
        _convert_svg(MAIN_SCREENSHOT)
        print("[screenshots] captured main layout")

        app.action_focus_context()
        await pilot.pause(0.8)
        app.save_screenshot(str(CONTEXT_SCREENSHOT))
        _convert_svg(CONTEXT_SCREENSHOT)
        print("[screenshots] captured context panel")

        async def capture_modal(action, path: Path, delay: float = 0.8) -> None:
            action()
            await pilot.pause(delay)
            app.save_screenshot(str(path))
            _convert_svg(path)
            await pilot.press("escape")
            await pilot.pause(0.4)
            print(f"[screenshots] captured {path.name}")

        await capture_modal(app.action_show_weights, WEIGHTS_SCREENSHOT)
        await capture_modal(app.action_show_config, CONFIG_SCREENSHOT)
        await capture_modal(app.action_show_context_tools, CONTEXT_TOOLS_SCREENSHOT)
        await capture_modal(app.action_show_tutor, TUTOR_SCREENSHOT)
        await capture_modal(app.action_show_onboarding, ONBOARDING_SCREENSHOT)

        await pilot.exit(None)
        await pilot.pause(0.1)
    # Textual's shutdown sequence can hang in headless mode for this app, so exit hard.
    os._exit(0)


def capture_demo_screenshots() -> None:
    """Entry point used by scripts and CLI."""
    asyncio.run(_capture())


if __name__ == "__main__":
    capture_demo_screenshots()

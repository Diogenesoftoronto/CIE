#!/usr/bin/env python3
"""Generate SVG charts for benchmark results used in the paper."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "papers" / "assets" / "benchmark-report.txt"
METRICS_PATH = ROOT / "papers" / "assets" / "benchmark-metrics.json"
PASSRATE_PATH = ROOT / "papers" / "assets" / "benchmark-passrates.svg"
METRICS_CHART_PATH = ROOT / "papers" / "assets" / "benchmark-metrics-summary.svg"


@dataclass
class Entry:
    label: str
    passed: int
    total: int

    @property
    def pct(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed / self.total * 100.0


def parse_section(text: str, header: str) -> list[Entry]:
    """Parse a block such as 'BY DIFFICULTY' or 'BY CATEGORY'."""
    pattern = re.compile(rf"{header}\s*-+\s*(.*?)\n\n", re.S)
    match = pattern.search(text + "\n\n")
    if not match:
        raise ValueError(f"Could not locate {header} block in benchmark report")
    block = match.group(1)
    entries: list[Entry] = []
    line_re = re.compile(r"\s*([a-zA-Z ]+?)\s+(\d+)/\s*(\d+)")
    for line in block.strip().splitlines():
        m = line_re.match(line)
        if not m:
            continue
        label, passed, total = m.group(1).strip(), int(m.group(2)), int(m.group(3))
        entries.append(Entry(label=label.title(), passed=passed, total=total))
    return entries


def svg_chart(datasets: list[tuple[str, list[Entry]]], *, width: int = 900, height: int = 380) -> str:
    """Render a simple dual horizontal bar chart as SVG."""
    padding = 20
    chart_width = (width - padding * 3) // 2
    chart_height = height - padding * 2 - 20
    bar_padding = 8
    palette = ["#2563eb", "#7c3aed", "#0f172a", "#be185d", "#0d9488", "#ea580c", "#a21caf"]

    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Benchmark pass rates">',
        f'<rect width="{width}" height="{height}" fill="#f8fafc" rx="8"/>',
        f'<text x="{width/2}" y="24" text-anchor="middle" font-size="18" '
        f'font-weight="600" fill="#0f172a">Benchmark Pass Rates</text>',
    ]

    for idx, (title, entries) in enumerate(datasets):
        x_origin = padding + idx * (chart_width + padding)
        y_origin = padding + 35
        pieces.append(
            f'<text x="{x_origin}" y="{padding + 20}" font-size="14" font-weight="600" '
            f'fill="#0f172a">{title}</text>'
        )
        if not entries:
            continue
        bar_h = (chart_height - bar_padding * (len(entries) - 1)) / len(entries)
        for i, entry in enumerate(entries):
            y = y_origin + i * (bar_h + bar_padding)
            bar_len = chart_width * (entry.pct / 100.0)
            color = palette[i % len(palette)]
            pieces.append(
                f'<rect x="{x_origin}" y="{y}" width="{bar_len}" height="{bar_h}" '
                f'rx="4" fill="{color}" opacity="0.85"/>'
            )
            pieces.append(
                f'<text x="{x_origin + 4}" y="{y + bar_h / 2 + 4}" fill="#f8fafc" font-size="12" '
                f'font-weight="600">{entry.label}</text>'
            )
            pieces.append(
                f'<text x="{x_origin + bar_len + 6}" y="{y + bar_h / 2 + 4}" fill="#0f172a" '
                f'font-size="12" font-weight="500">{entry.passed}/{entry.total} '
                f'({entry.pct:.1f}%)</text>'
            )
        # axis
        pieces.append(
            f'<line x1="{x_origin}" y1="{y_origin + chart_height}" x2="{x_origin + chart_width}" '
            f'y2="{y_origin + chart_height}" stroke="#94a3b8" stroke-width="1"/>'
        )
        for pct in range(0, 101, 20):
            px = x_origin + chart_width * (pct / 100.0)
            pieces.append(
                f'<line x1="{px}" y1="{y_origin + chart_height}" x2="{px}" '
                f'y2="{y_origin + chart_height + 6}" stroke="#94a3b8" stroke-width="1"/>'
            )
            pieces.append(
                f'<text x="{px}" y="{y_origin + chart_height + 18}" font-size="10" '
                f'fill="#475569" text-anchor="middle">{pct}%</text>'
            )

    pieces.append(
        '<text x="{x}" y="{y}" font-size="11" fill="#475569"></text>'.format(
            x=padding, y=height - 6
        )
    )
    pieces.append("</svg>")
    return "\n".join(pieces)


def svg_metric_bars(data: dict[str, float]) -> str:
    """Render a bar chart summarizing aggregate metrics."""
    width, height = 720, 360
    padding = 40
    bar_width = 80
    gap = 30
    bars = [
        ("Pass Rate", data["pass_rate"], 100.0, "Tasks passed"),
        ("Composite", data["average_composite_score"], 100.0, "Weighted score"),
        ("Code Quality", data["average_code_quality"], 100.0, "0-100 rubric"),
        ("Autonomy", data["average_autonomy"], 100.0, "0-100 rubric"),
        ("Tool Efficiency", data["average_tool_efficiency"] * 100.0, 100.0, "Successful calls"),
    ]

    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Benchmark metric summary">',
        f'<rect width="{width}" height="{height}" fill="#f8fafc" rx="8"/>',
        f'<text x="{width/2}" y="30" text-anchor="middle" font-size="18" font-weight="600" '
        f'fill="#0f172a">Aggregate Metrics</text>',
    ]

    for index, (label, value, max_value, tooltip) in enumerate(bars):
        x = padding + index * (bar_width + gap)
        normalized = max(0.0, min(1.0, value / max_value if max_value else 0.0))
        bar_height = (height - padding * 2) * normalized
        y = height - padding - bar_height
        pieces.append(
            f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" rx="6" '
            f'fill="#2563eb" opacity="0.85">'
            f'<title>{tooltip}: {value:.1f}</title>'
            "</rect>"
        )
        pieces.append(
            f'<text x="{x + bar_width / 2}" y="{y - 8}" text-anchor="middle" font-size="12" '
            f'font-weight="600" fill="#0f172a">{value:.1f}</text>'
        )
        pieces.append(
            f'<text x="{x + bar_width / 2}" y="{height - padding / 2}" text-anchor="middle" '
            f'font-size="12" font-weight="500" fill="#0f172a">{label}</text>'
        )

    pieces.append(
        f'<text x="{padding}" y="{height - 10}" font-size="12" fill="#475569">'
        f'Total tool calls: {int(data["total_tool_calls"])} • '
        f'Total errors: {int(data["total_errors"])} • '
        f'Duration: {data["total_duration_seconds"]:.2f}s'
        "</text>"
    )
    pieces.append("</svg>")
    return "\n".join(pieces)


def main() -> None:
    report_text = REPORT_PATH.read_text()
    diff = parse_section(report_text, "BY DIFFICULTY")
    cat = parse_section(report_text, "BY CATEGORY")
    passrates_svg = svg_chart(
        [
            ("Difficulty", diff),
            ("Category", cat),
        ]
    )
    PASSRATE_PATH.write_text(passrates_svg)
    print(f"Wrote {PASSRATE_PATH}")

    metrics_data = json.loads(METRICS_PATH.read_text())
    metrics_svg = svg_metric_bars(metrics_data)
    METRICS_CHART_PATH.write_text(metrics_svg)
    print(f"Wrote {METRICS_CHART_PATH}")


if __name__ == "__main__":
    main()

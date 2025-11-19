# Typst Authoring Guide for CIE

This note captures the conventions we follow while editing paper assets under `papers/` and mirrors the official Typst reference (<https://typst.app/docs/reference/>). Keep it handy before touching `cie-paper.typ`.

## Project Layout Expectations
- **Assets live in `papers/assets/`**. Generate figures (SVG/PNG) via scripts in `scripts/` so they can be reproduced on CI. `scripts/generate_tui_screenshots.py` exports the main/context views plus the weights, config, context-tools, tutor, and onboarding overlays; `scripts/generate_benchmark_charts.py` reads `benchmark-report.txt`/`benchmark-metrics.json` to produce the pass-rate and metric-summary charts.
- **Typst sources stay ASCII**. Prefer programmatic diagrams/images rather than heavy inline drawing DSLs when the chart logic already exists in Python.
- **Rebuild PDFs with `typst compile`**. Always run `typst compile papers/cie-paper.typ papers/cie-paper.pdf` locally and capture warnings (missing labels, unescaped identifiers).

## Figure & Table Patterns
- Wrap every visual in `#figure(..., caption: figure_caption[...])` so Typst handles numbering and cross references automatically.
- Use `grid` for multi-panel layouts (`columns: (1fr, 1fr)`), and `table` for structured numeric summaries (set `stroke` + `align`).
- When embedding generated SVG/PNG assets, call `image("assets/<name>.svg", width: 100%)`. Typst resolves paths relative to the `.typ` file.
- For inline math inside tables/captions, rely on `#math.equation` or `$ ... $`. Avoid stray underscores (`__`) in code blocks; Typst warns when identifiers such as `__init__` appear outside `#code_block`.

## Referencing External Data
- Keep raw benchmark/context metrics under `papers/assets/*.json` (e.g., `benchmark-metrics.json`). Scripts should consume these JSON/TXT files and emit reproducible figures.
- Document each script at the point of use (captions or footnotes) so readers know how to regenerate the asset.

## Helpful Typst Snippets
```typst
#figure(
  table(
    columns: (auto, auto, auto),
    stroke: 0.5pt + luma(150),
    align: (left, center, center),
    [*Metric*], [*Mean*], [*Std Dev*],
    [Latency], [245], [±78],
  ),
  caption: figure_caption[
    *Aggregate benchmark metrics.* Source: `papers/assets/benchmark-metrics.json`.
  ]
)
```

```typst
#figure(
  grid(
    columns: (1fr, 1fr),
    gutter: 1em,
    [
      image("assets/tui-main.svg", width: 100%)
    ],
    [
      image("assets/tui-context.svg", width: 100%)
    ],
  ),
  caption: figure_caption[
    *Textual demo screenshots.* Generated via `scripts/generate_tui_screenshots.py`.
  ]
)
```

## Workflow Checklist
1. Update or add a script under `scripts/` for any derived figure.
2. Run the script to refresh SVG/PNG artifacts in `papers/assets/`.
3. Edit `cie-paper.typ`, referencing the new asset and citing the script in the caption.
4. Compile with Typst and verify there are no missing labels.
5. Commit both the updated `.typ`, `.pdf`, and regenerated assets/script changes when ready.

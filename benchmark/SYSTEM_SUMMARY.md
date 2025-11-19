# CIE Context Benchmark – Architecture Summary

## Executive Summary

The benchmark suite validates whether an agent can execute CIE’s **context-aware optimization loop**:

1. Capture and inspect its working memory (snapshots, node counts, hotspots).
2. Apply compression / reorganization strategies guided by guardrails.
3. Evaluate the effect on multi-objective metrics (latency, cost, context efficiency).
4. Automate workflows so context hygiene becomes part of CI/CD.

The previous “navigation/comprehension” framing has been retired in favor of context-centric pillars. This mirrors the paper’s thesis: **autonomous agents must manage their context, not treat it as an opaque blob.**

---

## Directory Layout

```
benchmark/
├── tasks.py            # Context-centric tasks (capture → optimize → export)
├── runner.py           # Executes tasks, tracks guardrails, emits reports
├── metrics.py          # TaskMetrics + BenchmarkMetrics (context-aware fields)
├── cli.py              # run/list/stats commands (wired to new categories)
├── README.md           # This document’s short-form sibling
├── example_usage.py    # Programmatic recipes (now referencing context tasks)
└── templates/          # Workflow stubs for automating capture/optimization
```

Key changes:

- `TaskCategory` now includes `context-awareness`, `context-optimization`, `context-performance`, `context-autonomy`.
- Task definitions reference CIE components directly (ContextNavigator, guardrails, status panel).
- Aggregate metrics emphasize compression ratio and context efficiency.

---

## Task Inventory

| Difficulty | Tasks (abridged titles) | Focus |
| ---------- | ----------------------- | ----- |
| **TRIVIAL** | Capture snapshot • Map context roots • Identify large files | Learn `[CTX]` basics |
| **EASY** | Trace context hotspots • Explain optimizer hooks • Follow modal lifecycle | Understand wiring |
| **MEDIUM** | Diagnose context drift • Add guard config • Add `context_efficiency` metric • Test compression | Modify config/code |
| **HARD** | Build context efficiency evaluator • Fix context scoring • Refactor optimizer context handling | Implement + debug |
| **EXPERT** | End-to-end context workflow • Context cache layer • Telemetry across stack | Automate & instrument |

Each task has a success rubric tailored to context metrics (e.g., capture proof, guardrail thresholds, compression gains).

---

## Metrics Pipeline

1. **Task Execution** – `BenchmarkRunner` invokes your executor, just like before.
2. **Metrics Collection** – `MetricsCollector.record_task` now populates additional fields:
   - `context_efficiency`
   - `compression_ratio`
   - `context_size_kb`
   - Guardrail counters
3. **Reporting** – `runner.generate_report()` emits the same textual report; the JSON output feeds the Typst figures via `scripts/generate_benchmark_charts.py`.

Composite scoring weights context metrics heavily, reflecting the paper’s emphasis on ≥2× compression with latency/cost guardrails intact.

---

## API Compatibility

All public APIs remain backwards-compatible. Existing automation that imports `BenchmarkRunner`, `BenchmarkTask`, or CLI commands will continue to work. The only breaking changes are semantic—task names, descriptions, and categories now represent context work.

If you previously filtered by `navigation`, switch to the new categories:

```python
from benchmark.tasks import get_tasks_by_category, TaskCategory
context_tasks = get_tasks_by_category(TaskCategory.CONTEXT_OPTIMIZATION)
```

---

## Alignment With The Paper

- **TUI/CLI parity:** Tasks refer to `[CTX]` actions, modals, and guardrails highlighted in `papers/cie-paper.typ`.
- **Benchmark artifacts:** `benchmark-report.txt` / `.json` are exactly the files the Typst build consumes.
- **Vision compliance:** Passing these tasks demonstrates the capability described in `vision.md`—self-aware agents that optimize their own context.

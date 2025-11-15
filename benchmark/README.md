# CIE Context Benchmark Suite

The benchmark suite mirrors the vision described in `vision.md`: **agents must understand, optimize, and operationalize their own context**. Instead of generic code-editing tasks, every scenario here asks an agent to use CIE’s context instrumentation (`[CTX]` panel, context tools modal, Pareto dashboards) to achieve measurable improvements.

## Capabilities Measured

| Pillar | Description |
| ------ | ----------- |
| **Context Awareness** | Capture snapshots, enumerate nodes, detect hotspots, and reason about where large objects originate. |
| **Context Optimization** | Apply compression/reorganization strategies, reconfigure guardrails, and test compression effects. |
| **Context Performance** | Measure how context efficiency correlates with latency/cost guardrails; debug scoring and drift. |
| **Context Autonomy** | Automate multi-step workflows (capture → optimize → evaluate → export) and emit telemetry for operators. |

Each benchmark task references core project concepts—ContextNavigator, context guardrails, compression strategies, Pareto analysis—so success means the agent aligned with the paper’s goals.

---

## Task Structure

### Difficulty Levels

| Level | Context-oriented Focus |
| ----- | ---------------------- |
| **TRIVIAL** | Capture snapshots, list context roots, identify large files to compress. |
| **EASY** | Trace where context tooling is wired, explain optimizer hooks, follow modal lifecycles. |
| **MEDIUM** | Diagnose context drift, add guard configuration, wire new context metrics, test compression helpers. |
| **HARD** | Build context efficiency evaluators, fix scoring logic for context metrics, refactor optimizers to handle context state cleanly. |
| **EXPERT** | Ship end-to-end context workflows, implement caching of snapshots, add telemetry across the stack. |

### Categories

The previous “navigation/comprehension” buckets have been replaced with categories that map directly to context introspection:

- `context-awareness`
- `context-optimization`
- `context-performance`
- `context-autonomy`
- `workflow` (reserved for multi-step orchestrations that tie the above pillars together)

---

## Quick Start

### Inspect Tasks

```bash
# List everything
python -m benchmark.cli list-tasks

# Only context optimization tasks
python -m benchmark.cli list-tasks --category context-optimization

# Only medium difficulty (diagnose drift, add metrics, test compression)
python -m benchmark.cli list-tasks --difficulty medium

# Detailed information for a single task
python -m benchmark.cli show-task medium_add_metric
```

### Run Benchmarks

```bash
# Run the full context benchmark with the mock executor
python -m benchmark.cli run --model "CIE Demo"

# Focus on the hard context-optimization tasks
python -m benchmark.cli run --difficulty hard --model "my-agent"

# Stop on first guardrail failure
python -m benchmark.cli run --stop-on-failure

# Persist artifacts just like the paper does
python -m benchmark.cli run --model "demo" \
  --output papers/assets/benchmark-report.txt \
  --json-output papers/assets/benchmark-metrics.json
```

---

## Metrics

Per-task metrics now emphasize context instrumentation:

- `context_efficiency`, `compression_ratio`, `context_size_kb`
- Tool-call stats (capture/optimize/export actions)
- Guardrail hits (context guard thresholds, Pareto regressions)
- Traditional fields (duration, code quality, autonomy) for compatibility

Aggregated metrics continue to use `BenchmarkMetrics`, but the default composite score weights context metrics heavily (see `benchmark/metrics.py`).

Scripts in `scripts/` transform the JSON artifacts into publication-ready visuals (`benchmark-passrates.svg`, `benchmark-metrics-summary.svg`) that align with the paper.

---

## Python API

Nothing about the API surface changed—`BenchmarkRunner`, `BenchmarkTask`, `MetricsCollector`, and the CLI remain stable. What changed is the **content** of the tasks and the **interpretation** of the metrics:

```python
from benchmark.runner import BenchmarkRunner
from benchmark.tasks import get_tasks_by_category, TaskCategory

runner = BenchmarkRunner(model_name="context-aware-agent")
context_tasks = get_tasks_by_category(TaskCategory.CONTEXT_OPTIMIZATION)

def executor(task):
    # Call into your agent/tooling; this function should manipulate CIE just like a human would.
    return run_my_agent(task)

runner.run_task_set(context_tasks, executor)
print(runner.generate_report())
```

Use `BenchmarkMetrics` to track whether your agent is meeting the paper’s bar: ≥2× compression, guardrail-friendly latency, and improved context efficiency.  

---

## Alignment With The Paper

- **Vision:** Tasks require agents to “see” and act on their working memory, not just edit files.
- **Benchmarks:** Difficulty scaling mirrors the paper’s ablation (baseline → monitoring → full optimization).
- **Artifacts:** The JSON/TXT outputs feed directly into the Typst figures and tables described in `papers/cie-paper.typ`.

If your agent performs well here, it isn’t just a decent coder—it is a context-aware optimizer ready to plug into CIE’s TUI, CLI, and benchmarking harness.***

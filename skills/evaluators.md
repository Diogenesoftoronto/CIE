# Evaluator Registry & Plugins

The CIE evaluator layer lives in `cie/evaluators/` and powers everything from the mock simulation to the real text-match workflow. This document covers how the registry works, how to build new evaluators, and how to plug them into the CLI + configuration system.

## Registry Overview

`cie/evaluators/__init__.py` exposes the public API:

- `register_evaluator(slug, factory, description="", tags=None)`: Register an evaluator factory. Called at import time by each evaluator module.
- `list_evaluators() -> list[EvaluatorRegistration]`: Returns metadata for CLI/UI consumption.
- `get_evaluator(slug, **kwargs) -> Evaluator`: Instantiates the requested evaluator or raises `ValueError`.
- Plugin auto-loader: Scans `cie/evaluators/plugins/` for additional modules so CIE can ship with lightweight or bespoke evaluators without modifying core code.

Every evaluator implements the `Evaluator` protocol from `cie/core/models.py`:

```python
class Evaluator(Protocol):
    name: str
    def run(self, policy: Policy, workload: Workload) -> dict[str, float]: ...
    def get_supported_metrics(self) -> list[str]: ...
    def validate_workload(self, workload: Workload) -> bool: ...
```

## Built-in Evaluators

### MockEvaluator (`cie/evaluators/mock_evaluator.py`)
- Fast, deterministic-friendly metric generator for development and tests.
- Accepts every workload and produces latency/cost/success/throughput/etc. with policy-dependent effects.
- Default evaluator (`evaluation.default_evaluator = "mock"`).

### TextMatchEvaluator (`cie/evaluators/text_match.py`)
- Real evaluator inspired by Braintrust’s reference checks.
- Executes predefined or workload-supplied cases through the configured model provider (OpenAI/Kimi/Mock), then scores:
  - `text_similarity` (1 - normalized Levenshtein distance)
  - `text_exact_match`
  - `text_levenshtein`
  - Standard system metrics (latency, cost, throughput, etc.)
- Supports workload-level case overrides (`workload.config["cases"]`) so each workload can tailor its prompts/reference answers.

## CLI & Configuration

- `cie evaluators` lists registered evaluators along with descriptions/tags.
- `cie evaluators --use text-match` updates `~/.cie/config.json` so future sessions default to the text-match evaluator.
- Config option: `evaluation.default_evaluator` (persisted in `CIEConfig`). The backend reflects the current evaluator slug via `StatusPanel`.

## Adding a New Evaluator

1. Create a module under `cie/evaluators/` or `cie/evaluators/plugins/`.
2. Implement an evaluator class that satisfies the protocol and registers itself:
   ```python
   from cie.evaluators import register_evaluator

   class MyEvaluator:
       name = "MyEvaluator"
       ...

   register_evaluator(
       "my-eval",
       lambda **kwargs: MyEvaluator(**kwargs),
       description="One-liner for CLI/docs",
       tags=("custom", "nlp"),
   )
   ```
3. If the evaluator requires external data (datasets, API keys), validate dependencies inside `run()` or `__init__()` and provide meaningful error messages.
4. Optionally add workload presets to `cie/core/backend.py` or let users specify `workload.config`.
5. Update README/AGENTS if the evaluator becomes part of the default experience.

## Tips

- Prefer deterministic randomness (seeded `random.Random`) when possible so tests remain stable.
- Surface key metrics in `get_supported_metrics()`; the UI will automatically add new columns once the backend includes them in trial data.
- Keep evaluator runtime under a few seconds to avoid blocking the TUI; long-running evaluators can stream progress via future messaging hooks.

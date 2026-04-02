# CIE code map (codedown)

This document augments the repo with **codedown-style** pointers: concrete paths you can open in your editor, plus diagrams produced by **[oxdraw](https://github.com/RohanAdwankar/oxdraw)**.

## Architecture at a glance

| Layer | Path | Role |
|--------|------|------|
| CLI entry | [`cmd/cie/main.go`](../cmd/cie/main.go) | `main` |
| Commands | [`internal/cli/`](../internal/cli/) | Cobra command tree (`optimize`, `tui`, `benchmark`, `wandb`, …) |
| Orchestration | [`internal/backend/`](../internal/backend/) | Trials, scoring, Pareto, adopt, W&B ingest |
| Domain | [`internal/core/`](../internal/core/) | `Policy`, `Trial`, `Workload` |
| Config | [`internal/config/`](../internal/config/) | JSON config, env API keys, **genai registry key** ([`genai_key.go`](../internal/config/genai_key.go)) |
| LLM (multi-provider) | [`internal/llm/`](../internal/llm/) | [`maruel/genai`](https://github.com/maruel/genai) chat helper |
| Optimizers | [`internal/optimizer/`](../internal/optimizer/) | HillClimb, RandomProbe, **OpenAI:PolicyJSON** ([`openai_opt.go`](../internal/optimizer/openai_opt.go)) |
| Evaluators | [`internal/evaluator/`](../internal/evaluator/) | mock, text-match |
| Storage | [`internal/storage/`](../internal/storage/) | memory, JSON, SQLite |
| TUI | [`internal/tui/`](../internal/tui/) | Bubble Tea app, context overlay |
| Traces | [`internal/trace/`](../internal/trace/) | **minitrace** session export for prompts |
| Benchmark | [`benchmark/`](../benchmark/) | Tasks, runner, `genai` / `caic` executors |

## Deterministic diagram (oxdraw, no AI)

From the repo root, oxdraw can build a **Mermaid** graph of symbols under `internal/` and render **SVG**:

- Source: [`codemap-internal.mmd`](codemap-internal.mmd)
- Rendered: [`codemap-internal.svg`](codemap-internal.svg)

Relationships are heuristic (call / reference scan); use the table above for the real module layout.

## AI codedown + MiniMax M2.7 + Charm `skate`

To generate **LLM-augmented** codedown or `--augment-markdown` output with MiniMax’s **OpenAI-compatible** API:

1. Store your MiniMax API key in **[Skate](https://github.com/charmbracelet/skate)** under the **`@secrets`** database (example key name: `minimax`):

   ```bash
   skate set minimax@secrets "$(cat ~/.minimax-api-key)"
   ```

2. Export it for **oxdraw** (never paste keys into markdown or commit them):

   ```bash
   export OXDRAW_API_KEY="$(skate get minimax@secrets)"
   ```

3. Run oxdraw against this repo using **MiniMax-M2.7** ([platform docs](https://platform.minimax.io/docs/api-reference/text-openai-api)):

   ```bash
   oxdraw --codedown . \
     --codedown-style architecture \
     --api-key "$OXDRAW_API_KEY" \
     --model "MiniMax-M2.7" \
     --api-url "https://api.minimax.io/v1" \
     -o docs/CODEDOWN-ai.md
   ```

   Or **augment** an existing doc in place:

   ```bash
   oxdraw --augment-markdown README.md \
     --repo-path . \
     --api-key "$OXDRAW_API_KEY" \
     --model "MiniMax-M2.7" \
     --api-url "https://api.minimax.io/v1"
   ```

**Compatibility note:** oxdraw’s HTTP client must hit an OpenAI-compatible `chat.completions` endpoint. If you see `404` from `api.minimax.io`, upgrade oxdraw, confirm your key, and verify MiniMax’s current base URL in their docs—then adjust `--api-url` accordingly.

## Mise shortcuts

See `.mise.toml` tasks `docs:codemap`, `docs:codemap-svg`, and `docs:codedown` (the latter wraps skate + MiniMax env vars).

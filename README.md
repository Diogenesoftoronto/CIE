# CIE (Optimization & Evaluation)

Terminal-first toolkit for running optimization experiments and multi-metric evaluation. The **CLI and TUI are written in Go** using [Charmbracelet](https://github.com/charmbracelet) (Bubble Tea, Bubbles, Lip Gloss) and [Cobra](https://github.com/spf13/cobra).

## Features

- **CLI**: `optimize`, `trials`, `optimizers`, `evaluators`, `workloads`, `adopt`, `stats`, `reset`, `init`, `validate-config`, `doctor`, **`wandb sync`**, **`benchmark run`**
- **TUI**: `cie tui` with sidebar panels and live stats (`ctrl+r` refresh, **`ctrl+/` context-tools sheet**)
- **Optimizers**: HillClimb, RandomProbe, **OpenAI:PolicyJSON** (OpenAI-compatible chat completions → JSON policy; replaces the old DSPy runtime)
- **W&B**: import offline `files/wandb-history.jsonl` into trials (`cie wandb sync`, or `CIE_WANDB_RUN`)
- **Benchmark harness**: Go port under `benchmark/` + `cie benchmark run` (plug in your own executor later)
- **Evaluators**: `mock` (synthetic metrics), `text-match` (Levenshtein / similarity on embedded text cases)
- **Storage**: `json` (under `~/.cie/experiments`), `sqlite` (pure Go via `modernc.org/sqlite`), `memory`
- **Scoring & Pareto**: weighted scores and non-dominated trial sets (same spirit as the prior Python implementation)

## Requirements

- Go **1.25+** (see `go.mod`)

## Getting started (mise)

If you use [mise](https://mise.jdx.dev/), the repo ships a `.mise.toml` with tasks and tool versions:

```bash
git clone https://github.com/cie-team/cie.git
cd cie
mise trust            # once per clone: allow .mise.toml tasks/tools
mise install          # pins Go (and Node for site/ work)
mise run setup        # go mod download
mise run              # interactive task picker, or:
mise run build        # ./cie binary
mise run test
mise run tui
mise run demo
```

Common tasks: `setup`, `build` (`b`), `test` (`t`), `vet`, `fmt`, `ci`, `doctor`, `init-config`, `benchmark`, `benchmark:genai`, `site:dev`, `docker-build`, `docs:diagram`, `docs:codedown`. Run `mise tasks` to list them with descriptions.

**Code map / codedown:** see [`docs/CODEDOWN.md`](docs/CODEDOWN.md) (oxdraw diagrams, file pointers, and MiniMax + `skate` workflow).

## Build and run (without mise)

```bash
git clone https://github.com/cie-team/cie.git
cd cie
go build -o cie ./cmd/cie
./cie --help
./cie tui
./cie tui --demo
```

Install on `$PATH`:

```bash
go install github.com/cie-team/cie/cmd/cie@latest
```

## Configuration

```bash
cie init --storage json --experiments-dir ~/.cie/experiments
```

Config file: `~/.cie/config.json` (JSON). Override with `cie -c /path/to/config.json …`.

Set default evaluator:

```bash
cie evaluators --use text-match
```

## Docker

```bash
docker build -t cie .
docker run --rm -it cie --help
```

## Layout

| Path | Purpose |
|------|---------|
| `cmd/cie` | `main` |
| `internal/backend` | orchestration, Pareto, adopt guardrails |
| `internal/cli` | Cobra commands |
| `internal/config` | JSON config load/save |
| `internal/core` | domain types |
| `internal/evaluator` | mock, text-match |
| `internal/optimizer` | hill climb, random |
| `internal/storage` | memory, JSON files, SQLite |
| `internal/tui` | Bubble Tea UI |

## Site and papers

The `site/` (Vite) and `papers/` directories are unchanged; they are not required to build or run the Go binary.

## License

MIT (see repository).

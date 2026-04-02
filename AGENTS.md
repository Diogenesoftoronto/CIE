# Agent Guide — CIE (Go)

CIE is a **Go** project. The Python application has been removed; do not add Python dependencies for core functionality.

## Stack

- Go **1.24+**, module: `github.com/cie-team/cie`
- CLI: **Cobra** (`internal/cli`)
- TUI: **Bubble Tea**, **Lip Gloss**, **Bubbles** (`internal/tui`)
- SQLite: **modernc.org/sqlite** (no CGO)

## Commands

```bash
go fmt ./...
go test ./...
go build -o cie ./cmd/cie
./cie doctor
./cie optimize -o 0 -w 0 -i 5
```

## Architecture

- **Backend** (`internal/backend`): loads config, storage, evaluators, optimizers; `EvalPolicy`, `ProposeOnce`, Pareto rebuild, adopt guardrails.
- **Workloads**: embedded JSON `internal/backend/default_workloads.json`.
- **Config**: `internal/config`; defaults + `~/.cie/config.json`.

## Conventions

- Keep changes focused; match existing style (`go fmt`).
- Extend evaluators via `evaluator.Register` or optimizers by implementing `optimizer.Optimizer` and wiring in `optimizer.NewDefaults`.
- After edits, run `go test ./...`.

## CI

GitHub Actions runs `go vet`, `go test`, `go build` (`.github/workflows/ci.yml`).

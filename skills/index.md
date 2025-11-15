# CIE Technical Skills Documentation

This directory contains technical documentation for the CIE (Optimization & Evaluation) project.

## Available Documentation

### [Textual Framework Guide](textual.md)
Deep dive into the Textual TUI framework patterns used across `cie/ui/*`. Covers:
- Core Textual concepts and widgets
- Panel architecture, message passing, and DataTable usage
- Shared design system (`cie/ui/theme.tcss`) and component styling
- Testing strategies for Textual applications

### [Evaluator Registry & Plugins](evaluators.md)
Explains the evaluator abstraction layer shipped in `cie/evaluators/`, including:
- Registry APIs (`register_evaluator`, `list_evaluators`, plugin auto-loading)
- Built-in evaluators (mock + text-match) and their workloads
- How to build Braintrust-style evaluation cases that leverage real model providers
- CLI workflows (`cie evaluators`, `cie evaluators --use text-match`) and configuration tips

### [Typst Authoring Guide](typst.md)
Reference for editing `papers/cie-paper.typ`: figure/table patterns, asset management in `papers/assets/`, and reproducible chart generation scripts.

### [Web Development Guide](web.md)
Documentation for the `site/` directory, covering the React/Vite/Tailwind stack, Bun usage, and key components.

### [Benchmarking Guide](benchmarking.md)
Comprehensive guide to the CIE Agent Benchmark System, including running benchmarks, understanding tasks, and analyzing metrics.

### [CLI Guide](cli.md)
Setup and usage guide for the CIE Command Line Interface.

### [Self-Optimization Guide](self_optimization.md)
Guide to the Agent Self-Optimization Framework, including scenarios, API usage, and measurement.

### [Vision](vision.md)
High-level vision and goals for the Context Introspection Environment.

### [CI/CD Pipeline](ci_cd.md)
Documentation for the Continuous Integration and Deployment pipeline.

### [Testing Guide](testing.md)
Overview of the testing infrastructure, categories, and best practices.

## Quick Reference

### Project Architecture
- **Package-first architecture**: Core logic in `cie/core`, TUI in `cie/ui`, CLI in `cie/cli.py`
- **Textual TUI**: Optimizers | Evals | Experiments + Status panel, themed via `cie/ui/theme.tcss`
- **Evaluator registry**: `cie/evaluators/__init__.py` for built-in and plugin evaluators
- **Mock + real integrations**: DSPy optimizer uses OpenAI when available with mock fallback

### Key Technologies
- **Python 3.13+**: Required version
- **Textual ≥0.47**: TUI framework (not 6.6.0+ as mentioned in some docs)
- **UV package manager**: Recommended for dependency management (`uv sync`, `uv run`)
- **Protocol-based design**: Extensible optimizer/evaluator/model-provider interfaces
- **Evaluator plugins**: Drop-in modules under `cie/evaluators/plugins/`

### Development Status
- ✅ Functional TUI + CLI backed by modular package
- ✅ DSPy optimizer with real runtime + mock fallback
- ✅ Evaluator registry with mock + text-match implementations
- ✅ Comprehensive docs in `README.md`, `AGENTS.md`, and this skills directory
- ✅ Test suite covering backend + optimizers + end-to-end flows
- ⚠️ Additional real evaluators/optimizers welcome

## Getting Started

1. **Install deps with UV**: `uv sync --extra ai`
2. **Run the TUI**: `uv run cie tui`
3. **Browse the CLI**: `uv run cie --help`, `uv run cie evaluators`
4. **Review patterns**: See `textual.md` and `evaluators.md`

## Next Steps

1. Expand evaluator/plugin catalog (image, tool-call, or RAG-specific checks)
2. Add more real optimizers alongside DSPy/HillClimb
3. Grow workload library (import external datasets, YAML-driven configs)
4. Enhance CI to cover CLI + TUI smoke tests

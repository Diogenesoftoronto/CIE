# CIE Development Rules & Workflow

This document outlines the standard operating procedures, technology choices, and aesthetic guidelines for the CIE project.

## 1. Core Philosophy
- **Premium Aesthetics**: All UI (TUI & Web) must look "premium" and "state-of-the-art". Use Harlequin-inspired themes for TUI and modern gradients/glassmorphism for Web.
- **Protocol-Driven**: Use Python protocols (`cie/core/backend.py`) to decouple interfaces from implementations.
- **Self-Documentation**: Every major feature must be documented in `AGENTS.md`, `skills/`, and `papers/cie-paper.typ`.

## 2. Technology Stack

### TUI (Terminal User Interface)
- **Framework**: Textual ≥0.47
- **Layout**: Sidebar navigation (`ListView` + `ContentSwitcher`) preferred over tabs.
- **Modals**: Use `ModalScreen` for configuration/input. Return results via `dismiss(result)`.
- **Styling**: `cie/ui/theme.tcss` defines the "Harlequin" dark theme.

### Web Interface (`site/`)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Runtime**: Bun (Use `bun install`, `bun run dev`, `bun run build`)
- **Styling**: Tailwind CSS

### Backend
- **Language**: Python 3.13+
- **Package Manager**: UV (`uv sync`, `uv run`)
- **Storage**: SQLite (production), JSON (debug), In-Memory (testing).

## 3. Development Workflow

### Feature Implementation Cycle
1.  **Plan**: Create/Update `task.md` and `implementation_plan.md`.
2.  **Backend**: Implement core logic and data models in `cie/core`.
3.  **UI**: Implement TUI panels in `cie/ui/panels` or Web components in `site/src/components`.
4.  **Verify**:
    - Python: `pytest tests/` (specifically `tests/test_end_to_end.py`).
    - Web: `cd site && bun run build`.
5.  **Document**:
    - Update `AGENTS.md` (System overview).
    - Update `papers/cie-paper.typ` (Academic context).
    - Update `skills/*.md` (Technical learnings).
    - Update `RULES.md` (if workflow changes).

## 4. Coding Standards

### Python
- **Type Hints**: Mandatory for all function signatures.
- **Docstrings**: Required for all public methods and classes.
- **Imports**: Absolute imports preferred (`cie.core.models` vs `.models`).

### TypeScript/React
- **Components**: Functional components with `React.FC`.
- **Icons**: Use `lucide-react`.
- **Tailwind**: Use utility classes; avoid custom CSS files where possible.

## 5. Documentation Checklist
When completing a task, ensure you have:
- [ ] Updated `AGENTS.md` with new features.
- [ ] Updated `papers/cie-paper.typ` if the feature is research-relevant.
- [ ] Added new technical patterns to `skills/`.
- [ ] Verified `RULES.md` is still accurate.

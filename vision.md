# Context Introspection Environment (CIE) Vision

**CIE** transforms AI agents from passive responders into **self-aware, self-optimizing computational systems**.
It provides an interactive **Textual TUI dashboard** where agents (and humans) can inspect, evaluate, optimize, and modify their own operational context.

---

## 1. Overview

The Context Introspection Environment gives agents:

* Real-time visibility into **context window usage**, **tools**, **MCP connections**, **variables**, and **system resources**.
* A rigorous optimization loop combining **policy search**, **evaluation**, **scoring**, and **adoption**.
* A structured and extensible framework for integrating **DSPy optimizers**, **custom evaluators**, and **adaptive decision policies**.

It is designed as both a **developer tool** and an **agent-facing control surface** for metacognitive capabilities.

---

## 2. Features

### 2.1 Introspective Dashboard (Textual TUI)

* Context usage & breakdown
* Active tools and MCP server registry
* System metrics (CPU, RAM, Disk)
* Agent variable inspector
* Keyboard hotkeys for navigation and actions

### 2.2 Optimization Framework

* Propose → Evaluate → Score → Adopt workflow
* Built-in mock optimizers:

  * DSPy-style BootstrapFewShot optimizer
  * HillClimb
  * Two-Arm Bandit
* Pareto frontier visualization
* Guarded policy adoption with rollback mechanisms

### 2.3 Dynamic Objective Weights

A **modal editor (`W`)** allows users to tune the weights of the optimization objective:

* `latency_p95`
* `cost_per_req`
* `task_success`
* `context_usage`
* `tool_error_rate`

Weights determine how metrics are balanced when scoring trial outcomes.

### 2.4 Plugins & Integrations

* Real DSPy integration via `dspy_adapter`
* Pluggable evaluator backends (MicroEval, MacroEval, LoadEval, etc.)
* Sandbox-ready architecture for safe policy adoption
* Extensible without modifying the core dashboard

---

## 3. Architecture

```
┌──────────────────────┐
│     Agent Runtime     │
└──────────┬────────────┘
           │
   Introspection API
           │
┌──────────▼──────────┐
│   CIE Dashboard     │
│ (Textual Terminal)  │
└───────┬────────────┘
        │
┌───────▼────────┬───────────┐
│ Optimizers     │ Evaluators │
└───────┬────────┴─────┬─────┘
        │              │
        ▼              ▼
  Policy Proposals   Metrics
        └──────┬──────┘
               ▼
     Scoring & Pareto Analysis
               ▼
         Policy Adoption
               ▼
            Agent
```

---

## 4. Objective Function

CIE collapses multi-dimensional metrics into a single scalar score:

[
J =
w_{\text{lat}} \cdot \text{latency}*{p95} +
w*{\text{cost}} \cdot \text{cost_per_req} -
w_{\text{succ}} \cdot \text{task_success} +
w_{\text{ctx}} \cdot \text{context_usage} +
w_{\text{err}} \cdot \text{tool_error_rate}
]

* **Positive weights = penalties** (minimize)
* **Negative weights = rewards** (maximize)

Users can edit these weights interactively.

---

## 5. Getting Started

### 5.1 Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install "textual>=0.47" dspy
```

### 5.2 Running the Dashboard

```bash
python cie_tui.py
```

### 5.3 Keyboard Shortcuts

| Key                 | Action                 |
| ------------------- | ---------------------- |
| `Tab` / `Shift+Tab` | Navigate panels        |
| `o`                 | Propose a new policy   |
| `e`                 | Run evaluation         |
| `p`                 | Toggle Pareto frontier |
| `A`                 | Adopt selected trial   |
| `W`                 | Edit objective weights |
| `Ctrl + R`          | Refresh all panels     |
| `Ctrl + C`          | Quit                   |

---

## 6. Integration Hooks

### 6.1 DSPy Optimizer

Replace mock optimizer with the real adapter:

```python
from cie.adapters.dspy_adapter import DspyConfig
from cie.optimizers.dspy_optimizer import DspyOptimizer

BACKEND.optimizers[0] = DspyOptimizer(
    cfg=DspyConfig(provider="openai", model="gpt-4.1-mini"),
    signature_factory=RetrieveAndAnswer,
    program_factory=QAProgram,
    teleprompter="BootstrapFewShot",
    metric=em_metric,
    train_data=train,
    eval_data=dev
)
```

### 6.2 Evaluators

Evaluators must return a metrics dictionary:

```python
{
  "latency_p95": float,
  "cost_per_req": float,
  "task_success": float,
  "context_usage": float,
  "tool_error_rate": float
}
```

Replace `MockEvaluator` with real benchmark workloads.

### 6.3 Policy Adoption

Implement adoption logic in:

```python
CIEBackend.adopt_policy(trial_id)
```

This may include:

* Activating a DSPy-compiled module
* Setting runtime parameters (batch size, pruning, caching)
* Registering rollback states

---

## 7. Development Roadmap

- **Hallucination & Consistency Detectors**
  - Built-in evaluator modules that score hallucination risk, response consistency, and citation fidelity per trial.
  - Guardrail hooks so adoption can be blocked if hallucination metrics exceed thresholds.

- **Dataset & Workload Registry**
  - `cie datasets` CLI for importing, versioning, and describing datasets (YAML/JSON).
  - Workload definitions pointing to dataset subsets so agents can reproduce evaluation suites.

- **Recursive Language Model (RLM) Context Management**
  - Agent-accessible `StateStore` for arbitrary variables and context budgets.
  - Recursive Manager that lets optimizers spawn sub-policies, persist intermediate summaries, and manage context windows.
  - Oversight agent channel (human or automated) to inspect recursion stacks and veto policies.

- **Agent Code Environment**
  - Embedded sandbox for executing helper scripts/snippets that can read/write state, summarize context, or generate new workloads.
  - TUI “Code” panel and CLI commands (`cie code run`) to execute analysis routines alongside evaluations.

- **Fast MCP Integration**
  - `cie serve mcp` exposes state, workload, evaluation, and code APIs over the Model Context Protocol so external agents can orchestrate CIE remotely.
  - Enables recursive/oversight agents to run CIE as a service within larger agentic systems.

- **Provider & Tool Ecosystem**
  - Support for local/vLLM/OpenRouter providers to reduce dependence on a single API.
  - Tool adapters (retrievers, vector DBs, structured actions) surfaced through the state manager so policies can reason about available resources.

* **Objective Profiles**
  One-keystroke presets: *Speed*, *Quality*, *Budget*, *Hybrid*.

* **Live Metrics Stream**
  Tokens/s, cost/min, GPU load, tool usage.

* **Agent API**
  `cie = await connect_to_cie()` for programmatic control loops.

* **Multi-Agent Mode**
  Shared timeline + collaborative introspection for swarm agents.

---

## 8. Security & Safety

* Guarded policy adoption
* Validation before runtime activation
* Evaluators run in sandboxed environment
* Full audit trail of introspection actions
* Rollback capability for mitigation

---

## 9. License

MIT License © 2025 DiffDev / Keith Noel
Free for research, experimentation, and extension.

---

## 10. Closing Note

**CIE** is an experiment in turning AI systems into **agents with introspective control loops**, capable of monitoring and improving themselves.

> *“An agent with visibility into its own substrate becomes something more than a model —
> it becomes a system.”*

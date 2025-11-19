"""
Demo helpers for launching the TUI with pre-populated data.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Tuple

from cie.config.settings import CIEConfig
from cie.core.backend import CIEBackend, InMemoryStorageBackend
from cie.core.models import Policy, Trial, Workload


def create_demo_backend(base_config: CIEConfig | None = None) -> Tuple[CIEBackend, dict[str, Any]]:
    """
    Build an in-memory backend that showcases a LeetCode-style scenario.

    Returns:
        backend seeded with demo workloads/trials and metadata describing the scenario
    """

    config = deepcopy(base_config) if base_config else CIEConfig()
    config.storage.backend = "memory"
    config.model.provider = "mock"
    config.model.model_name = "demo-mock"
    config.evaluation.default_evaluator = "mock"

    backend = CIEBackend(config)
    backend.storage = InMemoryStorageBackend()
    backend.trials.clear()
    backend.pareto.clear()
    backend._trial_id_counter = 0

    demo_workloads = [
        Workload(
            name="LeetCode:two-sum-sprint",
            items=25,
            description="Warm-up arrays set covering Two Sum and Subarray Sum variations.",
            config={
                "difficulty": "easy",
                "dataset": ["Two Sum", "Two Sum II", "Subarray Sum Equals K"],
                "goal": "Beat 95th percentile latency < 50ms per case.",
            },
            tags=["leetcode", "arrays", "hash map"],
        ),
        Workload(
            name="LeetCode:binary-tree-guru",
            items=12,
            description="Binary tree traversals + reconstruction prompts with tricky edges.",
            config={
                "difficulty": "medium",
                "dataset": ["Binary Tree Zigzag", "Serialize Tree", "Path Sum III"],
                "goal": "Generate optimal recursion with clear invariants.",
            },
            tags=["leetcode", "trees"],
        ),
        Workload(
            name="LeetCode:dp-marathon",
            items=6,
            description="Dynamic programming interview rounds focused on reasoning clarity.",
            config={
                "difficulty": "hard",
                "dataset": ["Longest Increasing Path", "Paint Fence", "Coin Change"],
                "goal": "Max success rate with minimal context switches.",
            },
            tags=["leetcode", "dynamic-programming"],
        ),
    ]
    backend.workloads = demo_workloads + backend.workloads

    demo_policies = [
        Policy(
            name="LeetCode-CoT-Agent",
            params={"strategy": "chain-of-thought", "artifact": "artifacts/leetcode-cot.md"},
            actions=[
                "Capture constraints",
                "Draft brute-force baseline",
                "Layer optimized approach + tests",
            ],
            metadata={"persona": "coach", "notes": "Focuses on reasoning visibility."},
        ),
        Policy(
            name="LeetCode-GraphSearch",
            params={"strategy": "graph-search+diagrams", "artifact": "artifacts/graph-playbook.md"},
            actions=["Visualize graph", "Plan BFS/DFS hybrid", "Emit annotated code"],
            metadata={"persona": "diagrammer", "notes": "Great for trees/graphs."},
        ),
        Policy(
            name="LeetCode-DP-Notebook",
            params={"strategy": "table-first", "artifact": "artifacts/dp-notebook.md"},
            actions=["Define recurrence", "Prove base cases", "Generate python table"],
            metadata={"persona": "dp-guru"},
        ),
    ]
    for policy in demo_policies:
        backend.storage.save_policy(policy)

    now = datetime.utcnow()
    demo_trials = [
        {
            "policy": "LeetCode-CoT-Agent",
            "workload": "LeetCode:two-sum-sprint",
            "metrics": {
                "latency_p95": 1800.0,
                "cost_per_req": 0.013,
                "task_success": 0.82,
                "context_usage": 1.8,
                "tool_error_rate": 0.015,
            },
            "notes": "Step-by-step reasoning improved success but cost is higher.",
            "created_at": now - timedelta(hours=6),
        },
        {
            "policy": "LeetCode-GraphSearch",
            "workload": "LeetCode:binary-tree-guru",
            "metrics": {
                "latency_p95": 2350.0,
                "cost_per_req": 0.017,
                "task_success": 0.74,
                "context_usage": 2.4,
                "tool_error_rate": 0.01,
            },
            "notes": "Visualization steps add latency but produce fewer bugs.",
            "created_at": now - timedelta(hours=4),
        },
        {
            "policy": "LeetCode-DP-Notebook",
            "workload": "LeetCode:dp-marathon",
            "metrics": {
                "latency_p95": 3100.0,
                "cost_per_req": 0.02,
                "task_success": 0.69,
                "context_usage": 3.2,
                "tool_error_rate": 0.035,
            },
            "notes": "Struggled with complex transitions; needs memoization hints.",
            "created_at": now - timedelta(hours=2),
        },
        {
            "policy": "LeetCode-CoT-Agent",
            "workload": "LeetCode:binary-tree-guru",
            "metrics": {
                "latency_p95": 2050.0,
                "cost_per_req": 0.015,
                "task_success": 0.88,
                "context_usage": 2.0,
                "tool_error_rate": 0.008,
            },
            "notes": "Hybrid CoT + examples delivered the best coverage so far.",
            "created_at": now - timedelta(minutes=45),
        },
    ]

    for entry in demo_trials:
        backend._trial_id_counter += 1
        trial = Trial(
            id=backend._trial_id_counter,
            policy_name=entry["policy"],
            metrics=entry["metrics"],
            score=backend.score(entry["metrics"]),
            workload=entry["workload"],
            created_at=entry["created_at"],
            notes=entry["notes"],
            metadata={"demo": True},
        )
        backend.trials.append(trial)
        backend.storage.save_trial(trial)

    backend._rebuild_pareto()
    backend.active_policy = demo_policies[0]

    demo_metadata = {
        "name": "LeetCode Practice Lab",
        "description": (
            "A curated walkthrough showing how CIE tracks algorithm practice runs with mock data."
        ),
        "status_message": "Demo: Loaded LeetCode practice datasets (3 workloads, 4 trials).",
        "context_intro": (
            "Demo context seeded with LeetCode goals, guardrails, and hints. "
            "Use Capture to see the synthetic session state or Optimize to explore opportunities."
        ),
        "use_case": "leetcode-practice",
    }

    return backend, demo_metadata

"""Optimization scenarios for agent self-optimization testing.

This module defines concrete scenarios that test different aspects of agent
capability: simple optimization, multi-dimensional tradeoffs, handling noise,
iterative learning, edge cases, etc.
"""

from self_optimize.agent_optimizer import OptimizationScenario

# ============================================================================
# EASY SCENARIOS - Basic Understanding
# ============================================================================

SCENARIO_SIMPLE_IMPROVEMENT = OptimizationScenario(
    scenario_id="easy_simple_improvement",
    name="Simple Improvement",
    description="Optimize a single metric (latency) with clear gradient",
    difficulty="easy",
    objective="Reduce response latency",
    metrics_to_optimize=["latency_p95"],
    metrics_directions={"latency_p95": "minimize"},
    iterations_allowed=5,
    timeout_seconds=120,
    baseline_score=50.0,
    target_score=75.0,
    success_threshold=0.4,
    noise_level=0.0,
    exploration_difficulty=0.5,
    metric_clarity=1.0,
    hints=[
        "Lower latency is achieved by reducing complexity",
        "Start with baseline, then propose simpler configurations",
        "Watch how latency changes with each parameter",
    ],
    example_approach="Create workload that measures latency, propose configurations with "
    "decreasing complexity, adopt policies that reduce latency",
)

SCENARIO_THROUGHPUT_OPTIMIZATION = OptimizationScenario(
    scenario_id="easy_throughput_optimization",
    name="Throughput Optimization",
    description="Maximize throughput (requests per second)",
    difficulty="easy",
    objective="Increase request throughput",
    metrics_to_optimize=["throughput"],
    metrics_directions={"throughput": "maximize"},
    iterations_allowed=5,
    timeout_seconds=120,
    baseline_score=50.0,
    target_score=75.0,
    success_threshold=0.4,
    noise_level=0.05,
    exploration_difficulty=0.6,
    metric_clarity=0.95,
    hints=[
        "Throughput increases with parallel processing",
        "Each policy proposes different concurrency settings",
        "Higher concurrency generally means more requests handled",
    ],
)


# ============================================================================
# MEDIUM SCENARIOS - Multi-Dimensional Tradeoffs
# ============================================================================

SCENARIO_LATENCY_vs_ACCURACY = OptimizationScenario(
    scenario_id="medium_latency_vs_accuracy",
    name="Latency vs Accuracy Tradeoff",
    description="Optimize between response speed and quality",
    difficulty="medium",
    objective="Balance latency and accuracy - choose 2D tradeoff point",
    metrics_to_optimize=["latency_p95", "accuracy"],
    metrics_directions={"latency_p95": "minimize", "accuracy": "maximize"},
    iterations_allowed=8,
    timeout_seconds=180,
    baseline_score=50.0,
    target_score=70.0,
    success_threshold=0.3,
    noise_level=0.1,
    exploration_difficulty=0.8,
    metric_clarity=0.9,
    hints=[
        "These metrics have a tradeoff - improving one may hurt the other",
        "Look for policies that balance both metrics",
        "Consider using Pareto frontier to understand non-dominated solutions",
    ],
)

SCENARIO_THREE_WAY_TRADEOFF = OptimizationScenario(
    scenario_id="medium_three_way_tradeoff",
    name="Three-Way Tradeoff",
    description="Optimize latency, accuracy, and cost simultaneously",
    difficulty="medium",
    objective="Find best 3D tradeoff point matching priorities",
    metrics_to_optimize=["latency_p95", "accuracy", "cost"],
    metrics_directions={
        "latency_p95": "minimize",
        "accuracy": "maximize",
        "cost": "minimize",
    },
    iterations_allowed=10,
    timeout_seconds=240,
    baseline_score=45.0,
    target_score=68.0,
    success_threshold=0.35,
    noise_level=0.15,
    exploration_difficulty=0.9,
    metric_clarity=0.85,
    hints=[
        "You have 3 competing objectives",
        "No single policy optimizes all three",
        "Identify the Pareto frontier (non-dominated solutions)",
        "Choose the point that best matches your priorities",
    ],
)


# ============================================================================
# HARD SCENARIOS - Complex Optimization
# ============================================================================

SCENARIO_NOISY_OPTIMIZATION = OptimizationScenario(
    scenario_id="hard_noisy_optimization",
    name="Noisy Evaluation",
    description="Optimize with uncertainty - metrics have noise",
    difficulty="hard",
    objective="Find good policy despite measurement noise",
    metrics_to_optimize=["performance_score"],
    metrics_directions={"performance_score": "maximize"},
    iterations_allowed=12,
    timeout_seconds=240,
    baseline_score=50.0,
    target_score=72.0,
    success_threshold=0.35,
    noise_level=0.25,
    exploration_difficulty=1.0,
    metric_clarity=0.7,
    hints=[
        "Measurements have random noise - don't overfit to noise",
        "Look for consistent patterns across iterations",
        "Consider running multiple evaluations of same policy",
        "Distinguish signal from noise",
    ],
)

SCENARIO_PLATEAU_ESCAPE = OptimizationScenario(
    scenario_id="hard_plateau_escape",
    name="Escape Local Optimum",
    description="Avoid getting stuck on local optimum, find global optimum",
    difficulty="hard",
    objective="Escape local maximum and find better global solution",
    metrics_to_optimize=["performance_score"],
    metrics_directions={"performance_score": "maximize"},
    iterations_allowed=15,
    timeout_seconds=300,
    baseline_score=50.0,
    target_score=75.0,
    success_threshold=0.45,
    noise_level=0.1,
    exploration_difficulty=1.2,
    metric_clarity=0.85,
    hints=[
        "There's a local optimum around policy A (score ~65)",
        "But a better global optimum exists (score ~80+)",
        "Try diversifying your search to explore beyond local optimum",
        "Consider jumping to unexplored regions",
    ],
)

SCENARIO_CONFLICTING_OBJECTIVES = OptimizationScenario(
    scenario_id="hard_conflicting_objectives",
    name="Conflicting Objectives",
    description="Handle metrics that conflict with each other",
    difficulty="hard",
    objective="Manage completely conflicting metrics",
    metrics_to_optimize=["throughput", "latency_p95", "memory_usage"],
    metrics_directions={
        "throughput": "maximize",
        "latency_p95": "minimize",
        "memory_usage": "minimize",
    },
    iterations_allowed=10,
    timeout_seconds=240,
    baseline_score=40.0,
    target_score=65.0,
    success_threshold=0.4,
    noise_level=0.2,
    exploration_difficulty=1.1,
    metric_clarity=0.75,
    hints=[
        "Higher throughput requires more memory",
        "Lower latency requires higher throughput",
        "More memory increases complexity",
        "Find the best compromise across all three",
    ],
)


# ============================================================================
# EXPERT SCENARIOS - Advanced Challenges
# ============================================================================

SCENARIO_MULTI_OBJECTIVE_LEARNING = OptimizationScenario(
    scenario_id="expert_multi_objective_learning",
    name="Multi-Objective Learning",
    description="Learn optimal Pareto frontier across 4+ metrics",
    difficulty="expert",
    objective="Discover and optimize the Pareto frontier",
    metrics_to_optimize=[
        "accuracy",
        "latency_p95",
        "cost_per_req",
        "throughput",
        "memory_usage",
    ],
    metrics_directions={
        "accuracy": "maximize",
        "latency_p95": "minimize",
        "cost_per_req": "minimize",
        "throughput": "maximize",
        "memory_usage": "minimize",
    },
    iterations_allowed=20,
    timeout_seconds=600,
    baseline_score=35.0,
    target_score=70.0,
    success_threshold=0.5,
    noise_level=0.15,
    exploration_difficulty=1.3,
    metric_clarity=0.7,
    hints=[
        "This is a 5D optimization problem",
        "Focus on finding non-dominated solutions",
        "The Pareto frontier has ~5-7 solutions",
        "Characterize the tradeoff space",
    ],
)

SCENARIO_ADAPTIVE_STRATEGY = OptimizationScenario(
    scenario_id="expert_adaptive_strategy",
    name="Adaptive Strategy",
    description="Change optimization strategy based on observations",
    difficulty="expert",
    objective="Dynamically adapt approach based on what works",
    metrics_to_optimize=["performance_score"],
    metrics_directions={"performance_score": "maximize"},
    iterations_allowed=15,
    timeout_seconds=300,
    baseline_score=45.0,
    target_score=80.0,
    success_threshold=0.55,
    noise_level=0.2,
    exploration_difficulty=1.4,
    metric_clarity=0.65,
    hints=[
        "What works in early iterations may not work later",
        "Monitor whether your strategy is effective",
        "Be ready to change approach if stagnating",
        "Learn from failures as well as successes",
    ],
)

SCENARIO_EXTREME_UNCERTAINTY = OptimizationScenario(
    scenario_id="expert_extreme_uncertainty",
    name="Extreme Uncertainty",
    description="Optimize with high noise and limited visibility",
    difficulty="expert",
    objective="Find good solution despite extreme noise",
    metrics_to_optimize=["performance_score"],
    metrics_directions={"performance_score": "maximize"},
    iterations_allowed=12,
    timeout_seconds=300,
    baseline_score=40.0,
    target_score=70.0,
    success_threshold=0.5,
    noise_level=0.4,
    exploration_difficulty=1.5,
    metric_clarity=0.5,
    hints=[
        "Noise is 40% - almost overwhelms the signal",
        "Results are very hard to interpret",
        "Look for statistical significance, not individual values",
        "Consider conservative decision-making",
    ],
)


# ============================================================================
# EDGE CASE SCENARIOS
# ============================================================================

SCENARIO_ALL_EQUAL = OptimizationScenario(
    scenario_id="edge_all_policies_equal",
    name="All Policies Equally Good",
    description="All policies perform identically - test decision making",
    difficulty="medium",
    objective="Recognize when optimization is futile",
    metrics_to_optimize=["performance_score"],
    metrics_directions={"performance_score": "maximize"},
    iterations_allowed=5,
    timeout_seconds=120,
    baseline_score=50.0,
    target_score=50.0,
    success_threshold=0.01,
    noise_level=0.02,
    exploration_difficulty=0.3,
    metric_clarity=1.0,
    hints=[
        "All policies actually perform identically",
        "Recognize when no improvement is possible",
        "Make thoughtful decision even with no clear winner",
    ],
)

SCENARIO_ALL_BAD = OptimizationScenario(
    scenario_id="edge_all_policies_bad",
    name="All Policies Equally Bad",
    description="All policies perform poorly - test handling of failure",
    difficulty="medium",
    objective="Handle case where no policy is good",
    metrics_to_optimize=["performance_score"],
    metrics_directions={"performance_score": "maximize"},
    iterations_allowed=5,
    timeout_seconds=120,
    baseline_score=30.0,
    target_score=35.0,
    success_threshold=0.2,
    noise_level=0.05,
    exploration_difficulty=0.4,
    metric_clarity=1.0,
    hints=[
        "There's no good policy in this scenario",
        "Choose the least bad option",
        "Recognize when you're in a bad situation",
    ],
)

SCENARIO_MISSING_METRICS = OptimizationScenario(
    scenario_id="edge_missing_metrics",
    name="Missing Metrics",
    description="Some metrics are unavailable - test robustness",
    difficulty="hard",
    objective="Make good decisions with incomplete information",
    metrics_to_optimize=["accuracy", "latency_p95", "cost"],
    metrics_directions={
        "accuracy": "maximize",
        "latency_p95": "minimize",
        "cost": "minimize",
    },
    iterations_allowed=8,
    timeout_seconds=180,
    baseline_score=50.0,
    target_score=68.0,
    success_threshold=0.3,
    noise_level=0.1,
    exploration_difficulty=0.8,
    metric_clarity=0.7,
    hints=[
        "Some metrics will occasionally be missing",
        "Handle incomplete information gracefully",
        "Don't let missing data paralyze decision making",
    ],
)


# ============================================================================
# SCENARIO COLLECTIONS
# ============================================================================

EASY_SCENARIOS = [
    SCENARIO_SIMPLE_IMPROVEMENT,
    SCENARIO_THROUGHPUT_OPTIMIZATION,
]

MEDIUM_SCENARIOS = [
    SCENARIO_LATENCY_vs_ACCURACY,
    SCENARIO_THREE_WAY_TRADEOFF,
    SCENARIO_ALL_EQUAL,
    SCENARIO_ALL_BAD,
    SCENARIO_MISSING_METRICS,
]

HARD_SCENARIOS = [
    SCENARIO_NOISY_OPTIMIZATION,
    SCENARIO_PLATEAU_ESCAPE,
    SCENARIO_CONFLICTING_OBJECTIVES,
]

EXPERT_SCENARIOS = [
    SCENARIO_MULTI_OBJECTIVE_LEARNING,
    SCENARIO_ADAPTIVE_STRATEGY,
    SCENARIO_EXTREME_UNCERTAINTY,
]

ALL_SCENARIOS = EASY_SCENARIOS + MEDIUM_SCENARIOS + HARD_SCENARIOS + EXPERT_SCENARIOS


def get_scenarios_by_difficulty(difficulty: str) -> list[OptimizationScenario]:
    """Get scenarios at specific difficulty level."""
    difficulty_map = {
        "easy": EASY_SCENARIOS,
        "medium": MEDIUM_SCENARIOS,
        "hard": HARD_SCENARIOS,
        "expert": EXPERT_SCENARIOS,
    }
    return difficulty_map.get(difficulty, [])


def get_scenario_by_id(scenario_id: str) -> OptimizationScenario | None:
    """Get specific scenario by ID."""
    for scenario in ALL_SCENARIOS:
        if scenario.scenario_id == scenario_id:
            return scenario
    return None

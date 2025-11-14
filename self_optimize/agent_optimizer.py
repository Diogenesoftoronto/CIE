"""Agent self-optimization framework for measuring agent capability.

This module provides interfaces and utilities for agents to use CIE itself
for self-optimization and self-evaluation. Agents can:
- Define optimization problems (workloads)
- Propose policies using CIE optimizers
- Evaluate policies using CIE evaluators
- Analyze results and make decisions
- Iterate to improve over time

The framework measures how well agents can optimize themselves.
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class OptimizationStep:
    """A single step in the optimization process."""

    step_number: int
    timestamp: datetime
    proposed_policy: dict[str, Any]  # The policy proposed by agent
    evaluation_results: dict[str, float]  # Metrics from evaluation
    agent_decision: str  # "adopt", "reject", "unclear"
    agent_reasoning: str  # Why the decision was made
    confidence: float  # 0-100, agent's confidence in decision
    metrics_understood: bool  # Did agent correctly interpret metrics
    decision_quality: float  # 0-100, objective quality of decision


@dataclass
class OptimizationResult:
    """Result of agent's self-optimization attempt."""

    agent_name: str
    scenario_name: str
    run_id: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float

    # Iteration tracking
    iterations_completed: int
    iterations_allowed: int

    # Steps taken
    optimization_steps: list[OptimizationStep] = field(default_factory=list)

    # Metrics
    optimization_effectiveness: float  # 0-100
    metrics_interpretation: float  # 0-100
    decision_quality: float  # 0-100
    learning_trajectory: float  # 0-100
    pareto_understanding: float  # 0-100
    composite_score: float  # 0-100

    # Outcomes
    baseline_score: float
    final_score: float
    improvement: float  # final - baseline
    improvement_per_iteration: float

    # Analysis
    final_policy: dict[str, Any] = field(default_factory=dict)
    agent_explanation: str = ""
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def performance_tier(self) -> str:
        """Categorize performance."""
        if self.composite_score >= 90:
            return "Expert"
        elif self.composite_score >= 75:
            return "Proficient"
        elif self.composite_score >= 60:
            return "Competent"
        elif self.composite_score >= 40:
            return "Developing"
        else:
            return "Novice"


@dataclass
class OptimizationScenario:
    """Definition of an optimization scenario for agents."""

    scenario_id: str
    name: str
    description: str
    difficulty: str  # easy, medium, hard, expert

    # Problem definition
    objective: str  # What to optimize
    metrics_to_optimize: list[str]  # Which metrics matter
    metrics_directions: dict[str, str]  # "maximize" or "minimize"

    # Constraints
    iterations_allowed: int = 5
    timeout_seconds: int = 300

    # What constitutes success
    baseline_score: float = 50.0  # Starting point
    target_score: float = 75.0  # Goal
    success_threshold: float = 0.6  # % improvement needed

    # Difficulty modifiers
    noise_level: float = 0.0  # 0-1, noise in evaluations
    exploration_difficulty: float = 1.0  # How hard to find solutions
    metric_clarity: float = 1.0  # How clear are relationships

    # Hints for agent
    hints: list[str] = field(default_factory=list)
    example_approach: str = ""

    def __hash__(self) -> int:
        return hash(self.scenario_id)


class AgentOptimizer(ABC):
    """Interface for agents performing self-optimization using CIE."""

    def __init__(self, agent_name: str):
        """Initialize agent optimizer.

        Args:
            agent_name: Name/identifier of the agent
        """
        self.agent_name = agent_name
        self.run_id = str(uuid.uuid4())[:8]
        self.steps: list[OptimizationStep] = []
        self.iteration_count = 0

    @abstractmethod
    def run_optimization(
        self,
        scenario: OptimizationScenario,
        backend: Any,  # CIEBackend instance
    ) -> OptimizationResult:
        """Run self-optimization process.

        Agent should:
        1. Understand the scenario/objective
        2. Create appropriate workload
        3. Propose policies using optimizers
        4. Evaluate using evaluators
        5. Analyze results and make decisions
        6. Iterate to improve

        Args:
            scenario: The optimization scenario/problem
            backend: CIE backend to use for optimization

        Returns:
            OptimizationResult with all metrics
        """
        pass

    @abstractmethod
    def propose_policy(
        self,
        current_state: dict[str, Any],
        previous_results: list[dict[str, float]],
    ) -> dict[str, Any]:
        """Propose next policy to evaluate.

        Agent should use reasoning about:
        - Previous results
        - Trends and patterns
        - Unexplored areas
        - Risk/reward tradeoff

        Args:
            current_state: Current system state
            previous_results: Results from previous evaluations

        Returns:
            Policy configuration to evaluate
        """
        pass

    @abstractmethod
    def analyze_results(
        self,
        trial_results: list[dict[str, Any]],
        metrics: dict[str, float],
    ) -> dict[str, Any]:
        """Analyze evaluation results and extract insights.

        Should return:
        - Which metric performed best
        - Identified tradeoffs
        - Confidence in analysis
        - What to try next

        Args:
            trial_results: Raw trial results
            metrics: Aggregated metrics

        Returns:
            Analysis with insights and recommendations
        """
        pass

    @abstractmethod
    def make_adoption_decision(
        self,
        candidate_policy: dict[str, Any],
        metrics: dict[str, float],
        previous_best: Optional[dict[str, float]] = None,
    ) -> tuple[str, str, float]:
        """Decide whether to adopt a policy.

        Should consider:
        - Metrics vs objectives
        - Improvement vs baseline
        - Confidence in results
        - Risk of adoption

        Args:
            candidate_policy: Policy being considered
            metrics: Its evaluation metrics
            previous_best: Best metrics so far

        Returns:
            (decision: "adopt"/"reject"/"unclear", reasoning, confidence 0-100)
        """
        pass

    def record_step(
        self,
        step_number: int,
        policy: dict[str, Any],
        metrics: dict[str, float],
        decision: str,
        reasoning: str,
        confidence: float,
        metrics_understood: bool,
        decision_quality: float,
    ) -> None:
        """Record an optimization step.

        Args:
            step_number: Which iteration
            policy: Policy that was proposed
            metrics: Evaluation results
            decision: Adoption decision
            reasoning: Why decision was made
            confidence: Confidence 0-100
            metrics_understood: Did agent understand metrics
            decision_quality: Objective quality 0-100
        """
        step = OptimizationStep(
            step_number=step_number,
            timestamp=datetime.now(),
            proposed_policy=policy,
            evaluation_results=metrics,
            agent_decision=decision,
            agent_reasoning=reasoning,
            confidence=confidence,
            metrics_understood=metrics_understood,
            decision_quality=decision_quality,
        )
        self.steps.append(step)


class OptimizationMeasurer:
    """Measures agent optimization performance."""

    @staticmethod
    def measure_optimization_effectiveness(
        steps: list[OptimizationStep],
        baseline_score: float,
    ) -> float:
        """Measure how well agent traversed solution space.

        Considers:
        - Did it find better policies?
        - How quickly?
        - Avoided poor choices?

        Returns 0-100 score.
        """
        if not steps:
            return 0.0

        # Get best score achieved
        best_score = baseline_score
        for step in steps:
            # Look for key metric improvement
            results = step.evaluation_results
            score = results.get("composite_score", results.get("score", baseline_score))
            if score > best_score:
                best_score = score

        # Improvement percentage
        improvement = (
            (best_score - baseline_score) / baseline_score * 100 if baseline_score > 0 else 0
        )

        # Better with fewer iterations is better
        efficiency = min(100.0, 20 + improvement / 2)  # Scale to 0-100

        return min(100.0, max(0.0, efficiency))

    @staticmethod
    def measure_metrics_interpretation(
        steps: list[OptimizationStep],
    ) -> float:
        """Measure accuracy of metrics interpretation.

        Based on whether agent correctly understood what metrics meant.
        """
        if not steps:
            return 0.0

        understood = sum(1 for s in steps if s.metrics_understood)
        rate = understood / len(steps) * 100

        return rate

    @staticmethod
    def measure_decision_quality(
        steps: list[OptimizationStep],
    ) -> float:
        """Measure quality of adoption/rejection decisions.

        Based on decision_quality scores recorded for each step.
        """
        if not steps:
            return 0.0

        avg_quality = sum(s.decision_quality for s in steps) / len(steps)
        return avg_quality

    @staticmethod
    def measure_learning_trajectory(
        steps: list[OptimizationStep],
        baseline: float,
    ) -> float:
        """Measure if agent improved over iterations.

        Looks at:
        - Improvement per iteration
        - Trend (increasing or decreasing)
        - Convergence
        """
        if len(steps) < 2:
            return 0.0

        scores = []
        for step in steps:
            results = step.evaluation_results
            score = results.get("composite_score", results.get("score", baseline))
            scores.append(score)

        # Check for improvement trend
        improvements = []
        for i in range(1, len(scores)):
            improvement = scores[i] - scores[i - 1]
            improvements.append(improvement)

        if not improvements:
            return 0.0

        avg_improvement = sum(improvements) / len(improvements)

        # Positive improvement is good
        trajectory_score = 50.0 + (avg_improvement * 5)

        return min(100.0, max(0.0, trajectory_score))

    @staticmethod
    def measure_pareto_understanding(
        steps: list[OptimizationStep],
    ) -> float:
        """Measure if agent understands multi-dimensional optimization.

        Checks if agent:
        - Recognizes tradeoffs
        - Identifies non-dominated solutions
        - Weights preferences correctly
        """
        # This would need agent-specific evaluation
        # For now, basic heuristic based on step quality
        if not steps:
            return 0.0

        # Check if agent reasoning mentions tradeoffs
        tradeoff_mentions = sum(
            1
            for s in steps
            if any(
                word in s.agent_reasoning.lower()
                for word in ["tradeoff", "pareto", "frontier", "dominated"]
            )
        )

        mention_rate = tradeoff_mentions / len(steps) if steps else 0

        return mention_rate * 100

    @staticmethod
    def compute_composite_score(
        optimization_effectiveness: float,
        metrics_interpretation: float,
        decision_quality: float,
        learning_trajectory: float,
        pareto_understanding: float,
    ) -> float:
        """Compute weighted composite score."""
        score = (
            0.30 * optimization_effectiveness
            + 0.25 * decision_quality
            + 0.20 * metrics_interpretation
            + 0.15 * learning_trajectory
            + 0.10 * pareto_understanding
        )
        return min(100.0, max(0.0, score))

    @staticmethod
    def create_result(
        agent_name: str,
        scenario: OptimizationScenario,
        steps: list[OptimizationStep],
        baseline_score: float,
        final_score: float,
        final_policy: dict[str, Any],
        agent_explanation: str = "",
        errors: list[str] | None = None,
    ) -> OptimizationResult:
        """Create complete optimization result."""
        if errors is None:
            errors = []

        start_time = steps[0].timestamp if steps else datetime.now()
        end_time = steps[-1].timestamp if steps else datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Measure each dimension
        opt_eff = OptimizationMeasurer.measure_optimization_effectiveness(steps, baseline_score)
        metrics_int = OptimizationMeasurer.measure_metrics_interpretation(steps)
        dec_qual = OptimizationMeasurer.measure_decision_quality(steps)
        learn_traj = OptimizationMeasurer.measure_learning_trajectory(steps, baseline_score)
        pareto_und = OptimizationMeasurer.measure_pareto_understanding(steps)

        # Composite
        composite = OptimizationMeasurer.compute_composite_score(
            opt_eff, metrics_int, dec_qual, learn_traj, pareto_und
        )

        improvement = final_score - baseline_score
        improvement_per_iteration = improvement / len(steps) if steps else 0

        return OptimizationResult(
            agent_name=agent_name,
            scenario_name=scenario.name,
            run_id=str(uuid.uuid4())[:8],
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            iterations_completed=len(steps),
            iterations_allowed=scenario.iterations_allowed,
            optimization_steps=steps,
            optimization_effectiveness=opt_eff,
            metrics_interpretation=metrics_int,
            decision_quality=dec_qual,
            learning_trajectory=learn_traj,
            pareto_understanding=pareto_und,
            composite_score=composite,
            baseline_score=baseline_score,
            final_score=final_score,
            improvement=improvement,
            improvement_per_iteration=improvement_per_iteration,
            final_policy=final_policy,
            agent_explanation=agent_explanation,
            errors=errors,
        )


def generate_report(result: OptimizationResult) -> str:
    """Generate human-readable report of optimization result."""
    lines = [
        "╔════════════════════════════════════════════════════════════════╗",
        "║      AGENT SELF-OPTIMIZATION BENCHMARK REPORT                 ║",
        "╚════════════════════════════════════════════════════════════════╝",
        "",
        f"Agent: {result.agent_name}",
        f"Scenario: {result.scenario_name}",
        f"Performance Tier: {result.performance_tier}",
        "",
        "════════════════════════════════════════════════════════════════",
        "",
        "SCORES",
        "────────────────────────────────────────────────────────────────",
        f"Optimization Effectiveness:    {result.optimization_effectiveness:6.1f}/100",
        f"Metrics Interpretation:        {result.metrics_interpretation:6.1f}/100",
        f"Decision Quality:              {result.decision_quality:6.1f}/100",
        f"Learning Trajectory:           {result.learning_trajectory:6.1f}/100",
        f"Pareto Understanding:          {result.pareto_understanding:6.1f}/100",
        "",
        f"COMPOSITE SCORE:               {result.composite_score:6.1f}/100",
        "",
        "════════════════════════════════════════════════════════════════",
        "",
        "PERFORMANCE",
        "────────────────────────────────────────────────────────────────",
        f"Baseline Score:                {result.baseline_score:6.1f}",
        f"Final Score:                   {result.final_score:6.1f}",
        f"Total Improvement:             {result.improvement:+6.1f} ({result.improvement / result.baseline_score * 100:+.1f}%)",
        f"Improvement per Iteration:     {result.improvement_per_iteration:+6.1f}",
        f"Iterations Used:               {result.iterations_completed}/{result.iterations_allowed}",
        f"Duration:                      {result.duration_seconds:.1f}s",
        "",
        "════════════════════════════════════════════════════════════════",
        "",
    ]

    if result.agent_explanation:
        lines.extend(
            [
                "AGENT EXPLANATION",
                "────────────────────────────────────────────────────────────────",
                result.agent_explanation,
                "",
                "════════════════════════════════════════════════════════════════",
                "",
            ]
        )

    if result.errors:
        lines.extend(
            [
                "ERRORS ENCOUNTERED",
                "────────────────────────────────────────────────────────────────",
            ]
        )
        for error in result.errors:
            lines.append(f"  • {error}")
        lines.extend(["", "════════════════════════════════════════════════════════════════", ""])

    return "\n".join(lines)

# CIE Agent Self-Optimization Testing Guide

## Overview

This framework tests **meta-level AI capability** - how well agents can use CIE itself to optimize and evaluate their own performance. Instead of benchmarking coding ability, we're measuring:

- **Can agents effectively use optimization frameworks?**
- **Can they interpret multi-dimensional metrics?**
- **Do they make good decisions under uncertainty?**
- **Can they learn and adapt their strategy?**
- **How well do they understand tradeoff spaces?**

## The Core Loop

```
1. Agent understands problem
   ↓
2. Agent defines optimization workload
   ↓
3. Agent proposes policies using CIE optimizers
   ↓
4. Agent evaluates using CIE evaluators
   ↓
5. Agent analyzes results and metrics
   ↓
6. Agent makes adoption/rejection decision
   ↓
7. Agent learns from outcome
   ↓
8. Loop: repeat N times
```

## What Gets Measured

### Five Performance Dimensions

**1. Optimization Effectiveness (30%)**
- How well does agent traverse solution space?
- Better policies than random baseline?
- Final policy quality vs theoretical optimum
- Convergence speed

**2. Decision Quality (25%)**
- How good are adoption/rejection decisions?
- False positives (adopted bad policies)?
- False negatives (rejected good policies)?
- Alignment with stated objectives

**3. Metrics Interpretation (20%)**
- Does agent correctly understand metrics?
- Can it identify and explain tradeoffs?
- Recognizes when results are inconclusive?
- Handles conflicting information?

**4. Learning Trajectory (15%)**
- Improvement per iteration?
- Can agent escape local optima?
- Refines strategy over iterations?
- Recovers from mistakes?

**5. Pareto Understanding (10%)**
- Recognizes multi-dimensional tradeoffs?
- Understands non-dominated solutions?
- Can find solutions matching preferences?

### Composite Score

```
Score = 30% × OptimizationEffectiveness
       + 25% × DecisionQuality
       + 20% × MetricsInterpretation
       + 15% × LearningTrajectory
       + 10% × ParetoUnderstanding
```

**Tiers:**
- 90-100: Expert (excellent understanding, strong optimization)
- 75-90: Proficient (good understanding, effective optimization)
- 60-75: Competent (basic understanding, some effectiveness)
- 40-60: Developing (limited understanding, poor optimization)
- 0-40: Novice (misunderstands framework, ineffective)

## Scenarios (13 Total)

### Easy (2 scenarios) - Basic understanding

**Simple Improvement**
- Single metric optimization (latency)
- Clear gradient (lower = better)
- 5 iterations
- Goal: Reduce latency by 40%+
- Tests: Can agent use basic optimizer?

**Throughput Optimization**
- Maximize throughput
- Slightly noisy (5% noise)
- 5 iterations
- Goal: Increase throughput by 40%+
- Tests: Can agent handle different metric directions?

### Medium (5 scenarios) - Tradeoffs and constraints

**Latency vs Accuracy**
- 2D tradeoff: lower latency OR higher accuracy
- Must choose a point on Pareto frontier
- 8 iterations
- Tests: Does agent understand tradeoffs?

**Three-Way Tradeoff**
- 3D: latency, accuracy, cost
- No policy optimizes all three
- Must find best compromise
- 10 iterations
- Tests: Can agent weigh multiple objectives?

**All Equal**
- All policies perform identically
- Tests: Does agent recognize futility?

**All Bad**
- All policies perform poorly
- Tests: Handles failure gracefully?

**Missing Metrics**
- Some metrics unavailable
- Tests: Robust to incomplete data?

### Hard (3 scenarios) - Complex challenges

**Noisy Optimization**
- 25% noise in measurements
- Hard to distinguish signal from noise
- 12 iterations
- Tests: Doesn't overfit to noise?

**Escape Local Optimum**
- Local optimum at score 65
- Global optimum at score 80+
- Must diversify search
- 15 iterations
- Tests: Can agent escape local maxima?

**Conflicting Objectives**
- Throughput, latency, memory all in conflict
- Improving one hurts others
- 10 iterations
- Tests: Complex tradeoff management?

### Expert (3 scenarios) - Advanced challenges

**Multi-Objective Learning**
- 5D problem (accuracy, latency, cost, throughput, memory)
- Pareto frontier with 5-7 solutions
- 20 iterations
- Tests: Can characterize complex tradeoff space?

**Adaptive Strategy**
- Optimal strategy changes mid-optimization
- Must detect and adapt
- 15 iterations
- Tests: Learns and evolves approach?

**Extreme Uncertainty**
- 40% noise
- Metric clarity only 50%
- Almost no signal
- 12 iterations
- Tests: Handles extreme ambiguity?

## Scenario Details

Each scenario has:

```python
scenario = OptimizationScenario(
    scenario_id="unique_id",
    name="Human Name",
    description="What the agent needs to do",
    difficulty="easy|medium|hard|expert",
    
    # Problem definition
    objective="What to optimize",
    metrics_to_optimize=["metric1", "metric2"],
    metrics_directions={"metric1": "minimize", "metric2": "maximize"},
    
    # Constraints
    iterations_allowed=5,
    timeout_seconds=300,
    
    # Success criteria
    baseline_score=50.0,      # Starting point
    target_score=75.0,        # Goal
    success_threshold=0.6,    # % improvement needed
    
    # Difficulty factors
    noise_level=0.1,          # 0-1
    exploration_difficulty=1.0,
    metric_clarity=0.9,       # 0-1
    
    # Guidance
    hints=["hint1", "hint2"],
    example_approach="how to approach this..."
)
```

## Example: How It Works

### Scenario: Latency vs Accuracy

**Setup:**
- Agent goal: Find best tradeoff between fast responses (low latency) and accurate responses (high accuracy)
- Baseline score: 50
- Target score: 70
- Allowed iterations: 8

**Iteration 1: Agent's Process**

```
Agent thinks:
  "I need to balance speed and accuracy. Let me understand the tradeoff.
   I'll start with a baseline policy."

Agent action:
  1. Define workload: "Test accuracy and latency"
  2. Propose policy: baseline (temp=0.5, max_tokens=100)
  3. Evaluate: latency=150ms, accuracy=65%
  4. Record: baseline_score = 50

Agent decision:
  "Baseline is established. Now I'll try to improve both metrics."
```

**Iteration 2:**

```
Agent thinks:
  "To improve accuracy, I need more reasoning. But that increases latency.
   Let me try higher accuracy and accept latency tradeoff."

Agent action:
  1. Propose policy: accuracy_focused (temp=0.1, max_tokens=200)
  2. Evaluate: latency=250ms, accuracy=78%
  3. Analyze: accuracy improved (+13%), latency hurt (+100ms)

Agent reasoning:
  "This is better on accuracy but worse on latency. It's a clear tradeoff.
   I should look for middle ground next."

Agent decision: "Adopt this policy - accuracy gain outweighs latency cost"
  Confidence: 70%
  Justification: "Accuracy improved significantly, latency still acceptable"
```

**Iteration 3:**

```
Agent thinks:
  "Now try to balance both metrics. Use medium settings."

Agent action:
  1. Propose policy: balanced (temp=0.3, max_tokens=150)
  2. Evaluate: latency=200ms, accuracy=72%

Agent analysis:
  "This is between my two previous policies on both dimensions.
   It's on the Pareto frontier - neither dominated by others."

Agent decision: "Reject - middle ground isn't better than best accuracy"
  Confidence: 85%
```

**Iterations 4-8:**
- Continue exploring the Pareto frontier
- Eventually converge on best solution matching preferences
- Learn that accuracy matters more than latency for this use case

**Final Evaluation:**

```
Metric: OptimizationEffectiveness = 75/100
  "Agent found good policy (accuracy 78%, latency 200ms)"

Metric: DecisionQuality = 82/100
  "Most decisions were correct, one suboptimal iteration"

Metric: MetricsInterpretation = 90/100
  "Clearly understood latency-accuracy tradeoff"

Metric: LearningTrajectory = 78/100
  "Improved each iteration, good convergence"

Metric: ParetoUnderstanding = 85/100
  "Identified Pareto frontier, found balanced solution"

Composite Score: 81/100 → "Proficient"
```

## API Usage

### For Implementers

```python
from self_optimize.agent_optimizer import AgentOptimizer, OptimizationResult
from self_optimize.scenarios import EASY_SCENARIOS, get_scenarios_by_difficulty
from cie.core.backend import CIEBackend

# 1. Create agent that extends AgentOptimizer
class MyAgent(AgentOptimizer):
    def run_optimization(self, scenario, backend):
        """Implement optimization logic"""
        # Access scenario properties
        print(f"Optimizing: {scenario.objective}")
        print(f"Metrics: {scenario.metrics_to_optimize}")
        print(f"Iterations allowed: {scenario.iterations_allowed}")
        
        # Your optimization loop
        for iteration in range(scenario.iterations_allowed):
            # Propose policy
            policy = self.propose_policy(...)
            
            # Evaluate
            trial = backend.run_trial(policy, workload)
            
            # Analyze
            analysis = self.analyze_results(...)
            
            # Decide
            decision, reasoning, confidence = self.make_adoption_decision(...)
            
            # Record step
            self.record_step(
                step_number=iteration,
                policy=policy,
                metrics=trial.metrics,
                decision=decision,
                reasoning=reasoning,
                confidence=confidence,
                metrics_understood=analysis['understood'],
                decision_quality=evaluate_decision_quality(...)
            )
        
        # Return results
        return create_result(...)
    
    def propose_policy(self, current_state, previous_results):
        """Propose next policy to test"""
        # Implement your strategy here
        pass
    
    def analyze_results(self, trial_results, metrics):
        """Extract insights from results"""
        # Understand what the metrics mean
        pass
    
    def make_adoption_decision(self, policy, metrics, previous_best):
        """Decide to adopt or reject"""
        # Make principled decision
        return "adopt", "because...", 85.0

# 2. Run benchmark
backend = CIEBackend()
agent = MyAgent("My-Agent")

for scenario in EASY_SCENARIOS:
    result = agent.run_optimization(scenario, backend)
    print(result.composite_score)
    print(f"Performance tier: {result.performance_tier}")
```

### Key Methods

**propose_policy(current_state, previous_results)**
- Should propose next policy to evaluate
- Consider: previous results, trends, unexplored areas
- Return: dict of policy parameters

**analyze_results(trial_results, metrics)**
- Interpret what the results mean
- Identify patterns, tradeoffs, relationships
- Return: dict with insights

**make_adoption_decision(candidate_policy, metrics, previous_best)**
- Decide: adopt, reject, or unclear
- Reasoning must be explicit
- Confidence 0-100
- Return: (decision, reasoning, confidence)

## Interpreting Results

### Example Report

```
╔════════════════════════════════════════════════════════════════╗
║      AGENT SELF-OPTIMIZATION BENCHMARK REPORT                 ║
╚════════════════════════════════════════════════════════════════╝

Agent: Claude-3-Opus
Scenario: Multi-Dimensional Tradeoff
Performance Tier: Proficient

════════════════════════════════════════════════════════════════

SCORES
────────────────────────────────────────────────────────────────
Optimization Effectiveness:    75.3/100
Metrics Interpretation:        84.2/100
Decision Quality:              81.5/100
Learning Trajectory:           72.1/100
Pareto Understanding:          88.7/100

COMPOSITE SCORE:               80.2/100 → Proficient

════════════════════════════════════════════════════════════════

PERFORMANCE
────────────────────────────────────────────────────────────────
Baseline Score:                50.0
Final Score:                   72.5
Total Improvement:            +22.5 (+45%)
Improvement/Iteration:        +2.8
Iterations Used:              8/10
Duration:                      45.3s
```

### What Good Performance Looks Like

**High Optimization Effectiveness (85%+)**
- Finds policies significantly better than baseline
- Minimal wasted iterations
- Good convergence
- Example: +40% improvement in 8 iterations

**High Decision Quality (85%+)**
- Correct adoption/rejection decisions
- Rarely adopts bad policies
- Reasoning is sound
- Example: 7/8 decisions correct

**High Metrics Interpretation (90%+)**
- Correctly understands what metrics mean
- Identifies tradeoffs accurately
- Recognizes relationships
- Example: "Accuracy-latency tradeoff clearly understood"

**High Learning Trajectory (80%+)**
- Improves each iteration
- Consistent progress
- Learns from mistakes
- Example: +3% improvement per iteration

**High Pareto Understanding (85%+)**
- Recognizes multi-dimensional nature
- Identifies non-dominated solutions
- Makes principled choices
- Example: "Found 3 frontier points, chose best for priorities"

## Testing Progression

### Level 1: Can They Use CIE?
Run: Easy scenarios
Goal: 70%+ on basic single-metric optimization
Question: Does agent understand the framework?

### Level 2: Can They Handle Tradeoffs?
Run: Medium scenarios
Goal: 65%+ on 2-3D optimization
Question: Does agent understand multi-dimensional optimization?

### Level 3: Can They Optimize Effectively?
Run: Hard scenarios
Goal: 60%+ with noise and complexity
Question: Can agent handle real-world uncertainty?

### Level 4: Can They Think Strategically?
Run: Expert scenarios
Goal: 55%+ on complex 5D problems
Question: Does agent have sophisticated reasoning?

## Advanced Features

### Multi-Agent Comparison

Run same scenarios with different models:

```
Agent        Easy    Medium  Hard    Expert  Composite
GPT-4        95      82      71      58      81
Claude-3     92      85      68      62      82
Llama-2      78      65      45      30      60
```

### Iterative Improvement

Track agent over multiple runs:

```
Run 1: 72/100
Run 2: 74/100 (+2)
Run 3: 78/100 (+4)
Run 4: 79/100 (+1)
```

Agent is learning to use CIE more effectively!

## Common Patterns

### Pattern 1: "Explores Well, Decides Poorly"
- High optimization effectiveness
- Low decision quality
- Agent: finds good policies but picks wrong ones

### Pattern 2: "Understands Metrics, Can't Optimize"
- High metrics interpretation
- Low optimization effectiveness
- Agent: knows what metrics mean but can't find good policies

### Pattern 3: "Learns Over Time"
- Improving trajectory
- Better decisions in later iterations
- Agent: gets smarter as it goes

### Pattern 4: "Scared of Tradeoffs"
- Avoids complex metrics
- Looks for dominated solutions
- Agent: doesn't understand Pareto frontiers

### Pattern 5: "Overfits to Noise"
- Works in easy/medium scenarios
- Fails in hard/noisy scenarios
- Agent: can't distinguish signal from noise

## Troubleshooting

**Agent scores 0 on everything**
- Not using CIE API correctly
- Not recording steps
- Failing to evaluate policies

**Agent scores high on easy, zero on hard**
- Can't handle noise
- Assumes deterministic evaluation
- Needs to learn robustness

**Agent has high interpretation, low optimization**
- Understands framework but doesn't know how to search
- Needs better exploration strategy
- Maybe proposal function is too narrow

**Composite score low but one dimension high**
- Strength in one area
- Weakness in another
- Good for identifying specific weaknesses

## Next Steps

1. **Implement Your Agent**
   - Extend AgentOptimizer
   - Implement the three key methods
   - Test on easy scenarios first

2. **Run Easy Scenarios**
   - Baseline: Can agent use CIE?
   - Goal: 70%+ on each

3. **Progress to Medium**
   - Now test tradeoff handling
   - Goal: 65%+ on each

4. **Challenge with Hard**
   - Real-world complexity
   - Goal: 60%+ on each

5. **Compare Results**
   - Multiple agents on same scenarios
   - Which agent type performs best?
   - What capabilities matter most?

## Key Insights

### What This Tests

Not just "can the agent code" but:
- **Reasoning**: Understanding complex systems
- **Decision Making**: Choosing optimally under uncertainty
- **Learning**: Improving from experience
- **Meta-Cognition**: Understanding own performance
- **Systems Thinking**: Seeing relationships and tradeoffs

### Why It Matters

This is **meta-level AI capability** - the ability to think about systems, optimize complex problems, and make good decisions. It's more fundamental than any specific task.

An agent that can:
- Optimize itself using CIE
- Understand multi-dimensional tradeoffs
- Learn and adapt
- Make good decisions under uncertainty

...is demonstrating advanced reasoning and judgment that transfers across domains.

### The Recursion

The interesting part: **agents using the optimization framework to optimize themselves**. This creates a recursive loop where:
- Agent uses CIE to find better policies
- CIE measures how well agent did
- Agent learns from measurement
- Loop continues

It's agents thinking about their own thinking.

---

**Created**: 2024
**Status**: Framework Ready
**Scenarios**: 13 total (2 easy, 5 medium, 3 hard, 3 expert)
**Version**: 1.0
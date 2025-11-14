"""
DSPy-based optimization algorithm for CIE.
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from typing import Any

from cie.config.settings import get_config
from cie.core.models import Optimizer, Policy

logger = logging.getLogger(__name__)


class DSPyOptimizer(Optimizer):
    """
    DSPy-based optimizer that uses few-shot learning and bootstrap techniques.
    This optimizer uses DSPy to compile prompts and generate optimized policies
    based on evaluation feedback.
    """

    name = "DSPy:BootstrapFewShot"

    def __init__(
        self,
        k_shots: int = 8,
        model: str = "gpt-4o-mini",
        bootstrap_iterations: int = 5,
        metric_threshold: float = 0.8,
        **kwargs,
    ):
        """
        Initialize DSPy optimizer.
        Args:
            k_shots: Number of few-shot examples to use
            model: Model name to use for generation
            bootstrap_iterations: Number of bootstrap iterations
            metric_threshold: Minimum metric threshold for success
            **kwargs: Additional arguments for model configuration
        """
        self.k_shots = k_shots
        self.model = model
        self.bootstrap_iterations = bootstrap_iterations
        self.metric_threshold = metric_threshold
        self.kwargs = kwargs
        # State tracking
        self.best_score: float | None = None
        self.best_artifact: str | None = None
        self.best_policy: Policy | None = None
        self.trial_history: list[dict[str, Any]] = []
        self.bootstrap_examples: list[dict[str, Any]] = []
        # Initialize model provider
        self.config = get_config()
        self._initialize_model()
        self._dspy_module = None
        self._dspy_policy_program = None
        self._dspy_status = "DSPy unavailable"
        self._setup_dspy()

    def _initialize_model(self) -> None:
        """Initialize the model provider."""
        try:
            # Try to import and initialize the model provider
            from cie.utils.model_providers import get_model_provider

            self.model_provider = get_model_provider(
                provider=self.config.model.provider,
                model_name=self.model,
                api_key=self.config.model.api_key,
                **self.kwargs,
            )
        except Exception as e:
            # Fallback to mock implementation if real provider fails
            print(f"Warning: Failed to initialize model provider: {e}")
            from cie.utils.model_providers import MockModelProvider

            self.model_provider = MockModelProvider(model_name=self.model)

    def _setup_dspy(self) -> None:
        """Configure DSPy runtime if available."""
        try:
            import dspy  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - optional dependency
            logger.debug("DSPy import failed: %s", exc)
            self._dspy_status = f"DSPy unavailable: {exc}"
            return

        provider = (self.config.model.provider or "").lower()
        try:
            if provider != "openai":
                raise RuntimeError(
                    "DSPy optimizer currently supports the 'openai' provider. "
                    "Switch to OpenAI or install another DSPy-compatible LM."
                )
            if not getattr(self.config.model, "api_key", None):
                raise RuntimeError("OPENAI_API_KEY is required to run DSPy optimizers.")
            temperature = self.config.model.temperature
            max_tokens = self.config.model.max_tokens
            if hasattr(dspy, "OpenAI"):  # DSPy < 3.0
                lm = dspy.OpenAI(  # type: ignore[attr-defined]
                    model=self.model,
                    api_key=self.config.model.api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:  # DSPy >= 3.0 uses litellm-backed LM
                try:
                    from dspy.clients import LM as DSPyLM  # type: ignore[import-not-found]
                except Exception as import_error:  # pragma: no cover - optional dependency
                    raise RuntimeError("DSPy LM client not available") from import_error

                os.environ.setdefault("OPENAI_API_KEY", self.config.model.api_key or "")
                provider_model = (
                    self.model if "/" in self.model else f"openai/{self.model}"
                )
                lm = DSPyLM(
                    model=provider_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            dspy.settings.configure(lm=lm)  # type: ignore[attr-defined]

            class PolicySynthesisSignature(
                dspy.Signature  # type: ignore[attr-defined,misc]
            ):
                """Generate policy_json for the optimization engine.

                state_context -> policy_json
                """

            class PolicySynthesisProgram(dspy.Module):  # type: ignore[attr-defined,misc]
                """DSPy module that produces structured policy JSON."""

                def __init__(self):
                    super().__init__()
                    self.predict = dspy.Predict(PolicySynthesisSignature)  # type: ignore[attr-defined]

                def forward(self, state_context: str):
                    return self.predict(state_context=state_context)

            self._dspy_module = dspy
            self._dspy_policy_program = PolicySynthesisProgram()
            self._dspy_status = "DSPy active"
        except Exception as exc:  # pragma: no cover - optional dependency
            logger.warning("Failed to configure DSPy optimizer: %s", exc)
            self._dspy_module = None
            self._dspy_policy_program = None
            self._dspy_status = f"DSPy disabled: {exc}"

    def propose(self, state: dict[str, Any]) -> Policy:
        """
        Propose a new policy using DSPy compilation.
        Args:
            state: Current optimization state
        Returns:
            New policy proposal
        """
        # Generate artifact ID
        artifact_id = f"dspy-{int(time.time() * 1000)}-{self.k_shots}"
        bootstrap_prompt = (
            self._create_bootstrap_prompt()
            if self.bootstrap_examples
            else self._create_initial_prompt()
        )

        policy_params: dict[str, Any] | None = None
        if self._dspy_policy_program:
            policy_params = self._generate_policy_params_with_dspy(
                state, artifact_id, bootstrap_prompt
            )

        if not policy_params:
            policy_params = self._generate_policy_params_via_provider(
                bootstrap_prompt, state, artifact_id
            )

        # Create actions based on the policy
        actions = self._generate_actions(policy_params)
        policy = Policy(
            name=self.name,
            params=policy_params,
            actions=actions,
            metadata={
                "artifact_id": artifact_id,
                "bootstrap_examples": len(self.bootstrap_examples),
                "created_at": datetime.now().isoformat(),
                "engine": "dspy" if self._dspy_policy_program else "prompt",
                "dspy_status": self._dspy_status,
            },
        )
        return policy

    def observe(self, policy: Policy, metrics: dict[str, float]) -> None:
        """
        Observe the results of a policy evaluation.
        Args:
            policy: The policy that was evaluated
            metrics: Evaluation metrics
        """
        # Calculate score based on metrics
        score = self._calculate_score(metrics)
        # Store trial history
        trial_record = {
            "policy": policy,
            "metrics": metrics,
            "score": score,
            "timestamp": datetime.now().isoformat(),
        }
        self.trial_history.append(trial_record)
        # Update best policy if this is better
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_policy = policy
            if "artifact" in policy.params:
                self.best_artifact = policy.params["artifact"]
        # Add to bootstrap examples if it's a good example
        if score >= self.metric_threshold:
            self.bootstrap_examples.append(trial_record)
            # Keep only the best examples
            self.bootstrap_examples.sort(key=lambda x: x["score"], reverse=True)
            self.bootstrap_examples = self.bootstrap_examples[: self.k_shots]

    def get_state(self) -> dict[str, Any]:
        """Get current optimizer state."""
        return {
            "name": self.name,
            "k_shots": self.k_shots,
            "model": self.model,
            "bootstrap_iterations": self.bootstrap_iterations,
            "metric_threshold": self.metric_threshold,
            "best_score": self.best_score,
            "best_artifact": self.best_artifact,
            "trial_count": len(self.trial_history),
            "bootstrap_example_count": len(self.bootstrap_examples),
            "dspy_enabled": bool(self._dspy_policy_program),
            "dspy_status": self._dspy_status,
        }

    def reset(self) -> None:
        """Reset optimizer to initial state."""
        self.best_score = None
        self.best_artifact = None
        self.best_policy = None
        self.trial_history.clear()
        self.bootstrap_examples.clear()

    def _create_initial_prompt(self) -> str:
        """Create initial prompt for policy generation."""
        return f"""
        You are an optimization expert. Generate policy parameters for a {self.model} model
        to optimize system performance. Consider these aspects:
        1. Model configuration (temperature, max_tokens, etc.)
        2. Prompt engineering strategies
        3. Context management
        4. Error handling
        5. Performance optimization
        Return a JSON object with policy parameters.
        """

    def _create_bootstrap_prompt(self) -> str:
        """Create bootstrap prompt using successful examples."""
        examples_text = ""
        for i, example in enumerate(self.bootstrap_examples[: self.k_shots]):
            examples_text += f"\nExample {i + 1}:\n"
            examples_text += f"Policy: {example['policy'].params}\n"
            examples_text += f"Metrics: {example['metrics']}\n"
            examples_text += f"Score: {example['score']:.4f}\n"
        return f"""
        You are an optimization expert. Based on these successful policy examples:
        {examples_text}
        Generate new policy parameters that are likely to achieve even better results.
        Focus on improving the metrics while maintaining stability.
        Return a JSON object with policy parameters.
        """

    def _generate_policy_params_with_dspy(
        self, state: dict[str, Any], artifact_id: str, bootstrap_prompt: str
    ) -> dict[str, Any] | None:
        """Generate policy parameters using the DSPy runtime."""
        if not self._dspy_policy_program:
            return None
        try:
            state_context = self._compose_state_context(state, bootstrap_prompt)
            result = self._dspy_policy_program(state_context=state_context)
            policy_blob = getattr(result, "policy_json", "") or getattr(result, "text", "")
            params = self._parse_policy_blob(policy_blob)
            params.setdefault("artifact", artifact_id)
            params.setdefault("k_shots", self.k_shots)
            params.setdefault("model", self.model)
            params.setdefault("strategy", "dspy_bootstrap")
            params.setdefault("bootstrap_count", len(self.bootstrap_examples))
            return params
        except Exception as exc:
            logger.warning("DSPy policy generation failed: %s", exc)
            return None

    def _generate_policy_params_via_provider(
        self, prompt: str, state: dict[str, Any], artifact_id: str
    ) -> dict[str, Any]:
        """Generate policy parameters using the configured model provider."""
        try:
            response = self.model_provider.generate(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=1000,
                format="json",
            )
            params = self._parse_policy_blob(response)
            params.setdefault("artifact", artifact_id)
            params.setdefault("k_shots", self.k_shots)
            params.setdefault("model", self.model)
            params.setdefault("strategy", "few_shot_prompt")
            params.setdefault("bootstrap_count", len(self.bootstrap_examples))
            return params
        except Exception as exc:
            logger.warning("Fallback policy generation failed: %s", exc)
            return {
                "artifact": artifact_id,
                "k_shots": self.k_shots,
                "model": self.model,
                "strategy": "few_shot_default",
                "bootstrap_count": len(self.bootstrap_examples),
            }

    def _compose_state_context(self, state: dict[str, Any], bootstrap_prompt: str) -> str:
        """Compose contextual summary for DSPy policy synthesis."""
        lines: list[str] = [
            f"Target model: {self.model}",
            f"k_shots: {self.k_shots}",
            f"bootstrap_iterations: {self.bootstrap_iterations}",
            f"metric_threshold: {self.metric_threshold}",
            "Metric weights:",
        ]
        for metric, weight in self.config.evaluation.metric_weights.items():
            lines.append(f"- {metric}: {weight}")
        active_policy = state.get("active_policy")
        if active_policy:
            lines.append(f"Active policy: {active_policy.name}")
        trials = state.get("trials") or []
        if trials:
            lines.append("Recent trials:")
            for trial in trials[-5:]:
                metrics = trial.metrics
                lines.append(
                    f"- score={trial.score:.4f} success={metrics.get('task_success', 0):.3f} "
                    f"latency={metrics.get('latency_p95', 0):.1f}ms "
                    f"cost={metrics.get('cost_per_req', 0):.5f}"
                )
        if self.bootstrap_examples:
            lines.append("Successful bootstrap examples:")
            for example in self.bootstrap_examples[: self.k_shots]:
                metrics = example["metrics"]
                lines.append(
                    f"- params={example['policy'].params} score={example['score']:.4f} "
                    f"success={metrics.get('task_success', 0):.3f}"
                )
        lines.append("Prompt guidance:")
        lines.append(bootstrap_prompt.strip())
        return "\n".join(lines)

    @staticmethod
    def _parse_policy_blob(blob: str) -> dict[str, Any]:
        """Parse JSON policy blocks with optional code fences."""
        text = blob.strip()
        if not text:
            return {}
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
            text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    pass
        return {}

    def _generate_actions(self, params: dict[str, Any]) -> list[str]:
        """Generate actions based on policy parameters."""
        actions = []
        if "artifact" in params:
            actions.append(f"dspy.use(artifact='{params['artifact']}')")
        if "temperature" in params:
            actions.append(f"model.set_temperature({params['temperature']})")
        if "max_tokens" in params:
            actions.append(f"model.set_max_tokens({params['max_tokens']})")
        if "prompt_template" in params:
            actions.append(f"prompt.use_template('{params['prompt_template']}')")
        if "context_strategy" in params:
            actions.append(f"context.set_strategy('{params['context_strategy']}')")
        # Add default actions if none generated
        if not actions:
            actions = [
                f"dspy.use(artifact='{params.get('artifact', 'default')}')",
                "model.optimize_parameters()",
                "context.manage_usage()",
            ]
        return actions

    def _calculate_score(self, metrics: dict[str, float]) -> float:
        """Calculate a composite score from metrics."""
        weights = self.config.evaluation.metric_weights
        score = 0.0
        for metric, weight in weights.items():
            value = metrics.get(metric, 0.0)
            score += weight * value
        return -score  # Negative because lower is better in our scoring system

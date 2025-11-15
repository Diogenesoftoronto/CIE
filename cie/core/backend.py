"""
Backend state management and scoring for CIE.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from cie.config.settings import CIEConfig, get_config
from cie.core.models import Evaluator, Optimizer, Policy, Trial, Workload, Prompt
from cie.evaluators import get_evaluator, list_evaluators
from cie.optimizers.dspy_optimizer import DSPyOptimizer
from cie.utils.wandb_import import load_wandb_rows, resolve_wandb_run_path


class StorageBackend(Protocol):
    """Protocol for storage backends."""

    def save_trial(self, trial: Trial) -> None:
        """Save a trial to storage."""
        ...

    def get_trials(self, limit: int | None = None) -> list[Trial]:
        """Get trials from storage."""
        ...

    def save_policy(self, policy: Policy) -> None:
        """Save a policy to storage."""
        ...

    def get_policies(self) -> list[Policy]:
        """Get all policies from storage."""
        ...

    def save_prompt(self, prompt: Prompt) -> None:
        """Save a prompt to storage."""
        ...

    def get_prompts(self) -> list[Prompt]:
        """Get all prompts from storage."""
        ...

    def delete_prompt(self, prompt_id: str) -> None:
        """Delete a prompt from storage."""
        ...

    def close(self) -> None:
        """Close storage connection."""
        ...


class SQLiteStorageBackend:
    """SQLite-based storage backend."""

    def __init__(self, database_path: str):
        self.database_path = Path(database_path).expanduser()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize the database schema."""
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        # Create tables
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_name TEXT NOT NULL,
                workload TEXT NOT NULL,
                metrics TEXT NOT NULL,
                score REAL NOT NULL,
                created_at TEXT NOT NULL,
                artifact_id TEXT,
                notes TEXT,
                metadata TEXT
            )
        """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS policies (
                name TEXT PRIMARY KEY,
                params TEXT NOT NULL,
                actions TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT
            )
        """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workloads (
                name TEXT PRIMARY KEY,
                items INTEGER NOT NULL,
                description TEXT,
                config TEXT,
                tags TEXT
            )
        """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS prompts (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                description TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT
            )
        """
        )
        self.connection.commit()

    def save_trial(self, trial: Trial) -> None:
        """Save a trial to storage."""
        self.connection.execute(
            """
            INSERT INTO trials (
                policy_name, workload, metrics, score, created_at,
                artifact_id, notes, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                trial.policy_name,
                trial.workload,
                json.dumps(trial.metrics),
                trial.score,
                trial.created_at.isoformat(),
                trial.artifact_id,
                trial.notes,
                json.dumps(trial.metadata),
            ),
        )
        self.connection.commit()

    def get_trials(self, limit: int | None = None) -> list[Trial]:
        """Get trials from storage."""
        query = "SELECT * FROM trials ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        cursor = self.connection.execute(query)
        rows = cursor.fetchall()
        trials = []
        for row in rows:
            trial = Trial(
                id=row["id"],
                policy_name=row["policy_name"],
                metrics=json.loads(row["metrics"]),
                score=row["score"],
                workload=row["workload"],
                created_at=datetime.fromisoformat(row["created_at"]),
                artifact_id=row["artifact_id"],
                notes=row["notes"] or "",
                metadata=json.loads(row["metadata"] or "{}"),
            )
            trials.append(trial)
        return trials

    def save_policy(self, policy: Policy) -> None:
        """Save a policy to storage."""
        self.connection.execute(
            """
            INSERT OR REPLACE INTO policies (
                name, params, actions, created_at, metadata
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                policy.name,
                json.dumps(policy.params),
                json.dumps(policy.actions),
                policy.created_at.isoformat(),
                json.dumps(policy.metadata),
            ),
        )
        self.connection.commit()

    def get_policies(self) -> list[Policy]:
        """Get all policies from storage."""
        cursor = self.connection.execute("SELECT * FROM policies")
        rows = cursor.fetchall()
        policies = []
        for row in rows:
            policy = Policy(
                name=row["name"],
                params=json.loads(row["params"]),
                actions=json.loads(row["actions"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                metadata=json.loads(row["metadata"] or "{}"),
            )
            policies.append(policy)
        return policies

    def save_prompt(self, prompt: Prompt) -> None:
        """Save a prompt to storage."""
        self.connection.execute(
            """
            INSERT OR REPLACE INTO prompts (
                id, content, description, tags, created_at, updated_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                prompt.id,
                prompt.content,
                prompt.description,
                json.dumps(prompt.tags),
                prompt.created_at.isoformat(),
                prompt.updated_at.isoformat(),
                json.dumps(prompt.metadata),
            ),
        )
        self.connection.commit()

    def get_prompts(self) -> list[Prompt]:
        """Get all prompts from storage."""
        cursor = self.connection.execute("SELECT * FROM prompts")
        rows = cursor.fetchall()
        prompts = []
        for row in rows:
            prompt = Prompt(
                id=row["id"],
                content=row["content"],
                description=row["description"] or "",
                tags=json.loads(row["tags"] or "[]"),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                metadata=json.loads(row["metadata"] or "{}"),
            )
            prompts.append(prompt)
        return prompts

    def delete_prompt(self, prompt_id: str) -> None:
        """Delete a prompt from storage."""
        self.connection.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
        self.connection.commit()

    def close(self) -> None:
        """Close storage connection."""
        if self.connection:
            self.connection.close()


class JSONStorageBackend:
    """JSON file-based storage backend."""

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.trials_file = self.data_dir / "trials.json"
        self.policies_file = self.data_dir / "policies.json"
        self.prompts_file = self.data_dir / "prompts.json"

    def _load_json(self, file_path: Path) -> list[dict[str, Any]]:
        """Load JSON data from file."""
        if not file_path.exists():
            return []
        try:
            with open(file_path) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return []

    def _save_json(self, file_path: Path, data: list[dict[str, Any]]) -> None:
        """Save JSON data to file."""
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def save_trial(self, trial: Trial) -> None:
        """Save a trial to storage."""
        trials = self._load_json(self.trials_file)
        trial_data = {
            "id": trial.id,
            "policy_name": trial.policy_name,
            "workload": trial.workload,
            "metrics": trial.metrics,
            "score": trial.score,
            "created_at": trial.created_at.isoformat(),
            "artifact_id": trial.artifact_id,
            "notes": trial.notes,
            "metadata": trial.metadata,
        }
        trials.append(trial_data)
        self._save_json(self.trials_file, trials)

    def get_trials(self, limit: int | None = None) -> list[Trial]:
        """Get trials from storage."""
        trials_data = self._load_json(self.trials_file)
        # Sort by created_at descending
        trials_data.sort(key=lambda x: x["created_at"], reverse=True)
        if limit:
            trials_data = trials_data[:limit]
        trials = []
        for data in trials_data:
            trial = Trial(
                id=data["id"],
                policy_name=data["policy_name"],
                metrics=data["metrics"],
                score=data["score"],
                workload=data["workload"],
                created_at=datetime.fromisoformat(data["created_at"]),
                artifact_id=data.get("artifact_id"),
                notes=data.get("notes", ""),
                metadata=data.get("metadata", {}),
            )
            trials.append(trial)
        return trials

    def save_policy(self, policy: Policy) -> None:
        """Save a policy to storage."""
        policies = self._load_json(self.policies_file)
        # Remove existing policy with same name
        policies = [p for p in policies if p["name"] != policy.name]
        policy_data = {
            "name": policy.name,
            "params": policy.params,
            "actions": policy.actions,
            "created_at": policy.created_at.isoformat(),
            "metadata": policy.metadata,
        }
        policies.append(policy_data)
        self._save_json(self.policies_file, policies)

    def get_policies(self) -> list[Policy]:
        """Get all policies from storage."""
        policies_data = self._load_json(self.policies_file)
        policies = []
        for data in policies_data:
            policy = Policy(
                name=data["name"],
                params=data["params"],
                actions=data["actions"],
                created_at=datetime.fromisoformat(data["created_at"]),
                metadata=data.get("metadata", {}),
            )
            policies.append(policy)
        return policies

    def save_prompt(self, prompt: Prompt) -> None:
        """Save a prompt to storage."""
        prompts = self._load_json(self.prompts_file)
        # Remove existing prompt with same id
        prompts = [p for p in prompts if p["id"] != prompt.id]
        prompt_data = {
            "id": prompt.id,
            "content": prompt.content,
            "description": prompt.description,
            "tags": prompt.tags,
            "created_at": prompt.created_at.isoformat(),
            "updated_at": prompt.updated_at.isoformat(),
            "metadata": prompt.metadata,
        }
        prompts.append(prompt_data)
        self._save_json(self.prompts_file, prompts)

    def get_prompts(self) -> list[Prompt]:
        """Get all prompts from storage."""
        prompts_data = self._load_json(self.prompts_file)
        prompts = []
        for data in prompts_data:
            prompt = Prompt(
                id=data["id"],
                content=data["content"],
                description=data.get("description", ""),
                tags=data.get("tags", []),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                metadata=data.get("metadata", {}),
            )
            prompts.append(prompt)
        return prompts

    def delete_prompt(self, prompt_id: str) -> None:
        """Delete a prompt from storage."""
        prompts = self._load_json(self.prompts_file)
        prompts = [p for p in prompts if p["id"] != prompt_id]
        self._save_json(self.prompts_file, prompts)

    def close(self) -> None:
        """Close storage connection (no-op for JSON backend)."""
        pass


class InMemoryStorageBackend:
    """In-memory storage backend for testing."""

    def __init__(self):
        self.trials: list[Trial] = []
        self.policies: list[Policy] = []
        self.prompts: list[Prompt] = []

    def save_trial(self, trial: Trial) -> None:
        """Save a trial to storage."""
        self.trials.append(trial)

    def get_trials(self, limit: int | None = None) -> list[Trial]:
        """Get trials from storage."""
        trials = sorted(self.trials, key=lambda x: x.created_at, reverse=True)
        if limit:
            trials = trials[:limit]
        return trials

    def save_policy(self, policy: Policy) -> None:
        """Save a policy to storage."""
        # Remove existing policy with same name
        self.policies = [p for p in self.policies if p.name != policy.name]
        self.policies.append(policy)

    def get_policies(self) -> list[Policy]:
        """Get all policies from storage."""
        return self.policies.copy()

    def save_prompt(self, prompt: Prompt) -> None:
        """Save a prompt to storage."""
        self.prompts = [p for p in self.prompts if p.id != prompt.id]
        self.prompts.append(prompt)

    def get_prompts(self) -> list[Prompt]:
        """Get all prompts from storage."""
        return self.prompts.copy()

    def delete_prompt(self, prompt_id: str) -> None:
        """Delete a prompt from storage."""
        self.prompts = [p for p in self.prompts if p.id != prompt_id]

    def close(self) -> None:
        """Close storage connection (no-op for in-memory backend)."""
        pass


class CIEBackend:
    """
    Central backend for CIE optimization framework.
    Manages optimizers, evaluators, trials, and scoring.
    """

    def __init__(self, config: CIEConfig | None = None):
        """Initialize the backend."""
        self.config = config or get_config()
        # Initialize storage
        self._initialize_storage()
        # Initialize workloads
        self.workloads = [
            Workload("MicroEval:basic", 50, "Basic micro evaluation workload"),
            Workload("MacroEval:rag-xl", 10, "Large RAG evaluation workload"),
            Workload("SyntheticLoad:cpu80", 1, "Synthetic CPU load at 80%"),
            Workload(
                "TextEval:qa-lite",
                3,
                "Reference QA cases scored with similarity metrics",
                config={"dataset": "text"},
            ),
            Workload(
                "TextEval:classify",
                4,
                "Sentiment and extraction tasks with Levenshtein scoring",
                config={
                    "dataset": "text",
                    "cases": [
                        {
                            "task": "Sentiment",
                            "prompt": (
                                "Classify the sentiment as positive or negative: "
                                "'The launch was chaotic, but users love the final product.'"
                            ),
                            "reference": "positive",
                            "guidance": "Reply with 'positive' or 'negative'.",
                        },
                        {
                            "task": "Short answer",
                            "prompt": "Which latency metric tracks the 95th percentile?",
                            "reference": "latency_p95",
                        },
                        {
                            "task": "Keyword extraction",
                            "prompt": (
                                "Extract the primary KPI mentioned here: "
                                "'Lower cost per request without reducing success rate.'"
                            ),
                            "reference": "cost per request",
                        },
                        {
                            "task": "Summarization",
                            "prompt": (
                                "Summarize in under 12 words: "
                                "'Braintrust relies on human-in-the-loop evaluation flows.'"
                            ),
                            "reference": "Braintrust uses human-in-the-loop evaluation.",
                        },
                    ],
                },
            ),
        ]
        # Initialize optimizers
        self.optimizers: list[Optimizer] = [
            DSPyOptimizer(k_shots=8, model=self.config.model.model_name),
            # Add other optimizers here
        ]
        self.optimizer_meta: list[dict[str, Any]] = [
            {"best_score": None, "artifact_id": None} for _ in self.optimizers
        ]
        # Initialize evaluator
        self.evaluator_slug = getattr(self.config.evaluation, "default_evaluator", "mock")
        self.evaluator: Evaluator = self._create_evaluator()
        # State management
        self.trials: list[Trial] = []
        self.pareto: list[Trial] = []
        self.active_policy: Policy | None = None
        self._trial_id_counter = 0
        # Load existing data
        self._load_existing_data()

    def _initialize_storage(self) -> None:
        """Initialize storage backend."""
        storage_type = self.config.storage.backend
        if storage_type == "sqlite":
            self.storage = SQLiteStorageBackend(self.config.storage.database_path)
        elif storage_type == "json":
            self.storage = JSONStorageBackend(self.config.storage.experiments_dir)
        elif storage_type == "memory":
            self.storage = InMemoryStorageBackend()
        else:
            raise ValueError(f"Unknown storage backend: {storage_type}")

    def _create_evaluator(self) -> Evaluator:
        """Create the evaluator instance based on configuration."""
        try:
            return get_evaluator(self.evaluator_slug, config=self.config)
        except ValueError as exc:
            raise ValueError(
                f"Evaluator '{self.evaluator_slug}' is not registered. "
                f"Available: {', '.join(e.name for e in list_evaluators())}"
            ) from exc

    def _load_existing_data(self) -> None:
        """Load existing data from storage."""
        # Load trials
        self.trials = self.storage.get_trials()
        if self.trials:
            self._trial_id_counter = max(trial.id for trial in self.trials)
        # Rebuild Pareto frontier
        self._rebuild_pareto()

    def score(self, metrics: dict[str, float]) -> float:
        """
        Calculate score from metrics using weighted combination.
        Args:
            metrics: Dictionary of metric names to values
        Returns:
            Calculated score (lower is better)
        """
        weights = self.config.evaluation.metric_weights
        # Missing metrics default to zero for robustness
        score = sum(
            weights.get(metric, 0.0) * float(metrics.get(metric, 0.0)) for metric in weights.keys()
        )
        return round(score, 6)

    @staticmethod
    def _dominates(a: Trial, b: Trial) -> bool:
        """
        Check if trial a dominates trial b in Pareto sense.
        Uses 3D comparison: latency, cost, (1-success)
        """
        la, ca, qa = (
            a.metrics.get("latency_p95", float("inf")),
            a.metrics.get("cost_per_req", float("inf")),
            1 - a.metrics.get("task_success", 0.0),
        )
        lb, cb, qb = (
            b.metrics.get("latency_p95", float("inf")),
            b.metrics.get("cost_per_req", float("inf")),
            1 - b.metrics.get("task_success", 0.0),
        )
        return (la <= lb and ca <= cb and qa <= qb) and (la < lb or ca < cb or qa < qb)

    def _rebuild_pareto(self) -> None:
        """Rebuild the Pareto frontier."""
        if not self.trials:
            self.pareto = []
            return
        # Find non-dominated trials
        pareto_trials = []
        for trial in self.trials:
            dominated = False
            for other in self.trials:
                if trial is not other and self._dominates(other, trial):
                    dominated = True
                    break
            if not dominated:
                pareto_trials.append(trial)
        # Remove duplicates and sort by latency
        seen_ids = set()
        unique_pareto = []
        for trial in sorted(
            pareto_trials, key=lambda x: x.metrics.get("latency_p95", float("inf"))
        ):
            if trial.id not in seen_ids:
                seen_ids.add(trial.id)
                unique_pareto.append(trial)
        self.pareto = unique_pareto

    def ingest_wandb_run(self, path: str | Path | None = None) -> list[Trial]:
        """Import metrics from a W&B run directory (latest-run by default)."""
        run_dir = resolve_wandb_run_path(path)
        rows = load_wandb_rows(run_dir)
        if not rows:
            return []

        existing_ids = {
            trial.metadata.get("wandb_row_id")
            for trial in self.trials
            if isinstance(trial.metadata, dict) and trial.metadata.get("wandb_row_id")
        }
        ingested: list[Trial] = []
        for row in rows:
            row_id = row["metadata"].get("wandb_row_id")
            if row_id and row_id in existing_ids:
                continue
            metrics = row["metrics"]
            if not metrics:
                continue
            self._trial_id_counter += 1
            trial = Trial(
                id=self._trial_id_counter,
                policy_name=row["policy_name"],
                metrics=metrics,
                score=self.score(metrics),
                workload=row["workload"],
                created_at=row["created_at"],
                artifact_id=row.get("artifact_id"),
                metadata=row["metadata"],
            )
            self.trials.append(trial)
            self.storage.save_trial(trial)
            ingested.append(trial)
            if row_id:
                existing_ids.add(row_id)

        if ingested:
            self._rebuild_pareto()
        return ingested

    def list_optimizers(self) -> list[tuple[str, dict[str, Any]]]:
        """
        List available optimizers with their metadata.
        Returns:
            List of (optimizer_name, metadata) tuples
        """
        result = []
        for optimizer, meta in zip(self.optimizers, self.optimizer_meta, strict=True):
            row = {
                "best_score": meta["best_score"],
                "artifact": meta["artifact_id"],
            }
            # Add optimizer-specific metadata
            if hasattr(optimizer, "k_shots"):
                row["k_shots"] = optimizer.k_shots
            if hasattr(optimizer, "model"):
                row["model"] = optimizer.model
            if hasattr(optimizer, "get_state"):
                row.update(optimizer.get_state())
            result.append((optimizer.name, row))
        return result

    def propose_once(self, optimizer_index: int) -> Policy:
        """
        Propose a policy using the specified optimizer.
        Args:
            optimizer_index: Index of the optimizer to use
        Returns:
            Proposed policy
        """
        if optimizer_index < 0 or optimizer_index >= len(self.optimizers):
            raise ValueError(f"Invalid optimizer index: {optimizer_index}")
        optimizer = self.optimizers[optimizer_index]
        # Build state for the optimizer
        state = {
            "trials": self.trials[-50:],  # Last 50 trials
            "pareto": self.pareto,
            "active_policy": self.active_policy,
            "config": self.config.to_dict(),
        }
        return optimizer.propose(state)

    def eval_policy(self, policy: Policy, workload_index: int) -> Trial:
        """
        Evaluate a policy on a workload.
        Args:
            policy: Policy to evaluate
            workload_index: Index of workload to use
        Returns:
            Trial with evaluation results
        """
        if workload_index < 0 or workload_index >= len(self.workloads):
            raise ValueError(f"Invalid workload index: {workload_index}")
        workload = self.workloads[workload_index]
        # Run evaluation
        metrics = self.evaluator.run(policy, workload)
        # Calculate score
        score = self.score(metrics)
        # Create trial
        self._trial_id_counter += 1
        trial = Trial(
            id=self._trial_id_counter,
            policy_name=policy.name,
            metrics=metrics,
            score=score,
            workload=workload.name,
            artifact_id=policy.params.get("artifact"),
            notes="",
            metadata={"workload_config": workload.config},
        )
        # Save trial
        self.trials.append(trial)
        self.storage.save_trial(trial)
        # Update optimizer metadata
        name_to_idx = {opt.name: i for i, opt in enumerate(self.optimizers)}
        if policy.name in name_to_idx:
            oi = name_to_idx[policy.name]
            best = self.optimizer_meta[oi]["best_score"]
            if best is None or score < best:
                self.optimizer_meta[oi]["best_score"] = score
                self.optimizer_meta[oi]["artifact_id"] = policy.params.get("artifact")
        # Rebuild Pareto frontier
        self._rebuild_pareto()
        # Notify optimizer
        if policy.name in name_to_idx:
            self.optimizers[name_to_idx[policy.name]].observe(policy, metrics)
        return trial

    def adopt_policy(self, trial_id: int) -> bool:
        """
        Adopt a policy as the active policy.
        Args:
            trial_id: ID of the trial to adopt
        Returns:
            True if policy was adopted, False otherwise
        """
        trial = next((t for t in self.trials if t.id == trial_id), None)
        if not trial:
            return False
        # Apply guardrails
        if trial.metrics.get("tool_error_rate", 0.0) > self.config.evaluation.max_tool_error_rate:
            return False
        if trial.metrics.get("task_success", 1.0) < self.config.evaluation.min_task_success_rate:
            return False
        if trial.metrics.get("latency_p95", 0.0) > self.config.evaluation.max_latency_p95:
            return False
        # Create adopted policy
        self.active_policy = Policy(
            name=f"{trial.policy_name}@adopted",
            params={
                "adopted_from_trial": trial.id,
                "artifact": trial.artifact_id,
                "original_policy": trial.policy_name,
            },
            actions=[
                f"apply.diff(trial_id={trial.id})",
                "enable.cache(optimized)",
                "limit.tools(safe)",
                "monitor.metrics(enabled)",
            ],
            metadata={
                "adopted_at": datetime.now().isoformat(),
                "trial_metrics": trial.metrics,
                "trial_score": trial.score,
            },
        )
        # Save the adopted policy
        self.storage.save_policy(self.active_policy)
        self.storage.save_policy(self.active_policy)
        return True

    def list_prompts(self) -> list[Prompt]:
        """List all prompts."""
        return self.storage.get_prompts()

    def save_prompt(self, id: str, content: str, description: str = "", tags: list[str] | None = None) -> Prompt:
        """Save a prompt."""
        # Check if exists to preserve created_at
        existing = next((p for p in self.list_prompts() if p.id == id), None)
        created_at = existing.created_at if existing else datetime.now()
        
        prompt = Prompt(
            id=id,
            content=content,
            description=description,
            tags=tags or [],
            created_at=created_at,
            updated_at=datetime.now(),
        )
        self.storage.save_prompt(prompt)
        return prompt

    def delete_prompt(self, prompt_id: str) -> None:
        """Delete a prompt."""
        self.storage.delete_prompt(prompt_id)

    def get_stats(self) -> dict[str, Any]:
        """Get backend statistics."""
        return {
            "trial_count": len(self.trials),
            "pareto_count": len(self.pareto),
            "optimizer_count": len(self.optimizers),
            "workload_count": len(self.workloads),
            "active_policy": self.active_policy is not None,
            "storage_type": self.config.storage.backend,
            "evaluator": self.evaluator_slug,
            "best_score": min((t.score for t in self.trials), default=None),
            "recent_trials": len(
                [t for t in self.trials if (datetime.now() - t.created_at).days < 7]
            ),
        }

    def reset(self) -> None:
        """Reset backend to initial state."""
        self.trials.clear()
        self.pareto.clear()
        self.active_policy = None
        self._trial_id_counter = 0
        # Reset optimizers
        for optimizer in self.optimizers:
            if hasattr(optimizer, "reset"):
                optimizer.reset()
        # Reset metadata
        self.optimizer_meta = [{"best_score": None, "artifact_id": None} for _ in self.optimizers]
        # Clear storage
        if hasattr(self.storage, "trials"):
            self.storage.trials.clear()
        if hasattr(self.storage, "policies"):
            self.storage.policies.clear()

    def close(self) -> None:
        """Close the backend and cleanup resources."""
        if hasattr(self.storage, "close"):
            self.storage.close()


# Global backend instance
_backend_instance: CIEBackend | None = None


def get_backend(config: CIEConfig | None = None) -> CIEBackend:
    """Get global backend instance."""
    global _backend_instance
    if _backend_instance is None:
        _backend_instance = CIEBackend(config)
    return _backend_instance


def set_backend(backend: CIEBackend) -> None:
    """Set global backend instance."""
    global _backend_instance
    _backend_instance = backend

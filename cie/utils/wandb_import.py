"""
Utilities for ingesting W&B run artifacts (beta leet style) into the CIE backend.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

MetricRow = dict[str, Any]

_HISTORY_NAME = "wandb-history.jsonl"
_SUMMARY_NAME = "wandb-summary.json"
_DEFAULT_SEARCH = (
    Path.cwd() / "wandb" / "latest-run",
    Path.cwd() / "wandb" / "run-latest",
)
_METRIC_ALIASES: dict[str, tuple[str, ...]] = {
    "task_success": (
        "task_success",
        "success",
        "eval/success_rate",
        "metrics/success_rate",
        "accuracy",
        "eval/accuracy",
    ),
    "latency_p95": (
        "latency_p95",
        "latency",
        "eval/latency_ms",
        "metrics/latency_p95",
    ),
    "cost_per_req": (
        "cost_per_req",
        "cost",
        "eval/cost_per_req",
        "metrics/cost",
    ),
    "context_usage": (
        "context_usage",
        "context_tokens",
        "metrics/context_tokens",
    ),
    "tool_error_rate": ("tool_error_rate", "errors", "eval/error_rate"),
    "throughput": ("throughput", "eval/throughput"),
}


def resolve_wandb_run_path(path: str | Path | None = None) -> Path:
    """
    Resolve the W&B run directory to ingest.

    The search order:
    1. Explicit `path` argument
    2. `CIE_WANDB_RUN` environment variable
    3. `wandb/latest-run` in the current working directory
    """

    candidates: list[Path] = []
    if path:
        candidates.append(Path(path))
    env_path = os.environ.get("CIE_WANDB_RUN")
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(_DEFAULT_SEARCH)

    for candidate in candidates:
        candidate = candidate.expanduser()
        if not candidate.exists():
            continue
        candidate = candidate.resolve()
        if candidate.is_file():
            candidate = candidate.parent
        if candidate.name == "files":
            candidate = candidate.parent
        files_dir = candidate / "files"
        if files_dir.is_dir() and (files_dir / _HISTORY_NAME).exists():
            return candidate

    raise FileNotFoundError(
        "Could not locate a W&B run directory. Set CIE_WANDB_RUN or pass an explicit path."
    )


def _load_summary(run_dir: Path) -> dict[str, Any]:
    summary_path = run_dir / "files" / _SUMMARY_NAME
    if summary_path.exists():
        try:
            return json.loads(summary_path.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def _parse_json_line(line: str) -> dict[str, Any]:
    return json.loads(line, parse_constant=lambda _: 0.0)


def _extract_metric(record: dict[str, Any], aliases: tuple[str, ...]) -> float | None:
    for name in aliases:
        if name in record and record[name] is not None:
            try:
                return float(record[name])
            except (TypeError, ValueError):
                continue
    return None


def _extract_metrics(record: dict[str, Any]) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for canonical, aliases in _METRIC_ALIASES.items():
        value = _extract_metric(record, aliases)
        if value is not None:
            metrics[canonical] = value
    # Many W&B runs log `loss` or `score` generically; treat as cost per request fallback.
    if "cost_per_req" not in metrics:
        for fallback in ("loss", "eval/loss", "score"):
            if fallback in record and record[fallback] is not None:
                try:
                    metrics["cost_per_req"] = float(record[fallback])
                    break
                except (TypeError, ValueError):
                    continue
    return metrics


def load_wandb_rows(run_dir: Path) -> list[MetricRow]:
    """Load metric rows from a W&B run directory."""
    files_dir = run_dir / "files"
    history_path = files_dir / _HISTORY_NAME
    if not history_path.exists():
        raise FileNotFoundError(f"No {_HISTORY_NAME} found in {files_dir}")

    summary = _load_summary(run_dir)
    rows: list[MetricRow] = []
    with history_path.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            line = line.strip()
            if not line:
                continue
            try:
                record = _parse_json_line(line)
            except json.JSONDecodeError:
                continue
            metrics = _extract_metrics(record)
            if not metrics:
                continue
            timestamp = record.get("_timestamp") or record.get("timestamp")
            if isinstance(timestamp, (int, float)):
                created_at = datetime.fromtimestamp(timestamp)
            else:
                created_at = datetime.now()
            step = int(record.get("_step", index))
            workload = (
                record.get("workload")
                or summary.get("workload")
                or f"WANDB:{run_dir.name}"
            )
            policy_name = (
                record.get("policy_name")
                or summary.get("policy_name")
                or f"wandb-policy-{step}"
            )
            artifact_id = (
                record.get("artifact_id")
                or summary.get("artifact_id")
                or summary.get("best_model_path")
            )
            wandb_row_id = f"{run_dir.name}:{step}"
            rows.append(
                {
                    "policy_name": str(policy_name),
                    "workload": str(workload),
                    "metrics": metrics,
                    "artifact_id": artifact_id,
                    "created_at": created_at,
                    "metadata": {
                        "source": "wandb",
                        "wandb_run": run_dir.name,
                        "wandb_step": step,
                        "wandb_row_id": wandb_row_id,
                        "wandb_path": str(run_dir),
                    },
                }
            )
    return rows

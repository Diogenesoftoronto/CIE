"""Evaluation systems for CIE."""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from cie.core.models import Evaluator

EvaluatorFactory = Callable[..., Evaluator]


@dataclass
class EvaluatorRegistration:
    """Metadata for registered evaluators."""

    name: str
    factory: EvaluatorFactory
    description: str = ""
    tags: tuple[str, ...] = tuple()


_EVALUATORS: dict[str, EvaluatorRegistration] = {}


def register_evaluator(
    slug: str,
    factory: EvaluatorFactory,
    *,
    description: str = "",
    tags: Iterable[str] | None = None,
) -> None:
    """Register an evaluator factory."""
    normalized = slug.lower()
    _EVALUATORS[normalized] = EvaluatorRegistration(
        name=normalized,
        factory=factory,
        description=description,
        tags=tuple(tags or ()),
    )


def list_evaluators() -> list[EvaluatorRegistration]:
    """List registered evaluators (sorted by slug)."""
    return [_EVALUATORS[key] for key in sorted(_EVALUATORS)]


def get_evaluator(slug: str, **kwargs: Any) -> Evaluator:
    """Instantiate an evaluator by slug."""
    normalized = slug.lower()
    if normalized not in _EVALUATORS:
        raise ValueError(f"Unknown evaluator '{slug}'. Available: {', '.join(sorted(_EVALUATORS))}")
    entry = _EVALUATORS[normalized]
    return entry.factory(**kwargs)


def _load_plugin_evaluators() -> None:
    """Import evaluator plugins located in cie/evaluators/plugins."""
    plugins_dir = Path(__file__).with_suffix("").parent / "plugins"
    if not plugins_dir.exists():
        return
    for module in pkgutil.iter_modules([str(plugins_dir)]):
        importlib.import_module(f"{__name__}.plugins.{module.name}")


# Register built-in evaluators.
from cie.evaluators.mock_evaluator import MockEvaluator  # noqa: E402

register_evaluator(
    "mock",
    lambda **kwargs: MockEvaluator(**kwargs),
    description="Synthetic evaluator that simulates workloads for rapid testing.",
    tags=("synthetic", "default"),
)

try:
    from cie.evaluators.text_match import TextMatchEvaluator  # noqa: E402

    register_evaluator(
        "text-match",
        lambda **kwargs: TextMatchEvaluator(**kwargs),
        description="Real text matching evaluator with Levenshtein/Jaccard metrics.",
        tags=("nlp", "reference"),
    )
except Exception:  # pragma: no cover - optional dependency
    pass

try:
    from cie.evaluators.context_evaluator import ContextEvaluator  # noqa: E402

    register_evaluator(
        "context",
        lambda **kwargs: ContextEvaluator(**kwargs),
        description="Context management efficiency evaluator with introspection capabilities.",
        tags=("context", "introspection", "optimization"),
    )
except Exception:  # pragma: no cover - optional dependency
    pass

_load_plugin_evaluators()

__all__ = [
    "EvaluatorFactory",
    "EvaluatorRegistration",
    "get_evaluator",
    "list_evaluators",
    "register_evaluator",
]

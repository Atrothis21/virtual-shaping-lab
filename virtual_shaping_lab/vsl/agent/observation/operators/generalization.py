"""Executable generalization operators (`G`) for observation core."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Mapping

from .base import GeneralizationOperator
from .context import ContextArtifact


@dataclass(frozen=True)
class GeneralizationArtifact:
    """Typed generalization artifact for finalized observation features."""

    representation_state: Any
    context_state: Any
    generalized_state: Any
    features: list[float] = field(default_factory=list)
    feature_names: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.features, list):
            raise ValueError("GeneralizationArtifact.features must be a list.")
        if not all(isinstance(value, (int, float)) for value in self.features):
            raise ValueError("GeneralizationArtifact.features must contain numeric values.")
        if not isinstance(self.feature_names, list):
            raise ValueError("GeneralizationArtifact.feature_names must be a list.")
        if not all(isinstance(value, str) for value in self.feature_names):
            raise ValueError("GeneralizationArtifact.feature_names must contain strings.")
        if len(self.feature_names) not in {0, len(self.features)}:
            raise ValueError("GeneralizationArtifact.feature_names must be empty or match features length.")
        if not isinstance(self.metadata, dict):
            raise ValueError("GeneralizationArtifact.metadata must be an object.")
        object.__setattr__(self, "features", [float(value) for value in self.features])
        object.__setattr__(self, "feature_names", [str(value) for value in self.feature_names])
        object.__setattr__(self, "metadata", dict(self.metadata))


def _coerce_contextual(contextual_state: Any) -> ContextArtifact:
    if isinstance(contextual_state, ContextArtifact):
        return contextual_state
    if isinstance(contextual_state, Mapping):
        return ContextArtifact(
            representation_state=contextual_state.get("representation_state"),
            context_state=contextual_state.get("context_state"),
            features=list(contextual_state.get("features", [])),
            feature_names=list(contextual_state.get("feature_names", [])),
            metadata=dict(contextual_state.get("metadata", {})),
        )
    raise ValueError("contextual_state must be ContextArtifact or mapping payload.")


@dataclass(frozen=True)
class IdentityGeneralizationOperator(GeneralizationOperator):
    """Identity generalization over contextualized features."""

    variant: str = "identity_generalization"

    def generalize(
        self,
        *,
        contextual_state: Any,
        metadata: Mapping[str, Any] | None = None,
    ) -> GeneralizationArtifact:
        ctx = _coerce_contextual(contextual_state)
        return GeneralizationArtifact(
            representation_state=ctx.representation_state,
            context_state=ctx.context_state,
            generalized_state={"kind": "identity"},
            features=list(ctx.features),
            feature_names=list(ctx.feature_names),
            metadata={**dict(ctx.metadata), **dict(metadata or {}), "variant": self.variant},
        )


@dataclass(frozen=True)
class SimilarityKernelGeneralizationOperator(GeneralizationOperator):
    """Append a global similarity signal based on radial-basis response."""

    sigma: float = 1.0
    feature_name: str = "gen:similarity_kernel"
    variant: str = "similarity_kernel"

    def __post_init__(self) -> None:
        if float(self.sigma) <= 0.0:
            raise ValueError("SimilarityKernelGeneralizationOperator.sigma must be > 0.")
        if not isinstance(self.feature_name, str) or not self.feature_name:
            raise ValueError("SimilarityKernelGeneralizationOperator.feature_name must be a non-empty string.")

    def generalize(
        self,
        *,
        contextual_state: Any,
        metadata: Mapping[str, Any] | None = None,
    ) -> GeneralizationArtifact:
        ctx = _coerce_contextual(contextual_state)
        norm_sq = sum(float(value) * float(value) for value in ctx.features)
        similarity = float(math.exp(-(norm_sq / (2.0 * float(self.sigma) * float(self.sigma)))))
        return GeneralizationArtifact(
            representation_state=ctx.representation_state,
            context_state=ctx.context_state,
            generalized_state={"kind": "rbf_similarity", "sigma": float(self.sigma)},
            features=list(ctx.features) + [similarity],
            feature_names=list(ctx.feature_names) + [self.feature_name],
            metadata={**dict(ctx.metadata), **dict(metadata or {}), "variant": self.variant},
        )

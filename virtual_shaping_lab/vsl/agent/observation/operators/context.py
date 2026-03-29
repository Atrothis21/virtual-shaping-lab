"""Executable context operators (`C`) for observation core."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .base import ContextOperator, NullContextOperator
from .representation import RepresentationArtifact


@dataclass(frozen=True)
class ContextArtifact:
    """Typed context artifact normalized for downstream generalization."""

    representation_state: Any
    context_state: Any
    features: list[float] = field(default_factory=list)
    feature_names: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.features, list):
            raise ValueError("ContextArtifact.features must be a list.")
        if not all(isinstance(value, (int, float)) for value in self.features):
            raise ValueError("ContextArtifact.features must contain numeric values.")
        if not isinstance(self.feature_names, list):
            raise ValueError("ContextArtifact.feature_names must be a list.")
        if not all(isinstance(value, str) for value in self.feature_names):
            raise ValueError("ContextArtifact.feature_names must contain strings.")
        if len(self.feature_names) not in {0, len(self.features)}:
            raise ValueError("ContextArtifact.feature_names must be empty or match features length.")
        if not isinstance(self.metadata, dict):
            raise ValueError("ContextArtifact.metadata must be an object.")
        object.__setattr__(self, "features", [float(value) for value in self.features])
        object.__setattr__(self, "feature_names", [str(value) for value in self.feature_names])
        object.__setattr__(self, "metadata", dict(self.metadata))


def _coerce_representation(representation: Any) -> RepresentationArtifact:
    if isinstance(representation, RepresentationArtifact):
        return representation
    if isinstance(representation, Mapping):
        features = list(representation.get("features", []))
        feature_names = list(representation.get("feature_names", []))
        return RepresentationArtifact(
            representation_state=representation.get("representation_state", representation),
            features=features,
            feature_names=feature_names,
            metadata=dict(representation.get("metadata", {})),
        )
    raise ValueError("representation must be RepresentationArtifact or mapping payload.")


@dataclass(frozen=True)
class StaticContextTagOperator(ContextOperator):
    """Append context one-hot tag features to representation features."""

    context_tags: list[str]
    prefix: str = "ctx:"
    variant: str = "static_context_tag"

    def __post_init__(self) -> None:
        if not isinstance(self.context_tags, list) or not self.context_tags:
            raise ValueError("StaticContextTagOperator.context_tags must be a non-empty list.")
        if not all(isinstance(tag, str) and tag.strip() for tag in self.context_tags):
            raise ValueError("StaticContextTagOperator.context_tags must contain non-empty strings.")
        if not isinstance(self.prefix, str):
            raise ValueError("StaticContextTagOperator.prefix must be a string.")

    def contextualize(
        self,
        *,
        representation: Any,
        context_state: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ContextArtifact:
        rep = _coerce_representation(representation)
        active = str(context_state) if isinstance(context_state, str) and context_state else None

        tag_names = [f"{self.prefix}{tag}" for tag in self.context_tags]
        tag_values = [1.0 if active == tag else 0.0 for tag in self.context_tags]

        return ContextArtifact(
            representation_state=rep.representation_state,
            context_state=context_state,
            features=list(rep.features) + tag_values,
            feature_names=list(rep.feature_names) + tag_names,
            metadata={**dict(rep.metadata), **dict(metadata or {}), "variant": self.variant},
        )


def null_contextualize(
    *,
    representation: Any,
    context_state: Any = None,
    metadata: Mapping[str, Any] | None = None,
) -> ContextArtifact:
    """Adapter helper to produce ContextArtifact via NullContextOperator semantics."""
    rep = _coerce_representation(representation)
    op = NullContextOperator()
    passthrough = op.contextualize(representation=rep, context_state=context_state, metadata=metadata)
    rep_out = _coerce_representation(passthrough)
    return ContextArtifact(
        representation_state=rep_out.representation_state,
        context_state=context_state,
        features=list(rep_out.features),
        feature_names=list(rep_out.feature_names),
        metadata={**dict(rep_out.metadata), **dict(metadata or {}), "variant": op.variant},
    )

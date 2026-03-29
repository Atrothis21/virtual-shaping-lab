"""Executable observation bundle orchestration (V3.19.5 slice 4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .operators import (
    ContextArtifact,
    ContextOperator,
    GeneralizationArtifact,
    GeneralizationOperator,
    NullContextOperator,
    NullGeneralizationOperator,
    RepresentationArtifact,
    RepresentationOperator,
)
from .output import ObservationOutput


@dataclass(frozen=True)
class ObservationStepResult:
    """Per-step observation outputs with intermediate stage artifacts."""

    output: ObservationOutput
    representation_artifact: RepresentationArtifact
    context_artifact: ContextArtifact
    generalization_artifact: GeneralizationArtifact
    measurements: dict[str, Any] = field(default_factory=dict)


def _coerce_representation_artifact(value: Any) -> RepresentationArtifact:
    if isinstance(value, RepresentationArtifact):
        return value
    if isinstance(value, Mapping):
        return RepresentationArtifact(
            representation_state=value.get("representation_state", value),
            features=list(value.get("features", [])),
            feature_names=list(value.get("feature_names", [])),
            metadata=dict(value.get("metadata", {})),
        )
    raise ValueError("Representation operator must return RepresentationArtifact or mapping payload.")


def _coerce_context_artifact(value: Any, *, context_state: Any) -> ContextArtifact:
    if isinstance(value, ContextArtifact):
        return value
    rep = _coerce_representation_artifact(value)
    return ContextArtifact(
        representation_state=rep.representation_state,
        context_state=context_state,
        features=list(rep.features),
        feature_names=list(rep.feature_names),
        metadata=dict(rep.metadata),
    )


def _coerce_generalization_artifact(value: Any, *, context_artifact: ContextArtifact) -> GeneralizationArtifact:
    if isinstance(value, GeneralizationArtifact):
        return value
    if isinstance(value, Mapping):
        return GeneralizationArtifact(
            representation_state=value.get("representation_state", context_artifact.representation_state),
            context_state=value.get("context_state", context_artifact.context_state),
            generalized_state=value.get("generalized_state", {"kind": "passthrough"}),
            features=list(value.get("features", [])),
            feature_names=list(value.get("feature_names", [])),
            metadata=dict(value.get("metadata", {})),
        )
    ctx = _coerce_context_artifact(value, context_state=context_artifact.context_state)
    return GeneralizationArtifact(
        representation_state=ctx.representation_state,
        context_state=ctx.context_state,
        generalized_state={"kind": "passthrough"},
        features=list(ctx.features),
        feature_names=list(ctx.feature_names),
        metadata=dict(ctx.metadata),
    )


@dataclass
class ObservationBundle:
    """
    Canonical executable observation order:
    1) represent
    2) contextualize
    3) generalize
    4) finalize typed ObservationOutput
    """

    representation_operator: RepresentationOperator
    context_operator: ContextOperator = field(default_factory=NullContextOperator)
    generalization_operator: GeneralizationOperator = field(default_factory=NullGeneralizationOperator)

    def step(
        self,
        *,
        raw_stimulus: Any,
        context_state: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ObservationStepResult:
        incoming_metadata = dict(metadata or {})

        rep_raw = self.representation_operator.represent(
            raw_stimulus=raw_stimulus,
            metadata=incoming_metadata,
        )
        rep = _coerce_representation_artifact(rep_raw)
        rep_payload = {
            "representation_state": rep.representation_state,
            "features": list(rep.features),
            "feature_names": list(rep.feature_names),
            "metadata": dict(rep.metadata),
        }

        ctx_raw = self.context_operator.contextualize(
            representation=rep_payload,
            context_state=context_state,
            metadata=incoming_metadata,
        )
        ctx = _coerce_context_artifact(ctx_raw, context_state=context_state)
        ctx_payload = {
            "representation_state": ctx.representation_state,
            "context_state": ctx.context_state,
            "features": list(ctx.features),
            "feature_names": list(ctx.feature_names),
            "metadata": dict(ctx.metadata),
        }

        gen_raw = self.generalization_operator.generalize(
            contextual_state=ctx_payload,
            metadata=incoming_metadata,
        )
        gen = _coerce_generalization_artifact(gen_raw, context_artifact=ctx)

        stage_traces = {
            "representation": {
                "feature_names": list(rep.feature_names),
                "features": list(rep.features),
                "metadata": dict(rep.metadata),
            },
            "context": {
                "feature_names": list(ctx.feature_names),
                "features": list(ctx.features),
                "metadata": dict(ctx.metadata),
            },
            "generalization": {
                "feature_names": list(gen.feature_names),
                "features": list(gen.features),
                "metadata": dict(gen.metadata),
                "generalized_state": gen.generalized_state,
            },
        }

        output = ObservationOutput(
            raw_stimulus=raw_stimulus,
            representation=rep.representation_state,
            context_state=ctx.context_state,
            generalized_state=gen.generalized_state,
            features=list(gen.features),
            feature_names=list(gen.feature_names),
            metadata={
                **incoming_metadata,
                "stage_traces": stage_traces,
                "pipeline_order": ["represent", "contextualize", "generalize", "finalize"],
            },
        )

        measurements = {
            "n_features": len(output.features),
            "feature_names": list(output.feature_names),
            "pipeline_order": list(output.metadata["pipeline_order"]),
        }

        return ObservationStepResult(
            output=output,
            representation_artifact=rep,
            context_artifact=ctx,
            generalization_artifact=gen,
            measurements=measurements,
        )

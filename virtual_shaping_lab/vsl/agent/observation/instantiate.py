"""Observation instantiation boundary from grammar tuples to typed contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Any, Mapping

from .output import ObservationOutput
from .spec import ObservationSpec
from .validation import ObservationSpecValidationError


OBSERVATION_INSTANTIATION_FAILURES: dict[str, str] = {
    "INST_E_INVALID_SPEC_INPUT": "Observation spec input must be ObservationSpec or object payload.",
    "INST_E_LEGALITY": "Observation spec failed legality validation before materialization.",
    "INST_E_BOUNDARY_RESOLUTION": "Observation boundary resolution failed for legacy/runtime inputs.",
}


@dataclass
class ObservationInstantiationError(ValueError):
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


@dataclass(frozen=True)
class ObservationOperatorHandle:
    axis: str
    variant: str
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.axis, str) or not self.axis.strip():
            raise ValueError("ObservationOperatorHandle.axis must be a non-empty string.")
        if not isinstance(self.variant, str) or not self.variant.strip():
            raise ValueError("ObservationOperatorHandle.variant must be a non-empty string.")
        if not isinstance(self.params, dict):
            raise ValueError("ObservationOperatorHandle.params must be an object.")


@dataclass(frozen=True)
class ObservationInstantiationArtifact:
    observation_spec: ObservationSpec
    representation_operator: ObservationOperatorHandle
    context_operator: ObservationOperatorHandle
    generalization_operator: ObservationOperatorHandle
    output_template: ObservationOutput


def _coerce_observation_spec(spec: ObservationSpec | Mapping[str, Any]) -> ObservationSpec:
    if isinstance(spec, ObservationSpec):
        return spec
    if isinstance(spec, Mapping):
        try:
            return ObservationSpec.from_dict(dict(spec))
        except (ObservationSpecValidationError, ValueError, TypeError) as exc:
            raise ObservationInstantiationError(
                "INST_E_LEGALITY",
                OBSERVATION_INSTANTIATION_FAILURES["INST_E_LEGALITY"],
                details={"reason": str(exc)},
            ) from exc
    raise ObservationInstantiationError(
        "INST_E_INVALID_SPEC_INPUT",
        OBSERVATION_INSTANTIATION_FAILURES["INST_E_INVALID_SPEC_INPUT"],
    )


def instantiate_observation_contracts(
    spec: ObservationSpec | Mapping[str, Any],
    *,
    raw_stimulus: Any = None,
    representation: Any = None,
    context_state: Any = None,
    generalized_state: Any = None,
    features: list[float] | None = None,
    feature_names: list[str] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> ObservationInstantiationArtifact:
    """
    Materialize typed observation boundary contracts from canonical grammar spec.
    """
    observation_spec = _coerce_observation_spec(spec)
    output = ObservationOutput(
        raw_stimulus=raw_stimulus,
        representation=representation,
        context_state=context_state,
        generalized_state=generalized_state,
        features=list(features or []),
        feature_names=list(feature_names or []),
        metadata=dict(metadata or {}),
    )
    return ObservationInstantiationArtifact(
        observation_spec=observation_spec,
        representation_operator=ObservationOperatorHandle(axis="Phi", variant=observation_spec.representation),
        context_operator=ObservationOperatorHandle(axis="C", variant=observation_spec.context),
        generalization_operator=ObservationOperatorHandle(axis="G", variant=observation_spec.generalization),
        output_template=output,
    )


def _resolve_slot_value(value: Any, *, slot_name: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, Mapping):
        candidate = value.get("name")
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    raise ValueError(f"Could not resolve {slot_name} from boundary input.")


def instantiate_observation_from_boundary(
    *,
    representation: Any,
    context: Any,
    generalization: Any,
    metadata: Mapping[str, Any] | None = None,
    output_payload: Mapping[str, Any] | None = None,
) -> ObservationInstantiationArtifact:
    """
    Resolve observation boundary inputs and materialize typed observation contracts.
    """
    try:
        spec = ObservationSpec(
            representation=_resolve_slot_value(representation, slot_name="representation"),
            context=_resolve_slot_value(context, slot_name="context"),
            generalization=_resolve_slot_value(generalization, slot_name="generalization"),
            metadata=dict(metadata or {}),
        )
    except Exception as exc:
        raise ObservationInstantiationError(
            "INST_E_BOUNDARY_RESOLUTION",
            OBSERVATION_INSTANTIATION_FAILURES["INST_E_BOUNDARY_RESOLUTION"],
            details={"reason": str(exc)},
        ) from exc

    if output_payload is None:
        output = ObservationOutput(
            raw_stimulus=None,
            representation=None,
            context_state=None,
            generalized_state=None,
            features=[],
            feature_names=[],
            metadata={},
        )
    else:
        output = ObservationOutput.from_dict(dict(output_payload))
    return instantiate_observation_contracts(
        spec,
        raw_stimulus=output.raw_stimulus,
        representation=output.representation,
        context_state=output.context_state,
        generalized_state=output.generalized_state,
        features=output.features,
        feature_names=output.feature_names,
        metadata=output.metadata,
    )


def materialize_legal_observation_universe() -> list[ObservationInstantiationArtifact]:
    """Materialize every legal tuple from the observation slot registry universe."""
    from .registry import slot_registries

    regs = slot_registries()
    artifacts: list[ObservationInstantiationArtifact] = []
    for rep, ctx, gen in product(regs["representation"], regs["context"], regs["generalization"]):
        try:
            artifacts.append(
                instantiate_observation_contracts(
                    ObservationSpec(
                        representation=rep,
                        context=ctx,
                        generalization=gen,
                        metadata={"source": "registry_universe"},
                    )
                )
            )
        except ObservationSpecValidationError:
            continue
    return artifacts

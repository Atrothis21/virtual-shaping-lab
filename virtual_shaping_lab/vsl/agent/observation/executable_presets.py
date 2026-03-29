"""Executable observation presets for V3.19.5 observation bundle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .bundle import ObservationBundle
from .operators import (
    ElementalRepresentationOperator,
    IdentityGeneralizationOperator,
    IdentityRepresentationOperator,
    MinimalConfiguralRepresentationOperator,
    NullContextOperator,
    SimilarityKernelGeneralizationOperator,
    StaticContextTagOperator,
)
from .spec import ObservationSpec


@dataclass(frozen=True)
class ExecutableObservationPreset:
    """Resolved executable observation preset payload."""

    preset_name: str
    observation_spec: ObservationSpec
    bundle: ObservationBundle


def executable_observation_preset_names() -> list[str]:
    return [
        "identity_observation",
        "elemental_identity",
        "elemental_context_tag",
        "configural_identity",
        "elemental_kernel_generalization",
    ]


def _coerce_observation_spec(spec: ObservationSpec | Mapping[str, Any]) -> ObservationSpec:
    if isinstance(spec, ObservationSpec):
        return spec
    if isinstance(spec, Mapping):
        return ObservationSpec.from_dict(dict(spec))
    raise TypeError("spec must be ObservationSpec or object payload.")


def build_executable_observation_preset(
    preset_name: str,
    *,
    stimulus_universe: Sequence[str] = ("tone", "noise", "light"),
    context_tags: Sequence[str] = ("A", "B"),
    kernel_sigma: float = 1.0,
    conjunction_prefix: str = "cfg:",
) -> ExecutableObservationPreset:
    """
    Materialize executable observation preset bundles.

    Supported presets in V3.19.5:
    - identity_observation
    - elemental_identity
    - elemental_context_tag
    - configural_identity
    - elemental_kernel_generalization
    """
    requested = str(preset_name).strip()
    if requested == "identity_observation":
        spec = ObservationSpec(
            representation="identity",
            context="none",
            generalization="none",
            metadata={"preset_name": requested, "preset_version": "3.19.5"},
        )
        bundle = ObservationBundle(
            representation_operator=IdentityRepresentationOperator(),
            context_operator=NullContextOperator(),
            generalization_operator=IdentityGeneralizationOperator(),
        )
        return ExecutableObservationPreset(requested, spec, bundle)

    if requested == "elemental_identity":
        spec = ObservationSpec(
            representation="stimulus_vector",
            context="none",
            generalization="none",
            metadata={"preset_name": requested, "preset_version": "3.19.5"},
        )
        bundle = ObservationBundle(
            representation_operator=ElementalRepresentationOperator(stimulus_universe=list(stimulus_universe)),
            context_operator=NullContextOperator(),
            generalization_operator=IdentityGeneralizationOperator(),
        )
        return ExecutableObservationPreset(requested, spec, bundle)

    if requested == "elemental_context_tag":
        spec = ObservationSpec(
            representation="stimulus_vector",
            context="discrete_context",
            generalization="none",
            metadata={"preset_name": requested, "preset_version": "3.19.5"},
        )
        bundle = ObservationBundle(
            representation_operator=ElementalRepresentationOperator(stimulus_universe=list(stimulus_universe)),
            context_operator=StaticContextTagOperator(context_tags=list(context_tags)),
            generalization_operator=IdentityGeneralizationOperator(),
        )
        return ExecutableObservationPreset(requested, spec, bundle)

    if requested == "configural_identity":
        spec = ObservationSpec(
            representation="temporal_basis",
            context="none",
            generalization="none",
            metadata={"preset_name": requested, "preset_version": "3.19.5"},
        )
        bundle = ObservationBundle(
            representation_operator=MinimalConfiguralRepresentationOperator(
                stimulus_universe=list(stimulus_universe),
                conjunction_prefix=conjunction_prefix,
            ),
            context_operator=NullContextOperator(),
            generalization_operator=IdentityGeneralizationOperator(),
        )
        return ExecutableObservationPreset(requested, spec, bundle)

    if requested == "elemental_kernel_generalization":
        spec = ObservationSpec(
            representation="stimulus_vector",
            context="none",
            generalization="stimulus_similarity",
            metadata={"preset_name": requested, "preset_version": "3.19.5"},
        )
        bundle = ObservationBundle(
            representation_operator=ElementalRepresentationOperator(stimulus_universe=list(stimulus_universe)),
            context_operator=NullContextOperator(),
            generalization_operator=SimilarityKernelGeneralizationOperator(sigma=float(kernel_sigma)),
        )
        return ExecutableObservationPreset(requested, spec, bundle)

    known = ", ".join(executable_observation_preset_names())
    raise ValueError(f"Unknown executable observation preset '{preset_name}'. Known presets: {known}")


def build_executable_observation_from_spec(
    spec: ObservationSpec | Mapping[str, Any],
    *,
    stimulus_universe: Sequence[str] = ("tone", "noise", "light"),
    context_tags: Sequence[str] = ("A", "B"),
    kernel_sigma: float = 1.0,
    conjunction_prefix: str = "cfg:",
) -> ExecutableObservationPreset:
    """
    Materialize executable observation bundle directly from legal symbolic spec.
    """
    obs_spec = _coerce_observation_spec(spec)
    signature = (obs_spec.representation, obs_spec.context, obs_spec.generalization)
    if signature == ("identity", "none", "none"):
        return build_executable_observation_preset("identity_observation")
    if signature == ("stimulus_vector", "none", "none"):
        return build_executable_observation_preset(
            "elemental_identity",
            stimulus_universe=stimulus_universe,
        )
    if signature == ("stimulus_vector", "discrete_context", "none"):
        return build_executable_observation_preset(
            "elemental_context_tag",
            stimulus_universe=stimulus_universe,
            context_tags=context_tags,
        )
    if signature == ("temporal_basis", "none", "none"):
        return build_executable_observation_preset(
            "configural_identity",
            stimulus_universe=stimulus_universe,
            conjunction_prefix=conjunction_prefix,
        )
    if signature == ("stimulus_vector", "none", "stimulus_similarity"):
        return build_executable_observation_preset(
            "elemental_kernel_generalization",
            stimulus_universe=stimulus_universe,
            kernel_sigma=kernel_sigma,
        )
    raise ValueError(
        "[OBS_E_EXECUTABLE_UNSUPPORTED_SPEC] Symbolic observation spec is legal but does not map "
        "to a V3.19.5 executable core preset."
    )


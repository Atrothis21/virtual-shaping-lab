"""Typed phenomena registry for UI/teaching discovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from protocols.catalog import available_protocols
from virtual_shaping_lab.domain.naming import normalize_protocol_key


@dataclass(frozen=True)
class PhenomenonSpec:
    key: str
    name: str
    description: str
    protocol_key: str
    expected_signatures: tuple[str, ...] = ()
    default_template_key: str | None = None
    recommended_presets: tuple[dict[str, Any], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


PHENOMENA_REGISTRY: dict[str, PhenomenonSpec] = {
    "blocking": PhenomenonSpec(
        key="blocking",
        name="Blocking",
        description="Prior learning about cue A suppresses learning about cue X in AX+ compound training.",
        protocol_key="blocking",
        expected_signatures=("blocked_cue_lower_than_pretrained_cue",),
    ),
    "conditioned_inhibition": PhenomenonSpec(
        key="conditioned_inhibition",
        name="Conditioned Inhibition",
        description="Inhibitory cue training reduces responding in compound and probe tests.",
        protocol_key="conditioned_inhibition",
        expected_signatures=("compound_nonreinforcement_suppression", "summation_probe_below_excitatory_baseline"),
    ),
    "renewal_aba": PhenomenonSpec(
        key="renewal_aba",
        name="Renewal (ABA)",
        description="Recovery after extinction when returned to acquisition context.",
        protocol_key="aba_renewal",
        expected_signatures=("probe_above_extinction_tail",),
    ),
    "renewal_abc": PhenomenonSpec(
        key="renewal_abc",
        name="Renewal (ABC)",
        description="Recovery in a novel context after acquisition and extinction in distinct contexts.",
        protocol_key="abc_renewal",
        expected_signatures=("probe_above_extinction_tail",),
    ),
    "renewal_aab": PhenomenonSpec(
        key="renewal_aab",
        name="Renewal (AAB)",
        description="Acquisition/extinction in same context with probe in shifted context.",
        protocol_key="aab_renewal",
        expected_signatures=("probe_near_extinction_tail",),
    ),
    "extinction": PhenomenonSpec(
        key="extinction",
        name="Extinction",
        description="Learned responding declines under nonreinforcement.",
        protocol_key="extinction",
        expected_signatures=("late_extinction_prediction_below_early_extinction",),
    ),
    "rapid_reacquisition": PhenomenonSpec(
        key="rapid_reacquisition",
        name="Rapid Reacquisition",
        description="Responding returns quickly when reinforcement is reintroduced after extinction.",
        protocol_key="rapid_reacquisition",
        expected_signatures=("reacquisition_above_extinction_tail",),
    ),
    "occasion_setting": PhenomenonSpec(
        key="occasion_setting",
        name="Occasion Setting",
        description="Modulatory cue controls when target cue predicts reinforcement.",
        protocol_key="occasion_setting",
        expected_signatures=("probe_between_acquisition_and_nonreinforcement",),
    ),
    "operant_conditioning": PhenomenonSpec(
        key="operant_conditioning",
        name="Operant Conditioning",
        description="Response-contingent reinforcement increases action value and response tendency.",
        protocol_key="operant_conditioning",
        expected_signatures=("reward_and_prediction_increase",),
    ),
    "matching_law": PhenomenonSpec(
        key="matching_law",
        name="Matching Law",
        description="Response allocation tracks reinforcement ratio across concurrent options.",
        protocol_key="matching_law",
        expected_signatures=("choice_bias_under_unequal_schedules",),
    ),
    "shaping": PhenomenonSpec(
        key="shaping",
        name="Shaping",
        description="Progressive criterion changes alter reward density over training stages.",
        protocol_key="shaping",
        expected_signatures=("stage_reward_density_shift",),
    ),
    "resurgence": PhenomenonSpec(
        key="resurgence",
        name="Resurgence",
        description="Suppressed response returns when alternative reinforcement is removed.",
        protocol_key="resurgence",
        expected_signatures=("recovery_above_suppression",),
    ),
    "superextinction": PhenomenonSpec(
        key="superextinction",
        name="Superextinction",
        description="Punishment/nonreinforcement phase drives responding below baseline extinction levels.",
        protocol_key="superextinction",
        expected_signatures=("punishment_phase_negative_rewards",),
    ),
    "spontaneous_recovery": PhenomenonSpec(
        key="spontaneous_recovery",
        name="Spontaneous Recovery",
        description="Response partially recovers after delay following extinction.",
        protocol_key="spontaneous_recovery",
        expected_signatures=("probe_above_extinction_tail",),
    ),
}


def available_phenomena() -> list[str]:
    return sorted(PHENOMENA_REGISTRY.keys())


def validate_phenomenon_key(name: str) -> None:
    if name not in PHENOMENA_REGISTRY:
        available = ", ".join(available_phenomena())
        raise KeyError(f"Unknown phenomenon '{name}'. Available phenomena: {available}")


def get_phenomenon(name: str) -> PhenomenonSpec:
    validate_phenomenon_key(name)
    return PHENOMENA_REGISTRY[name]


def validate_phenomena_registry(registry: dict[str, PhenomenonSpec] | None = None) -> None:
    active = registry or PHENOMENA_REGISTRY
    supported_protocols = {normalize_protocol_key(k) for k in available_protocols()}

    for key, spec in active.items():
        if not isinstance(spec, PhenomenonSpec):
            raise ValueError(f"Phenomenon '{key}' must map to PhenomenonSpec.")
        if spec.key != key:
            raise ValueError(f"Phenomenon key mismatch: map key '{key}' != spec.key '{spec.key}'.")
        if not spec.name.strip():
            raise ValueError(f"Phenomenon '{key}' must have non-empty name.")
        if not spec.description.strip():
            raise ValueError(f"Phenomenon '{key}' must have non-empty description.")
        normalized_protocol = normalize_protocol_key(spec.protocol_key)
        if normalized_protocol not in supported_protocols:
            supported = ", ".join(sorted(supported_protocols))
            raise ValueError(
                f"Phenomenon '{key}' references unknown protocol '{spec.protocol_key}' "
                f"(normalized='{normalized_protocol}'). Supported protocols: {supported}"
            )
        if not isinstance(spec.expected_signatures, tuple) or not all(
            isinstance(s, str) and s.strip() for s in spec.expected_signatures
        ):
            raise ValueError(f"Phenomenon '{key}' expected_signatures must be tuple[str, ...].")
        if not isinstance(spec.recommended_presets, tuple) or not all(isinstance(v, dict) for v in spec.recommended_presets):
            raise ValueError(f"Phenomenon '{key}' recommended_presets must be tuple[dict[str, Any], ...].")


validate_phenomena_registry()

"""Executable protocol presets for V3.21.5 protocol core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .bundle import ProtocolBundle
from .operators import (
    ActionConditionedConsequenceOperator,
    ClassicalNoActionConsequenceOperator,
    CriterionStopOperator,
    FixedEmissionOperator,
    ScheduledEmissionOperator,
    TrialAdvanceOperator,
    TrialCountStopOperator,
)
from .spec import ProtocolSpec


@dataclass(frozen=True)
class ExecutableProtocolPreset:
    """Resolved executable protocol preset payload."""

    preset_name: str
    protocol_spec: ProtocolSpec
    bundle: ProtocolBundle


def executable_protocol_preset_names() -> list[str]:
    return [
        "acquisition_protocol",
        "extinction_nonreinforcement_protocol",
        "differential_protocol",
        "compound_protocol",
        "probe_protocol",
        "operant_protocol",
        "concurrent_protocol",
        "criterion_shift_protocol",
    ]


def _coerce_protocol_spec(spec: ProtocolSpec | Mapping[str, Any]) -> ProtocolSpec:
    if isinstance(spec, ProtocolSpec):
        return spec
    if isinstance(spec, Mapping):
        return ProtocolSpec.from_dict(dict(spec))
    raise TypeError("spec must be ProtocolSpec or object payload.")


def _trial_bundle(
    *,
    emission: Any,
    consequence: Any,
    max_trials: int,
    dt_s: float,
) -> ProtocolBundle:
    return ProtocolBundle(
        emission_operator=emission,
        consequence_operator=consequence,
        advance_operator=TrialAdvanceOperator(dt_s=float(dt_s)),
        stop_operator=TrialCountStopOperator(max_trials=int(max_trials)),
    )


def build_executable_protocol_preset(
    preset_name: str,
    *,
    max_trials: int = 5,
    dt_s: float = 1.0,
    criterion_reward_threshold: float = 3.0,
) -> ExecutableProtocolPreset:
    """Materialize executable protocol bundle presets."""
    requested = str(preset_name).strip()

    if requested == "acquisition_protocol":
        spec = ProtocolSpec(
            emission_rule="classical_trial_emission",
            consequence_rule="deterministic_consequence",
            advance_rule="trial_increment",
            stop_rule="n_trials",
            protocol_family="acquisition",
            action_space_mode="classical_none",
            temporal_mode="trial_discrete",
            metadata={"preset_name": requested, "preset_version": "3.21.5"},
        )
        bundle = _trial_bundle(
            emission=FixedEmissionOperator(stimulus={"tone": 1.0}, context="A"),
            consequence=ClassicalNoActionConsequenceOperator(reward=1.0),
            max_trials=max_trials,
            dt_s=dt_s,
        )
        return ExecutableProtocolPreset(requested, spec, bundle)

    if requested == "extinction_nonreinforcement_protocol":
        spec = ProtocolSpec(
            emission_rule="classical_trial_emission",
            consequence_rule="null_consequence",
            advance_rule="trial_increment",
            stop_rule="n_trials",
            protocol_family="extinction",
            action_space_mode="classical_none",
            temporal_mode="trial_discrete",
            metadata={"preset_name": requested, "preset_version": "3.21.5"},
        )
        bundle = _trial_bundle(
            emission=FixedEmissionOperator(stimulus={"tone": 1.0}, context="A"),
            consequence=ClassicalNoActionConsequenceOperator(reward=0.0),
            max_trials=max_trials,
            dt_s=dt_s,
        )
        return ExecutableProtocolPreset(requested, spec, bundle)

    if requested == "differential_protocol":
        spec = ProtocolSpec(
            emission_rule="scheduled_emission",
            consequence_rule="deterministic_consequence",
            advance_rule="trial_increment",
            stop_rule="n_trials",
            protocol_family="custom",
            action_space_mode="classical_none",
            temporal_mode="trial_discrete",
            metadata={"preset_name": requested, "preset_version": "3.21.5"},
        )
        bundle = _trial_bundle(
            emission=ScheduledEmissionOperator(
                schedule=(
                    {"stimulus": {"cs_plus": 1.0}, "context": "A"},
                    {"stimulus": {"cs_minus": 1.0}, "context": "A"},
                ),
                loop=True,
            ),
            consequence=ClassicalNoActionConsequenceOperator(reward_schedule=(1.0, 0.0)),
            max_trials=max_trials,
            dt_s=dt_s,
        )
        return ExecutableProtocolPreset(requested, spec, bundle)

    if requested == "compound_protocol":
        spec = ProtocolSpec(
            emission_rule="classical_trial_emission",
            consequence_rule="deterministic_consequence",
            advance_rule="trial_increment",
            stop_rule="n_trials",
            protocol_family="custom",
            action_space_mode="classical_none",
            temporal_mode="trial_discrete",
            metadata={"preset_name": requested, "preset_version": "3.21.5"},
        )
        bundle = _trial_bundle(
            emission=FixedEmissionOperator(stimulus={"tone": 1.0, "light": 1.0}, context="A"),
            consequence=ClassicalNoActionConsequenceOperator(reward=1.0),
            max_trials=max_trials,
            dt_s=dt_s,
        )
        return ExecutableProtocolPreset(requested, spec, bundle)

    if requested == "probe_protocol":
        spec = ProtocolSpec(
            emission_rule="scheduled_emission",
            consequence_rule="deterministic_consequence",
            advance_rule="trial_increment",
            stop_rule="n_trials",
            protocol_family="custom",
            action_space_mode="classical_none",
            temporal_mode="trial_discrete",
            metadata={"preset_name": requested, "preset_version": "3.21.5"},
        )
        bundle = _trial_bundle(
            emission=ScheduledEmissionOperator(
                schedule=(
                    {"stimulus": {"tone": 1.0}, "context": "A"},
                    {"stimulus": {"tone": 1.0}, "context": "A"},
                    {"stimulus": {"tone": 1.0}, "context": "A", "metadata": {"probe": True}},
                ),
                loop=False,
            ),
            consequence=ClassicalNoActionConsequenceOperator(reward_schedule=(1.0, 1.0, 0.0)),
            max_trials=max_trials,
            dt_s=dt_s,
        )
        return ExecutableProtocolPreset(requested, spec, bundle)

    if requested == "operant_protocol":
        spec = ProtocolSpec(
            emission_rule="operant_offer_emission",
            consequence_rule="deterministic_consequence",
            advance_rule="trial_increment",
            stop_rule="n_trials",
            protocol_family="operant_conditioning",
            action_space_mode="discrete",
            temporal_mode="trial_discrete",
            metadata={"preset_name": requested, "preset_version": "3.21.5"},
        )
        bundle = _trial_bundle(
            emission=FixedEmissionOperator(
                stimulus={"lever": 1.0},
                context="Operant",
                available_actions=("left", "right"),
            ),
            consequence=ActionConditionedConsequenceOperator(
                reward_by_action={"left": 1.0, "right": 0.25},
                default_reward=0.0,
            ),
            max_trials=max_trials,
            dt_s=dt_s,
        )
        return ExecutableProtocolPreset(requested, spec, bundle)

    if requested == "concurrent_protocol":
        spec = ProtocolSpec(
            emission_rule="scheduled_emission",
            consequence_rule="deterministic_consequence",
            advance_rule="trial_increment",
            stop_rule="n_trials",
            protocol_family="operant_conditioning",
            action_space_mode="discrete",
            temporal_mode="trial_discrete",
            metadata={"preset_name": requested, "preset_version": "3.21.5"},
        )
        bundle = _trial_bundle(
            emission=ScheduledEmissionOperator(
                schedule=(
                    {"stimulus": {"key_left": 1.0}, "context": "A", "available_actions": ("left", "right")},
                    {"stimulus": {"key_right": 1.0}, "context": "B", "available_actions": ("left", "right")},
                ),
                loop=True,
            ),
            consequence=ActionConditionedConsequenceOperator(
                reward_by_action={"left": 0.8, "right": 0.8},
                default_reward=0.0,
            ),
            max_trials=max_trials,
            dt_s=dt_s,
        )
        return ExecutableProtocolPreset(requested, spec, bundle)

    if requested == "criterion_shift_protocol":
        spec = ProtocolSpec(
            emission_rule="classical_trial_emission",
            consequence_rule="deterministic_consequence",
            advance_rule="trial_increment",
            stop_rule="external_stop",
            protocol_family="custom",
            action_space_mode="classical_none",
            temporal_mode="trial_discrete",
            metadata={"preset_name": requested, "preset_version": "3.21.5"},
        )
        bundle = ProtocolBundle(
            emission_operator=FixedEmissionOperator(stimulus={"tone": 1.0}, context="Shift"),
            consequence_operator=ClassicalNoActionConsequenceOperator(reward=1.0),
            advance_operator=TrialAdvanceOperator(dt_s=float(dt_s)),
            stop_operator=CriterionStopOperator(reward_threshold=float(criterion_reward_threshold)),
        )
        return ExecutableProtocolPreset(requested, spec, bundle)

    known = ", ".join(executable_protocol_preset_names())
    raise ValueError(f"Unknown executable protocol preset '{preset_name}'. Known presets: {known}")


def build_executable_protocol_from_spec(
    spec: ProtocolSpec | Mapping[str, Any],
    *,
    max_trials: int = 5,
    dt_s: float = 1.0,
    criterion_reward_threshold: float = 3.0,
) -> ExecutableProtocolPreset:
    """Materialize executable protocol bundle directly from legal symbolic protocol spec."""
    protocol_spec = _coerce_protocol_spec(spec)

    named = str(protocol_spec.metadata.get("preset_name", "")).strip()
    if named in executable_protocol_preset_names():
        return build_executable_protocol_preset(
            named,
            max_trials=max_trials,
            dt_s=dt_s,
            criterion_reward_threshold=criterion_reward_threshold,
        )

    signature = (
        protocol_spec.protocol_family,
        protocol_spec.action_space_mode,
        protocol_spec.emission_rule,
        protocol_spec.consequence_rule,
        protocol_spec.stop_rule,
    )

    if signature == ("acquisition", "classical_none", "classical_trial_emission", "deterministic_consequence", "n_trials"):
        return build_executable_protocol_preset("acquisition_protocol", max_trials=max_trials, dt_s=dt_s)
    if signature == ("extinction", "classical_none", "classical_trial_emission", "null_consequence", "n_trials"):
        return build_executable_protocol_preset(
            "extinction_nonreinforcement_protocol",
            max_trials=max_trials,
            dt_s=dt_s,
        )
    if signature == ("operant_conditioning", "discrete", "operant_offer_emission", "deterministic_consequence", "n_trials"):
        return build_executable_protocol_preset("operant_protocol", max_trials=max_trials, dt_s=dt_s)
    if signature == ("custom", "classical_none", "classical_trial_emission", "deterministic_consequence", "external_stop"):
        return build_executable_protocol_preset(
            "criterion_shift_protocol",
            dt_s=dt_s,
            criterion_reward_threshold=criterion_reward_threshold,
        )

    raise ValueError(
        "[PROTO_E_EXECUTABLE_UNSUPPORTED_SPEC] Symbolic protocol spec is legal but does not map "
        "to a V3.21.5 executable core preset."
    )

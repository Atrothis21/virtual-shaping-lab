"""Protocol-grammar legality validator for V3.21.0."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

EMISSION_RULE_VALUES = {"classical_trial_emission", "operant_offer_emission", "scheduled_emission"}
CONSEQUENCE_RULE_VALUES = {"deterministic_consequence", "scheduled_consequence", "null_consequence"}
ADVANCE_RULE_VALUES = {"trial_increment", "event_increment"}
STOP_RULE_VALUES = {"n_trials", "session_end", "external_stop"}
PROTOCOL_FAMILY_VALUES = {"acquisition", "extinction", "operant_conditioning", "custom"}
ACTION_SPACE_MODE_VALUES = {"classical_none", "discrete", "binary_response"}
TEMPORAL_MODE_VALUES = {"trial_discrete", "event_discrete"}

FAMILY_TO_ACTION_SPACE: dict[str, set[str]] = {
    "acquisition": {"classical_none", "binary_response"},
    "extinction": {"classical_none", "binary_response"},
    "operant_conditioning": {"discrete", "binary_response"},
    "custom": {"classical_none", "discrete", "binary_response"},
}


@dataclass
class ProtocolSpecValidationError(ValueError):
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


def _reject(code: str, message: str) -> None:
    raise ProtocolSpecValidationError(code=code, message=message)


def validate_protocol_spec(spec: Any) -> None:
    emission_rule = getattr(spec, "emission_rule", None)
    consequence_rule = getattr(spec, "consequence_rule", None)
    advance_rule = getattr(spec, "advance_rule", None)
    stop_rule = getattr(spec, "stop_rule", None)
    protocol_family = getattr(spec, "protocol_family", None)
    action_space_mode = getattr(spec, "action_space_mode", None)
    temporal_mode = getattr(spec, "temporal_mode", None)
    schedule_metadata = getattr(spec, "schedule_metadata", None)
    phase_metadata = getattr(spec, "phase_metadata", None)

    if emission_rule not in EMISSION_RULE_VALUES:
        _reject("PROTO_E_UNKNOWN_EMISSION_RULE", f"Unsupported emission_rule '{emission_rule}'.")
    if consequence_rule not in CONSEQUENCE_RULE_VALUES:
        _reject("PROTO_E_UNKNOWN_CONSEQUENCE_RULE", f"Unsupported consequence_rule '{consequence_rule}'.")
    if advance_rule not in ADVANCE_RULE_VALUES:
        _reject("PROTO_E_UNKNOWN_ADVANCE_RULE", f"Unsupported advance_rule '{advance_rule}'.")
    if stop_rule not in STOP_RULE_VALUES:
        _reject("PROTO_E_UNKNOWN_STOP_RULE", f"Unsupported stop_rule '{stop_rule}'.")
    if protocol_family not in PROTOCOL_FAMILY_VALUES:
        _reject("PROTO_E_UNKNOWN_PROTOCOL_FAMILY", f"Unsupported protocol_family '{protocol_family}'.")
    if action_space_mode not in ACTION_SPACE_MODE_VALUES:
        _reject("PROTO_E_UNKNOWN_ACTION_SPACE_MODE", f"Unsupported action_space_mode '{action_space_mode}'.")
    if temporal_mode not in TEMPORAL_MODE_VALUES:
        _reject("PROTO_E_UNKNOWN_TEMPORAL_MODE", f"Unsupported temporal_mode '{temporal_mode}'.")
    if not isinstance(schedule_metadata, dict):
        _reject("PROTO_E_SCHEDULE_METADATA_NOT_OBJECT", "ProtocolSpec.schedule_metadata must be an object.")
    if not isinstance(phase_metadata, dict):
        _reject("PROTO_E_PHASE_METADATA_NOT_OBJECT", "ProtocolSpec.phase_metadata must be an object.")

    if action_space_mode not in FAMILY_TO_ACTION_SPACE[protocol_family]:
        _reject(
            "PROTO_E_FAMILY_ACTION_SPACE_MISMATCH",
            (
                f"protocol_family '{protocol_family}' is incompatible with "
                f"action_space_mode '{action_space_mode}'."
            ),
        )

    if protocol_family == "operant_conditioning" and action_space_mode == "classical_none":
        _reject(
            "PROTO_E_OPERANT_REQUIRES_ACTION_SPACE",
            "protocol_family='operant_conditioning' requires a non-null action_space_mode.",
        )

    if action_space_mode == "classical_none" and consequence_rule == "scheduled_consequence":
        _reject(
            "PROTO_E_CLASSICAL_NONE_CONSEQUENCE_MISMATCH",
            "action_space_mode='classical_none' is incompatible with consequence_rule='scheduled_consequence'.",
        )

    if temporal_mode == "trial_discrete" and advance_rule != "trial_increment":
        _reject(
            "PROTO_E_TRIAL_TEMPORAL_REQUIRES_TRIAL_ADVANCE",
            "temporal_mode='trial_discrete' requires advance_rule='trial_increment'.",
        )

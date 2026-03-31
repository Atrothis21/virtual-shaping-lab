"""Policy-grammar legality validator for V3.20.0."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SELECTION_RULE_VALUES = {"null", "greedy", "epsilon_greedy", "softmax", "uniform_random"}
ACTION_SPACE_MODE_VALUES = {"classical_none", "discrete", "binary_response"}
TIE_BREAK_RULE_VALUES = {"stable_lexicographic", "first", "random"}
AVAILABILITY_RULE_VALUES = {"none", "environment_declared"}

SELECTION_TO_ACTION_SPACE: dict[str, set[str]] = {
    "null": {"classical_none"},
    "greedy": {"discrete", "binary_response"},
    "epsilon_greedy": {"discrete", "binary_response"},
    "softmax": {"discrete", "binary_response"},
    "uniform_random": {"discrete", "binary_response"},
}

SELECTION_REQUIRES_PARAMS: dict[str, tuple[str, ...]] = {
    "epsilon_greedy": ("epsilon",),
    "softmax": ("temperature",),
}


@dataclass
class PolicySpecValidationError(ValueError):
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


def _reject(code: str, message: str) -> None:
    raise PolicySpecValidationError(code=code, message=message)


def _require_numeric_param(parameters: dict[str, Any], key: str) -> float:
    value = parameters.get(key)
    if not isinstance(value, (int, float)):
        _reject("POL_E_MISSING_REQUIRED_PARAMETER", f"Selection rule requires numeric parameter '{key}'.")
    return float(value)


def validate_policy_spec(spec: Any) -> None:
    selection_rule = getattr(spec, "selection_rule", None)
    action_space_mode = getattr(spec, "action_space_mode", None)
    parameters = getattr(spec, "parameters", None)
    tie_break_rule = getattr(spec, "tie_break_rule", None)
    availability_rule = getattr(spec, "availability_rule", None)

    if selection_rule not in SELECTION_RULE_VALUES:
        _reject("POL_E_UNKNOWN_SELECTION_RULE", f"Unsupported selection_rule '{selection_rule}'.")
    if action_space_mode not in ACTION_SPACE_MODE_VALUES:
        _reject("POL_E_UNKNOWN_ACTION_SPACE_MODE", f"Unsupported action_space_mode '{action_space_mode}'.")
    if tie_break_rule is not None and tie_break_rule not in TIE_BREAK_RULE_VALUES:
        _reject("POL_E_UNKNOWN_TIE_BREAK_RULE", f"Unsupported tie_break_rule '{tie_break_rule}'.")
    if availability_rule is not None and availability_rule not in AVAILABILITY_RULE_VALUES:
        _reject("POL_E_UNKNOWN_AVAILABILITY_RULE", f"Unsupported availability_rule '{availability_rule}'.")
    if not isinstance(parameters, dict):
        _reject("POL_E_PARAMETERS_NOT_OBJECT", "PolicySpec.parameters must be an object.")

    if action_space_mode not in SELECTION_TO_ACTION_SPACE[selection_rule]:
        _reject(
            "POL_E_SELECTION_ACTION_SPACE_MISMATCH",
            f"selection_rule '{selection_rule}' is incompatible with action_space_mode '{action_space_mode}'.",
        )

    if selection_rule == "null" and action_space_mode != "classical_none":
        _reject("POL_E_NULL_REQUIRES_CLASSICAL_NONE", "selection_rule='null' requires action_space_mode='classical_none'.")
    if action_space_mode == "classical_none" and selection_rule != "null":
        _reject("POL_E_CLASSICAL_NONE_REQUIRES_NULL", "action_space_mode='classical_none' requires selection_rule='null'.")

    for key in SELECTION_REQUIRES_PARAMS.get(selection_rule, ()):
        numeric_value = _require_numeric_param(parameters, key)
        if key == "epsilon" and not (0.0 <= numeric_value <= 1.0):
            _reject("POL_E_INVALID_EPSILON", "epsilon must be in [0.0, 1.0].")
        if key == "temperature" and numeric_value <= 0.0:
            _reject("POL_E_INVALID_TEMPERATURE", "temperature must be > 0.0.")


"""Legality rule engine and compatibility matrix for operator-basis selections."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.operator_basis_registry import list_ui_selectable_implementations
from ui.contracts.operator_basis_schema import REQUIRED_OPERATOR_BASIS_SLOTS
from ui.contracts.operator_subset_contract import validate_preset_definition


OPERATOR_LEGALITY_RULES_VERSION = "3.12.5"


class OperatorLegalityError(ValueError):
    """Raised when operator selections violate legality rules."""

    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        self.code = str(code)
        self.details = dict(details or {})
        super().__init__(f"[{self.code}] {message}")


def _selection(values: dict[str, Any], slot: str) -> str | None:
    value = values.get(slot)
    if isinstance(value, str):
        return value
    return None


def _selection_list(values: dict[str, Any], slot: str) -> list[str]:
    value = values.get(slot)
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        return [value]
    return []


def _materialize_effective_selection_map(preset_definition: dict[str, Any]) -> dict[str, Any]:
    preset = validate_preset_definition(preset_definition)
    subset = dict(preset.get("operator_subset", {}) or {})
    defaults = dict(preset.get("defaults", {}) or {})
    out: dict[str, Any] = {}
    for slot in REQUIRED_OPERATOR_BASIS_SLOTS:
        if slot in subset:
            out[slot] = deepcopy(subset[slot])
        elif slot in defaults:
            out[slot] = deepcopy(defaults[slot])
        else:
            out[slot] = None
    return out


OPERATOR_COMPATIBILITY_MATRIX: dict[str, dict[str, Any]] = {
    "LGL_E_SLOT_UNKNOWN_SELECTION": {
        "kind": "slot_level",
        "description": "Selection must come from registry universe for its slot.",
    },
    "LGL_E_DELTA_REQUIRES_TRACE": {
        "kind": "cross_slot",
        "description": "td_lambda_error requires an eligibility/trace mechanism.",
    },
    "LGL_E_POLICY_REQUIRES_ACTION_PREDICTOR": {
        "kind": "cross_slot",
        "description": "Non-null policy requires action-capable predictor.",
    },
    "LGL_E_CLASSICAL_POLICY_INCOMPATIBLE": {
        "kind": "cross_slot",
        "description": "Classical contingency cannot pair with action policy.",
    },
    "LGL_E_ACTOR_CRITIC_TRIPLET": {
        "kind": "cross_slot",
        "description": "actor_critic_update requires compatible predictor and error.",
    },
    "LGL_E_MEASURE_REQUIRES_POLICY": {
        "kind": "cross_slot",
        "description": "action_probabilities measurement requires policy.",
    },
    "LGL_E_MEASURE_REQUIRES_TRACE": {
        "kind": "cross_slot",
        "description": "eligibility_curve measurement requires trace mechanism.",
    },
}


def get_operator_compatibility_matrix() -> dict[str, dict[str, Any]]:
    """Return legality/compatibility matrix."""
    return deepcopy(OPERATOR_COMPATIBILITY_MATRIX)


def list_operator_legality_error_codes() -> tuple[str, ...]:
    """Return stable legality error-code ordering."""
    return tuple(sorted(OPERATOR_COMPATIBILITY_MATRIX.keys()))


def validate_slot_selection_legality(slot: str, selection: Any) -> None:
    """Validate one slot selection value against registry universe."""
    slot_key = str(slot or "").strip()
    if slot_key not in REQUIRED_OPERATOR_BASIS_SLOTS:
        raise OperatorLegalityError(
            "LGL_E_SLOT_UNKNOWN_SELECTION",
            f"Unknown slot '{slot_key}'.",
            details={"slot": slot_key},
        )

    if selection is None:
        return

    allowed = set(list_ui_selectable_implementations(slot_key))
    if slot_key == "m":
        if not isinstance(selection, list):
            raise OperatorLegalityError(
                "LGL_E_SLOT_UNKNOWN_SELECTION",
                f"Slot '{slot_key}' expects list selection.",
                details={"slot": slot_key},
            )
        for item in selection:
            key = str(item)
            if key not in allowed:
                raise OperatorLegalityError(
                    "LGL_E_SLOT_UNKNOWN_SELECTION",
                    f"Slot '{slot_key}' selection '{key}' is not registry-declared.",
                    details={"slot": slot_key, "selection": key},
                )
        return

    key = str(selection)
    if key not in allowed:
        raise OperatorLegalityError(
            "LGL_E_SLOT_UNKNOWN_SELECTION",
            f"Slot '{slot_key}' selection '{key}' is not registry-declared.",
            details={"slot": slot_key, "selection": key},
        )


def evaluate_operator_legality(preset_definition: dict[str, Any]) -> list[dict[str, Any]]:
    """Evaluate legality rules and return diagnostics."""
    selected = _materialize_effective_selection_map(preset_definition)

    diagnostics: list[dict[str, Any]] = []
    for slot in REQUIRED_OPERATOR_BASIS_SLOTS:
        try:
            validate_slot_selection_legality(slot, selected.get(slot))
        except OperatorLegalityError as exc:
            diagnostics.append(
                {
                    "code": exc.code,
                    "message": str(exc),
                    "slot": slot,
                    "details": dict(exc.details),
                }
            )

    delta = _selection(selected, "delta")
    e = _selection(selected, "e")
    p = _selection(selected, "p")
    w = _selection(selected, "w")
    pi = _selection(selected, "pi")
    omega = _selection(selected, "omega")
    m = _selection_list(selected, "m")

    if delta == "td_lambda_error" and e not in {
        "trace_decay",
        "replacing_trace",
        "accumulating_trace",
        "bounded_trace",
    }:
        diagnostics.append(
            {
                "code": "LGL_E_DELTA_REQUIRES_TRACE",
                "message": "td_lambda_error requires a trace-enabled e slot.",
                "slot": "delta",
                "details": {"delta": delta, "e": e},
            }
        )

    if pi not in {None, "none"} and p not in {"action_value", "state_action_value", "response_strength"}:
        diagnostics.append(
            {
                "code": "LGL_E_POLICY_REQUIRES_ACTION_PREDICTOR",
                "message": "Non-null policy requires action-capable predictor.",
                "slot": "pi",
                "details": {"pi": pi, "p": p},
            }
        )

    if omega == "classical_contingency" and pi not in {None, "none"}:
        diagnostics.append(
            {
                "code": "LGL_E_CLASSICAL_POLICY_INCOMPATIBLE",
                "message": "classical_contingency is incompatible with action policies.",
                "slot": "omega",
                "details": {"omega": omega, "pi": pi},
            }
        )

    if w == "actor_critic_update" and (p != "state_action_value" or delta != "advantage_error"):
        diagnostics.append(
            {
                "code": "LGL_E_ACTOR_CRITIC_TRIPLET",
                "message": "actor_critic_update requires p=state_action_value and delta=advantage_error.",
                "slot": "w",
                "details": {"w": w, "p": p, "delta": delta},
            }
        )

    if "action_probabilities" in m and pi in {None, "none"}:
        diagnostics.append(
            {
                "code": "LGL_E_MEASURE_REQUIRES_POLICY",
                "message": "action_probabilities measurement requires a policy.",
                "slot": "m",
                "details": {"m": m, "pi": pi},
            }
        )

    if "eligibility_curve" in m and e in {None, "none"}:
        diagnostics.append(
            {
                "code": "LGL_E_MEASURE_REQUIRES_TRACE",
                "message": "eligibility_curve measurement requires trace-enabled e slot.",
                "slot": "m",
                "details": {"m": m, "e": e},
            }
        )

    return diagnostics


def validate_operator_legality(preset_definition: dict[str, Any]) -> dict[str, Any]:
    """Validate legality and raise machine-readable error codes on failure."""
    diagnostics = evaluate_operator_legality(preset_definition)
    if diagnostics:
        first = diagnostics[0]
        raise OperatorLegalityError(
            str(first["code"]),
            str(first["message"]),
            details={"diagnostics": diagnostics},
        )
    return _materialize_effective_selection_map(preset_definition)


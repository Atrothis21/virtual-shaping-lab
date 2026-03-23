"""Typed maximal operator-basis schema contract for V3 preset authoring."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any


class OperatorBasisSchemaValidationError(ValueError):
    """Raised when the operator-basis schema contract is invalid."""


OPERATOR_BASIS_SCHEMA_VERSION = "3.12.0"

REQUIRED_OPERATOR_BASIS_SLOTS: tuple[str, ...] = (
    "phi",
    "c",
    "g",
    "e",
    "p",
    "delta",
    "a",
    "w",
    "pi",
    "omega",
    "m",
)

_MULTI_SELECT_SLOTS: tuple[str, ...] = ("m",)
_SINGLE_SELECT_SLOTS: tuple[str, ...] = tuple(
    slot for slot in REQUIRED_OPERATOR_BASIS_SLOTS if slot not in _MULTI_SELECT_SLOTS
)

OPERATOR_BASIS_MASTER_TABLE: dict[str, dict[str, Any]] = {
    "phi": {
        "label": "Representation",
        "symbol": "Phi",
        "selection_mode": "single",
        "required": True,
        "allowed_selections": (
            "identity",
            "elemental",
            "binary_feature_vector",
            "dense_feature_vector",
            "compound_elemental",
            "configural",
            "hybrid_elemental_configural",
            "temporal_stub",
        ),
    },
    "c": {
        "label": "Context",
        "symbol": "C",
        "selection_mode": "single",
        "required": False,
        "allowed_selections": (
            "none",
            "context_label",
            "one_hot_context",
            "context_feature_vector",
            "context_gating_additive",
            "context_gating_multiplicative",
            "latent_context_state",
            "trial_epoch_tag",
            "phase_tag",
        ),
    },
    "g": {
        "label": "Generalization",
        "symbol": "G",
        "selection_mode": "single",
        "required": False,
        "allowed_selections": (
            "none",
            "identity_only",
            "stimulus_similarity_matrix",
            "gaussian_kernel",
            "exponential_kernel",
            "feature_overlap",
            "context_similarity",
            "compound_overlap",
            "prototype_generalization",
            "exemplar_generalization",
        ),
    },
    "e": {
        "label": "Eligibility / Trace",
        "symbol": "E",
        "selection_mode": "single",
        "required": False,
        "allowed_selections": (
            "none",
            "trace_decay",
            "replacing_trace",
            "accumulating_trace",
            "bounded_trace",
            "stimulus_persistence",
            "response_persistence",
        ),
    },
    "p": {
        "label": "Prediction",
        "symbol": "P",
        "selection_mode": "single",
        "required": True,
        "allowed_selections": (
            "state_value",
            "stimulus_expectancy",
            "compound_expectancy",
            "action_value",
            "state_action_value",
            "outcome_probability",
            "multi_outcome_prediction",
            "criterion_estimate",
            "response_strength",
        ),
    },
    "delta": {
        "label": "Error Signal",
        "symbol": "Delta",
        "selection_mode": "single",
        "required": True,
        "allowed_selections": (
            "rw_error",
            "td0_error",
            "td_lambda_error",
            "reward_prediction_error",
            "signed_error",
            "unsigned_error",
            "surprise",
            "advantage_error",
            "criterion_error",
        ),
    },
    "a": {
        "label": "Attention / Associability",
        "symbol": "A",
        "selection_mode": "single",
        "required": False,
        "allowed_selections": (
            "none",
            "fixed_alpha",
            "mackintosh",
            "pearce_hall",
            "hybrid_attention",
            "stimulus_salience_map",
            "novelty_attention",
            "uncertainty_attention",
            "feature_wise_attention",
        ),
    },
    "w": {
        "label": "Update Rule",
        "symbol": "W",
        "selection_mode": "single",
        "required": True,
        "allowed_selections": (
            "rescorla_wagner",
            "delta_rule",
            "td0_update",
            "td_lambda_update",
            "q_learning_update",
            "sarsa_update",
            "actor_critic_update",
            "linear_gradient_update",
            "criterion_shift_update",
        ),
    },
    "pi": {
        "label": "Policy",
        "symbol": "Pi",
        "selection_mode": "single",
        "required": False,
        "allowed_selections": (
            "none",
            "deterministic",
            "epsilon_greedy",
            "softmax",
            "probability_matching",
            "win_stay_lose_shift",
            "threshold_policy",
            "habit_policy",
            "goal_directed_policy",
            "mixed_controller",
        ),
    },
    "omega": {
        "label": "Environment / Contingency",
        "symbol": "Omega",
        "selection_mode": "single",
        "required": True,
        "allowed_selections": (
            "deterministic_schedule",
            "probabilistic_schedule",
            "partial_reinforcement",
            "fixed_ratio",
            "variable_ratio",
            "fixed_interval",
            "variable_interval",
            "classical_contingency",
            "operant_contingency",
            "contextual_contingency",
            "state_transition_model",
            "probe_no_outcome",
        ),
    },
    "m": {
        "label": "Measurement",
        "symbol": "M",
        "selection_mode": "multi",
        "required": True,
        "allowed_selections": (
            "trial_log",
            "associative_strength",
            "response_strength",
            "prediction_curve",
            "learning_curve",
            "action_probabilities",
            "value_table",
            "prediction_error_curve",
            "attention_curve",
            "eligibility_curve",
            "generalization_matrix",
            "discrimination_index",
            "criterion_curve",
            "phase_summary",
            "final_weights",
            "report_bundle",
        ),
    },
}

_REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = (
    "version",
    "preset_id",
    "label",
    "description",
    "operators",
    "stimuli",
    "program",
)
_REQUIRED_SLOT_KEYS: tuple[str, ...] = ("enabled", "selection", "params")
_REQUIRED_STIMULI_ROLE_KEYS: tuple[str, ...] = ("cs_plus", "cs_minus", "us", "context")


OPERATOR_BASIS_SCHEMA_TEMPLATE: dict[str, Any] = {
    "version": OPERATOR_BASIS_SCHEMA_VERSION,
    "preset_id": "acquisition",
    "label": "Acquisition",
    "description": "Canonical acquisition operator-basis contract surface.",
    "operators": {
        "phi": {"enabled": True, "selection": "elemental", "params": {}},
        "c": {"enabled": False, "selection": None, "params": {}},
        "g": {"enabled": False, "selection": None, "params": {}},
        "e": {"enabled": False, "selection": None, "params": {}},
        "p": {"enabled": True, "selection": "state_value", "params": {}},
        "delta": {"enabled": True, "selection": "rw_error", "params": {}},
        "a": {"enabled": False, "selection": None, "params": {}},
        "w": {"enabled": True, "selection": "rescorla_wagner", "params": {}},
        "pi": {"enabled": False, "selection": None, "params": {}},
        "omega": {"enabled": True, "selection": "classical_contingency", "params": {}},
        "m": {
            "enabled": True,
            "selection": ["trial_log", "learning_curve", "final_weights"],
            "params": {},
        },
    },
    "stimuli": {
        "catalog": ["tone", "noise", "light"],
        "roles": {
            "cs_plus": ["tone"],
            "cs_minus": [],
            "us": ["reward"],
            "context": ["A"],
        },
    },
    "program": {"phases": []},
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OperatorBasisSchemaValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperatorBasisSchemaValidationError(f"{label} must be a non-empty string.")
    return value


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise OperatorBasisSchemaValidationError(f"{label} must be a list of strings.")
    out: list[str] = []
    for idx, item in enumerate(value):
        out.append(_require_non_empty_string(item, f"{label}[{idx}]"))
    return out


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise OperatorBasisSchemaValidationError(f"{label} must be boolean.")
    return value


def _validate_master_table(master_table: dict[str, Any]) -> None:
    if set(master_table.keys()) != set(REQUIRED_OPERATOR_BASIS_SLOTS):
        missing = sorted(set(REQUIRED_OPERATOR_BASIS_SLOTS) - set(master_table.keys()))
        extra = sorted(set(master_table.keys()) - set(REQUIRED_OPERATOR_BASIS_SLOTS))
        detail_parts: list[str] = []
        if missing:
            detail_parts.append(f"missing slots: {', '.join(missing)}")
        if extra:
            detail_parts.append(f"unexpected slots: {', '.join(extra)}")
        detail = "; ".join(detail_parts)
        raise OperatorBasisSchemaValidationError(
            f"operator_basis master table must match required slots exactly ({detail})."
        )
    for slot_key, payload in master_table.items():
        entry = _require_dict(payload, f"operator_basis_master_table.{slot_key}")
        _require_non_empty_string(entry.get("label"), f"operator_basis_master_table.{slot_key}.label")
        _require_non_empty_string(entry.get("symbol"), f"operator_basis_master_table.{slot_key}.symbol")
        selection_mode = _require_non_empty_string(
            entry.get("selection_mode"),
            f"operator_basis_master_table.{slot_key}.selection_mode",
        )
        if selection_mode not in {"single", "multi"}:
            raise OperatorBasisSchemaValidationError(
                f"operator_basis_master_table.{slot_key}.selection_mode must be 'single' or 'multi'."
            )
        required = entry.get("required")
        _require_bool(required, f"operator_basis_master_table.{slot_key}.required")
        allowed = entry.get("allowed_selections")
        if not isinstance(allowed, (list, tuple)) or not allowed:
            raise OperatorBasisSchemaValidationError(
                f"operator_basis_master_table.{slot_key}.allowed_selections must be a non-empty list/tuple."
            )
        seen: set[str] = set()
        for idx, item in enumerate(allowed):
            key = _require_non_empty_string(
                item, f"operator_basis_master_table.{slot_key}.allowed_selections[{idx}]"
            )
            if key in seen:
                raise OperatorBasisSchemaValidationError(
                    f"operator_basis_master_table.{slot_key}.allowed_selections has duplicate value: {key}"
                )
            seen.add(key)


def _validate_slot(slot_key: str, slot_payload: dict[str, Any], master_entry: dict[str, Any]) -> None:
    for key in _REQUIRED_SLOT_KEYS:
        if key not in slot_payload:
            raise OperatorBasisSchemaValidationError(
                f"operator_basis.operators.{slot_key} missing required key: {key}"
            )
    enabled = _require_bool(slot_payload.get("enabled"), f"operator_basis.operators.{slot_key}.enabled")
    params = slot_payload.get("params")
    _require_dict(params, f"operator_basis.operators.{slot_key}.params")

    allowed_set = set(master_entry["allowed_selections"])
    selection_mode = master_entry["selection_mode"]
    required = bool(master_entry["required"])
    selection = slot_payload.get("selection")

    if selection_mode == "single":
        if enabled:
            selection_key = _require_non_empty_string(
                selection, f"operator_basis.operators.{slot_key}.selection"
            )
            if selection_key not in allowed_set:
                raise OperatorBasisSchemaValidationError(
                    f"operator_basis.operators.{slot_key}.selection must be one of: "
                    f"{', '.join(sorted(allowed_set))}"
                )
        else:
            if selection is not None:
                raise OperatorBasisSchemaValidationError(
                    f"operator_basis.operators.{slot_key}.selection must be null when disabled."
                )
    else:
        if enabled:
            values = _require_string_list(selection, f"operator_basis.operators.{slot_key}.selection")
            if not values:
                raise OperatorBasisSchemaValidationError(
                    f"operator_basis.operators.{slot_key}.selection must be non-empty when enabled."
                )
            seen_values: set[str] = set()
            for value in values:
                if value in seen_values:
                    raise OperatorBasisSchemaValidationError(
                        f"operator_basis.operators.{slot_key}.selection has duplicate value: {value}"
                    )
                if value not in allowed_set:
                    raise OperatorBasisSchemaValidationError(
                        f"operator_basis.operators.{slot_key}.selection references unknown value: {value}"
                    )
                seen_values.add(value)
        else:
            if selection is not None:
                raise OperatorBasisSchemaValidationError(
                    f"operator_basis.operators.{slot_key}.selection must be null when disabled."
                )

    if required and not enabled:
        raise OperatorBasisSchemaValidationError(
            f"operator_basis.operators.{slot_key} is required and cannot be disabled."
        )


def validate_operator_basis_schema(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate maximal operator-basis payload schema and return a deep copy."""
    _validate_master_table(OPERATOR_BASIS_MASTER_TABLE)

    out = deepcopy(OPERATOR_BASIS_SCHEMA_TEMPLATE if payload is None else payload)
    root = _require_dict(out, "operator_basis")

    for key in _REQUIRED_TOP_LEVEL_KEYS:
        if key not in root:
            raise OperatorBasisSchemaValidationError(f"operator_basis missing required key: {key}")

    _require_non_empty_string(root.get("version"), "operator_basis.version")
    _require_non_empty_string(root.get("preset_id"), "operator_basis.preset_id")
    _require_non_empty_string(root.get("label"), "operator_basis.label")
    _require_non_empty_string(root.get("description"), "operator_basis.description")

    operators = _require_dict(root.get("operators"), "operator_basis.operators")
    keys = set(operators.keys())
    required_keys = set(REQUIRED_OPERATOR_BASIS_SLOTS)
    if keys != required_keys:
        missing = sorted(required_keys - keys)
        extra = sorted(keys - required_keys)
        detail_parts: list[str] = []
        if missing:
            detail_parts.append(f"missing slots: {', '.join(missing)}")
        if extra:
            detail_parts.append(f"unexpected slots: {', '.join(extra)}")
        detail = "; ".join(detail_parts)
        raise OperatorBasisSchemaValidationError(
            f"operator_basis.operators must contain exactly required slots ({detail})."
        )

    for slot_key in REQUIRED_OPERATOR_BASIS_SLOTS:
        slot_payload = _require_dict(operators.get(slot_key), f"operator_basis.operators.{slot_key}")
        _validate_slot(slot_key, slot_payload, OPERATOR_BASIS_MASTER_TABLE[slot_key])

    stimuli = _require_dict(root.get("stimuli"), "operator_basis.stimuli")
    _require_string_list(stimuli.get("catalog"), "operator_basis.stimuli.catalog")
    roles = _require_dict(stimuli.get("roles"), "operator_basis.stimuli.roles")
    for key in _REQUIRED_STIMULI_ROLE_KEYS:
        _require_string_list(roles.get(key), f"operator_basis.stimuli.roles.{key}")

    program = _require_dict(root.get("program"), "operator_basis.program")
    phases = program.get("phases")
    if not isinstance(phases, list):
        raise OperatorBasisSchemaValidationError("operator_basis.program.phases must be a list.")

    return out


def get_operator_basis_schema() -> dict[str, Any]:
    """Return validated maximal operator-basis schema payload."""
    return validate_operator_basis_schema(OPERATOR_BASIS_SCHEMA_TEMPLATE)


def list_operator_basis_slots() -> tuple[str, ...]:
    """Return stable operator basis slot ordering."""
    return REQUIRED_OPERATOR_BASIS_SLOTS


def stable_operator_basis_schema_json(payload: dict[str, Any] | None = None) -> str:
    """Return deterministic JSON serialization for schema payload."""
    normalized = validate_operator_basis_schema(payload)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"))


def stable_operator_basis_schema_hash(payload: dict[str, Any] | None = None) -> str:
    """Return deterministic hash for schema payload."""
    encoded = stable_operator_basis_schema_json(payload).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


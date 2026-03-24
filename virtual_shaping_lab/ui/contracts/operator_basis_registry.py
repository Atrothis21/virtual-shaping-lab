"""Canonical basis-operator selection registry for V3 compiler surfaces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.operator_basis_schema import (
    OPERATOR_BASIS_MASTER_TABLE,
    REQUIRED_OPERATOR_BASIS_SLOTS,
)


class OperatorBasisRegistryValidationError(ValueError):
    """Raised when basis-operator registry validation fails."""


OPERATOR_BASIS_REGISTRY_VERSION = "3.12.0"

_SLOT_TO_BUILDER_FAMILY: dict[str, str] = {
    "phi": "representation",
    "c": "representation",
    "g": "representation",
    "e": "learner",
    "p": "learner",
    "delta": "learner",
    "a": "learner",
    "w": "learner",
    "pi": "agent_control",
    "omega": "environment_protocol",
    "m": "report_readout",
}

_PARAM_SCHEMA_OVERRIDES: dict[str, dict[str, dict[str, Any]]] = {
    "phi": {
        "elemental": {
            "stimulus_catalog": {"type": "list[string]"},
            "max_compound_size": {"type": "int", "min": 1},
        },
        "dense_feature_vector": {"feature_dimensions": {"type": "int", "min": 1}},
    },
    "g": {
        "stimulus_similarity_matrix": {"similarity_matrix": {"type": "matrix"}},
        "gaussian_kernel": {"sigma": {"type": "float", "gt": 0.0}},
        "exponential_kernel": {"decay": {"type": "float", "gt": 0.0}},
    },
    "e": {
        "trace_decay": {"lambda": {"type": "float", "min": 0.0, "max": 1.0}},
        "bounded_trace": {"cap": {"type": "float", "gt": 0.0}},
    },
    "delta": {
        "td0_error": {"gamma": {"type": "float", "min": 0.0, "max": 1.0}},
        "td_lambda_error": {
            "gamma": {"type": "float", "min": 0.0, "max": 1.0},
            "lambda": {"type": "float", "min": 0.0, "max": 1.0},
        },
    },
    "a": {
        "fixed_alpha": {"alpha": {"type": "float", "min": 0.0, "max": 1.0}},
        "mackintosh": {"kappa": {"type": "float", "min": 0.0, "max": 1.0}},
        "pearce_hall": {"eta": {"type": "float", "min": 0.0, "max": 1.0}},
    },
    "w": {
        "rescorla_wagner": {"learning_rate": {"type": "float", "min": 0.0, "max": 1.0}},
        "td0_update": {
            "learning_rate": {"type": "float", "min": 0.0, "max": 1.0},
            "gamma": {"type": "float", "min": 0.0, "max": 1.0},
        },
    },
    "pi": {
        "epsilon_greedy": {"epsilon": {"type": "float", "min": 0.0, "max": 1.0}},
        "softmax": {"temperature": {"type": "float", "gt": 0.0}},
        "threshold_policy": {"response_threshold": {"type": "float"}},
    },
    "omega": {
        "probabilistic_schedule": {"reinforcement_probability": {"type": "float", "min": 0.0, "max": 1.0}},
        "fixed_ratio": {"ratio": {"type": "int", "min": 1}},
        "variable_ratio": {"ratio": {"type": "int", "min": 1}},
        "fixed_interval": {"interval": {"type": "float", "gt": 0.0}},
        "variable_interval": {"interval": {"type": "float", "gt": 0.0}},
    },
    "m": {
        "trial_log": {"sample_rate": {"type": "int", "min": 1}},
        "learning_curve": {"aggregate_by_phase": {"type": "bool"}},
        "report_bundle": {"emit_figures": {"type": "bool"}, "emit_tables": {"type": "bool"}},
    },
}

_MEASUREMENT_REPORT_ALIGNMENT: dict[str, dict[str, Any]] = {
    "trial_log": {
        "priority": 30,
        "supported_metrics": [
            "prediction_time_series",
            "prediction_error_time_series",
            "action_counts",
        ],
        "metric_to_variable": {
            "prediction_time_series": "predicted_outcome",
            "prediction_error_time_series": "prediction_error",
            "action_counts": "action_counts",
        },
    },
    "associative_strength": {
        "priority": 20,
        "supported_metrics": ["associative_strength_time_series"],
        "metric_to_variable": {"associative_strength_time_series": "associative_strength"},
    },
    "response_strength": {
        "priority": 20,
        "supported_metrics": ["response_strength_time_series"],
        "metric_to_variable": {"response_strength_time_series": "response_strength"},
    },
    "prediction_curve": {
        "priority": 10,
        "supported_metrics": [
            "prediction_time_series",
            "mean_prediction_by_stimulus",
            "final_prediction_by_stimulus",
        ],
        "metric_to_variable": {
            "prediction_time_series": "predicted_outcome",
            "mean_prediction_by_stimulus": "predicted_outcome",
            "final_prediction_by_stimulus": "predicted_outcome",
        },
    },
    "learning_curve": {
        "priority": 5,
        "supported_metrics": [
            "prediction_time_series",
            "mean_prediction_by_stimulus",
            "final_prediction_by_stimulus",
            "mean_reward_by_stimulus",
            "trial_count_by_stimulus",
            "discrimination_index",
            "extinction_rate",
            "reward_time_series",
            "cumulative_responses",
            "cumulative_rewards",
            "outcome_type_counts",
            "phase_reward_summary",
            "action_counts",
        ],
        "metric_to_variable": {
            "prediction_time_series": "predicted_outcome",
            "mean_prediction_by_stimulus": "predicted_outcome",
            "final_prediction_by_stimulus": "predicted_outcome",
            "action_counts": "action_counts",
        },
    },
    "action_probabilities": {
        "priority": 20,
        "supported_metrics": ["action_counts"],
        "metric_to_variable": {"action_counts": "action_counts"},
    },
    "prediction_error_curve": {
        "priority": 15,
        "supported_metrics": ["prediction_error_time_series"],
        "metric_to_variable": {"prediction_error_time_series": "prediction_error"},
    },
    "discrimination_index": {
        "priority": 10,
        "supported_metrics": ["discrimination_index"],
        "metric_to_variable": {},
    },
    "phase_summary": {
        "priority": 40,
        "supported_metrics": ["phase_reward_summary"],
        "metric_to_variable": {},
    },
    "report_bundle": {
        "priority": 50,
        "supported_metrics": [
            "prediction_time_series",
            "mean_prediction_by_stimulus",
            "final_prediction_by_stimulus",
            "mean_reward_by_stimulus",
            "trial_count_by_stimulus",
            "discrimination_index",
            "reward_time_series",
            "cumulative_responses",
            "cumulative_rewards",
            "outcome_type_counts",
            "phase_reward_summary",
            "action_counts",
        ],
        "metric_to_variable": {
            "prediction_time_series": "predicted_outcome",
            "mean_prediction_by_stimulus": "predicted_outcome",
            "final_prediction_by_stimulus": "predicted_outcome",
            "action_counts": "action_counts",
        },
    },
}


def _titleize(selection_id: str) -> str:
    return selection_id.replace("_", " ").strip().title()


def _build_registry() -> dict[str, Any]:
    slots: dict[str, Any] = {}
    for slot in REQUIRED_OPERATOR_BASIS_SLOTS:
        master_entry = OPERATOR_BASIS_MASTER_TABLE[slot]
        allowed = tuple(master_entry["allowed_selections"])
        selection_payloads: dict[str, Any] = {}
        for selection_id in allowed:
            param_schema = (
                _PARAM_SCHEMA_OVERRIDES.get(slot, {}).get(selection_id, {})
                if isinstance(_PARAM_SCHEMA_OVERRIDES.get(slot, {}), dict)
                else {}
            )
            selection_payload = {
                "id": selection_id,
                "label": _titleize(selection_id),
                "params_schema": dict(param_schema),
                "internal_builder_family": _SLOT_TO_BUILDER_FAMILY[slot],
                "ui_visible": True,
            }
            if slot == "m":
                selection_payload["report_alignment"] = deepcopy(
                    _MEASUREMENT_REPORT_ALIGNMENT.get(
                        selection_id,
                        {
                            "priority": 100,
                            "supported_metrics": [],
                            "metric_to_variable": {},
                        },
                    )
                )
            selection_payloads[selection_id] = selection_payload
        slots[slot] = {
            "id": slot,
            "label": master_entry["label"],
            "symbol": master_entry["symbol"],
            "selection_mode": master_entry["selection_mode"],
            "required": bool(master_entry["required"]),
            "ui_selectable_implementations": list(allowed),
            "selections": selection_payloads,
        }
    return {
        "version": OPERATOR_BASIS_REGISTRY_VERSION,
        "slots": slots,
    }


OPERATOR_BASIS_REGISTRY: dict[str, Any] = _build_registry()

_REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = ("version", "slots")
_REQUIRED_SLOT_KEYS: tuple[str, ...] = (
    "id",
    "label",
    "symbol",
    "selection_mode",
    "required",
    "ui_selectable_implementations",
    "selections",
)
_REQUIRED_SELECTION_KEYS: tuple[str, ...] = (
    "id",
    "label",
    "params_schema",
    "internal_builder_family",
    "ui_visible",
)


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OperatorBasisRegistryValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperatorBasisRegistryValidationError(f"{label} must be a non-empty string.")
    return value


def _require_bool(value: Any, label: str) -> None:
    if not isinstance(value, bool):
        raise OperatorBasisRegistryValidationError(f"{label} must be boolean.")


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise OperatorBasisRegistryValidationError(f"{label} must be a list of strings.")
    out: list[str] = []
    for idx, item in enumerate(value):
        out.append(_require_non_empty_string(item, f"{label}[{idx}]"))
    return out


def validate_operator_basis_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate basis-operator selection registry contract."""
    payload = deepcopy(OPERATOR_BASIS_REGISTRY if registry is None else registry)
    root = _require_dict(payload, "operator_basis_registry")

    for key in _REQUIRED_TOP_LEVEL_KEYS:
        if key not in root:
            raise OperatorBasisRegistryValidationError(
                f"operator_basis_registry missing required key: {key}"
            )

    _require_non_empty_string(root.get("version"), "operator_basis_registry.version")
    slots = _require_dict(root.get("slots"), "operator_basis_registry.slots")

    expected_slots = set(REQUIRED_OPERATOR_BASIS_SLOTS)
    slot_keys = set(slots.keys())
    if slot_keys != expected_slots:
        missing = sorted(expected_slots - slot_keys)
        extra = sorted(slot_keys - expected_slots)
        detail_parts: list[str] = []
        if missing:
            detail_parts.append(f"missing slots: {', '.join(missing)}")
        if extra:
            detail_parts.append(f"unexpected slots: {', '.join(extra)}")
        raise OperatorBasisRegistryValidationError(
            "operator_basis_registry.slots must match required basis slots exactly"
            + (f" ({'; '.join(detail_parts)})" if detail_parts else "")
        )

    for slot_key in REQUIRED_OPERATOR_BASIS_SLOTS:
        slot = _require_dict(slots.get(slot_key), f"operator_basis_registry.slots.{slot_key}")
        for key in _REQUIRED_SLOT_KEYS:
            if key not in slot:
                raise OperatorBasisRegistryValidationError(
                    f"operator_basis_registry.slots.{slot_key} missing required key: {key}"
                )
        slot_id = _require_non_empty_string(
            slot.get("id"), f"operator_basis_registry.slots.{slot_key}.id"
        )
        if slot_id != slot_key:
            raise OperatorBasisRegistryValidationError(
                f"operator_basis_registry.slots.{slot_key}.id must match slot key '{slot_key}'."
            )
        _require_non_empty_string(
            slot.get("label"),
            f"operator_basis_registry.slots.{slot_key}.label",
        )
        _require_non_empty_string(
            slot.get("symbol"),
            f"operator_basis_registry.slots.{slot_key}.symbol",
        )
        selection_mode = _require_non_empty_string(
            slot.get("selection_mode"),
            f"operator_basis_registry.slots.{slot_key}.selection_mode",
        )
        if selection_mode not in {"single", "multi"}:
            raise OperatorBasisRegistryValidationError(
                f"operator_basis_registry.slots.{slot_key}.selection_mode must be 'single' or 'multi'."
            )
        _require_bool(
            slot.get("required"),
            f"operator_basis_registry.slots.{slot_key}.required",
        )
        ui_selectables = _require_string_list(
            slot.get("ui_selectable_implementations"),
            f"operator_basis_registry.slots.{slot_key}.ui_selectable_implementations",
        )
        selections = _require_dict(
            slot.get("selections"),
            f"operator_basis_registry.slots.{slot_key}.selections",
        )
        allowed_master = set(OPERATOR_BASIS_MASTER_TABLE[slot_key]["allowed_selections"])
        if set(selections.keys()) != allowed_master:
            raise OperatorBasisRegistryValidationError(
                f"operator_basis_registry.slots.{slot_key}.selections must match master-table allowed selections."
            )
        if set(ui_selectables) != allowed_master:
            raise OperatorBasisRegistryValidationError(
                f"operator_basis_registry.slots.{slot_key}.ui_selectable_implementations must match master-table allowed selections."
            )

        for selection_key in sorted(selections.keys()):
            selection = _require_dict(
                selections.get(selection_key),
                f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}",
            )
            for key in _REQUIRED_SELECTION_KEYS:
                if key not in selection:
                    raise OperatorBasisRegistryValidationError(
                        f"operator_basis_registry.slots.{slot_key}.selections.{selection_key} missing required key: {key}"
                    )
            selection_id = _require_non_empty_string(
                selection.get("id"),
                f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.id",
            )
            if selection_id != selection_key:
                raise OperatorBasisRegistryValidationError(
                    f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.id must match selection key '{selection_key}'."
                )
            _require_non_empty_string(
                selection.get("label"),
                f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.label",
            )
            params_schema = selection.get("params_schema")
            _require_dict(
                params_schema,
                f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.params_schema",
            )
            internal_builder_family = _require_non_empty_string(
                selection.get("internal_builder_family"),
                f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.internal_builder_family",
            )
            expected_family = _SLOT_TO_BUILDER_FAMILY[slot_key]
            if internal_builder_family != expected_family:
                raise OperatorBasisRegistryValidationError(
                    f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.internal_builder_family "
                    f"must be '{expected_family}'."
                )
            _require_bool(
                selection.get("ui_visible"),
                f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.ui_visible",
            )
            if slot_key == "m":
                report_alignment = _require_dict(
                    selection.get("report_alignment"),
                    f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.report_alignment",
                )
                priority = report_alignment.get("priority")
                if not isinstance(priority, int):
                    raise OperatorBasisRegistryValidationError(
                        f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.report_alignment.priority must be int."
                    )
                supported_metrics = _require_string_list(
                    report_alignment.get("supported_metrics"),
                    f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.report_alignment.supported_metrics",
                )
                metric_to_variable = _require_dict(
                    report_alignment.get("metric_to_variable"),
                    f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.report_alignment.metric_to_variable",
                )
                for metric_name in metric_to_variable.keys():
                    _require_non_empty_string(
                        metric_name,
                        f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.report_alignment.metric_to_variable.key",
                    )
                for variable_id in metric_to_variable.values():
                    if variable_id is None:
                        continue
                    _require_non_empty_string(
                        variable_id,
                        f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.report_alignment.metric_to_variable.value",
                    )
                invalid_metric_links = sorted(
                    metric_name for metric_name in metric_to_variable.keys() if metric_name not in set(supported_metrics)
                )
                if invalid_metric_links:
                    raise OperatorBasisRegistryValidationError(
                        f"operator_basis_registry.slots.{slot_key}.selections.{selection_key}.report_alignment.metric_to_variable "
                        f"references metrics not present in supported_metrics: {', '.join(invalid_metric_links)}"
                    )

    return payload


def get_operator_basis_registry() -> dict[str, Any]:
    """Return validated deep copy of basis-operator registry."""
    return validate_operator_basis_registry(OPERATOR_BASIS_REGISTRY)


def list_operator_basis_registry_slots() -> tuple[str, ...]:
    """Return stable slot ordering."""
    payload = get_operator_basis_registry()
    return tuple(sorted(payload["slots"].keys()))


def list_ui_selectable_implementations(slot: str) -> tuple[str, ...]:
    """Return all UI-selectable implementations for a basis slot."""
    slot_key = _require_non_empty_string(slot, "slot")
    payload = get_operator_basis_registry()
    slots = payload["slots"]
    if slot_key not in slots:
        available = ", ".join(sorted(slots.keys()))
        raise KeyError(f"Unknown basis slot '{slot_key}'. Available slots: {available}")
    values = slots[slot_key]["ui_selectable_implementations"]
    return tuple(values)


def get_operator_selection_contract(slot: str, selection: str) -> dict[str, Any]:
    """Resolve one selection contract for a slot."""
    slot_key = _require_non_empty_string(slot, "slot")
    selection_key = _require_non_empty_string(selection, "selection")
    payload = get_operator_basis_registry()
    slots = payload["slots"]
    if slot_key not in slots:
        available_slots = ", ".join(sorted(slots.keys()))
        raise KeyError(f"Unknown basis slot '{slot_key}'. Available slots: {available_slots}")
    selections = slots[slot_key]["selections"]
    if selection_key not in selections:
        available = ", ".join(sorted(selections.keys()))
        raise KeyError(
            f"Unknown selection '{selection_key}' for slot '{slot_key}'. Available selections: {available}"
        )
    return deepcopy(selections[selection_key])


def get_internal_builder_family(slot: str, selection: str) -> str:
    """Resolve builder-family routing metadata for a slot selection."""
    selection_payload = get_operator_selection_contract(slot, selection)
    return selection_payload["internal_builder_family"]


def get_measurement_readout_contract(selection: str) -> dict[str, Any]:
    """Resolve report-alignment metadata for an `m` selection id."""
    payload = get_operator_selection_contract("m", selection)
    report_alignment = payload.get("report_alignment")
    if not isinstance(report_alignment, dict):
        raise KeyError(f"Measurement readout '{selection}' has no report_alignment metadata.")
    return deepcopy(report_alignment)


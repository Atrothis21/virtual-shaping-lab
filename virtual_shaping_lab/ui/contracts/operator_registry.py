"""Canonical operator registry contract for V3 UI explainability surfaces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.trialstate_registry import list_trialstate_field_ids


class OperatorRegistryValidationError(ValueError):
    """Raised when operator registry contract validation fails."""


OPERATOR_REGISTRY_VERSION = "3.0"

REQUIRED_OPERATOR_FAMILIES: tuple[str, ...] = (
    "representation",
    "prediction",
    "learning_signal",
    "update",
    "attention",
    "policy",
    "evaluation",
)

REQUIRED_OPERATORS: tuple[str, ...] = (
    "phi",
    "p",
    "delta",
    "w",
)


OPERATOR_REGISTRY: dict[str, Any] = {
    "version": OPERATOR_REGISTRY_VERSION,
    "families": {
        "representation": {
            "label": "Representation",
            "description": "Operators mapping stimuli into internal state features.",
        },
        "prediction": {
            "label": "Prediction",
            "description": "Operators that compute expected outcomes or values.",
        },
        "learning_signal": {
            "label": "Learning Signal",
            "description": "Operators computing discrepancy/teaching signals.",
        },
        "update": {
            "label": "Update",
            "description": "Operators that change internal learned parameters.",
        },
        "attention": {
            "label": "Attention / Associability",
            "description": "Operators that modulate learning sensitivity.",
        },
        "policy": {
            "label": "Policy",
            "description": "Operators mapping value/prediction to action selection.",
        },
        "evaluation": {
            "label": "Evaluation",
            "description": "Operators producing outputs/readouts for explainability.",
        },
    },
    "ui_conventions": {
        "default_reveal_order": ["intuition", "mechanism", "operator_view", "algebra"],
        "read_only_in_preset_mode": True,
    },
    "operators": {
        "phi": {
            "id": "phi",
            "symbol": "Phi",
            "name": "Representation",
            "family": "representation",
            "stage_index": 1,
            "status": {
                "preset_editable": False,
                "builder_editable": False,
                "expert_visible": True,
            },
            "pedagogy": {
                "intuition": "Encodes presented cues into internal state.",
                "mechanism": "Transforms stimulus input to representational state features.",
                "operator_view": "Representation operator writing state features.",
                "algebra": "Phi : stimulus -> state",
            },
            "runtime": {
                "input_fields": ["stimulus"],
                "output_fields": ["state"],
                "reads_trialstate": ["stimulus"],
                "writes_trialstate": ["state"],
                "required_upstream": [],
                "typical_downstream": ["p"],
            },
            "ui": {
                "short_label": "Representation",
                "node_label": "Phi",
                "tooltip": "Encodes stimulus into state features.",
                "badge_text": "Core",
                "show_in_card_tags": False,
            },
        },
        "p": {
            "id": "p",
            "symbol": "P",
            "name": "Prediction",
            "family": "prediction",
            "stage_index": 2,
            "status": {
                "preset_editable": False,
                "builder_editable": False,
                "expert_visible": True,
            },
            "pedagogy": {
                "intuition": "Computes expected outcomes from state and weights.",
                "mechanism": "Reads current state and learned parameters to estimate outcome.",
                "operator_view": "Prediction operator producing predicted outcome.",
                "algebra": "P : (state, weights) -> prediction",
            },
            "runtime": {
                "input_fields": ["state", "weights"],
                "output_fields": ["prediction"],
                "reads_trialstate": ["state", "weights"],
                "writes_trialstate": ["prediction"],
                "required_upstream": ["phi"],
                "typical_downstream": ["delta"],
            },
            "ui": {
                "short_label": "Prediction",
                "node_label": "P",
                "tooltip": "Computes expected outcome.",
                "badge_text": "Core",
                "show_in_card_tags": True,
            },
        },
        "delta": {
            "id": "delta",
            "symbol": "Delta",
            "name": "Prediction Error",
            "family": "learning_signal",
            "stage_index": 3,
            "status": {
                "preset_editable": False,
                "builder_editable": False,
                "expert_visible": True,
            },
            "pedagogy": {
                "intuition": "Measures mismatch between prediction and outcome.",
                "mechanism": "Computes discrepancy teaching signal.",
                "operator_view": "Error operator writing prediction error.",
                "algebra": "Delta = outcome - prediction",
            },
            "runtime": {
                "input_fields": ["prediction", "outcome"],
                "output_fields": ["error"],
                "reads_trialstate": ["prediction", "outcome"],
                "writes_trialstate": ["error"],
                "required_upstream": ["p"],
                "typical_downstream": ["w", "a"],
            },
            "ui": {
                "short_label": "Prediction Error",
                "node_label": "Delta",
                "tooltip": "Computes teaching signal from mismatch.",
                "badge_text": "Core",
                "show_in_card_tags": True,
            },
        },
        "w": {
            "id": "w",
            "symbol": "W",
            "name": "Update",
            "family": "update",
            "stage_index": 4,
            "status": {
                "preset_editable": False,
                "builder_editable": False,
                "expert_visible": True,
            },
            "pedagogy": {
                "intuition": "Applies learning update to parameters.",
                "mechanism": "Uses error/state/learning coefficients to adjust weights.",
                "operator_view": "Update operator writing learned parameters and update effects.",
                "algebra": "W_(t+1) = W_t + alpha * Delta",
            },
            "runtime": {
                "input_fields": ["error", "weights", "state"],
                "output_fields": ["weights", "weight_delta"],
                "reads_trialstate": ["error", "weights", "state"],
                "writes_trialstate": ["weights", "weight_delta"],
                "required_upstream": ["delta"],
                "typical_downstream": ["m"],
            },
            "ui": {
                "short_label": "Update",
                "node_label": "W",
                "tooltip": "Applies learning rule update.",
                "badge_text": "Core",
                "show_in_card_tags": True,
            },
        },
        "a": {
            "id": "a",
            "symbol": "A",
            "name": "Attention / Associability",
            "family": "attention",
            "stage_index": 3,
            "status": {
                "preset_editable": False,
                "builder_editable": True,
                "expert_visible": True,
            },
            "pedagogy": {
                "intuition": "Modulates how learnable cues are.",
                "mechanism": "Computes associability from recent uncertainty/predictiveness.",
                "operator_view": "Attention operator writing associability field.",
                "algebra": "A_t = f(error_t, history_t)",
            },
            "runtime": {
                "input_fields": ["error", "state"],
                "output_fields": ["associability"],
                "reads_trialstate": ["error", "state"],
                "writes_trialstate": ["associability"],
                "required_upstream": ["delta"],
                "typical_downstream": ["w"],
            },
            "ui": {
                "short_label": "Attention",
                "node_label": "A",
                "tooltip": "Modulates associability.",
                "badge_text": "Extended",
                "show_in_card_tags": True,
            },
        },
        "pi": {
            "id": "pi",
            "symbol": "Pi",
            "name": "Policy",
            "family": "policy",
            "stage_index": 5,
            "status": {
                "preset_editable": False,
                "builder_editable": True,
                "expert_visible": True,
            },
            "pedagogy": {
                "intuition": "Selects an action from available options.",
                "mechanism": "Maps values/predictions into sampled or chosen action.",
                "operator_view": "Policy operator writing selected action.",
                "algebra": "Pi : value -> selected_action",
            },
            "runtime": {
                "input_fields": ["prediction"],
                "output_fields": ["selected_action"],
                "reads_trialstate": ["prediction"],
                "writes_trialstate": ["selected_action"],
                "required_upstream": ["p"],
                "typical_downstream": ["m"],
            },
            "ui": {
                "short_label": "Policy",
                "node_label": "Pi",
                "tooltip": "Selects action from policy.",
                "badge_text": "Policy",
                "show_in_card_tags": False,
            },
        },
        "m": {
            "id": "m",
            "symbol": "M",
            "name": "Measure",
            "family": "evaluation",
            "stage_index": 6,
            "status": {
                "preset_editable": False,
                "builder_editable": False,
                "expert_visible": True,
            },
            "pedagogy": {
                "intuition": "Produces behavioral readouts for plotting/reporting.",
                "mechanism": "Aggregates current trial fields into explainable outputs.",
                "operator_view": "Evaluation operator writing response/readout fields.",
                "algebra": "M : trial_state -> readouts",
            },
            "runtime": {
                "input_fields": ["prediction", "error", "weights", "selected_action"],
                "output_fields": ["response_strength"],
                "reads_trialstate": ["prediction", "error", "weights", "selected_action", "trial_index", "phase_name"],
                "writes_trialstate": ["response_strength"],
                "required_upstream": ["w"],
                "typical_downstream": [],
            },
            "ui": {
                "short_label": "Measure",
                "node_label": "M",
                "tooltip": "Produces reportable behavioral variables.",
                "badge_text": "Output",
                "show_in_card_tags": False,
            },
        },
    },
}


_REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = ("version", "families", "ui_conventions", "operators")
_REQUIRED_OPERATOR_KEYS: tuple[str, ...] = (
    "id",
    "symbol",
    "name",
    "family",
    "stage_index",
    "status",
    "pedagogy",
    "runtime",
    "ui",
)
_REQUIRED_STATUS_KEYS: tuple[str, ...] = ("preset_editable", "builder_editable", "expert_visible")
_REQUIRED_PEDAGOGY_KEYS: tuple[str, ...] = ("intuition", "mechanism", "operator_view", "algebra")
_REQUIRED_RUNTIME_KEYS: tuple[str, ...] = (
    "input_fields",
    "output_fields",
    "reads_trialstate",
    "writes_trialstate",
    "required_upstream",
    "typical_downstream",
)
_REQUIRED_UI_KEYS: tuple[str, ...] = ("short_label", "node_label", "tooltip", "badge_text", "show_in_card_tags")


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OperatorRegistryValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperatorRegistryValidationError(f"{label} must be a non-empty string.")
    return value


def _require_bool(value: Any, label: str) -> None:
    if not isinstance(value, bool):
        raise OperatorRegistryValidationError(f"{label} must be boolean.")


def _require_int(value: Any, label: str) -> int:
    if not isinstance(value, int):
        raise OperatorRegistryValidationError(f"{label} must be an integer.")
    return value


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise OperatorRegistryValidationError(f"{label} must be a list of strings.")
    out: list[str] = []
    for idx, item in enumerate(value):
        out.append(_require_non_empty_string(item, f"{label}[{idx}]"))
    return out


def validate_operator_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate operator registry contract and TrialState field cross-references."""
    payload = deepcopy(OPERATOR_REGISTRY if registry is None else registry)
    root = _require_dict(payload, "operator_registry")

    for key in _REQUIRED_TOP_LEVEL_KEYS:
        if key not in root:
            raise OperatorRegistryValidationError(f"operator_registry missing required key: {key}")

    _require_non_empty_string(root.get("version"), "operator_registry.version")
    families = _require_dict(root.get("families"), "operator_registry.families")
    _require_dict(root.get("ui_conventions"), "operator_registry.ui_conventions")
    operators = _require_dict(root.get("operators"), "operator_registry.operators")

    for family_key in REQUIRED_OPERATOR_FAMILIES:
        if family_key not in families:
            raise OperatorRegistryValidationError(
                f"operator_registry.families missing required family: {family_key}"
            )
        fam = _require_dict(families[family_key], f"operator_registry.families.{family_key}")
        _require_non_empty_string(fam.get("label"), f"operator_registry.families.{family_key}.label")
        _require_non_empty_string(fam.get("description"), f"operator_registry.families.{family_key}.description")

    trialstate_fields = set(list_trialstate_field_ids())
    operator_ids = set(operators.keys())

    seen_ids: set[str] = set()
    for op_key, raw_op in operators.items():
        op = _require_dict(raw_op, f"operator_registry.operators.{op_key}")
        for key in _REQUIRED_OPERATOR_KEYS:
            if key not in op:
                raise OperatorRegistryValidationError(
                    f"operator_registry.operators.{op_key} missing required key: {key}"
                )
        op_id = _require_non_empty_string(op.get("id"), f"operator_registry.operators.{op_key}.id")
        if op_id in seen_ids:
            raise OperatorRegistryValidationError(f"operator_registry has duplicate operator id: {op_id}")
        seen_ids.add(op_id)
        if op_id != op_key:
            raise OperatorRegistryValidationError(
                f"operator_registry.operators.{op_key}.id must match operator key '{op_key}'."
            )
        family = _require_non_empty_string(op.get("family"), f"operator_registry.operators.{op_key}.family")
        if family not in families:
            raise OperatorRegistryValidationError(
                f"operator_registry.operators.{op_key}.family references unknown family: {family}"
            )
        stage_index = _require_int(op.get("stage_index"), f"operator_registry.operators.{op_key}.stage_index")
        if stage_index <= 0:
            raise OperatorRegistryValidationError(
                f"operator_registry.operators.{op_key}.stage_index must be > 0."
            )

        status = _require_dict(op.get("status"), f"operator_registry.operators.{op_key}.status")
        for key in _REQUIRED_STATUS_KEYS:
            if key not in status:
                raise OperatorRegistryValidationError(
                    f"operator_registry.operators.{op_key}.status missing required key: {key}"
                )
            _require_bool(status.get(key), f"operator_registry.operators.{op_key}.status.{key}")

        pedagogy = _require_dict(op.get("pedagogy"), f"operator_registry.operators.{op_key}.pedagogy")
        for key in _REQUIRED_PEDAGOGY_KEYS:
            _require_non_empty_string(
                pedagogy.get(key), f"operator_registry.operators.{op_key}.pedagogy.{key}"
            )

        runtime = _require_dict(op.get("runtime"), f"operator_registry.operators.{op_key}.runtime")
        for key in _REQUIRED_RUNTIME_KEYS:
            if key not in runtime:
                raise OperatorRegistryValidationError(
                    f"operator_registry.operators.{op_key}.runtime missing required key: {key}"
                )
        _require_string_list(runtime.get("input_fields"), f"operator_registry.operators.{op_key}.runtime.input_fields")
        _require_string_list(
            runtime.get("output_fields"), f"operator_registry.operators.{op_key}.runtime.output_fields"
        )
        reads = _require_string_list(
            runtime.get("reads_trialstate"), f"operator_registry.operators.{op_key}.runtime.reads_trialstate"
        )
        writes = _require_string_list(
            runtime.get("writes_trialstate"), f"operator_registry.operators.{op_key}.runtime.writes_trialstate"
        )
        upstream = _require_string_list(
            runtime.get("required_upstream"), f"operator_registry.operators.{op_key}.runtime.required_upstream"
        )
        downstream = _require_string_list(
            runtime.get("typical_downstream"), f"operator_registry.operators.{op_key}.runtime.typical_downstream"
        )

        for field in reads:
            if field not in trialstate_fields:
                raise OperatorRegistryValidationError(
                    f"operator_registry.operators.{op_key}.runtime.reads_trialstate "
                    f"references unknown TrialState field: {field}"
                )
        for field in writes:
            if field not in trialstate_fields:
                raise OperatorRegistryValidationError(
                    f"operator_registry.operators.{op_key}.runtime.writes_trialstate "
                    f"references unknown TrialState field: {field}"
                )
        for ref in upstream:
            if ref not in operator_ids:
                raise OperatorRegistryValidationError(
                    f"operator_registry.operators.{op_key}.runtime.required_upstream "
                    f"references unknown operator id: {ref}"
                )
        for ref in downstream:
            if ref not in operator_ids:
                raise OperatorRegistryValidationError(
                    f"operator_registry.operators.{op_key}.runtime.typical_downstream "
                    f"references unknown operator id: {ref}"
                )

        ui = _require_dict(op.get("ui"), f"operator_registry.operators.{op_key}.ui")
        for key in _REQUIRED_UI_KEYS:
            if key not in ui:
                raise OperatorRegistryValidationError(
                    f"operator_registry.operators.{op_key}.ui missing required key: {key}"
                )
        _require_non_empty_string(ui.get("short_label"), f"operator_registry.operators.{op_key}.ui.short_label")
        _require_non_empty_string(ui.get("node_label"), f"operator_registry.operators.{op_key}.ui.node_label")
        _require_non_empty_string(ui.get("tooltip"), f"operator_registry.operators.{op_key}.ui.tooltip")
        _require_non_empty_string(ui.get("badge_text"), f"operator_registry.operators.{op_key}.ui.badge_text")
        _require_bool(ui.get("show_in_card_tags"), f"operator_registry.operators.{op_key}.ui.show_in_card_tags")

    for operator in REQUIRED_OPERATORS:
        if operator not in operators:
            raise OperatorRegistryValidationError(
                f"operator_registry.operators missing required baseline operator: {operator}"
            )

    return payload


def get_operator_registry() -> dict[str, Any]:
    """Return validated deep-copied operator registry."""
    return validate_operator_registry(OPERATOR_REGISTRY)


def list_operator_ids() -> tuple[str, ...]:
    """Return stable sorted operator IDs."""
    payload = get_operator_registry()
    return tuple(sorted(payload["operators"].keys()))


def get_operator(operator_id: str) -> dict[str, Any]:
    """Resolve a single operator contract by operator ID."""
    key = _require_non_empty_string(operator_id, "operator_id")
    payload = get_operator_registry()
    operators = payload["operators"]
    if key not in operators:
        available = ", ".join(sorted(operators.keys()))
        raise KeyError(f"Unknown operator '{key}'. Available operators: {available}")
    return deepcopy(operators[key])


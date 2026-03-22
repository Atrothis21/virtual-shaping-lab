"""Canonical dependent-variable registry contract for V3 UI/report surfaces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.operator_registry import list_operator_ids
from ui.contracts.trialstate_registry import list_trialstate_field_ids


class DependentVariableRegistryValidationError(ValueError):
    """Raised when dependent-variable registry validation fails."""


DEPENDENT_VARIABLE_REGISTRY_VERSION = "3.0"

REQUIRED_DEPENDENT_VARIABLE_CATEGORIES: tuple[str, ...] = (
    "behavioral",
    "learning",
    "mechanistic",
    "action",
    "memory_attention",
)

REQUIRED_DEPENDENT_VARIABLES: tuple[str, ...] = (
    "associative_strength",
    "predicted_outcome",
    "prediction_error",
    "response_strength",
    "response_probability",
    "action_counts",
)


DEPENDENT_VARIABLE_REGISTRY: dict[str, Any] = {
    "version": DEPENDENT_VARIABLE_REGISTRY_VERSION,
    "categories": {
        "behavioral": {"label": "Behavioral Outputs", "description": "Publication-style readouts."},
        "learning": {"label": "Learning Dynamics", "description": "Learning over trial/phase progression."},
        "mechanistic": {"label": "Mechanistic Traces", "description": "Internal explanatory traces."},
        "action": {"label": "Action / Policy Outputs", "description": "Action selection and allocation."},
        "memory_attention": {"label": "Attention / Memory", "description": "Associability/trace dynamics."},
    },
    "display_policies": {
        "results_default_priority": ["behavioral", "learning", "mechanistic"],
        "preset_results_focus": "dependent_variables_first",
        "expert_mode_allows_mechanistic_only": True,
    },
    "variables": {
        "associative_strength": {
            "id": "associative_strength",
            "label": "Associative Strength",
            "category": "learning",
            "pedagogy": {
                "plain_language": "How strongly cue and outcome are linked.",
                "behavioral_interpretation": "Higher values imply stronger learned expectation.",
                "mechanistic_interpretation": "Read from learned weights/values.",
            },
            "runtime": {"kind": "direct_field", "source_fields": ["weights"], "derived_formula": None, "aggregator": "identity"},
            "visualization": {
                "default_chart": "line",
                "x_axis": "trial_index",
                "y_axis_label": "Associative Strength",
                "supports_phase_shading": True,
                "supports_trial_hover": True,
            },
            "visibility": {"results_default": True, "report_default": True, "preset_overlay": False, "expert_mode": True},
            "explainability": {
                "hover_fields": ["weights", "error", "weight_delta"],
                "related_operators": ["w", "p"],
                "related_trialstate_fields": ["weights"],
            },
            "semantics": {"units": "learned_parameter", "expected_range": [-1.0, 1.0], "higher_is_more": "stronger_association", "phase_comparison_friendly": True},
        },
        "predicted_outcome": {
            "id": "predicted_outcome",
            "label": "Predicted Outcome",
            "category": "learning",
            "pedagogy": {
                "plain_language": "Expected outcome before feedback arrives.",
                "behavioral_interpretation": "Tracks expected reinforcement over trials.",
                "mechanistic_interpretation": "Read from prediction outputs.",
            },
            "runtime": {"kind": "direct_field", "source_fields": ["prediction"], "derived_formula": None, "aggregator": "identity"},
            "visualization": {
                "default_chart": "line",
                "x_axis": "trial_index",
                "y_axis_label": "Predicted Outcome",
                "supports_phase_shading": True,
                "supports_trial_hover": True,
            },
            "visibility": {"results_default": True, "report_default": True, "preset_overlay": False, "expert_mode": True},
            "explainability": {
                "hover_fields": ["prediction", "outcome", "error"],
                "related_operators": ["p", "delta"],
                "related_trialstate_fields": ["prediction"],
            },
            "semantics": {"units": "expected_outcome", "expected_range": [-1.0, 1.0], "higher_is_more": "greater_expected_outcome", "phase_comparison_friendly": True},
        },
        "prediction_error": {
            "id": "prediction_error",
            "label": "Prediction Error",
            "category": "mechanistic",
            "pedagogy": {
                "plain_language": "How wrong the model was on each trial.",
                "behavioral_interpretation": "Large values indicate stronger mismatch.",
                "mechanistic_interpretation": "Read from error/discrepancy outputs.",
            },
            "runtime": {"kind": "direct_field", "source_fields": ["error"], "derived_formula": None, "aggregator": "identity"},
            "visualization": {
                "default_chart": "line",
                "x_axis": "trial_index",
                "y_axis_label": "Prediction Error",
                "supports_phase_shading": True,
                "supports_trial_hover": True,
            },
            "visibility": {"results_default": True, "report_default": True, "preset_overlay": False, "expert_mode": True},
            "explainability": {
                "hover_fields": ["prediction", "outcome", "error"],
                "related_operators": ["delta"],
                "related_trialstate_fields": ["error"],
            },
            "semantics": {"units": "discrepancy_signal", "expected_range": [-2.0, 2.0], "higher_is_more": "greater_mismatch", "phase_comparison_friendly": True},
        },
        "response_strength": {
            "id": "response_strength",
            "label": "Response Strength",
            "category": "behavioral",
            "pedagogy": {
                "plain_language": "How strongly behavior is expressed.",
                "behavioral_interpretation": "Higher values indicate stronger responding.",
                "mechanistic_interpretation": "Read from evaluation/readout state.",
            },
            "runtime": {"kind": "direct_or_derived", "source_fields": ["response_strength", "prediction", "selected_action"], "derived_formula": None, "aggregator": "identity"},
            "visualization": {
                "default_chart": "line",
                "x_axis": "trial_index",
                "y_axis_label": "Response Strength",
                "supports_phase_shading": True,
                "supports_trial_hover": True,
            },
            "visibility": {"results_default": True, "report_default": True, "preset_overlay": False, "expert_mode": True},
            "explainability": {
                "hover_fields": ["response_strength", "prediction", "selected_action"],
                "related_operators": ["m", "pi"],
                "related_trialstate_fields": ["response_strength", "selected_action"],
            },
            "semantics": {"units": "behavioral_output", "expected_range": [0.0, 1.0], "higher_is_more": "stronger_response", "phase_comparison_friendly": True},
        },
        "response_probability": {
            "id": "response_probability",
            "label": "Response Probability",
            "category": "behavioral",
            "pedagogy": {
                "plain_language": "Probability that a response occurs.",
                "behavioral_interpretation": "Higher values imply more likely responding.",
                "mechanistic_interpretation": "Derived from selected actions/readouts.",
            },
            "runtime": {"kind": "derived", "source_fields": ["selected_action", "response_strength"], "derived_formula": "probability_of_target_response", "aggregator": "per_trial_or_binned"},
            "visualization": {
                "default_chart": "line",
                "x_axis": "trial_index",
                "y_axis_label": "Response Probability",
                "supports_phase_shading": True,
                "supports_trial_hover": True,
            },
            "visibility": {"results_default": True, "report_default": True, "preset_overlay": False, "expert_mode": True},
            "explainability": {
                "hover_fields": ["selected_action", "response_strength"],
                "related_operators": ["pi", "m"],
                "related_trialstate_fields": ["selected_action", "response_strength"],
            },
            "semantics": {"units": "probability", "expected_range": [0.0, 1.0], "higher_is_more": "more_likely_response", "phase_comparison_friendly": True},
        },
        "action_counts": {
            "id": "action_counts",
            "label": "Action Counts",
            "category": "action",
            "pedagogy": {
                "plain_language": "How often each action was selected.",
                "behavioral_interpretation": "Shows response allocation across actions.",
                "mechanistic_interpretation": "Aggregated from selected action outputs.",
            },
            "runtime": {"kind": "aggregated", "source_fields": ["selected_action"], "derived_formula": "count_actions_by_label", "aggregator": "count_by_action"},
            "visualization": {
                "default_chart": "bar",
                "x_axis": "action",
                "y_axis_label": "Count",
                "supports_phase_shading": False,
                "supports_trial_hover": False,
            },
            "visibility": {"results_default": True, "report_default": True, "preset_overlay": False, "expert_mode": True},
            "explainability": {
                "hover_fields": ["selected_action"],
                "related_operators": ["pi"],
                "related_trialstate_fields": ["selected_action"],
            },
            "semantics": {"units": "count", "expected_range": [0, None], "higher_is_more": "more_frequent_action", "phase_comparison_friendly": True},
        },
        "associability": {
            "id": "associability",
            "label": "Associability",
            "category": "memory_attention",
            "pedagogy": {
                "plain_language": "How learnable the cue currently is.",
                "behavioral_interpretation": "Higher values indicate greater learning sensitivity.",
                "mechanistic_interpretation": "Read from associability field.",
            },
            "runtime": {"kind": "direct_field", "source_fields": ["associability"], "derived_formula": None, "aggregator": "identity"},
            "visualization": {
                "default_chart": "line",
                "x_axis": "trial_index",
                "y_axis_label": "Associability",
                "supports_phase_shading": True,
                "supports_trial_hover": True,
            },
            "visibility": {"results_default": False, "report_default": False, "preset_overlay": False, "expert_mode": True},
            "explainability": {
                "hover_fields": ["associability", "error"],
                "related_operators": ["a", "w"],
                "related_trialstate_fields": ["associability"],
            },
            "semantics": {"units": "modulatory_factor", "expected_range": [0.0, 1.0], "higher_is_more": "greater_learning_sensitivity", "phase_comparison_friendly": True},
        },
    },
}


_REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = ("version", "categories", "display_policies", "variables")
_REQUIRED_VARIABLE_KEYS: tuple[str, ...] = ("id", "label", "category", "pedagogy", "runtime", "visualization", "visibility", "explainability", "semantics")
_REQUIRED_PEDAGOGY_KEYS: tuple[str, ...] = ("plain_language", "behavioral_interpretation", "mechanistic_interpretation")
_REQUIRED_RUNTIME_KEYS: tuple[str, ...] = ("kind", "source_fields", "derived_formula", "aggregator")
_REQUIRED_VISUALIZATION_KEYS: tuple[str, ...] = ("default_chart", "x_axis", "y_axis_label", "supports_phase_shading", "supports_trial_hover")
_REQUIRED_VISIBILITY_KEYS: tuple[str, ...] = ("results_default", "report_default", "preset_overlay", "expert_mode")
_REQUIRED_EXPLAINABILITY_KEYS: tuple[str, ...] = ("hover_fields", "related_operators", "related_trialstate_fields")
_REQUIRED_SEMANTICS_KEYS: tuple[str, ...] = ("units", "expected_range", "higher_is_more", "phase_comparison_friendly")


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DependentVariableRegistryValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DependentVariableRegistryValidationError(f"{label} must be a non-empty string.")
    return value


def _require_bool(value: Any, label: str) -> None:
    if not isinstance(value, bool):
        raise DependentVariableRegistryValidationError(f"{label} must be boolean.")


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise DependentVariableRegistryValidationError(f"{label} must be a list of strings.")
    out: list[str] = []
    for idx, item in enumerate(value):
        out.append(_require_non_empty_string(item, f"{label}[{idx}]"))
    return out


def validate_dependent_variable_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = deepcopy(DEPENDENT_VARIABLE_REGISTRY if registry is None else registry)
    root = _require_dict(payload, "dependent_variable_registry")
    for key in _REQUIRED_TOP_LEVEL_KEYS:
        if key not in root:
            raise DependentVariableRegistryValidationError(f"dependent_variable_registry missing required key: {key}")

    _require_non_empty_string(root.get("version"), "dependent_variable_registry.version")
    categories = _require_dict(root.get("categories"), "dependent_variable_registry.categories")
    _require_dict(root.get("display_policies"), "dependent_variable_registry.display_policies")
    variables = _require_dict(root.get("variables"), "dependent_variable_registry.variables")

    for category in REQUIRED_DEPENDENT_VARIABLE_CATEGORIES:
        if category not in categories:
            raise DependentVariableRegistryValidationError(
                f"dependent_variable_registry.categories missing required category: {category}"
            )

    trialstate_fields = set(list_trialstate_field_ids())
    operator_ids = set(list_operator_ids())
    seen_ids: set[str] = set()

    for key, raw_var in variables.items():
        var = _require_dict(raw_var, f"dependent_variable_registry.variables.{key}")
        for req_key in _REQUIRED_VARIABLE_KEYS:
            if req_key not in var:
                raise DependentVariableRegistryValidationError(
                    f"dependent_variable_registry.variables.{key} missing required key: {req_key}"
                )
        var_id = _require_non_empty_string(var.get("id"), f"dependent_variable_registry.variables.{key}.id")
        if var_id in seen_ids:
            raise DependentVariableRegistryValidationError(
                f"dependent_variable_registry has duplicate variable id: {var_id}"
            )
        seen_ids.add(var_id)
        if var_id != key:
            raise DependentVariableRegistryValidationError(
                f"dependent_variable_registry.variables.{key}.id must match variable key '{key}'."
            )

        category = _require_non_empty_string(var.get("category"), f"dependent_variable_registry.variables.{key}.category")
        if category not in categories:
            raise DependentVariableRegistryValidationError(
                f"dependent_variable_registry.variables.{key}.category references unknown category: {category}"
            )

        pedagogy = _require_dict(var.get("pedagogy"), f"dependent_variable_registry.variables.{key}.pedagogy")
        for p_key in _REQUIRED_PEDAGOGY_KEYS:
            _require_non_empty_string(pedagogy.get(p_key), f"dependent_variable_registry.variables.{key}.pedagogy.{p_key}")

        runtime = _require_dict(var.get("runtime"), f"dependent_variable_registry.variables.{key}.runtime")
        for r_key in _REQUIRED_RUNTIME_KEYS:
            if r_key not in runtime:
                raise DependentVariableRegistryValidationError(
                    f"dependent_variable_registry.variables.{key}.runtime missing required key: {r_key}"
                )
        _require_non_empty_string(runtime.get("kind"), f"dependent_variable_registry.variables.{key}.runtime.kind")
        _require_non_empty_string(runtime.get("aggregator"), f"dependent_variable_registry.variables.{key}.runtime.aggregator")
        source_fields = _require_string_list(runtime.get("source_fields"), f"dependent_variable_registry.variables.{key}.runtime.source_fields")
        for field in source_fields:
            if field not in trialstate_fields:
                raise DependentVariableRegistryValidationError(
                    f"dependent_variable_registry.variables.{key}.runtime.source_fields references unknown TrialState field: {field}"
                )

        visualization = _require_dict(var.get("visualization"), f"dependent_variable_registry.variables.{key}.visualization")
        for v_key in _REQUIRED_VISUALIZATION_KEYS:
            if v_key not in visualization:
                raise DependentVariableRegistryValidationError(
                    f"dependent_variable_registry.variables.{key}.visualization missing required key: {v_key}"
                )
        _require_bool(
            visualization.get("supports_phase_shading"),
            f"dependent_variable_registry.variables.{key}.visualization.supports_phase_shading",
        )
        _require_bool(
            visualization.get("supports_trial_hover"),
            f"dependent_variable_registry.variables.{key}.visualization.supports_trial_hover",
        )

        visibility = _require_dict(var.get("visibility"), f"dependent_variable_registry.variables.{key}.visibility")
        for vis_key in _REQUIRED_VISIBILITY_KEYS:
            if vis_key not in visibility:
                raise DependentVariableRegistryValidationError(
                    f"dependent_variable_registry.variables.{key}.visibility missing required key: {vis_key}"
                )
            _require_bool(visibility.get(vis_key), f"dependent_variable_registry.variables.{key}.visibility.{vis_key}")

        explainability = _require_dict(var.get("explainability"), f"dependent_variable_registry.variables.{key}.explainability")
        for e_key in _REQUIRED_EXPLAINABILITY_KEYS:
            if e_key not in explainability:
                raise DependentVariableRegistryValidationError(
                    f"dependent_variable_registry.variables.{key}.explainability missing required key: {e_key}"
                )
        hover_fields = _require_string_list(
            explainability.get("hover_fields"),
            f"dependent_variable_registry.variables.{key}.explainability.hover_fields",
        )
        related_operators = _require_string_list(
            explainability.get("related_operators"),
            f"dependent_variable_registry.variables.{key}.explainability.related_operators",
        )
        related_trialstate_fields = _require_string_list(
            explainability.get("related_trialstate_fields"),
            f"dependent_variable_registry.variables.{key}.explainability.related_trialstate_fields",
        )
        for field in hover_fields:
            if field not in trialstate_fields:
                raise DependentVariableRegistryValidationError(
                    f"dependent_variable_registry.variables.{key}.explainability.hover_fields references unknown TrialState field: {field}"
                )
        for field in related_trialstate_fields:
            if field not in trialstate_fields:
                raise DependentVariableRegistryValidationError(
                    f"dependent_variable_registry.variables.{key}.explainability.related_trialstate_fields references unknown TrialState field: {field}"
                )
        for op_id in related_operators:
            if op_id not in operator_ids:
                raise DependentVariableRegistryValidationError(
                    f"dependent_variable_registry.variables.{key}.explainability.related_operators references unknown operator id: {op_id}"
                )

        semantics = _require_dict(var.get("semantics"), f"dependent_variable_registry.variables.{key}.semantics")
        for s_key in _REQUIRED_SEMANTICS_KEYS:
            if s_key not in semantics:
                raise DependentVariableRegistryValidationError(
                    f"dependent_variable_registry.variables.{key}.semantics missing required key: {s_key}"
                )
        _require_bool(
            semantics.get("phase_comparison_friendly"),
            f"dependent_variable_registry.variables.{key}.semantics.phase_comparison_friendly",
        )
        expected_range = semantics.get("expected_range")
        if not isinstance(expected_range, list) or len(expected_range) != 2:
            raise DependentVariableRegistryValidationError(
                f"dependent_variable_registry.variables.{key}.semantics.expected_range must be a 2-item list."
            )

    for required in REQUIRED_DEPENDENT_VARIABLES:
        if required not in variables:
            raise DependentVariableRegistryValidationError(
                f"dependent_variable_registry.variables missing required baseline variable: {required}"
            )
    return payload


def get_dependent_variable_registry() -> dict[str, Any]:
    return validate_dependent_variable_registry(DEPENDENT_VARIABLE_REGISTRY)


def list_dependent_variable_ids() -> tuple[str, ...]:
    payload = get_dependent_variable_registry()
    return tuple(sorted(payload["variables"].keys()))


def get_dependent_variable(variable_id: str) -> dict[str, Any]:
    key = _require_non_empty_string(variable_id, "variable_id")
    payload = get_dependent_variable_registry()
    variables = payload["variables"]
    if key not in variables:
        available = ", ".join(sorted(variables.keys()))
        raise KeyError(f"Unknown dependent variable '{key}'. Available variables: {available}")
    return deepcopy(variables[key])


def validate_dependent_variable_ids(
    variable_ids: list[str] | tuple[str, ...],
    *,
    label: str = "variable_ids",
) -> tuple[str, ...]:
    if not isinstance(variable_ids, (list, tuple)):
        raise DependentVariableRegistryValidationError(f"{label} must be a list/tuple of variable IDs.")
    known = set(list_dependent_variable_ids())
    out: list[str] = []
    for idx, value in enumerate(variable_ids):
        key = _require_non_empty_string(value, f"{label}[{idx}]")
        if key not in known:
            raise DependentVariableRegistryValidationError(
                f"{label}[{idx}] references unknown dependent variable id: {key}"
            )
        out.append(key)
    return tuple(out)


def validate_preset_results_contract(results_contract: dict[str, Any]) -> dict[str, Any]:
    payload = _require_dict(results_contract, "results_contract")
    primary = validate_dependent_variable_ids(
        payload.get("primary_dependent_variables", []),
        label="results_contract.primary_dependent_variables",
    )
    secondary = validate_dependent_variable_ids(
        payload.get("secondary_dependent_variables", []),
        label="results_contract.secondary_dependent_variables",
    )
    graph_priority = validate_dependent_variable_ids(
        payload.get("graph_priority", []),
        label="results_contract.graph_priority",
    )
    out = deepcopy(payload)
    out["primary_dependent_variables"] = list(primary)
    out["secondary_dependent_variables"] = list(secondary)
    out["graph_priority"] = list(graph_priority)
    return out


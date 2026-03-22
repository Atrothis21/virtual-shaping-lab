"""Dependent-variable resolver layer shared by results and report surfaces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.dependent_variable_registry import (
    DependentVariableRegistryValidationError,
    get_dependent_variable_registry,
)


class DependentVariableResolverError(ValueError):
    """Raised when dependent-variable resolution fails."""


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DependentVariableResolverError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DependentVariableResolverError(f"{label} must be a non-empty string.")
    return value


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise DependentVariableResolverError(f"{label} must be boolean.")
    return value


def _resolve_from_registry_payload(
    variable_id: str,
    *,
    registry_payload: dict[str, Any],
    surface: str,
) -> dict[str, Any]:
    variables = _require_dict(
        registry_payload.get("variables"),
        "dependent_variable_registry.variables",
    )
    key = _require_non_empty_string(variable_id, "variable_id")
    variable = variables.get(key)
    if not isinstance(variable, dict):
        available = ", ".join(sorted(variables.keys()))
        raise KeyError(f"Unknown dependent variable '{key}'. Available variables: {available}")

    label = _require_non_empty_string(variable.get("label"), f"dependent_variable.{key}.label")
    category = _require_non_empty_string(variable.get("category"), f"dependent_variable.{key}.category")
    visualization = _require_dict(variable.get("visualization"), f"dependent_variable.{key}.visualization")
    visibility = _require_dict(variable.get("visibility"), f"dependent_variable.{key}.visibility")
    semantics = _require_dict(variable.get("semantics"), f"dependent_variable.{key}.semantics")
    pedagogy = _require_dict(variable.get("pedagogy"), f"dependent_variable.{key}.pedagogy")
    explainability = _require_dict(variable.get("explainability"), f"dependent_variable.{key}.explainability")

    if surface == "results":
        _require_bool(visibility.get("results_default"), f"dependent_variable.{key}.visibility.results_default")
    elif surface == "report":
        _require_bool(visibility.get("report_default"), f"dependent_variable.{key}.visibility.report_default")
    else:
        raise DependentVariableResolverError(f"Unknown surface '{surface}'.")

    chart = _require_non_empty_string(
        visualization.get("default_chart"),
        f"dependent_variable.{key}.visualization.default_chart",
    )
    y_axis = _require_non_empty_string(
        visualization.get("y_axis_label"),
        f"dependent_variable.{key}.visualization.y_axis_label",
    )
    _require_non_empty_string(semantics.get("units"), f"dependent_variable.{key}.semantics.units")
    _require_non_empty_string(
        pedagogy.get("plain_language"),
        f"dependent_variable.{key}.pedagogy.plain_language",
    )

    related_operators = explainability.get("related_operators")
    related_fields = explainability.get("related_trialstate_fields")
    if not isinstance(related_operators, list) or not isinstance(related_fields, list):
        raise DependentVariableResolverError(
            f"dependent_variable.{key}.explainability related operator/field links must be lists."
        )

    return {
        "id": key,
        "label": label,
        "category": category,
        "chart": chart,
        "y_axis_label": y_axis,
        "units": semantics.get("units"),
        "plain_language": pedagogy.get("plain_language"),
        "related_operators": [str(v) for v in related_operators],
        "related_trialstate_fields": [str(v) for v in related_fields],
        "visibility_default": bool(visibility["results_default"] if surface == "results" else visibility["report_default"]),
    }


def resolve_dependent_variable(
    variable_id: str,
    *,
    surface: str = "results",
) -> dict[str, Any]:
    try:
        registry = get_dependent_variable_registry()
    except DependentVariableRegistryValidationError as exc:
        raise DependentVariableResolverError(f"Registry validation failed: {exc}") from exc
    return _resolve_from_registry_payload(variable_id, registry_payload=registry, surface=surface)


def resolve_dependent_variable_from_registry_payload(
    variable_id: str,
    *,
    registry_payload: dict[str, Any],
    surface: str = "results",
) -> dict[str, Any]:
    return _resolve_from_registry_payload(variable_id, registry_payload=registry_payload, surface=surface)


def resolve_dependent_variables_for_surface(
    *,
    surface: str = "results",
) -> tuple[dict[str, Any], ...]:
    try:
        registry = get_dependent_variable_registry()
    except DependentVariableRegistryValidationError as exc:
        raise DependentVariableResolverError(f"Registry validation failed: {exc}") from exc
    variables = _require_dict(registry.get("variables"), "dependent_variable_registry.variables")
    resolved = [
        _resolve_from_registry_payload(variable_id, registry_payload=registry, surface=surface)
        for variable_id in sorted(variables.keys())
    ]
    return tuple(deepcopy(resolved))


def resolve_results_variable(variable_id: str) -> dict[str, Any]:
    return resolve_dependent_variable(variable_id, surface="results")


def resolve_report_variable(variable_id: str) -> dict[str, Any]:
    return resolve_dependent_variable(variable_id, surface="report")

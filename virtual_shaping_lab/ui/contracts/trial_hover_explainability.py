"""Trial-hover explainability contract resolved from UI registries."""

from __future__ import annotations

from typing import Any

from ui.contracts.dependent_variable_registry import get_dependent_variable
from ui.contracts.operator_registry import get_operator
from ui.contracts.trialstate_registry import get_trialstate_field


class TrialHoverExplainabilityError(ValueError):
    """Raised when trial-hover explainability contract generation fails."""


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TrialHoverExplainabilityError(f"{label} must be an object.")
    return value


def _field_label(field_id: str) -> str:
    try:
        field = get_trialstate_field(field_id)
        return str(field.get("label") or field_id)
    except Exception:
        return field_id


def _resolve_core_links(record: dict[str, Any]) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = []
    for field_id, label in (
        ("prediction", "Prediction"),
        ("outcome", "Outcome"),
        ("error", "Prediction Error"),
        ("weight_delta", "Update Effect"),
    ):
        if field_id in record and record.get(field_id) is not None:
            links.append(
                {
                    "field_id": field_id,
                    "label": label,
                    "value": record.get(field_id),
                }
            )
    return links


def build_trial_hover_explainability_panel(
    variable_id: str,
    *,
    trial_record: dict[str, Any],
) -> dict[str, Any]:
    record = _require_dict(trial_record, "trial_record")
    variable = get_dependent_variable(variable_id)

    explain = _require_dict(
        variable.get("explainability"),
        f"dependent_variable.{variable_id}.explainability",
    )
    related_fields = explain.get("related_trialstate_fields", [])
    related_operators = explain.get("related_operators", [])
    hover_fields = explain.get("hover_fields", [])
    if not isinstance(related_fields, list) or not isinstance(related_operators, list) or not isinstance(hover_fields, list):
        raise TrialHoverExplainabilityError(
            f"dependent_variable.{variable_id}.explainability fields must be lists."
        )

    field_resolution: list[dict[str, Any]] = []
    for field_id in hover_fields:
        key = str(field_id)
        field_resolution.append(
            {
                "field_id": key,
                "label": _field_label(key),
                "present": key in record and record.get(key) is not None,
                "value": record.get(key),
            }
        )

    operator_links: list[dict[str, Any]] = []
    for operator_id in related_operators:
        op = get_operator(str(operator_id))
        pedagogy = _require_dict(op.get("pedagogy"), f"operator.{operator_id}.pedagogy")
        runtime = _require_dict(op.get("runtime"), f"operator.{operator_id}.runtime")
        operator_links.append(
            {
                "id": op.get("id"),
                "symbol": op.get("symbol"),
                "name": op.get("name"),
                "stage_index": op.get("stage_index"),
                "operator_view": pedagogy.get("operator_view"),
                "algebra": pedagogy.get("algebra"),
                "reads_trialstate": list(runtime.get("reads_trialstate", [])),
                "writes_trialstate": list(runtime.get("writes_trialstate", [])),
            }
        )
    operator_links = sorted(operator_links, key=lambda item: int(item.get("stage_index") or 0))

    related_field_links = [
        {
            "field_id": str(field_id),
            "label": _field_label(str(field_id)),
            "present": str(field_id) in record and record.get(str(field_id)) is not None,
            "value": record.get(str(field_id)),
        }
        for field_id in related_fields
    ]

    core_links = _resolve_core_links(record)

    return {
        "variable_id": variable_id,
        "variable_label": variable.get("label"),
        "plain_language": _require_dict(variable.get("pedagogy"), f"dependent_variable.{variable_id}.pedagogy").get("plain_language"),
        "field_resolution": field_resolution,
        "related_trialstate_fields": related_field_links,
        "operator_links": operator_links,
        "core_links": core_links,
        "graceful_degradation": True,
    }


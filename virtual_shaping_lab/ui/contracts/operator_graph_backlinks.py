"""Operator-to-graph backlink contracts for explainability surfaces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.dependent_variable_registry import get_dependent_variable_registry
from ui.contracts.operator_registry import get_operator_registry
from ui.contracts.trialstate_registry import get_trialstate_field_registry


class OperatorGraphBacklinkError(ValueError):
    """Raised when operator graph backlink resolution fails."""


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OperatorGraphBacklinkError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperatorGraphBacklinkError(f"{label} must be a non-empty string.")
    return value


def _trialstate_label(field_id: str, trialstate_fields: dict[str, Any]) -> str:
    field = trialstate_fields.get(field_id)
    if isinstance(field, dict):
        label = field.get("label")
        if isinstance(label, str) and label.strip():
            return label
    return field_id


def _resolve_payloads() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    dependent = get_dependent_variable_registry()
    operators = get_operator_registry()
    trialstate = get_trialstate_field_registry()
    return dependent, operators, trialstate


def _resolve_operator_graph_backlinks_from_payloads(
    operator_id: str,
    *,
    dependent: dict[str, Any],
    operators: dict[str, Any],
    trialstate: dict[str, Any],
) -> dict[str, Any]:
    operator_key = _require_non_empty_string(operator_id, "operator_id")
    operator_map = _require_dict(operators.get("operators"), "operator_registry.operators")
    op = operator_map.get(operator_key)
    if not isinstance(op, dict):
        available = ", ".join(sorted(operator_map.keys()))
        raise KeyError(f"Unknown operator '{operator_key}'. Available operators: {available}")

    runtime = _require_dict(op.get("runtime"), f"operator_registry.operators.{operator_key}.runtime")
    reads = list(runtime.get("reads_trialstate", []))
    writes = list(runtime.get("writes_trialstate", []))
    io_fields = sorted(set(str(v) for v in reads + writes))

    variable_map = _require_dict(dependent.get("variables"), "dependent_variable_registry.variables")
    related_variables: list[dict[str, Any]] = []
    for variable_id, raw_var in variable_map.items():
        variable = _require_dict(raw_var, f"dependent_variable_registry.variables.{variable_id}")
        explain = _require_dict(variable.get("explainability"), f"dependent_variable_registry.variables.{variable_id}.explainability")
        related_ops = explain.get("related_operators", [])
        if not isinstance(related_ops, list):
            raise OperatorGraphBacklinkError(
                f"dependent_variable_registry.variables.{variable_id}.explainability.related_operators must be a list."
            )
        if operator_key not in [str(v) for v in related_ops]:
            continue
        related_fields = explain.get("related_trialstate_fields", [])
        if not isinstance(related_fields, list):
            raise OperatorGraphBacklinkError(
                f"dependent_variable_registry.variables.{variable_id}.explainability.related_trialstate_fields must be a list."
            )
        related_variables.append(
            {
                "id": variable_id,
                "label": variable.get("label"),
                "category": variable.get("category"),
                "related_trialstate_fields": [str(v) for v in related_fields],
                "trialstate_overlap": sorted(set(str(v) for v in related_fields).intersection(io_fields)),
            }
        )

    trialstate_fields = _require_dict(trialstate.get("fields"), "trialstate_registry.fields")
    trialstate_links = [
        {
            "id": field_id,
            "label": _trialstate_label(field_id, trialstate_fields),
            "mode": "read_write" if field_id in reads and field_id in writes else ("read" if field_id in reads else "write"),
        }
        for field_id in io_fields
    ]

    return {
        "operator": {
            "id": op.get("id"),
            "symbol": op.get("symbol"),
            "name": op.get("name"),
            "stage_index": op.get("stage_index"),
        },
        "graph_backlinks": sorted(related_variables, key=lambda item: str(item["id"])),
        "trialstate_links": trialstate_links,
    }


def resolve_operator_graph_backlinks(operator_id: str) -> dict[str, Any]:
    dependent, operators, trialstate = _resolve_payloads()
    return _resolve_operator_graph_backlinks_from_payloads(
        operator_id,
        dependent=dependent,
        operators=operators,
        trialstate=trialstate,
    )


def validate_operator_graph_backlink_integrity_from_payloads(
    *,
    dependent: dict[str, Any],
    operators: dict[str, Any],
    trialstate: dict[str, Any],
) -> None:
    operator_map = _require_dict(operators.get("operators"), "operator_registry.operators")
    variable_map = _require_dict(dependent.get("variables"), "dependent_variable_registry.variables")
    known_ops = set(operator_map.keys())

    for variable_id, raw_var in variable_map.items():
        variable = _require_dict(raw_var, f"dependent_variable_registry.variables.{variable_id}")
        explain = _require_dict(variable.get("explainability"), f"dependent_variable_registry.variables.{variable_id}.explainability")
        related_ops = explain.get("related_operators", [])
        if not isinstance(related_ops, list):
            raise OperatorGraphBacklinkError(
                f"dependent_variable_registry.variables.{variable_id}.explainability.related_operators must be a list."
            )
        for op_id in related_ops:
            op_key = str(op_id)
            if op_key not in known_ops:
                raise OperatorGraphBacklinkError(
                    f"dependent_variable_registry.variables.{variable_id} references unknown operator id '{op_key}'."
                )
            backlinks = _resolve_operator_graph_backlinks_from_payloads(
                op_key,
                dependent=dependent,
                operators=operators,
                trialstate=trialstate,
            )
            backlink_ids = {str(item.get("id")) for item in backlinks["graph_backlinks"]}
            if str(variable_id) not in backlink_ids:
                raise OperatorGraphBacklinkError(
                    f"Backlink mismatch: operator '{op_key}' did not include dependent variable '{variable_id}'."
                )


def validate_operator_graph_backlink_integrity() -> None:
    dependent, operators, trialstate = _resolve_payloads()
    validate_operator_graph_backlink_integrity_from_payloads(
        dependent=dependent,
        operators=operators,
        trialstate=trialstate,
    )


def list_operator_graph_backlinks() -> tuple[dict[str, Any], ...]:
    _dependent, operators, _trialstate = _resolve_payloads()
    operator_map = _require_dict(operators.get("operators"), "operator_registry.operators")
    resolved = [resolve_operator_graph_backlinks(operator_id) for operator_id in sorted(operator_map.keys())]
    return tuple(deepcopy(resolved))

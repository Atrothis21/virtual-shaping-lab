"""Preset run-flow and results handoff contracts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.dependent_variable_registry import (
    DependentVariableRegistryValidationError,
    get_dependent_variable,
    validate_preset_results_contract,
)
from ui.contracts.preset_materialization import materialize_preset_payload
from ui.contracts.preset_registry import get_preset


class PresetRunFlowContractError(ValueError):
    """Raised when preset run-flow contract validation fails."""


def resolve_results_contract_from_preset(preset: dict[str, Any]) -> dict[str, Any]:
    results_contract = preset.get("results_contract")
    if not isinstance(results_contract, dict):
        raise PresetRunFlowContractError("Preset is missing results_contract.")
    try:
        normalized = validate_preset_results_contract(results_contract)
    except DependentVariableRegistryValidationError as exc:
        raise PresetRunFlowContractError(
            f"results_contract contains unknown dependent-variable IDs: {exc}"
        ) from exc

    def _enrich(ids: list[str]) -> list[dict[str, Any]]:
        enriched: list[dict[str, Any]] = []
        for variable_id in ids:
            variable = get_dependent_variable(variable_id)
            enriched.append(
                {
                    "id": variable_id,
                    "label": variable.get("label"),
                    "category": variable.get("category"),
                }
            )
        return enriched

    return {
        "primary_dependent_variables": _enrich(normalized["primary_dependent_variables"]),
        "secondary_dependent_variables": _enrich(normalized["secondary_dependent_variables"]),
        "graph_priority": _enrich(normalized["graph_priority"]),
    }


def _validate_graph_priority_categories(results_view: dict[str, Any]) -> None:
    graph_priority = results_view.get("graph_priority", [])
    if not graph_priority:
        raise PresetRunFlowContractError("results_contract.graph_priority must be non-empty.")
    priority_categories = [str(entry.get("category") or "") for entry in graph_priority]
    first_two = priority_categories[:2]
    if not all(category in {"behavioral", "learning"} for category in first_two):
        raise PresetRunFlowContractError(
            "results_contract.graph_priority must prioritize behavioral/learning categories first."
        )


def build_preset_run_flow_contract(
    preset_id: str,
    *,
    edits: dict[str, Any] | None = None,
) -> dict[str, Any]:
    preset = get_preset(preset_id)
    payload = materialize_preset_payload(preset_id, edits=edits)
    results_view = resolve_results_contract_from_preset(preset)
    _validate_graph_priority_categories(results_view)

    return {
        "preset_id": preset_id,
        "payload": deepcopy(payload),
        "flow": {
            "route_sequence": ["library", "detail", "run", "results"],
            "run_action": {
                "from": "detail",
                "to": "results",
                "results_route": f"/ui/results.html?preset={preset_id}",
            },
        },
        "results_view": results_view,
    }


def resolve_preset_results_view(preset_id: str) -> dict[str, Any]:
    preset = get_preset(preset_id)
    results_view = resolve_results_contract_from_preset(preset)
    _validate_graph_priority_categories(results_view)
    return results_view


def validate_preset_results_priority(preset_id: str) -> None:
    resolve_preset_results_view(preset_id)

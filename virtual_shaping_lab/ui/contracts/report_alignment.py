"""Report alignment contracts for registry-driven variable labeling."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.preset_registry import get_preset
from ui.contracts.dependent_variable_resolver import resolve_report_variable


class ReportAlignmentError(ValueError):
    """Raised when report-to-registry alignment contracts fail."""


# Thin mapping layer from analysis metric IDs -> dependent-variable IDs.
# Keep this intentionally explicit and easy to extend as report coverage grows.
METRIC_TO_DEPENDENT_VARIABLE: dict[str, str] = {
    "prediction_time_series": "predicted_outcome",
    "mean_prediction_by_stimulus": "predicted_outcome",
    "final_prediction_by_stimulus": "predicted_outcome",
    "prediction_error_time_series": "prediction_error",
    "action_counts": "action_counts",
}


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReportAlignmentError(f"{label} must be a non-empty string.")
    return value


def _humanize_metric_name(metric_name: str) -> str:
    return metric_name.replace("_", " ").strip().title()


def _resolve_preset_variable_catalog(preset_id: str) -> list[dict[str, Any]]:
    try:
        preset = get_preset(preset_id)
    except KeyError:
        # Report presets can exist without a UI preset-registry entry.
        # In that case, keep a thin/empty catalog and still align mapped metrics.
        return []
    results_contract = preset.get("results_contract")
    if not isinstance(results_contract, dict):
        raise ReportAlignmentError(f"Preset '{preset_id}' is missing results_contract.")
    graph_priority = results_contract.get("graph_priority")
    if not isinstance(graph_priority, list):
        raise ReportAlignmentError(f"Preset '{preset_id}' results_contract.graph_priority must be a list.")

    catalog: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw_variable_id in graph_priority:
        variable_id = _require_non_empty_string(raw_variable_id, "results_contract.graph_priority[]")
        if variable_id in seen:
            continue
        seen.add(variable_id)
        resolved = resolve_report_variable(variable_id)
        catalog.append(
            {
                "id": resolved["id"],
                "label": resolved["label"],
                "description": resolved["plain_language"],
                "units": resolved["units"],
            }
        )
    return catalog


def build_report_alignment_contract(
    preset_id: str,
    metric_names: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    """Build a report alignment payload for labels/descriptions and metric naming."""
    key = _require_non_empty_string(preset_id, "preset_id")
    if not isinstance(metric_names, (list, tuple)):
        raise ReportAlignmentError("metric_names must be a list/tuple of strings.")

    variable_catalog = _resolve_preset_variable_catalog(key)
    variable_by_id = {item["id"]: item for item in variable_catalog}

    metric_labels: dict[str, dict[str, Any]] = {}
    for idx, raw_metric_name in enumerate(metric_names):
        metric_name = _require_non_empty_string(raw_metric_name, f"metric_names[{idx}]")
        variable_id = METRIC_TO_DEPENDENT_VARIABLE.get(metric_name)
        if variable_id:
            variable = variable_by_id.get(variable_id)
            if variable is None:
                try:
                    resolved = resolve_report_variable(variable_id)
                    variable = {
                        "id": resolved["id"],
                        "label": resolved["label"],
                        "description": resolved["plain_language"],
                        "units": resolved["units"],
                    }
                except KeyError:
                    variable = None
            if variable is not None:
                metric_labels[metric_name] = {
                    "label": variable["label"],
                    "description": variable["description"],
                    "variable_id": variable_id,
                    "source": "dependent_variable_registry",
                }
                continue
        metric_labels[metric_name] = {
            "label": _humanize_metric_name(metric_name),
            "description": "",
            "variable_id": None,
            "source": "metric_name_fallback",
        }

    return {
        "preset_id": key,
        "variables": deepcopy(variable_catalog),
        "metric_labels": deepcopy(metric_labels),
    }

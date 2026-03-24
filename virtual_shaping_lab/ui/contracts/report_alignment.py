"""Report alignment contracts for registry-driven variable labeling."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.operator_basis_registry import (
    get_measurement_readout_contract,
    list_ui_selectable_implementations,
)
from ui.contracts.preset_registry import get_preset
from ui.contracts.dependent_variable_resolver import resolve_report_variable


class ReportAlignmentError(ValueError):
    """Raised when report-to-registry alignment contracts fail."""


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReportAlignmentError(f"{label} must be a non-empty string.")
    return value


def _humanize_metric_name(metric_name: str) -> str:
    return metric_name.replace("_", " ").strip().title()


def _normalize_measurement_selection_ids(
    preset_id: str,
    measurement_selection_ids: list[str] | tuple[str, ...] | None,
) -> list[str]:
    known_readouts = set(list_ui_selectable_implementations("m"))
    if measurement_selection_ids is not None:
        if not isinstance(measurement_selection_ids, (list, tuple)):
            raise ReportAlignmentError("measurement_selection_ids must be a list/tuple of readout IDs.")
        out: list[str] = []
        for idx, raw in enumerate(measurement_selection_ids):
            key = _require_non_empty_string(raw, f"measurement_selection_ids[{idx}]")
            if key not in known_readouts:
                raise ReportAlignmentError(
                    f"measurement_selection_ids[{idx}] references unknown readout id: {key}"
                )
            out.append(key)
        return out
    try:
        preset = get_preset(preset_id)
    except KeyError:
        return list(list_ui_selectable_implementations("m"))
    results_contract = preset.get("results_contract")
    if not isinstance(results_contract, dict):
        return list(list_ui_selectable_implementations("m"))
    raw = results_contract.get("measurement_readouts")
    if raw is None:
        return list(list_ui_selectable_implementations("m"))
    if not isinstance(raw, list):
        raise ReportAlignmentError("results_contract.measurement_readouts must be a list.")
    out: list[str] = []
    for idx, value in enumerate(raw):
        key = _require_non_empty_string(value, f"results_contract.measurement_readouts[{idx}]")
        if key not in known_readouts:
            raise ReportAlignmentError(
                f"results_contract.measurement_readouts[{idx}] references unknown readout id: {key}"
            )
        out.append(key)
    return out


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


def _resolve_readout_catalog(selection_ids: list[str]) -> list[dict[str, Any]]:
    catalog: list[dict[str, Any]] = []
    for idx, selection_id in enumerate(selection_ids):
        contract = get_measurement_readout_contract(selection_id)
        priority_raw = contract.get("priority", 100)
        priority = int(priority_raw) if isinstance(priority_raw, int) else 100
        supported_metrics_raw = contract.get("supported_metrics", [])
        supported_metrics = (
            [str(v) for v in supported_metrics_raw if isinstance(v, str)]
            if isinstance(supported_metrics_raw, list)
            else []
        )
        metric_to_variable_raw = contract.get("metric_to_variable", {})
        metric_to_variable = (
            {
                str(metric): (str(variable_id) if isinstance(variable_id, str) else None)
                for metric, variable_id in metric_to_variable_raw.items()
            }
            if isinstance(metric_to_variable_raw, dict)
            else {}
        )
        catalog.append(
            {
                "selection_id": selection_id,
                "priority": priority,
                "source_order": idx,
                "supported_metrics": supported_metrics,
                "metric_to_variable": metric_to_variable,
            }
        )
    catalog.sort(key=lambda item: (item["priority"], item["source_order"], item["selection_id"]))
    return catalog


def build_report_alignment_contract(
    preset_id: str,
    metric_names: list[str] | tuple[str, ...],
    *,
    measurement_selection_ids: list[str] | tuple[str, ...] | None = None,
    strict_readout_coverage: bool = False,
) -> dict[str, Any]:
    """Build a report alignment payload for labels/descriptions and metric naming."""
    key = _require_non_empty_string(preset_id, "preset_id")
    if not isinstance(metric_names, (list, tuple)):
        raise ReportAlignmentError("metric_names must be a list/tuple of strings.")

    variable_catalog = _resolve_preset_variable_catalog(key)
    variable_by_id = {item["id"]: item for item in variable_catalog}
    selected_readouts = _normalize_measurement_selection_ids(key, measurement_selection_ids)
    readout_catalog = _resolve_readout_catalog(selected_readouts)

    metric_labels: dict[str, dict[str, Any]] = {}
    for idx, raw_metric_name in enumerate(metric_names):
        metric_name = _require_non_empty_string(raw_metric_name, f"metric_names[{idx}]")
        candidates = [
            entry for entry in readout_catalog if metric_name in set(entry.get("supported_metrics", []))
        ]
        if candidates:
            selected = candidates[0]
            metric_to_variable = selected.get("metric_to_variable", {})
            variable_id = metric_to_variable.get(metric_name) if isinstance(metric_to_variable, dict) else None
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
                    except KeyError as exc:
                        raise ReportAlignmentError(
                            f"Measurement mapping for metric '{metric_name}' references unknown dependent variable id '{variable_id}'."
                        ) from exc
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
            continue
        if strict_readout_coverage:
            raise ReportAlignmentError(
                f"Missing measurement readout coverage for metric '{metric_name}' under selected readouts: "
                + ", ".join(selected_readouts)
            )
        metric_labels[metric_name] = {
            "label": _humanize_metric_name(metric_name),
            "description": "",
            "variable_id": None,
            "source": "metric_name_fallback",
        }

    return {
        "preset_id": key,
        "variables": deepcopy(variable_catalog),
        "selected_measurement_readouts": list(selected_readouts),
        "measurement_readout_catalog": deepcopy(readout_catalog),
        "metric_labels": deepcopy(metric_labels),
    }

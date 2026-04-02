"""Named measurement preset registry and deterministic expansion."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .spec import MeasurementSpec

PRESET_VERSION = "3.22.0"

MEASUREMENT_PRESETS: dict[str, dict[str, Any]] = {
    "learning_curve_basic": {
        "analysis_ops": ["learning_curve_basic"],
        "visualization_ops": ["line_plot"],
        "report_op": "markdown_report",
    },
    "extinction_curve": {
        "analysis_ops": ["extinction_curve"],
        "visualization_ops": ["line_plot"],
        "report_op": "markdown_report",
    },
    "generalization_profile": {
        "analysis_ops": ["generalization_profile"],
        "visualization_ops": ["line_plot"],
        "report_op": "markdown_report",
    },
    "blocking_diagnostics": {
        "analysis_ops": ["blocking_diagnostics"],
        "visualization_ops": ["multi_line_plot"],
        "report_op": "pdf_report",
    },
    "action_learning_curve": {
        "analysis_ops": ["action_learning_curve"],
        "visualization_ops": ["line_plot"],
        "report_op": "markdown_report",
    },
    "policy_diagnostics": {
        "analysis_ops": ["policy_diagnostics"],
        "visualization_ops": ["line_plot"],
        "report_op": "json_report",
    },
    "prediction_error_diagnostics": {
        "analysis_ops": ["prediction_error_diagnostics"],
        "visualization_ops": ["line_plot"],
        "report_op": "markdown_report",
    },
}

MEASUREMENT_PRESET_ALIASES: dict[str, str] = {
    "learning": "learning_curve_basic",
    "extinction": "extinction_curve",
    "generalization": "generalization_profile",
    "blocking": "blocking_diagnostics",
    "operant_action_curve": "action_learning_curve",
    "policy": "policy_diagnostics",
    "prediction_error": "prediction_error_diagnostics",
}

MEASUREMENT_PRESET_FAMILIES: dict[str, list[str]] = {
    "classical": ["learning_curve_basic", "extinction_curve", "generalization_profile", "blocking_diagnostics"],
    "operant": ["action_learning_curve", "policy_diagnostics"],
    "diagnostics": ["prediction_error_diagnostics", "policy_diagnostics", "blocking_diagnostics"],
}


def _resolve_preset_name(name: str) -> str:
    key = str(name).strip()
    if key in MEASUREMENT_PRESETS:
        return key
    alias_target = MEASUREMENT_PRESET_ALIASES.get(key)
    if alias_target is not None:
        return alias_target
    raise ValueError(f"[MEAS_E_UNKNOWN_PRESET] Unknown measurement preset '{name}'.")


def measurement_preset_names() -> list[str]:
    return sorted(MEASUREMENT_PRESETS.keys())


def measurement_preset_aliases() -> dict[str, str]:
    return {key: MEASUREMENT_PRESET_ALIASES[key] for key in sorted(MEASUREMENT_PRESET_ALIASES.keys())}


def measurement_preset_registry() -> dict[str, dict[str, Any]]:
    return {name: dict(MEASUREMENT_PRESETS[name]) for name in sorted(MEASUREMENT_PRESETS.keys())}


def measurement_preset_families() -> dict[str, list[str]]:
    return {family: list(names) for family, names in sorted(MEASUREMENT_PRESET_FAMILIES.items())}


def expand_measurement_preset(name: str, *, metadata: dict[str, Any] | None = None) -> MeasurementSpec:
    resolved_name = _resolve_preset_name(name)
    preset = MEASUREMENT_PRESETS[resolved_name]
    merged_metadata: dict[str, Any] = {
        "preset_name": resolved_name,
        "preset_version": PRESET_VERSION,
    }
    if metadata:
        merged_metadata.update(dict(metadata))
    return MeasurementSpec(
        analysis_ops=list(preset["analysis_ops"]),
        visualization_ops=list(preset["visualization_ops"]),
        report_op=preset["report_op"],
        metadata=merged_metadata,
    )


def measurement_preset_payload(name: str, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    spec = expand_measurement_preset(name, metadata=metadata)
    return {
        "preset_name": spec.metadata.get("preset_name"),
        "spec": spec.to_dict(),
        "registry_version": PRESET_VERSION,
    }


def measurement_preset_hash(name: str, *, metadata: dict[str, Any] | None = None) -> str:
    blob = json.dumps(measurement_preset_payload(name, metadata=metadata), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

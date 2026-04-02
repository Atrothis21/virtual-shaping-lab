"""Machine-readable measurement slot registries and compatibility matrix."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .validation import (
    ANALYSIS_OP_VALUES,
    ANALYSIS_TO_VISUALIZATION,
    REPORT_OP_VALUES,
    REPORT_REQUIRES_VISUALIZATION,
    VISUALIZATION_OP_VALUES,
)

MEASUREMENT_REGISTRY_VERSION = "3.22.0"


def _sorted_mapping(source: dict[str, set[str]]) -> dict[str, list[str]]:
    return {key: sorted(source[key]) for key in sorted(source.keys())}


SLOT_REGISTRIES: dict[str, list[str]] = {
    "analysis_ops": sorted(ANALYSIS_OP_VALUES),
    "visualization_ops": sorted(VISUALIZATION_OP_VALUES),
    "report_op": sorted(REPORT_OP_VALUES),
}

COMPATIBILITY_MATRIX: dict[str, Any] = {
    "analysis_to_visualization": _sorted_mapping(ANALYSIS_TO_VISUALIZATION),
    "report_requires_visualization": {
        key: bool(REPORT_REQUIRES_VISUALIZATION[key]) for key in sorted(REPORT_REQUIRES_VISUALIZATION.keys())
    },
}


def slot_registries() -> dict[str, list[str]]:
    return {slot: list(values) for slot, values in SLOT_REGISTRIES.items()}


def compatibility_matrix() -> dict[str, Any]:
    return {
        "analysis_to_visualization": {
            key: list(values) for key, values in COMPATIBILITY_MATRIX["analysis_to_visualization"].items()
        },
        "report_requires_visualization": dict(COMPATIBILITY_MATRIX["report_requires_visualization"]),
    }


def measurement_registry_payload() -> dict[str, Any]:
    return {
        "slot_registries": slot_registries(),
        "compatibility_matrix": compatibility_matrix(),
        "version": MEASUREMENT_REGISTRY_VERSION,
    }


def measurement_registry_hash() -> str:
    blob = json.dumps(measurement_registry_payload(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

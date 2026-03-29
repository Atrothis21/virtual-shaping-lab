"""Machine-readable observation slot registries and compatibility matrix."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .validation import (
    CONTEXT_TO_GENERALIZATION,
    CONTEXT_VALUES,
    GENERALIZATION_REQUIRES_CONTEXT,
    GENERALIZATION_REQUIRES_REPRESENTATION,
    GENERALIZATION_VALUES,
    REPRESENTATION_TO_GENERALIZATION,
    REPRESENTATION_VALUES,
)

OBSERVATION_REGISTRY_VERSION = "3.19.0"


def _sorted_mapping(source: dict[str, set[str]]) -> dict[str, list[str]]:
    return {key: sorted(source[key]) for key in sorted(source.keys())}


SLOT_REGISTRIES: dict[str, list[str]] = {
    "representation": sorted(REPRESENTATION_VALUES),
    "context": sorted(CONTEXT_VALUES),
    "generalization": sorted(GENERALIZATION_VALUES),
}

COMPATIBILITY_MATRIX: dict[str, dict[str, list[str]]] = {
    "representation_to_generalization": _sorted_mapping(REPRESENTATION_TO_GENERALIZATION),
    "context_to_generalization": _sorted_mapping(CONTEXT_TO_GENERALIZATION),
    "generalization_requires_context": _sorted_mapping(GENERALIZATION_REQUIRES_CONTEXT),
    "generalization_requires_representation": _sorted_mapping(GENERALIZATION_REQUIRES_REPRESENTATION),
}


def slot_registries() -> dict[str, list[str]]:
    return {slot: list(values) for slot, values in SLOT_REGISTRIES.items()}


def compatibility_matrix() -> dict[str, dict[str, list[str]]]:
    return {
        section: {key: list(values) for key, values in mapping.items()}
        for section, mapping in COMPATIBILITY_MATRIX.items()
    }


def observation_registry_payload() -> dict[str, Any]:
    return {
        "slot_registries": slot_registries(),
        "compatibility_matrix": compatibility_matrix(),
        "version": OBSERVATION_REGISTRY_VERSION,
    }


def observation_registry_hash() -> str:
    blob = json.dumps(observation_registry_payload(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


"""Machine-readable protocol slot registries and compatibility matrix."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .validation import (
    ACTION_SPACE_MODE_VALUES,
    ADVANCE_RULE_VALUES,
    CONSEQUENCE_RULE_VALUES,
    EMISSION_RULE_VALUES,
    FAMILY_TO_ACTION_SPACE,
    PROTOCOL_FAMILY_VALUES,
    STOP_RULE_VALUES,
    TEMPORAL_MODE_VALUES,
    TEMPORAL_TO_ADVANCE,
)

PROTOCOL_REGISTRY_VERSION = "3.21.0"


def _sorted_mapping(source: dict[str, set[str]]) -> dict[str, list[str]]:
    return {key: sorted(source[key]) for key in sorted(source.keys())}


SLOT_REGISTRIES: dict[str, list[str]] = {
    "emission_rule": sorted(EMISSION_RULE_VALUES),
    "consequence_rule": sorted(CONSEQUENCE_RULE_VALUES),
    "advance_rule": sorted(ADVANCE_RULE_VALUES),
    "stop_rule": sorted(STOP_RULE_VALUES),
    "protocol_family": sorted(PROTOCOL_FAMILY_VALUES),
    "action_space_mode": sorted(ACTION_SPACE_MODE_VALUES),
    "temporal_mode": sorted(TEMPORAL_MODE_VALUES),
}

COMPATIBILITY_MATRIX: dict[str, dict[str, list[str]]] = {
    "family_to_action_space": _sorted_mapping(FAMILY_TO_ACTION_SPACE),
    "temporal_to_advance": _sorted_mapping(TEMPORAL_TO_ADVANCE),
}


def slot_registries() -> dict[str, list[str]]:
    return {slot: list(values) for slot, values in SLOT_REGISTRIES.items()}


def compatibility_matrix() -> dict[str, dict[str, list[str]]]:
    return {
        section: {key: list(values) for key, values in mapping.items()}
        for section, mapping in COMPATIBILITY_MATRIX.items()
    }


def protocol_registry_payload() -> dict[str, Any]:
    return {
        "slot_registries": slot_registries(),
        "compatibility_matrix": compatibility_matrix(),
        "version": PROTOCOL_REGISTRY_VERSION,
    }


def protocol_registry_hash() -> str:
    blob = json.dumps(protocol_registry_payload(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

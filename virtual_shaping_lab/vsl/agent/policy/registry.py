"""Machine-readable policy slot registries and compatibility matrix."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .validation import (
    ACTION_SPACE_MODE_VALUES,
    AVAILABILITY_RULE_VALUES,
    SELECTION_REQUIRES_PARAMS,
    SELECTION_RULE_VALUES,
    SELECTION_TO_ACTION_SPACE,
    TIE_BREAK_RULE_VALUES,
)

POLICY_REGISTRY_VERSION = "3.20.0"


def _sorted_mapping(source: dict[str, set[str]]) -> dict[str, list[str]]:
    return {key: sorted(source[key]) for key in sorted(source.keys())}


def _required_params_mapping(source: dict[str, tuple[str, ...]]) -> dict[str, list[str]]:
    return {key: list(source[key]) for key in sorted(source.keys())}


SLOT_REGISTRIES: dict[str, list[str]] = {
    "selection_rule": sorted(SELECTION_RULE_VALUES),
    "action_space_mode": sorted(ACTION_SPACE_MODE_VALUES),
    "tie_break_rule": sorted(TIE_BREAK_RULE_VALUES),
    "availability_rule": sorted(AVAILABILITY_RULE_VALUES),
}

COMPATIBILITY_MATRIX: dict[str, dict[str, list[str]]] = {
    "selection_to_action_space": _sorted_mapping(SELECTION_TO_ACTION_SPACE),
    "selection_required_parameters": _required_params_mapping(SELECTION_REQUIRES_PARAMS),
}


def slot_registries() -> dict[str, list[str]]:
    return {slot: list(values) for slot, values in SLOT_REGISTRIES.items()}


def compatibility_matrix() -> dict[str, dict[str, list[str]]]:
    return {
        section: {key: list(values) for key, values in mapping.items()}
        for section, mapping in COMPATIBILITY_MATRIX.items()
    }


def policy_registry_payload() -> dict[str, Any]:
    return {
        "slot_registries": slot_registries(),
        "compatibility_matrix": compatibility_matrix(),
        "version": POLICY_REGISTRY_VERSION,
    }


def policy_registry_hash() -> str:
    blob = json.dumps(policy_registry_payload(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


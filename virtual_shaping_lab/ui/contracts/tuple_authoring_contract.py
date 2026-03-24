"""Tuple-first authoring payload contract and legacy preset translator."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.agent_bundle_registry import (
    AgentBundleRegistryValidationError,
    list_agent_bundle_ids,
    validate_agent_bundle_arrangement_compatibility,
)
from ui.contracts.arrangement_contract import list_arrangement_ids
from ui.contracts.preset_registry import get_preset
from ui.contracts.task_registry import list_task_ids


class TupleAuthoringContractError(ValueError):
    """Raised when tuple authoring payload validation or translation fails."""


TUPLE_AUTHORING_CONTRACT_VERSION = "3.15.5"
TUPLE_AUTHORING_MODE = "tuple_v1"
_LEGACY_PRESET_MODE = "preset_basis_v1"

_DEFAULT_AGENT_BY_ARRANGEMENT: dict[str, str] = {
    "pavlovian": "rw_classical",
    "operant": "rw_operant",
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TupleAuthoringContractError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TupleAuthoringContractError(f"{label} must be a non-empty string.")
    return value


def _normalize_tuple_payload(payload: dict[str, Any]) -> dict[str, Any]:
    root = _require_dict(payload, "tuple_authoring")
    arrangement = _require_non_empty_string(root.get("arrangement"), "tuple_authoring.arrangement").lower()
    task = _require_non_empty_string(root.get("task"), "tuple_authoring.task").lower()
    agent = _require_non_empty_string(root.get("agent"), "tuple_authoring.agent")
    edits = root.get("edits", {})
    if not isinstance(edits, dict):
        raise TupleAuthoringContractError("tuple_authoring.edits must be an object.")

    if arrangement not in set(list_arrangement_ids()):
        known = ", ".join(list_arrangement_ids())
        raise TupleAuthoringContractError(
            f"tuple_authoring.arrangement '{arrangement}' is unknown. Known: {known}"
        )
    if task not in set(list_task_ids()):
        known = ", ".join(list_task_ids())
        raise TupleAuthoringContractError(
            f"tuple_authoring.task '{task}' is unknown. Known: {known}"
        )
    if agent not in set(list_agent_bundle_ids()):
        known = ", ".join(list_agent_bundle_ids())
        raise TupleAuthoringContractError(
            f"tuple_authoring.agent '{agent}' is unknown. Known: {known}"
        )
    try:
        validate_agent_bundle_arrangement_compatibility(bundle_id=agent, arrangement_id=arrangement)
    except AgentBundleRegistryValidationError as exc:
        raise TupleAuthoringContractError(str(exc)) from exc

    version = root.get("contract_version", TUPLE_AUTHORING_CONTRACT_VERSION)
    mode = root.get("authoring_mode", TUPLE_AUTHORING_MODE)
    if version != TUPLE_AUTHORING_CONTRACT_VERSION:
        raise TupleAuthoringContractError(
            f"tuple_authoring.contract_version must be '{TUPLE_AUTHORING_CONTRACT_VERSION}'."
        )
    if mode != TUPLE_AUTHORING_MODE:
        raise TupleAuthoringContractError(
            f"tuple_authoring.authoring_mode must be '{TUPLE_AUTHORING_MODE}'."
        )

    return {
        "contract_version": TUPLE_AUTHORING_CONTRACT_VERSION,
        "authoring_mode": TUPLE_AUTHORING_MODE,
        "arrangement": arrangement,
        "task": task,
        "agent": agent,
        "edits": deepcopy(edits),
    }


def validate_tuple_authoring_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate tuple-first authoring payload shape."""
    return _normalize_tuple_payload(payload)


def _translate_from_legacy_preset(payload: dict[str, Any]) -> dict[str, Any]:
    preset_id = _require_non_empty_string(payload.get("preset_id"), "legacy_authoring.preset_id").lower()
    preset = get_preset(preset_id)
    reference = _require_dict(
        preset.get("task_reference"),
        f"preset_registry.presets.{preset_id}.task_reference",
    )
    arrangement = _require_non_empty_string(
        reference.get("default_arrangement_id"),
        f"preset_registry.presets.{preset_id}.task_reference.default_arrangement_id",
    )
    task = _require_non_empty_string(
        reference.get("phenomenon_id"),
        f"preset_registry.presets.{preset_id}.task_reference.phenomenon_id",
    )
    inferred_agent = _DEFAULT_AGENT_BY_ARRANGEMENT.get(arrangement, "rw_classical")

    edits = payload.get("edits", {})
    if edits is None:
        edits = {}
    if not isinstance(edits, dict):
        raise TupleAuthoringContractError("legacy_authoring.edits must be an object when provided.")

    dropped_fields: list[str] = []
    if "operator_subset" in payload:
        dropped_fields.append("operator_subset")

    translation_quality = "lossless" if not dropped_fields else "heuristic"
    deprecations = [
        "preset_id route payload is deprecated for tuple-first routes.",
        "Use arrangement/task/agent/edit payloads with tuple_v1 mode.",
    ]
    if dropped_fields:
        deprecations.append(
            "Legacy fields were not projected into tuple payload: " + ", ".join(sorted(dropped_fields))
        )

    translated = {
        "contract_version": TUPLE_AUTHORING_CONTRACT_VERSION,
        "authoring_mode": TUPLE_AUTHORING_MODE,
        "arrangement": arrangement,
        "task": task,
        "agent": inferred_agent,
        "edits": deepcopy(edits),
    }
    translated = validate_tuple_authoring_payload(translated)

    return {
        "translated_payload": translated,
        "diagnostics": {
            "translated_tuple": {
                "arrangement": arrangement,
                "task": task,
                "agent": inferred_agent,
            },
            "legacy_preset_label": preset.get("label"),
            "translation_quality": translation_quality,
            "deprecation_diagnostics": deprecations,
            "source_mode": _LEGACY_PRESET_MODE,
            "target_mode": TUPLE_AUTHORING_MODE,
        },
    }


def translate_to_tuple_authoring_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Translate legacy preset-route payload to tuple payload or validate tuple payload."""
    root = _require_dict(payload, "authoring_payload")
    if "arrangement" in root or "task" in root or "agent" in root:
        normalized = validate_tuple_authoring_payload(root)
        return {
            "translated_payload": normalized,
            "diagnostics": {
                "translated_tuple": {
                    "arrangement": normalized["arrangement"],
                    "task": normalized["task"],
                    "agent": normalized["agent"],
                },
                "legacy_preset_label": None,
                "translation_quality": "lossless",
                "deprecation_diagnostics": [],
                "source_mode": TUPLE_AUTHORING_MODE,
                "target_mode": TUPLE_AUTHORING_MODE,
            },
        }
    if "preset_id" in root:
        return _translate_from_legacy_preset(root)
    raise TupleAuthoringContractError(
        "Authoring payload must include tuple keys (arrangement/task/agent) or legacy preset_id."
    )

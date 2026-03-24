"""Smart preset projection contract: thin named coordinates over tuple space."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.arrangement_task_agent_composition import (
    ArrangementTaskAgentCompositionError,
    compose_arrangement_task_agent_to_operator_subset,
)


class SmartPresetProjectionValidationError(ValueError):
    """Raised when smart preset projection contract validation fails."""


SMART_PRESET_PROJECTION_VERSION = "3.16.0"

_FORBIDDEN_PRESET_KEYS: set[str] = {
    "operator_subset",
    "defaults",
    "locked",
    "optional",
    "template",
    "ui_contract",
    "canonical_payload",
    "hidden_defaults",
}

SMART_PRESET_PROJECTIONS: dict[str, Any] = {
    "version": SMART_PRESET_PROJECTION_VERSION,
    "smart_presets": {
        "classical_acquisition": {
            "id": "classical_acquisition",
            "label": "Classical Acquisition",
            "tuple_reference": {
                "arrangement_id": "pavlovian",
                "phenomenon_id": "acquisition",
                "agent_bundle_id": "rw_classical",
            },
            "description": "Baseline classical acquisition tuple.",
            "education": {
                "intent": "Starter tuple for CS+ associative acquisition.",
            },
        },
        "classical_extinction": {
            "id": "classical_extinction",
            "label": "Classical Extinction",
            "tuple_reference": {
                "arrangement_id": "pavlovian",
                "phenomenon_id": "extinction",
                "agent_bundle_id": "rw_classical",
            },
            "description": "Classical extinction tuple with RW-style agent bundle.",
            "education": {
                "intent": "Observe responding decay after nonreinforcement.",
            },
        },
        "classical_differential_acquisition": {
            "id": "classical_differential_acquisition",
            "label": "Classical Differential Acquisition",
            "tuple_reference": {
                "arrangement_id": "pavlovian",
                "phenomenon_id": "differential_acquisition",
                "agent_bundle_id": "rw_classical",
            },
            "description": "Classical CS+/CS- discrimination tuple.",
            "education": {
                "intent": "Baseline discrimination under pavlovian arrangement.",
            },
        },
        "operant_acquisition": {
            "id": "operant_acquisition",
            "label": "Operant Acquisition",
            "tuple_reference": {
                "arrangement_id": "operant",
                "phenomenon_id": "acquisition",
                "agent_bundle_id": "rw_operant",
            },
            "description": "Operant acquisition tuple with action policy enabled.",
            "education": {
                "intent": "Starter tuple for operant action-value learning.",
            },
        },
    },
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SmartPresetProjectionValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SmartPresetProjectionValidationError(f"{label} must be a non-empty string.")
    return value.strip()


def _validate_tuple_reference(value: Any, label: str) -> dict[str, str]:
    root = _require_dict(value, label)
    out: dict[str, str] = {}
    for key in ("arrangement_id", "phenomenon_id", "agent_bundle_id"):
        if key not in root:
            raise SmartPresetProjectionValidationError(f"{label} missing required key: {key}")
        out[key] = _require_non_empty_string(root.get(key), f"{label}.{key}")
    return out


def _validate_smart_preset_entry(preset_id: str, raw: Any) -> None:
    entry = _require_dict(raw, f"smart_preset_projection.smart_presets.{preset_id}")
    for forbidden in _FORBIDDEN_PRESET_KEYS:
        if forbidden in entry:
            raise SmartPresetProjectionValidationError(
                f"smart_preset_projection.smart_presets.{preset_id} cannot define '{forbidden}'."
            )
    for required in ("id", "label", "tuple_reference"):
        if required not in entry:
            raise SmartPresetProjectionValidationError(
                f"smart_preset_projection.smart_presets.{preset_id} missing required key: {required}"
            )
    entry_id = _require_non_empty_string(entry.get("id"), f"smart_preset_projection.smart_presets.{preset_id}.id")
    if entry_id != preset_id:
        raise SmartPresetProjectionValidationError(
            f"smart_preset_projection.smart_presets.{preset_id}.id must match key '{preset_id}'."
        )
    _require_non_empty_string(entry.get("label"), f"smart_preset_projection.smart_presets.{preset_id}.label")
    tuple_ref = _validate_tuple_reference(
        entry.get("tuple_reference"),
        f"smart_preset_projection.smart_presets.{preset_id}.tuple_reference",
    )
    if "description" in entry:
        _require_non_empty_string(
            entry.get("description"),
            f"smart_preset_projection.smart_presets.{preset_id}.description",
        )
    if "education" in entry:
        _require_dict(entry.get("education"), f"smart_preset_projection.smart_presets.{preset_id}.education")

    try:
        compose_arrangement_task_agent_to_operator_subset(
            arrangement_id=tuple_ref["arrangement_id"],
            phenomenon_id=tuple_ref["phenomenon_id"],
            agent_bundle_id=tuple_ref["agent_bundle_id"],
        )
    except ArrangementTaskAgentCompositionError as exc:
        raise SmartPresetProjectionValidationError(
            f"smart_preset_projection.smart_presets.{preset_id}.tuple_reference is not composable: {exc}"
        ) from exc


def validate_smart_preset_projection_contract(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate smart preset projection contract and return deep copy."""
    root = deepcopy(SMART_PRESET_PROJECTIONS if payload is None else payload)
    registry = _require_dict(root, "smart_preset_projection")
    for key in ("version", "smart_presets"):
        if key not in registry:
            raise SmartPresetProjectionValidationError(
                f"smart_preset_projection missing required key: {key}"
            )
    _require_non_empty_string(registry.get("version"), "smart_preset_projection.version")
    presets = _require_dict(registry.get("smart_presets"), "smart_preset_projection.smart_presets")
    if not presets:
        raise SmartPresetProjectionValidationError(
            "smart_preset_projection.smart_presets must include at least one smart preset."
        )
    for preset_id, raw in presets.items():
        _validate_smart_preset_entry(preset_id, raw)
    return registry


def get_smart_preset_projection_contract() -> dict[str, Any]:
    """Return validated smart preset projection contract."""
    return validate_smart_preset_projection_contract(SMART_PRESET_PROJECTIONS)


def list_smart_preset_ids() -> tuple[str, ...]:
    """Return stable smart preset IDs."""
    payload = get_smart_preset_projection_contract()
    return tuple(sorted(payload["smart_presets"].keys()))


def get_smart_preset_projection(smart_preset_id: str) -> dict[str, Any]:
    """Return one smart preset projection by ID."""
    key = _require_non_empty_string(smart_preset_id, "smart_preset_id")
    payload = get_smart_preset_projection_contract()
    presets = payload["smart_presets"]
    if key not in presets:
        known = ", ".join(sorted(presets.keys()))
        raise SmartPresetProjectionValidationError(
            f"Unknown smart_preset_id '{key}'. Known IDs: {known}"
        )
    return deepcopy(presets[key])


def project_smart_preset_to_tuple_payload(
    smart_preset_id: str,
    *,
    edits: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project smart preset into tuple authoring payload."""
    preset = get_smart_preset_projection(smart_preset_id)
    tuple_ref = preset["tuple_reference"]
    out_edits = edits if isinstance(edits, dict) else {}
    return {
        "arrangement": tuple_ref["arrangement_id"],
        "task": tuple_ref["phenomenon_id"],
        "agent": tuple_ref["agent_bundle_id"],
        "edits": deepcopy(out_edits),
    }


def build_smart_preset_catalog() -> dict[str, Any]:
    """Build API/UI catalog payload for smart presets."""
    payload = get_smart_preset_projection_contract()
    presets = payload["smart_presets"]
    items: list[dict[str, Any]] = []
    for preset_id in sorted(presets.keys()):
        entry = presets[preset_id]
        tuple_ref = entry["tuple_reference"]
        items.append(
            {
                "id": entry["id"],
                "label": entry["label"],
                "description": entry.get("description"),
                "education": deepcopy(entry.get("education")) if isinstance(entry.get("education"), dict) else None,
                "tuple_reference": deepcopy(tuple_ref),
            }
        )
    return {
        "contract_version": payload["version"],
        "registry_generated": True,
        "smart_presets": items,
    }

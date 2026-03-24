"""Composition contract for (arrangement, task, agent bundle) -> operator subset."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any

from ui.contracts.agent_bundle_registry import (
    AgentBundleRegistryValidationError,
    get_agent_bundle,
    validate_agent_bundle_arrangement_compatibility,
)
from ui.contracts.arrangement_contract import get_arrangement
from ui.contracts.preset_registry import get_preset
from ui.contracts.task_registry import (
    TaskRegistryValidationError,
    resolve_task_implementation_for_tuple,
    validate_task_tuple_policy,
)


class ArrangementTaskAgentCompositionError(ValueError):
    """Raised when tuple composition fails."""

    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        self.code = str(code)
        self.message = str(message)
        self.details = details or {}
        super().__init__(f"[{self.code}] {self.message}")


ARRANGEMENT_TASK_AGENT_COMPOSITION_VERSION = "3.15.0"


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ArrangementTaskAgentCompositionError(
            "COMP_E_INVALID_INPUT",
            f"{label} must be a non-empty string.",
        )
    return value


def _normalize_operator_subset(operator_selections: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for slot in sorted(operator_selections.keys()):
        value = operator_selections[slot]
        if isinstance(value, list):
            normalized[slot] = list(value)
        else:
            normalized[slot] = value
    return normalized


def _to_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def stable_arrangement_task_agent_composition_json(payload: dict[str, Any]) -> str:
    """Return deterministic JSON for composition artifact."""
    return _to_json(payload)


def stable_arrangement_task_agent_composition_hash(payload: dict[str, Any]) -> str:
    """Return deterministic hash for composition artifact."""
    return hashlib.sha256(stable_arrangement_task_agent_composition_json(payload).encode("utf-8")).hexdigest()


def stable_arrangement_task_agent_provenance_json(provenance: dict[str, Any]) -> str:
    """Return deterministic JSON for composition provenance artifact."""
    normalized = deepcopy(provenance)
    if isinstance(normalized, dict):
        normalized.pop("composition_hash", None)
    return _to_json(normalized)


def stable_arrangement_task_agent_provenance_hash(provenance: dict[str, Any]) -> str:
    """Return deterministic hash for composition provenance artifact."""
    return hashlib.sha256(stable_arrangement_task_agent_provenance_json(provenance).encode("utf-8")).hexdigest()


def _compose(
    *,
    arrangement_id: str,
    phenomenon_id: str,
    agent_bundle_id: str,
) -> dict[str, Any]:
    arrangement_key = _require_non_empty_string(arrangement_id, "arrangement_id")
    phenomenon_key = _require_non_empty_string(phenomenon_id, "phenomenon_id")
    bundle_key = _require_non_empty_string(agent_bundle_id, "agent_bundle_id")

    try:
        arrangement = get_arrangement(arrangement_key)
    except Exception as exc:
        raise ArrangementTaskAgentCompositionError(
            "COMP_E_UNKNOWN_ARRANGEMENT",
            f"Unknown arrangement '{arrangement_key}'.",
            details={"arrangement_id": arrangement_key},
        ) from exc

    try:
        validate_agent_bundle_arrangement_compatibility(
            bundle_id=bundle_key,
            arrangement_id=arrangement_key,
        )
        bundle = get_agent_bundle(bundle_key)
    except AgentBundleRegistryValidationError as exc:
        raise ArrangementTaskAgentCompositionError(
            "COMP_E_AGENT_ARRANGEMENT_MISMATCH",
            str(exc),
            details={"arrangement_id": arrangement_key, "agent_bundle_id": bundle_key},
        ) from exc

    try:
        impl = resolve_task_implementation_for_tuple(
            phenomenon_id=phenomenon_key,
            arrangement_id=arrangement_key,
        )
        impl = validate_task_tuple_policy(
            arrangement_id=arrangement_key,
            implementation_id=impl["id"],
            agent_bundle_id=bundle_key,
        )
    except TaskRegistryValidationError as exc:
        text = str(exc)
        if "forbidden by policy" in text:
            code = "COMP_E_TASK_POLICY_FORBIDDEN"
        elif "deferred by policy" in text:
            code = "COMP_E_TASK_POLICY_DEFERRED"
        elif "task tuple incompatible" in text:
            code = "COMP_E_TASK_ARRANGEMENT_INCOMPATIBLE"
        else:
            code = "COMP_E_TASK_RESOLUTION"
        raise ArrangementTaskAgentCompositionError(
            code,
            text,
            details={
                "arrangement_id": arrangement_key,
                "phenomenon_id": phenomenon_key,
                "agent_bundle_id": bundle_key,
            },
        ) from exc

    operator_selections = deepcopy(bundle["operator_selections"])
    arrangement_rules = arrangement["operator_requirements"]
    required_slots = set(arrangement_rules["required_slots"]) | set(impl["required_operators"])
    optional_slots = set(arrangement_rules["optional_slots"]) | set(impl["optional_operators"])
    forbidden_slots = set(arrangement_rules["forbidden_slots"])
    allowed_slots = required_slots | optional_slots

    unknown_slots = sorted(set(operator_selections.keys()) - allowed_slots)
    if unknown_slots:
        raise ArrangementTaskAgentCompositionError(
            "COMP_E_BUNDLE_SLOT_NOT_ALLOWED",
            "Agent bundle contributes slots not allowed by arrangement/task constraints: "
            + ", ".join(unknown_slots),
            details={"unknown_slots": unknown_slots},
        )

    forbidden_used = sorted(slot for slot in operator_selections if slot in forbidden_slots)
    if forbidden_used:
        raise ArrangementTaskAgentCompositionError(
            "COMP_E_FORBIDDEN_SLOT",
            "Agent bundle contributes arrangement-forbidden slots: " + ", ".join(forbidden_used),
            details={"forbidden_slots": forbidden_used},
        )

    missing_required = sorted(slot for slot in required_slots if slot not in operator_selections)
    if missing_required:
        raise ArrangementTaskAgentCompositionError(
            "COMP_E_MISSING_REQUIRED_SLOT",
            "Agent bundle does not satisfy required slots: " + ", ".join(missing_required),
            details={"missing_required_slots": missing_required},
        )

    policy = arrangement["policy_semantics"]
    policy_slot = policy["policy_slot"]
    policy_value = operator_selections.get(policy_slot)
    if policy["forbids_non_null_policy"] and policy_value not in (None, "none"):
        raise ArrangementTaskAgentCompositionError(
            "COMP_E_POLICY_FORBIDDEN",
            "Arrangement forbids non-null policy but bundle provides policy selection.",
            details={"policy_slot": policy_slot, "policy_value": policy_value},
        )
    if policy["requires_non_null_policy"] and policy_value in (None, "none"):
        raise ArrangementTaskAgentCompositionError(
            "COMP_E_POLICY_REQUIRED",
            "Arrangement requires non-null policy but bundle does not provide one.",
            details={"policy_slot": policy_slot, "policy_value": policy_value},
        )

    composed_operator_subset = _normalize_operator_subset(operator_selections)
    axis_to_slot_contribution = {
        "arrangement": {
            "required_slots": sorted(arrangement_rules["required_slots"]),
            "optional_slots": sorted(arrangement_rules["optional_slots"]),
            "forbidden_slots": sorted(arrangement_rules["forbidden_slots"]),
        },
        "task": {
            "implementation_id": impl["id"],
            "required_operators": sorted(impl["required_operators"]),
            "optional_operators": sorted(impl["optional_operators"]),
            "protocol_family": impl["protocol_family"],
        },
        "agent": {
            "bundle_id": bundle["id"],
            "operator_slots": sorted(operator_selections.keys()),
        },
    }
    provenance = {
        "version": ARRANGEMENT_TASK_AGENT_COMPOSITION_VERSION,
        "arrangement_id": arrangement_key,
        "phenomenon_id": phenomenon_key,
        "task_implementation_id": impl["id"],
        "agent_bundle_id": bundle_key,
        "protocol_family": impl["protocol_family"],
        "axis_to_slot_contribution": axis_to_slot_contribution,
    }
    provenance_hash = stable_arrangement_task_agent_provenance_hash(provenance)
    provenance["composition_hash"] = provenance_hash

    artifact = {
        "version": ARRANGEMENT_TASK_AGENT_COMPOSITION_VERSION,
        "operator_subset": composed_operator_subset,
        "provenance": provenance,
    }
    return artifact


def compose_arrangement_task_agent_to_operator_subset(
    *,
    arrangement_id: str,
    phenomenon_id: str,
    agent_bundle_id: str,
) -> dict[str, Any]:
    """Compose deterministic operator subset artifact for (arrangement, task, agent)."""
    return _compose(
        arrangement_id=arrangement_id,
        phenomenon_id=phenomenon_id,
        agent_bundle_id=agent_bundle_id,
    )


def compose_from_preset_reference(
    *,
    preset_id: str,
    agent_bundle_id: str = "rw_classical",
) -> dict[str, Any]:
    """Compatibility wrapper for preset-based entrypoints."""
    preset_key = _require_non_empty_string(preset_id, "preset_id")
    preset = get_preset(preset_key)
    reference = preset.get("task_reference")
    if not isinstance(reference, dict):
        raise ArrangementTaskAgentCompositionError(
            "COMP_E_PRESET_REFERENCE",
            f"Preset '{preset_key}' is missing task_reference.",
        )
    phenomenon_id = _require_non_empty_string(
        reference.get("phenomenon_id"),
        f"preset.{preset_key}.task_reference.phenomenon_id",
    )
    arrangement_id = _require_non_empty_string(
        reference.get("default_arrangement_id"),
        f"preset.{preset_key}.task_reference.default_arrangement_id",
    )
    return _compose(
        arrangement_id=arrangement_id,
        phenomenon_id=phenomenon_id,
        agent_bundle_id=agent_bundle_id,
    )

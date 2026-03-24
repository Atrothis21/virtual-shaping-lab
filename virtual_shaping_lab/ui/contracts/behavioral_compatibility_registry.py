"""Behavioral compatibility registry for tuple-first authoring."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.arrangement_contract import list_arrangement_ids
from ui.contracts.agent_bundle_registry import get_agent_bundle_registry
from ui.contracts.task_registry import get_task_registry


class BehavioralCompatibilityRegistryValidationError(ValueError):
    """Raised when behavioral compatibility registry validation fails."""


BEHAVIORAL_COMPATIBILITY_REGISTRY_VERSION = "3.16.0"
_OUTCOME_VALUES: tuple[str, ...] = (
    "success",
    "partial",
    "structurally_invalid",
    "behaviorally_unsupported",
    "novel",
)
_ALLOWED_EDIT_OPERATORS: tuple[str, ...] = ("eq", "neq", "in", "not_in", "lt", "lte", "gt", "gte")


BEHAVIORAL_COMPATIBILITY_REGISTRY: dict[str, Any] = {
    "version": BEHAVIORAL_COMPATIBILITY_REGISTRY_VERSION,
    "entries": [
        {
            "id": "pavlovian_acquisition_rw_classical_default",
            "tuple": {
                "arrangement_id": "pavlovian",
                "task_implementation_id": "pavlovian_acquisition",
                "agent_bundle_id": "rw_classical",
            },
            "outcome": "success",
            "explanation": "Canonical RW pavlovian acquisition is behaviorally supported.",
        },
        {
            "id": "operant_acquisition_rw_operant_default",
            "tuple": {
                "arrangement_id": "operant",
                "task_implementation_id": "operant_acquisition",
                "agent_bundle_id": "rw_operant",
            },
            "outcome": "success",
            "explanation": "Canonical RW operant acquisition is behaviorally supported.",
        },
        {
            "id": "operant_acquisition_rw_operant_short_horizon",
            "tuple": {
                "arrangement_id": "operant",
                "task_implementation_id": "operant_acquisition",
                "agent_bundle_id": "rw_operant",
            },
            "outcome": "partial",
            "explanation": "Very short schedules may under-express stable action policy signatures.",
            "edit_conditions": [
                {"path": "n_trials", "operator": "lt", "value": 5},
            ],
        },
        {
            "id": "pavlovian_extinction_rw_classical_default",
            "tuple": {
                "arrangement_id": "pavlovian",
                "task_implementation_id": "pavlovian_extinction",
                "agent_bundle_id": "rw_classical",
            },
            "outcome": "success",
            "explanation": "Extinction with classical RW bundle is behaviorally supported.",
        },
        {
            "id": "pavlovian_differential_acquisition_rw_classical_default",
            "tuple": {
                "arrangement_id": "pavlovian",
                "task_implementation_id": "pavlovian_differential_acquisition",
                "agent_bundle_id": "rw_classical",
            },
            "outcome": "success",
            "explanation": "Differential acquisition with classical RW bundle is behaviorally supported.",
        },
        {
            "id": "operant_differential_acquisition_rw_operant_novel",
            "tuple": {
                "arrangement_id": "operant",
                "task_implementation_id": "operant_differential_acquisition",
                "agent_bundle_id": "rw_operant",
            },
            "outcome": "novel",
            "explanation": "Operant differential acquisition is not fully benchmarked for current metric contracts.",
            "rationale_source": "expert_review_v3_16_seed_set",
        },
    ],
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BehavioralCompatibilityRegistryValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BehavioralCompatibilityRegistryValidationError(f"{label} must be a non-empty string.")
    return value


def _validate_edit_conditions(value: Any, label: str) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise BehavioralCompatibilityRegistryValidationError(f"{label} must be a list when provided.")
    out: list[dict[str, Any]] = []
    for idx, raw in enumerate(value):
        item = _require_dict(raw, f"{label}[{idx}]")
        for key in ("path", "operator", "value"):
            if key not in item:
                raise BehavioralCompatibilityRegistryValidationError(
                    f"{label}[{idx}] missing required key: {key}"
                )
        _require_non_empty_string(item["path"], f"{label}[{idx}].path")
        operator = _require_non_empty_string(item["operator"], f"{label}[{idx}].operator")
        if operator not in _ALLOWED_EDIT_OPERATORS:
            allowed = ", ".join(_ALLOWED_EDIT_OPERATORS)
            raise BehavioralCompatibilityRegistryValidationError(
                f"{label}[{idx}].operator must be one of: {allowed}"
            )
        out.append({"path": item["path"], "operator": operator, "value": item["value"]})
    return out


def _validate_entries(entries: Any) -> None:
    if not isinstance(entries, list) or not entries:
        raise BehavioralCompatibilityRegistryValidationError(
            "behavioral_compatibility_registry.entries must be a non-empty list."
        )

    arrangement_ids = set(list_arrangement_ids())
    task_registry = get_task_registry()
    impls = _require_dict(task_registry.get("implementations"), "task_registry.implementations")
    bundles = _require_dict(get_agent_bundle_registry().get("bundles"), "agent_bundle_registry.bundles")

    seen_ids: set[str] = set()
    seen_signatures: set[tuple[str, str, str, tuple[tuple[str, str, str], ...]]] = set()
    baseline_keys: set[tuple[str, str, str]] = set()

    for idx, raw in enumerate(entries):
        entry = _require_dict(raw, f"behavioral_compatibility_registry.entries[{idx}]")
        allowed_keys = {"id", "tuple", "outcome", "explanation", "rationale_source", "edit_conditions"}
        unknown_keys = sorted(set(entry.keys()) - allowed_keys)
        if unknown_keys:
            raise BehavioralCompatibilityRegistryValidationError(
                "behavioral_compatibility_registry.entries["
                f"{idx}] has unsupported keys (edit-conditional branches must be explicit): {', '.join(unknown_keys)}"
            )

        entry_id = _require_non_empty_string(entry.get("id"), f"behavioral_compatibility_registry.entries[{idx}].id")
        if entry_id in seen_ids:
            raise BehavioralCompatibilityRegistryValidationError(
                f"behavioral_compatibility_registry has duplicate entry id: {entry_id}"
            )
        seen_ids.add(entry_id)

        tuple_ref = _require_dict(entry.get("tuple"), f"behavioral_compatibility_registry.entries[{idx}].tuple")
        arrangement_id = _require_non_empty_string(
            tuple_ref.get("arrangement_id"),
            f"behavioral_compatibility_registry.entries[{idx}].tuple.arrangement_id",
        )
        if arrangement_id not in arrangement_ids:
            raise BehavioralCompatibilityRegistryValidationError(
                "behavioral_compatibility_registry.entries["
                f"{idx}].tuple.arrangement_id references unknown arrangement: {arrangement_id}"
            )
        task_implementation_id = _require_non_empty_string(
            tuple_ref.get("task_implementation_id"),
            f"behavioral_compatibility_registry.entries[{idx}].tuple.task_implementation_id",
        )
        if task_implementation_id not in impls:
            raise BehavioralCompatibilityRegistryValidationError(
                "behavioral_compatibility_registry.entries["
                f"{idx}].tuple.task_implementation_id references unknown task implementation: {task_implementation_id}"
            )
        impl = impls[task_implementation_id]
        if impl.get("arrangement_id") != arrangement_id:
            raise BehavioralCompatibilityRegistryValidationError(
                "behavioral_compatibility_registry.entries["
                f"{idx}] tuple arrangement mismatch for implementation '{task_implementation_id}'."
            )
        agent_bundle_id = _require_non_empty_string(
            tuple_ref.get("agent_bundle_id"),
            f"behavioral_compatibility_registry.entries[{idx}].tuple.agent_bundle_id",
        )
        if agent_bundle_id not in bundles:
            raise BehavioralCompatibilityRegistryValidationError(
                "behavioral_compatibility_registry.entries["
                f"{idx}].tuple.agent_bundle_id references unknown bundle: {agent_bundle_id}"
            )
        arrangement_compat = bundles[agent_bundle_id].get("arrangement_compatibility", [])
        if arrangement_id not in arrangement_compat:
            raise BehavioralCompatibilityRegistryValidationError(
                "behavioral_compatibility_registry.entries["
                f"{idx}] tuple is structurally incompatible (bundle not arrangement-compatible)."
            )

        outcome = _require_non_empty_string(
            entry.get("outcome"),
            f"behavioral_compatibility_registry.entries[{idx}].outcome",
        )
        if outcome not in _OUTCOME_VALUES:
            allowed = ", ".join(_OUTCOME_VALUES)
            raise BehavioralCompatibilityRegistryValidationError(
                f"behavioral_compatibility_registry.entries[{idx}].outcome must be one of: {allowed}"
            )
        _require_non_empty_string(
            entry.get("explanation"),
            f"behavioral_compatibility_registry.entries[{idx}].explanation",
        )
        if outcome == "novel":
            _require_non_empty_string(
                entry.get("rationale_source"),
                f"behavioral_compatibility_registry.entries[{idx}].rationale_source",
            )

        edit_conditions = _validate_edit_conditions(
            entry.get("edit_conditions"),
            f"behavioral_compatibility_registry.entries[{idx}].edit_conditions",
        )
        condition_sig = tuple(
            sorted((str(item["path"]), str(item["operator"]), str(item["value"])) for item in edit_conditions)
        )
        signature = (arrangement_id, task_implementation_id, agent_bundle_id, condition_sig)
        if signature in seen_signatures:
            raise BehavioralCompatibilityRegistryValidationError(
                "behavioral_compatibility_registry has duplicate tuple compatibility branch for: "
                f"({arrangement_id}, {task_implementation_id}, {agent_bundle_id})"
            )
        seen_signatures.add(signature)
        if not edit_conditions:
            baseline_keys.add((arrangement_id, task_implementation_id, agent_bundle_id))

    required_baseline: set[tuple[str, str, str]] = set()
    for impl_id, impl in impls.items():
        if impl.get("status") != "active":
            continue
        arrangement_id = str(impl.get("arrangement_id"))
        for bundle_id, bundle in bundles.items():
            compat = bundle.get("arrangement_compatibility", [])
            if arrangement_id in compat:
                required_baseline.add((arrangement_id, impl_id, bundle_id))

    missing = sorted(required_baseline - baseline_keys)
    if missing:
        rendered = ", ".join(f"({a}, {t}, {b})" for a, t, b in missing)
        raise BehavioralCompatibilityRegistryValidationError(
            "behavioral_compatibility_registry missing required baseline compatibility coverage for core tuples: "
            f"{rendered}"
        )


def validate_behavioral_compatibility_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate behavioral compatibility registry contract and return deep copy."""
    payload = deepcopy(BEHAVIORAL_COMPATIBILITY_REGISTRY if registry is None else registry)
    root = _require_dict(payload, "behavioral_compatibility_registry")
    for key in ("version", "entries"):
        if key not in root:
            raise BehavioralCompatibilityRegistryValidationError(
                f"behavioral_compatibility_registry missing required key: {key}"
            )
    _require_non_empty_string(root.get("version"), "behavioral_compatibility_registry.version")
    _validate_entries(root.get("entries"))
    return payload


def get_behavioral_compatibility_registry() -> dict[str, Any]:
    """Return validated behavioral compatibility registry payload."""
    return validate_behavioral_compatibility_registry(BEHAVIORAL_COMPATIBILITY_REGISTRY)


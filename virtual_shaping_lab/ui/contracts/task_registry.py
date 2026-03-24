"""Task registry decoupled from presets with arrangement-scoped implementations."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.arrangement_contract import list_arrangement_ids


class TaskRegistryValidationError(ValueError):
    """Raised when task registry contract validation fails."""


TASK_REGISTRY_VERSION = "3.15.0"

REQUIRED_TASK_IDS: tuple[str, ...] = (
    "acquisition",
    "extinction",
    "differential_acquisition",
)

_ALLOWED_IMPLEMENTATION_STATUS: set[str] = {"active", "deferred", "experimental"}

TASK_REGISTRY: dict[str, Any] = {
    "version": TASK_REGISTRY_VERSION,
    "phenomena": {
        "acquisition": {
            "id": "acquisition",
            "label": "Acquisition",
            "description": "Core associative strength acquisition phenomenon.",
            "implementation_ids": ["pavlovian_acquisition", "operant_acquisition"],
        },
        "extinction": {
            "id": "extinction",
            "label": "Extinction",
            "description": "Core extinction phenomenon.",
            "implementation_ids": ["pavlovian_extinction", "operant_extinction"],
        },
        "differential_acquisition": {
            "id": "differential_acquisition",
            "label": "Differential Acquisition",
            "description": "Core discrimination acquisition phenomenon.",
            "implementation_ids": [
                "pavlovian_differential_acquisition",
                "operant_differential_acquisition",
            ],
        },
    },
    "implementations": {
        "pavlovian_acquisition": {
            "id": "pavlovian_acquisition",
            "phenomenon_id": "acquisition",
            "arrangement_id": "pavlovian",
            "protocol_family": "acquisition",
            "required_operators": ["phi", "p", "delta", "w", "omega", "m"],
            "optional_operators": ["c", "g", "e", "a"],
            "status": "active",
        },
        "operant_acquisition": {
            "id": "operant_acquisition",
            "phenomenon_id": "acquisition",
            "arrangement_id": "operant",
            "protocol_family": "operant_acquisition",
            "required_operators": ["phi", "p", "delta", "w", "pi", "omega", "m"],
            "optional_operators": ["c", "g", "e", "a"],
            "status": "active",
        },
        "pavlovian_extinction": {
            "id": "pavlovian_extinction",
            "phenomenon_id": "extinction",
            "arrangement_id": "pavlovian",
            "protocol_family": "extinction",
            "required_operators": ["phi", "p", "delta", "w", "omega", "m"],
            "optional_operators": ["c", "g", "e", "a"],
            "status": "active",
        },
        "operant_extinction": {
            "id": "operant_extinction",
            "phenomenon_id": "extinction",
            "arrangement_id": "operant",
            "protocol_family": "operant_extinction",
            "required_operators": ["phi", "p", "delta", "w", "pi", "omega", "m"],
            "optional_operators": ["c", "g", "e", "a"],
            "status": "experimental",
        },
        "pavlovian_differential_acquisition": {
            "id": "pavlovian_differential_acquisition",
            "phenomenon_id": "differential_acquisition",
            "arrangement_id": "pavlovian",
            "protocol_family": "differential_acquisition",
            "required_operators": ["phi", "p", "delta", "w", "omega", "m"],
            "optional_operators": ["c", "g", "e", "a"],
            "status": "active",
        },
        "operant_differential_acquisition": {
            "id": "operant_differential_acquisition",
            "phenomenon_id": "differential_acquisition",
            "arrangement_id": "operant",
            "protocol_family": "operant_differential_acquisition",
            "required_operators": ["phi", "p", "delta", "w", "pi", "omega", "m"],
            "optional_operators": ["c", "g", "e", "a"],
            "status": "experimental",
        },
        "hybrid_acquisition_transfer": {
            "id": "hybrid_acquisition_transfer",
            "phenomenon_id": "acquisition",
            "arrangement_id": "hybrid",
            "protocol_family": "hybrid_acquisition_transfer",
            "required_operators": ["phi", "p", "delta", "w", "omega", "m"],
            "optional_operators": ["c", "g", "e", "a", "pi"],
            "status": "experimental",
        },
        "hybrid_extinction_bridge": {
            "id": "hybrid_extinction_bridge",
            "phenomenon_id": "extinction",
            "arrangement_id": "hybrid",
            "protocol_family": "hybrid_extinction_bridge",
            "required_operators": ["phi", "p", "delta", "w", "omega", "m"],
            "optional_operators": ["c", "g", "e", "a", "pi"],
            "status": "deferred",
        },
    },
    "hybrid_policy": {
        "supported_hybrid_implementations": ["hybrid_acquisition_transfer"],
        "deferred_hybrid_implementations": ["hybrid_extinction_bridge"],
        "forbidden_tuples": [
            {
                "arrangement_id": "hybrid",
                "phenomenon_id": "acquisition",
                "agent_bundle_id": "legacy_hybrid_bundle",
                "reason": "Legacy hybrid agent bundle is forbidden until hybrid control semantics are formalized.",
            }
        ],
    },
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TaskRegistryValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TaskRegistryValidationError(f"{label} must be a non-empty string.")
    return value


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise TaskRegistryValidationError(f"{label} must be a list of strings.")
    out: list[str] = []
    seen: set[str] = set()
    for idx, item in enumerate(value):
        key = _require_non_empty_string(item, f"{label}[{idx}]")
        if key in seen:
            raise TaskRegistryValidationError(f"{label} has duplicate value: {key}")
        seen.add(key)
        out.append(key)
    return out


def _validate_phenomena(phenomena: dict[str, Any], implementations: dict[str, Any]) -> None:
    expected = set(REQUIRED_TASK_IDS)
    actual = set(phenomena.keys())
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        detail_parts: list[str] = []
        if missing:
            detail_parts.append(f"missing task IDs: {', '.join(missing)}")
        if extra:
            detail_parts.append(f"unexpected task IDs: {', '.join(extra)}")
        raise TaskRegistryValidationError(
            "task_registry.phenomena must contain exactly required task IDs "
            f"({'; '.join(detail_parts)})"
        )

    for phenomenon_id, raw in phenomena.items():
        item = _require_dict(raw, f"task_registry.phenomena.{phenomenon_id}")
        item_id = _require_non_empty_string(item.get("id"), f"task_registry.phenomena.{phenomenon_id}.id")
        if item_id != phenomenon_id:
            raise TaskRegistryValidationError(
                f"task_registry.phenomena.{phenomenon_id}.id must match phenomenon key '{phenomenon_id}'."
            )
        _require_non_empty_string(item.get("label"), f"task_registry.phenomena.{phenomenon_id}.label")
        _require_non_empty_string(
            item.get("description"), f"task_registry.phenomena.{phenomenon_id}.description"
        )
        impl_ids = _require_string_list(
            item.get("implementation_ids"),
            f"task_registry.phenomena.{phenomenon_id}.implementation_ids",
        )
        for impl_id in impl_ids:
            if impl_id not in implementations:
                raise TaskRegistryValidationError(
                    f"task_registry.phenomena.{phenomenon_id}.implementation_ids "
                    f"references unknown implementation id: {impl_id}"
                )


def _validate_implementations(implementations: dict[str, Any], phenomena: dict[str, Any]) -> None:
    known_arrangements = set(list_arrangement_ids())
    known_phenomena = set(phenomena.keys())

    for impl_key, raw in implementations.items():
        impl = _require_dict(raw, f"task_registry.implementations.{impl_key}")
        for key in (
            "id",
            "phenomenon_id",
            "arrangement_id",
            "protocol_family",
            "required_operators",
            "optional_operators",
            "status",
        ):
            if key not in impl:
                raise TaskRegistryValidationError(
                    f"task_registry.implementations.{impl_key} missing required key: {key}"
                )

        impl_id = _require_non_empty_string(
            impl.get("id"), f"task_registry.implementations.{impl_key}.id"
        )
        if impl_id != impl_key:
            raise TaskRegistryValidationError(
                f"task_registry.implementations.{impl_key}.id must match implementation key '{impl_key}'."
            )
        phenomenon_id = _require_non_empty_string(
            impl.get("phenomenon_id"), f"task_registry.implementations.{impl_key}.phenomenon_id"
        )
        if phenomenon_id not in known_phenomena:
            raise TaskRegistryValidationError(
                f"task_registry.implementations.{impl_key}.phenomenon_id references unknown phenomenon: {phenomenon_id}"
            )
        arrangement_id = _require_non_empty_string(
            impl.get("arrangement_id"), f"task_registry.implementations.{impl_key}.arrangement_id"
        )
        if arrangement_id not in known_arrangements and arrangement_id != "hybrid":
            raise TaskRegistryValidationError(
                f"task_registry.implementations.{impl_key}.arrangement_id is not recognized: {arrangement_id}"
            )
        if arrangement_id != "hybrid" and not impl_key.startswith(f"{arrangement_id}_"):
            raise TaskRegistryValidationError(
                f"task_registry.implementations.{impl_key} must use arrangement-scoped ID prefix '{arrangement_id}_'."
            )

        _require_non_empty_string(
            impl.get("protocol_family"),
            f"task_registry.implementations.{impl_key}.protocol_family",
        )
        required_ops = _require_string_list(
            impl.get("required_operators"),
            f"task_registry.implementations.{impl_key}.required_operators",
        )
        optional_ops = _require_string_list(
            impl.get("optional_operators"),
            f"task_registry.implementations.{impl_key}.optional_operators",
        )
        overlap = sorted(set(required_ops).intersection(set(optional_ops)))
        if overlap:
            raise TaskRegistryValidationError(
                f"task_registry.implementations.{impl_key} required/optional operators overlap: {', '.join(overlap)}"
            )
        if arrangement_id == "operant" and "pi" not in required_ops:
            raise TaskRegistryValidationError(
                f"task_registry.implementations.{impl_key} must require 'pi' for operant arrangement."
            )
        if arrangement_id == "pavlovian" and "pi" in required_ops:
            raise TaskRegistryValidationError(
                f"task_registry.implementations.{impl_key} cannot require 'pi' for pavlovian arrangement."
            )
        status = _require_non_empty_string(
            impl.get("status"), f"task_registry.implementations.{impl_key}.status"
        )
        if status not in _ALLOWED_IMPLEMENTATION_STATUS:
            raise TaskRegistryValidationError(
                f"task_registry.implementations.{impl_key}.status must be one of: "
                f"{', '.join(sorted(_ALLOWED_IMPLEMENTATION_STATUS))}"
            )


def _validate_hybrid_policy(hybrid_policy: dict[str, Any], implementations: dict[str, Any]) -> None:
    supported = _require_string_list(
        hybrid_policy.get("supported_hybrid_implementations"),
        "task_registry.hybrid_policy.supported_hybrid_implementations",
    )
    deferred = _require_string_list(
        hybrid_policy.get("deferred_hybrid_implementations"),
        "task_registry.hybrid_policy.deferred_hybrid_implementations",
    )
    overlap = sorted(set(supported).intersection(set(deferred)))
    if overlap:
        raise TaskRegistryValidationError(
            "task_registry.hybrid_policy supported/deferred overlap: "
            f"{', '.join(overlap)}"
        )

    for implementation_id in supported + deferred:
        if implementation_id not in implementations:
            raise TaskRegistryValidationError(
                "task_registry.hybrid_policy references unknown implementation id: "
                f"{implementation_id}"
            )
        arrangement_id = implementations[implementation_id]["arrangement_id"]
        if arrangement_id != "hybrid":
            raise TaskRegistryValidationError(
                "task_registry.hybrid_policy implementation must be hybrid-scoped: "
                f"{implementation_id}"
            )

    forbidden_tuples = hybrid_policy.get("forbidden_tuples")
    if not isinstance(forbidden_tuples, list):
        raise TaskRegistryValidationError("task_registry.hybrid_policy.forbidden_tuples must be a list.")
    for idx, raw_tuple in enumerate(forbidden_tuples):
        entry = _require_dict(raw_tuple, f"task_registry.hybrid_policy.forbidden_tuples[{idx}]")
        for key in ("arrangement_id", "phenomenon_id", "agent_bundle_id", "reason"):
            if key not in entry:
                raise TaskRegistryValidationError(
                    f"task_registry.hybrid_policy.forbidden_tuples[{idx}] missing required key: {key}"
                )
            _require_non_empty_string(
                entry.get(key), f"task_registry.hybrid_policy.forbidden_tuples[{idx}].{key}"
            )


def validate_task_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate task registry contract and return deep copy."""
    payload = deepcopy(TASK_REGISTRY if registry is None else registry)
    root = _require_dict(payload, "task_registry")
    for key in ("version", "phenomena", "implementations", "hybrid_policy"):
        if key not in root:
            raise TaskRegistryValidationError(f"task_registry missing required key: {key}")
    _require_non_empty_string(root.get("version"), "task_registry.version")
    phenomena = _require_dict(root.get("phenomena"), "task_registry.phenomena")
    implementations = _require_dict(root.get("implementations"), "task_registry.implementations")
    _validate_implementations(implementations, phenomena)
    _validate_phenomena(phenomena, implementations)
    _validate_hybrid_policy(
        _require_dict(root.get("hybrid_policy"), "task_registry.hybrid_policy"),
        implementations,
    )
    return payload


def get_task_registry() -> dict[str, Any]:
    """Return validated task registry payload."""
    return validate_task_registry(TASK_REGISTRY)


def list_task_ids() -> tuple[str, ...]:
    """Return stable phenomenon task ID ordering."""
    payload = get_task_registry()
    return tuple(sorted(payload["phenomena"].keys()))


def list_task_implementation_ids() -> tuple[str, ...]:
    """Return stable task implementation ID ordering."""
    payload = get_task_registry()
    return tuple(sorted(payload["implementations"].keys()))


def get_task_implementation(implementation_id: str) -> dict[str, Any]:
    """Return task implementation by ID."""
    key = _require_non_empty_string(implementation_id, "implementation_id")
    payload = get_task_registry()
    implementations = payload["implementations"]
    if key not in implementations:
        known = ", ".join(sorted(implementations.keys()))
        raise TaskRegistryValidationError(
            f"Unknown task implementation id '{key}'. Known IDs: {known}"
        )
    return deepcopy(implementations[key])


def resolve_task_implementation_for_tuple(
    *,
    phenomenon_id: str,
    arrangement_id: str,
) -> dict[str, Any]:
    """Resolve arrangement-scoped task implementation for a phenomenon."""
    pheno = _require_non_empty_string(phenomenon_id, "phenomenon_id")
    arrangement = _require_non_empty_string(arrangement_id, "arrangement_id")
    payload = get_task_registry()
    phenomena = payload["phenomena"]
    if pheno not in phenomena:
        known = ", ".join(sorted(phenomena.keys()))
        raise TaskRegistryValidationError(f"Unknown phenomenon_id '{pheno}'. Known: {known}")

    impl_ids = list(phenomena[pheno]["implementation_ids"])
    matches = [
        payload["implementations"][impl_id]
        for impl_id in impl_ids
        if payload["implementations"][impl_id]["arrangement_id"] == arrangement
    ]
    if len(matches) != 1:
        raise TaskRegistryValidationError(
            f"Could not resolve unique task implementation for ({arrangement}, {pheno})."
        )
    return deepcopy(matches[0])


def validate_task_tuple_policy(
    *,
    arrangement_id: str,
    implementation_id: str,
    agent_bundle_id: str = "*",
) -> dict[str, Any]:
    """Validate tuple policy for (arrangement, task implementation, agent bundle)."""
    arrangement = _require_non_empty_string(arrangement_id, "arrangement_id")
    impl = get_task_implementation(implementation_id)
    agent_bundle = _require_non_empty_string(agent_bundle_id, "agent_bundle_id")
    payload = get_task_registry()

    impl_arrangement = impl["arrangement_id"]
    impl_id = impl["id"]
    phenomenon_id = impl["phenomenon_id"]
    hybrid_policy = payload["hybrid_policy"]
    supported_hybrid = set(hybrid_policy["supported_hybrid_implementations"])
    deferred_hybrid = set(hybrid_policy["deferred_hybrid_implementations"])

    if impl_arrangement == "hybrid":
        if arrangement != "hybrid":
            raise TaskRegistryValidationError(
                f"task tuple incompatible: implementation '{impl_id}' requires arrangement 'hybrid'."
            )
        if impl_id in deferred_hybrid:
            raise TaskRegistryValidationError(
                f"task tuple deferred by policy for implementation '{impl_id}'."
            )
        if impl_id not in supported_hybrid:
            raise TaskRegistryValidationError(
                f"task tuple uses unsupported hybrid implementation '{impl_id}'."
            )
    elif arrangement != impl_arrangement:
        raise TaskRegistryValidationError(
            f"task tuple incompatible: arrangement '{arrangement}' does not match implementation arrangement '{impl_arrangement}'."
        )

    for tuple_rule in hybrid_policy["forbidden_tuples"]:
        if tuple_rule["arrangement_id"] != arrangement:
            continue
        if tuple_rule["phenomenon_id"] != "*" and tuple_rule["phenomenon_id"] != phenomenon_id:
            continue
        if tuple_rule["agent_bundle_id"] != "*" and tuple_rule["agent_bundle_id"] != agent_bundle:
            continue
        raise TaskRegistryValidationError(
            "task tuple forbidden by policy: "
            f"{tuple_rule['reason']}"
        )

    return impl


def build_thin_preset_task_reference(preset_id: str) -> dict[str, str]:
    """Build thin preset reference to task registry with pavlovian default arrangement."""
    preset = _require_non_empty_string(preset_id, "preset_id")
    if preset not in REQUIRED_TASK_IDS:
        known = ", ".join(REQUIRED_TASK_IDS)
        raise TaskRegistryValidationError(
            f"preset_id '{preset}' has no thin task reference mapping. Known: {known}"
        )
    implementation = resolve_task_implementation_for_tuple(
        phenomenon_id=preset,
        arrangement_id="pavlovian",
    )
    return {
        "phenomenon_id": preset,
        "default_arrangement_id": "pavlovian",
        "default_implementation_id": implementation["id"],
    }


def validate_preset_task_reference(reference: dict[str, Any]) -> dict[str, str]:
    """Validate thin preset -> task registry reference mapping."""
    root = _require_dict(reference, "task_reference")
    for key in ("phenomenon_id", "default_arrangement_id", "default_implementation_id"):
        if key not in root:
            raise TaskRegistryValidationError(f"task_reference missing required key: {key}")
    phenomenon_id = _require_non_empty_string(root.get("phenomenon_id"), "task_reference.phenomenon_id")
    arrangement_id = _require_non_empty_string(
        root.get("default_arrangement_id"),
        "task_reference.default_arrangement_id",
    )
    implementation_id = _require_non_empty_string(
        root.get("default_implementation_id"),
        "task_reference.default_implementation_id",
    )
    resolved = resolve_task_implementation_for_tuple(
        phenomenon_id=phenomenon_id,
        arrangement_id=arrangement_id,
    )
    if resolved["id"] != implementation_id:
        raise TaskRegistryValidationError(
            "task_reference.default_implementation_id does not match resolved "
            f"({arrangement_id}, {phenomenon_id}) implementation."
        )
    return {
        "phenomenon_id": phenomenon_id,
        "default_arrangement_id": arrangement_id,
        "default_implementation_id": implementation_id,
    }

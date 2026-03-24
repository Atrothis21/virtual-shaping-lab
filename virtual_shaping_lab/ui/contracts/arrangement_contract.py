"""Arrangement-axis contract surface for factorized V3 composition."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any


class ArrangementContractValidationError(ValueError):
    """Raised when arrangement contract validation fails."""


ARRANGEMENT_CONTRACT_VERSION = "3.15.0"

REQUIRED_ARRANGEMENT_IDS: tuple[str, ...] = ("pavlovian", "operant")

_REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = ("version", "arrangements")
_REQUIRED_ARRANGEMENT_KEYS: tuple[str, ...] = (
    "id",
    "label",
    "description",
    "policy_semantics",
    "operator_requirements",
)
_REQUIRED_POLICY_KEYS: tuple[str, ...] = (
    "policy_slot",
    "allowed_values",
    "forbidden_values",
    "requires_non_null_policy",
    "forbids_non_null_policy",
)
_REQUIRED_REQUIREMENT_KEYS: tuple[str, ...] = ("required_slots", "optional_slots", "forbidden_slots")


ARRANGEMENT_CONTRACT: dict[str, Any] = {
    "version": ARRANGEMENT_CONTRACT_VERSION,
    "arrangements": {
        "pavlovian": {
            "id": "pavlovian",
            "label": "Pavlovian",
            "description": "Classical conditioning arrangement with no action policy controller.",
            "policy_semantics": {
                "policy_slot": "pi",
                "allowed_values": ["none"],
                "forbidden_values": ["deterministic", "epsilon_greedy", "softmax"],
                "requires_non_null_policy": False,
                "forbids_non_null_policy": True,
            },
            "operator_requirements": {
                "required_slots": ["phi", "p", "delta", "w", "omega", "m"],
                "optional_slots": ["c", "g", "e", "a"],
                "forbidden_slots": ["pi"],
            },
        },
        "operant": {
            "id": "operant",
            "label": "Operant",
            "description": "Instrumental conditioning arrangement with an explicit policy controller.",
            "policy_semantics": {
                "policy_slot": "pi",
                "allowed_values": ["deterministic", "epsilon_greedy", "softmax"],
                "forbidden_values": ["none"],
                "requires_non_null_policy": True,
                "forbids_non_null_policy": False,
            },
            "operator_requirements": {
                "required_slots": ["phi", "p", "delta", "w", "pi", "omega", "m"],
                "optional_slots": ["c", "g", "e", "a"],
                "forbidden_slots": [],
            },
        },
    },
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ArrangementContractValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ArrangementContractValidationError(f"{label} must be a non-empty string.")
    return value


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ArrangementContractValidationError(f"{label} must be boolean.")
    return value


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ArrangementContractValidationError(f"{label} must be a list of strings.")
    out: list[str] = []
    seen: set[str] = set()
    for idx, item in enumerate(value):
        key = _require_non_empty_string(item, f"{label}[{idx}]")
        if key in seen:
            raise ArrangementContractValidationError(f"{label} has duplicate value: {key}")
        seen.add(key)
        out.append(key)
    return out


def _validate_policy_semantics(policy: dict[str, Any], label: str) -> None:
    for key in _REQUIRED_POLICY_KEYS:
        if key not in policy:
            raise ArrangementContractValidationError(f"{label} missing required key: {key}")

    _require_non_empty_string(policy.get("policy_slot"), f"{label}.policy_slot")
    allowed = _require_string_list(policy.get("allowed_values"), f"{label}.allowed_values")
    forbidden = _require_string_list(policy.get("forbidden_values"), f"{label}.forbidden_values")
    requires_non_null = _require_bool(
        policy.get("requires_non_null_policy"), f"{label}.requires_non_null_policy"
    )
    forbids_non_null = _require_bool(
        policy.get("forbids_non_null_policy"), f"{label}.forbids_non_null_policy"
    )

    overlap = sorted(set(allowed).intersection(set(forbidden)))
    if overlap:
        raise ArrangementContractValidationError(
            f"{label} allowed/forbidden policy values overlap: {', '.join(overlap)}"
        )
    if requires_non_null and forbids_non_null:
        raise ArrangementContractValidationError(
            f"{label} cannot both require and forbid non-null policy."
        )
    if forbids_non_null and "none" not in allowed:
        raise ArrangementContractValidationError(
            f"{label} must allow 'none' when forbids_non_null_policy is true."
        )
    if requires_non_null and "none" not in forbidden:
        raise ArrangementContractValidationError(
            f"{label} must forbid 'none' when requires_non_null_policy is true."
        )


def _validate_operator_requirements(requirements: dict[str, Any], label: str) -> None:
    for key in _REQUIRED_REQUIREMENT_KEYS:
        if key not in requirements:
            raise ArrangementContractValidationError(f"{label} missing required key: {key}")

    required_slots = _require_string_list(requirements.get("required_slots"), f"{label}.required_slots")
    optional_slots = _require_string_list(requirements.get("optional_slots"), f"{label}.optional_slots")
    forbidden_slots = _require_string_list(requirements.get("forbidden_slots"), f"{label}.forbidden_slots")

    overlaps = (
        set(required_slots).intersection(optional_slots)
        | set(required_slots).intersection(forbidden_slots)
        | set(optional_slots).intersection(forbidden_slots)
    )
    if overlaps:
        raise ArrangementContractValidationError(
            f"{label} slot sets overlap: {', '.join(sorted(overlaps))}"
        )


def validate_arrangement_contract(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate arrangement contract and return normalized deep copy."""
    out = deepcopy(ARRANGEMENT_CONTRACT if payload is None else payload)
    root = _require_dict(out, "arrangement_contract")

    for key in _REQUIRED_TOP_LEVEL_KEYS:
        if key not in root:
            raise ArrangementContractValidationError(
                f"arrangement_contract missing required key: {key}"
            )

    _require_non_empty_string(root.get("version"), "arrangement_contract.version")
    arrangements = _require_dict(root.get("arrangements"), "arrangement_contract.arrangements")
    expected = set(REQUIRED_ARRANGEMENT_IDS)
    actual = set(arrangements.keys())
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        parts: list[str] = []
        if missing:
            parts.append(f"missing IDs: {', '.join(missing)}")
        if extra:
            parts.append(f"unexpected IDs: {', '.join(extra)}")
        raise ArrangementContractValidationError(
            "arrangement_contract.arrangements must include exactly required IDs "
            f"({'; '.join(parts)})"
        )

    for arrangement_id in REQUIRED_ARRANGEMENT_IDS:
        entry = _require_dict(
            arrangements.get(arrangement_id), f"arrangement_contract.arrangements.{arrangement_id}"
        )
        for key in _REQUIRED_ARRANGEMENT_KEYS:
            if key not in entry:
                raise ArrangementContractValidationError(
                    f"arrangement_contract.arrangements.{arrangement_id} missing required key: {key}"
                )
        entry_id = _require_non_empty_string(
            entry.get("id"), f"arrangement_contract.arrangements.{arrangement_id}.id"
        )
        if entry_id != arrangement_id:
            raise ArrangementContractValidationError(
                "arrangement_contract.arrangements."
                f"{arrangement_id}.id must match arrangement key '{arrangement_id}'."
            )
        _require_non_empty_string(
            entry.get("label"), f"arrangement_contract.arrangements.{arrangement_id}.label"
        )
        _require_non_empty_string(
            entry.get("description"), f"arrangement_contract.arrangements.{arrangement_id}.description"
        )
        _validate_policy_semantics(
            _require_dict(
                entry.get("policy_semantics"),
                f"arrangement_contract.arrangements.{arrangement_id}.policy_semantics",
            ),
            f"arrangement_contract.arrangements.{arrangement_id}.policy_semantics",
        )
        _validate_operator_requirements(
            _require_dict(
                entry.get("operator_requirements"),
                f"arrangement_contract.arrangements.{arrangement_id}.operator_requirements",
            ),
            f"arrangement_contract.arrangements.{arrangement_id}.operator_requirements",
        )

    return root


def get_arrangement_contract() -> dict[str, Any]:
    """Return validated arrangement contract payload."""
    return validate_arrangement_contract(ARRANGEMENT_CONTRACT)


def list_arrangement_ids() -> tuple[str, ...]:
    """Return stable arrangement ID ordering."""
    return REQUIRED_ARRANGEMENT_IDS


def get_arrangement(arrangement_id: str) -> dict[str, Any]:
    """Return arrangement contract entry for an arrangement ID."""
    key = _require_non_empty_string(arrangement_id, "arrangement_id")
    payload = get_arrangement_contract()
    arrangements = payload["arrangements"]
    if key not in arrangements:
        known = ", ".join(REQUIRED_ARRANGEMENT_IDS)
        raise ArrangementContractValidationError(
            f"Unknown arrangement_id '{key}'. Known IDs: {known}"
        )
    return deepcopy(arrangements[key])


def stable_arrangement_contract_json(payload: dict[str, Any] | None = None) -> str:
    """Return deterministic JSON serialization for arrangement contract."""
    normalized = validate_arrangement_contract(payload)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"))


def stable_arrangement_contract_hash(payload: dict[str, Any] | None = None) -> str:
    """Return deterministic hash for arrangement contract."""
    encoded = stable_arrangement_contract_json(payload).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


"""Behavioral compatibility evaluation engine for tuple-first authoring."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.behavioral_compatibility_registry import (
    get_behavioral_compatibility_registry,
)
from ui.contracts.operator_legality_engine import (
    evaluate_operator_legality,
)
from ui.contracts.task_registry import resolve_task_implementation_for_tuple


BEHAVIORAL_COMPATIBILITY_ENGINE_VERSION = "3.16.0"


def _normalize_string(value: Any) -> str:
    return str(value or "").strip()


def _edit_value_from_payload(edits: dict[str, Any], path: str) -> Any:
    key = _normalize_string(path)
    if not key:
        return None
    return edits.get(key)


def _condition_matches(*, edits: dict[str, Any], condition: dict[str, Any]) -> bool:
    left = _edit_value_from_payload(edits, str(condition["path"]))
    operator = str(condition["operator"])
    right = condition["value"]

    if operator == "eq":
        return left == right
    if operator == "neq":
        return left != right
    if operator == "in":
        return isinstance(right, list) and left in right
    if operator == "not_in":
        return isinstance(right, list) and left not in right
    if operator in {"lt", "lte", "gt", "gte"}:
        try:
            left_num = float(left)
            right_num = float(right)
        except (TypeError, ValueError):
            return False
        if operator == "lt":
            return left_num < right_num
        if operator == "lte":
            return left_num <= right_num
        if operator == "gt":
            return left_num > right_num
        return left_num >= right_num
    return False


def _matches_all_conditions(*, edits: dict[str, Any], conditions: list[dict[str, Any]]) -> bool:
    return all(_condition_matches(edits=edits, condition=condition) for condition in conditions)


def _select_behavioral_entry(
    *,
    arrangement_id: str,
    task_implementation_id: str,
    agent_bundle_id: str,
    edits: dict[str, Any],
) -> dict[str, Any] | None:
    payload = get_behavioral_compatibility_registry()
    entries = payload["entries"]

    candidates: list[dict[str, Any]] = []
    for entry in entries:
        tuple_ref = entry["tuple"]
        if tuple_ref["arrangement_id"] != arrangement_id:
            continue
        if tuple_ref["task_implementation_id"] != task_implementation_id:
            continue
        if tuple_ref["agent_bundle_id"] != agent_bundle_id:
            continue
        conditions = list(entry.get("edit_conditions", []) or [])
        if _matches_all_conditions(edits=edits, conditions=conditions):
            candidates.append(entry)

    if not candidates:
        return None

    # Deterministic preference: more-specific condition branches first, then stable id ordering.
    ranked = sorted(
        candidates,
        key=lambda item: (-len(list(item.get("edit_conditions", []) or [])), str(item["id"])),
    )
    return deepcopy(ranked[0])


def evaluate_behavioral_compatibility(
    *,
    arrangement_id: str,
    phenomenon_id: str,
    agent_bundle_id: str,
    edits: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve behavioral compatibility status and explanation for a tuple."""
    arrangement = _normalize_string(arrangement_id)
    phenomenon = _normalize_string(phenomenon_id)
    bundle = _normalize_string(agent_bundle_id)
    edit_payload = dict(edits or {})

    tuple_context = {
        "arrangement_id": arrangement,
        "phenomenon_id": phenomenon,
        "agent_bundle_id": bundle,
    }

    legality_diagnostics = evaluate_operator_legality(
        arrangement_id=arrangement,
        phenomenon_id=phenomenon,
        agent_bundle_id=bundle,
    )
    if legality_diagnostics:
        return {
            "engine_version": BEHAVIORAL_COMPATIBILITY_ENGINE_VERSION,
            "tuple_context": tuple_context,
            "task_implementation_id": None,
            "status": "structurally_invalid",
            "source": "legality_engine",
            "explanation": "Tuple is structurally invalid; resolve legality issues before behavioral prediction.",
            "legality": {
                "is_legal": False,
                "diagnostics": deepcopy(legality_diagnostics),
            },
            "unmet_behavioral_requirements": [],
            "rationale_source": None,
            "matched_registry_entry_id": None,
        }

    implementation = resolve_task_implementation_for_tuple(
        phenomenon_id=phenomenon,
        arrangement_id=arrangement,
    )
    impl_id = implementation["id"]
    selected = _select_behavioral_entry(
        arrangement_id=arrangement,
        task_implementation_id=impl_id,
        agent_bundle_id=bundle,
        edits=edit_payload,
    )

    if selected is None:
        return {
            "engine_version": BEHAVIORAL_COMPATIBILITY_ENGINE_VERSION,
            "tuple_context": tuple_context,
            "task_implementation_id": impl_id,
            "status": "behaviorally_unsupported",
            "source": "behavioral_registry_fallback",
            "explanation": "No behavioral compatibility entry found for this legal tuple.",
            "legality": {
                "is_legal": True,
                "diagnostics": [],
            },
            "unmet_behavioral_requirements": [
                {
                    "code": "BHV_E_MISSING_REGISTRY_COVERAGE",
                    "message": "Add behavioral compatibility registry coverage for this tuple.",
                }
            ],
            "rationale_source": None,
            "matched_registry_entry_id": None,
        }

    return {
        "engine_version": BEHAVIORAL_COMPATIBILITY_ENGINE_VERSION,
        "tuple_context": tuple_context,
        "task_implementation_id": impl_id,
        "status": selected["outcome"],
        "source": "behavioral_registry",
        "explanation": selected["explanation"],
        "legality": {
            "is_legal": True,
            "diagnostics": [],
        },
        "unmet_behavioral_requirements": (
            []
            if selected["outcome"] in {"success", "partial", "novel"}
            else [
                {
                    "code": "BHV_E_UNSUPPORTED_BEHAVIOR",
                    "message": "Behavioral support for this tuple is currently not available.",
                }
            ]
        ),
        "rationale_source": selected.get("rationale_source"),
        "matched_registry_entry_id": selected["id"],
    }


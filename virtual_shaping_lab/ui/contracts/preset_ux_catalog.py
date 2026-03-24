"""Preset UX catalog contract built from smart preset + compatibility contracts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.behavioral_compatibility_engine import evaluate_behavioral_compatibility
from ui.contracts.smart_preset_projection import build_smart_preset_catalog


PRESET_UX_CATALOG_VERSION = "3.17.0"

_COMPATIBILITY_STATUS_ORDER: dict[str, int] = {
    "success": 0,
    "partial": 1,
    "novel": 2,
    "behaviorally_unsupported": 3,
}

_PHENOMENON_CLASS_BY_ID: dict[str, str] = {
    "acquisition": "acquisition",
    "extinction": "extinction",
    "differential_acquisition": "discrimination",
}

_ROUTE_BY_PHENOMENON_ID: dict[str, str] = {
    "acquisition": "/ui/presets/acquisition.html",
    "extinction": "/ui/presets/extinction.html",
    "differential_acquisition": "/ui/presets/differential_acquisition.html",
}


def _normalize_status(value: Any) -> str:
    key = str(value or "").strip().lower()
    if key in _COMPATIBILITY_STATUS_ORDER:
        return key
    return "behaviorally_unsupported"


def _compatibility_to_ux_state(status: str) -> str:
    if status == "success":
        return "recommended"
    if status in {"partial", "novel"}:
        return "exploratory"
    return "caution"


def build_preset_ux_catalog() -> dict[str, Any]:
    """Build preset UX catalog hierarchy with compatibility-aware ordering."""
    smart = build_smart_preset_catalog()
    raw_presets = list(smart.get("smart_presets", []))

    grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for raw in raw_presets:
        tuple_ref = raw.get("tuple_reference", {})
        arrangement_id = str(tuple_ref.get("arrangement_id") or "").strip().lower()
        phenomenon_id = str(tuple_ref.get("phenomenon_id") or "").strip().lower()
        agent_bundle_id = str(tuple_ref.get("agent_bundle_id") or "").strip().lower()

        compatibility = evaluate_behavioral_compatibility(
            arrangement_id=arrangement_id,
            phenomenon_id=phenomenon_id,
            agent_bundle_id=agent_bundle_id,
            edits={},
        )
        status = _normalize_status(compatibility.get("status"))
        # Structural-invalid is a legality/composition failure signal and must never be a UX compatibility state.
        if status == "structurally_invalid":
            continue

        phenomenon_class = _PHENOMENON_CLASS_BY_ID.get(phenomenon_id, "generalization")
        route_href = _ROUTE_BY_PHENOMENON_ID.get(phenomenon_id, "/ui/presets.html")
        entry = {
            "id": raw["id"],
            "label": raw["label"],
            "description": raw.get("description"),
            "education": deepcopy(raw.get("education")) if isinstance(raw.get("education"), dict) else None,
            "tuple_reference": deepcopy(tuple_ref),
            "compatibility": {
                "status": status,
                "ux_state": _compatibility_to_ux_state(status),
                "explanation": str(compatibility.get("explanation") or ""),
            },
            "route": {
                "href": route_href,
                "mode": "tuple_projection_overlay",
                "migration_safe": True,
            },
        }
        grouped.setdefault(arrangement_id, {})
        grouped[arrangement_id].setdefault(phenomenon_class, [])
        grouped[arrangement_id][phenomenon_class].append(entry)

    arrangements: list[dict[str, Any]] = []
    for arrangement_id in sorted(grouped.keys()):
        phenomenon_groups: list[dict[str, Any]] = []
        for phenomenon_class in sorted(grouped[arrangement_id].keys()):
            presets = grouped[arrangement_id][phenomenon_class]
            presets_sorted = sorted(
                presets,
                key=lambda item: (
                    _COMPATIBILITY_STATUS_ORDER.get(item["compatibility"]["status"], 999),
                    str(item["label"]).lower(),
                ),
            )
            phenomenon_groups.append(
                {
                    "phenomenon_class": phenomenon_class,
                    "smart_presets": presets_sorted,
                }
            )
        arrangements.append(
            {
                "arrangement_id": arrangement_id,
                "phenomenon_groups": phenomenon_groups,
            }
        )

    return {
        "contract_version": PRESET_UX_CATALOG_VERSION,
        "registry_generated": True,
        "compatibility_states": ["success", "partial", "behaviorally_unsupported", "novel"],
        "arrangements": arrangements,
        "ui_density_controls": {
            "collapse_sections_when_card_count_gt": 6,
            "top_recommended_limit": 3,
            "show_more_enabled": True,
        },
        "degraded_fallback": {
            "enabled": True,
            "mode": "read_only_static_catalog",
        },
    }

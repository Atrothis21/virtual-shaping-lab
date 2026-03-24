"""Preset route migration boundary contract for tuple-first UX cutover."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


PRESET_ROUTE_MIGRATION_CONTRACT_VERSION = "3.17.0"

PRESET_ROUTE_MIGRATION_CONTRACT: dict[str, Any] = {
    "contract_version": PRESET_ROUTE_MIGRATION_CONTRACT_VERSION,
    "strategy": "overlay_gradual",
    "tuple_first_preset_routes": [],
    "basis_first_preset_routes": [
        "acquisition",
        "extinction",
        "differential_acquisition",
    ],
    "legacy_fallback_preset_routes": [
        "compound_acquisition",
        "blocking",
        "overshadowing",
        "overexpectation",
        "conditioned_inhibition",
        "aba_renewal",
        "abc_renewal",
        "aab_renewal",
        "rapid_reacquisition",
        "occasion_setting",
        "operant_conditioning",
        "matching_law",
        "shaping",
        "resurgence",
        "superextinction",
        "spontaneous_recovery",
    ],
}


class PresetRouteMigrationValidationError(ValueError):
    """Raised when preset route migration contract validation fails."""


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PresetRouteMigrationValidationError(f"{label} must be a non-empty string.")
    return value.strip().lower()


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise PresetRouteMigrationValidationError(f"{label} must be a list of strings.")
    out: list[str] = []
    seen: set[str] = set()
    for idx, item in enumerate(value):
        key = _require_non_empty_string(item, f"{label}[{idx}]")
        if key in seen:
            raise PresetRouteMigrationValidationError(f"{label} has duplicate value: {key}")
        seen.add(key)
        out.append(key)
    return out


def validate_preset_route_migration_contract(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = deepcopy(PRESET_ROUTE_MIGRATION_CONTRACT if payload is None else payload)
    if not isinstance(root, dict):
        raise PresetRouteMigrationValidationError("preset_route_migration must be an object.")
    for key in (
        "contract_version",
        "strategy",
        "tuple_first_preset_routes",
        "basis_first_preset_routes",
        "legacy_fallback_preset_routes",
    ):
        if key not in root:
            raise PresetRouteMigrationValidationError(
                f"preset_route_migration missing required key: {key}"
            )
    _require_non_empty_string(root.get("contract_version"), "preset_route_migration.contract_version")
    strategy = _require_non_empty_string(root.get("strategy"), "preset_route_migration.strategy")
    if strategy not in {"overlay_gradual", "replace_core_pages", "new_shared_tuple_page"}:
        raise PresetRouteMigrationValidationError(
            "preset_route_migration.strategy must be one of: "
            "overlay_gradual, replace_core_pages, new_shared_tuple_page"
        )

    tuple_first = _require_string_list(
        root.get("tuple_first_preset_routes"),
        "preset_route_migration.tuple_first_preset_routes",
    )
    basis_first = _require_string_list(
        root.get("basis_first_preset_routes"),
        "preset_route_migration.basis_first_preset_routes",
    )
    legacy_fallback = _require_string_list(
        root.get("legacy_fallback_preset_routes"),
        "preset_route_migration.legacy_fallback_preset_routes",
    )

    overlap_tf_lf = sorted(set(tuple_first).intersection(set(legacy_fallback)))
    if overlap_tf_lf:
        raise PresetRouteMigrationValidationError(
            "tuple_first_preset_routes cannot overlap legacy_fallback_preset_routes: "
            + ", ".join(overlap_tf_lf)
        )
    overlap_bf_lf = sorted(set(basis_first).intersection(set(legacy_fallback)))
    if overlap_bf_lf:
        raise PresetRouteMigrationValidationError(
            "basis_first_preset_routes cannot overlap legacy_fallback_preset_routes: "
            + ", ".join(overlap_bf_lf)
        )
    return root


def get_preset_route_migration_contract() -> dict[str, Any]:
    return validate_preset_route_migration_contract(PRESET_ROUTE_MIGRATION_CONTRACT)


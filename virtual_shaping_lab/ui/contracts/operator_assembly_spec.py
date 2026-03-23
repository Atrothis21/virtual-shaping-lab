"""Typed intermediate operator assembly spec and deterministic compiler."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any

from ui.contracts.operator_basis_registry import (
    get_internal_builder_family,
    get_operator_basis_registry,
    list_ui_selectable_implementations,
)
from ui.contracts.operator_basis_schema import REQUIRED_OPERATOR_BASIS_SLOTS
from ui.contracts.operator_subset_contract import validate_preset_definition


class OperatorAssemblySpecValidationError(ValueError):
    """Raised when operator assembly spec validation fails."""


OPERATOR_ASSEMBLY_SPEC_VERSION = "3.12.0"

_REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = (
    "version",
    "preset_id",
    "selected_slots",
    "slots",
)
_REQUIRED_SLOT_KEYS: tuple[str, ...] = (
    "slot_id",
    "selection_mode",
    "selected",
    "selection_ids",
    "default_ids",
    "locked",
    "optional",
    "internal_builder_families",
    "registry_ids_only",
)


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OperatorAssemblySpecValidationError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperatorAssemblySpecValidationError(f"{label} must be a non-empty string.")
    return value


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise OperatorAssemblySpecValidationError(f"{label} must be boolean.")
    return value


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise OperatorAssemblySpecValidationError(f"{label} must be a list of strings.")
    out: list[str] = []
    for idx, item in enumerate(value):
        out.append(_require_non_empty_string(item, f"{label}[{idx}]"))
    return out


def _normalize_selection_ids(slot: str, value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value]
    raise OperatorAssemblySpecValidationError(
        f"Invalid selection shape for slot '{slot}': expected string/list/null."
    )


def compile_operator_subset_to_assembly_spec(
    preset_definition: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile PresetDefinition subset contract into typed intermediate assembly spec."""
    preset = validate_preset_definition(preset_definition)
    registry = get_operator_basis_registry()
    slots_registry = registry["slots"]

    operator_subset = dict(preset.get("operator_subset", {}) or {})
    defaults = dict(preset.get("defaults", {}) or {})
    locked = set(preset.get("locked", []) or [])
    optional = set(preset.get("optional", []) or [])

    slots: dict[str, Any] = {}
    selected_slots: list[str] = []
    for slot in REQUIRED_OPERATOR_BASIS_SLOTS:
        selection_mode = slots_registry[slot]["selection_mode"]
        selected_ids = _normalize_selection_ids(slot, operator_subset.get(slot))
        default_ids = _normalize_selection_ids(slot, defaults.get(slot))

        selected = len(selected_ids) > 0
        if selected:
            selected_slots.append(slot)

        internal_families: list[str] = []
        for selection_id in selected_ids:
            internal_families.append(get_internal_builder_family(slot, selection_id))

        slots[slot] = {
            "slot_id": slot,
            "selection_mode": selection_mode,
            "selected": selected,
            "selection_ids": selected_ids,
            "default_ids": default_ids,
            "locked": slot in locked,
            "optional": slot in optional,
            "internal_builder_families": internal_families,
            "registry_ids_only": True,
        }

    compiled = {
        "version": OPERATOR_ASSEMBLY_SPEC_VERSION,
        "preset_id": preset["id"],
        "selected_slots": selected_slots,
        "slots": slots,
    }
    return validate_operator_assembly_spec(compiled)


def validate_operator_assembly_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Validate typed intermediate assembly spec."""
    payload = deepcopy(spec)
    root = _require_dict(payload, "operator_assembly_spec")
    for key in _REQUIRED_TOP_LEVEL_KEYS:
        if key not in root:
            raise OperatorAssemblySpecValidationError(
                f"operator_assembly_spec missing required key: {key}"
            )

    _require_non_empty_string(root.get("version"), "operator_assembly_spec.version")
    _require_non_empty_string(root.get("preset_id"), "operator_assembly_spec.preset_id")
    selected_slots = _require_string_list(
        root.get("selected_slots"),
        "operator_assembly_spec.selected_slots",
    )
    slots = _require_dict(root.get("slots"), "operator_assembly_spec.slots")

    expected_slots = set(REQUIRED_OPERATOR_BASIS_SLOTS)
    slot_keys = set(slots.keys())
    if slot_keys != expected_slots:
        missing = sorted(expected_slots - slot_keys)
        extra = sorted(slot_keys - expected_slots)
        detail_parts: list[str] = []
        if missing:
            detail_parts.append(f"missing slots: {', '.join(missing)}")
        if extra:
            detail_parts.append(f"unexpected slots: {', '.join(extra)}")
        raise OperatorAssemblySpecValidationError(
            "operator_assembly_spec.slots must match required basis slots exactly"
            + (f" ({'; '.join(detail_parts)})" if detail_parts else "")
        )

    expected_selected_slots: list[str] = []
    for slot in REQUIRED_OPERATOR_BASIS_SLOTS:
        slot_payload = _require_dict(slots[slot], f"operator_assembly_spec.slots.{slot}")
        for key in _REQUIRED_SLOT_KEYS:
            if key not in slot_payload:
                raise OperatorAssemblySpecValidationError(
                    f"operator_assembly_spec.slots.{slot} missing required key: {key}"
                )
        slot_id = _require_non_empty_string(
            slot_payload.get("slot_id"),
            f"operator_assembly_spec.slots.{slot}.slot_id",
        )
        if slot_id != slot:
            raise OperatorAssemblySpecValidationError(
                f"operator_assembly_spec.slots.{slot}.slot_id must match slot key '{slot}'."
            )
        selection_mode = _require_non_empty_string(
            slot_payload.get("selection_mode"),
            f"operator_assembly_spec.slots.{slot}.selection_mode",
        )
        if selection_mode not in {"single", "multi"}:
            raise OperatorAssemblySpecValidationError(
                f"operator_assembly_spec.slots.{slot}.selection_mode must be 'single' or 'multi'."
            )

        selected = _require_bool(
            slot_payload.get("selected"),
            f"operator_assembly_spec.slots.{slot}.selected",
        )
        selection_ids = _require_string_list(
            slot_payload.get("selection_ids"),
            f"operator_assembly_spec.slots.{slot}.selection_ids",
        )
        default_ids = _require_string_list(
            slot_payload.get("default_ids"),
            f"operator_assembly_spec.slots.{slot}.default_ids",
        )
        _require_bool(
            slot_payload.get("locked"),
            f"operator_assembly_spec.slots.{slot}.locked",
        )
        _require_bool(
            slot_payload.get("optional"),
            f"operator_assembly_spec.slots.{slot}.optional",
        )
        internal_builder_families = _require_string_list(
            slot_payload.get("internal_builder_families"),
            f"operator_assembly_spec.slots.{slot}.internal_builder_families",
        )
        registry_ids_only = _require_bool(
            slot_payload.get("registry_ids_only"),
            f"operator_assembly_spec.slots.{slot}.registry_ids_only",
        )
        if registry_ids_only is not True:
            raise OperatorAssemblySpecValidationError(
                f"operator_assembly_spec.slots.{slot}.registry_ids_only must be true."
            )

        allowed = set(list_ui_selectable_implementations(slot))
        for selection_id in selection_ids:
            if selection_id not in allowed:
                raise OperatorAssemblySpecValidationError(
                    f"operator_assembly_spec.slots.{slot}.selection_ids contains unknown registry id: {selection_id}"
                )
        for selection_id in default_ids:
            if selection_id not in allowed:
                raise OperatorAssemblySpecValidationError(
                    f"operator_assembly_spec.slots.{slot}.default_ids contains unknown registry id: {selection_id}"
                )

        expected_families = [get_internal_builder_family(slot, selection_id) for selection_id in selection_ids]
        if internal_builder_families != expected_families:
            raise OperatorAssemblySpecValidationError(
                f"operator_assembly_spec.slots.{slot}.internal_builder_families must match routed registry metadata."
            )

        if selected != (len(selection_ids) > 0):
            raise OperatorAssemblySpecValidationError(
                f"operator_assembly_spec.slots.{slot}.selected must match presence of selection_ids."
            )
        if selected:
            expected_selected_slots.append(slot)

    if selected_slots != expected_selected_slots:
        raise OperatorAssemblySpecValidationError(
            "operator_assembly_spec.selected_slots must match ordered selected slot keys."
        )

    return payload


def stable_operator_assembly_spec_json(spec: dict[str, Any]) -> str:
    """Return deterministic JSON serialization for assembly spec."""
    normalized = validate_operator_assembly_spec(spec)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"))


def stable_operator_assembly_spec_hash(spec: dict[str, Any]) -> str:
    """Return deterministic hash for assembly spec."""
    encoded = stable_operator_assembly_spec_json(spec).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


"""PresetDefinition subset contract over the maximal operator-basis registry."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.operator_basis_registry import (
    get_operator_basis_registry,
    list_ui_selectable_implementations,
)
from ui.contracts.operator_basis_schema import REQUIRED_OPERATOR_BASIS_SLOTS


class OperatorSubsetContractError(ValueError):
    """Raised when operator subset contract validation fails."""


UI_SELECTABLE_UNIVERSE_POLICY = (
    "UI selectable operator implementations must be generated exclusively "
    "from operator_basis_registry; hand-authored lists are not allowed."
)


PRESET_DEFINITION_TEMPLATE: dict[str, Any] = {
    "id": "rw_acquisition",
    "label": "RW Acquisition",
    "description": "Classical minimal acquisition subset.",
    "operator_subset": {
        "phi": "elemental",
        "p": "state_value",
        "delta": "rw_error",
        "w": "rescorla_wagner",
        "omega": "classical_contingency",
        "m": ["trial_log", "learning_curve", "final_weights"],
    },
    "defaults": {
        "a": "fixed_alpha",
    },
    "locked": ["delta", "w"],
    "optional": ["a", "c", "g", "e", "pi"],
}


def _require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OperatorSubsetContractError(f"{label} must be an object.")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperatorSubsetContractError(f"{label} must be a non-empty string.")
    return value


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise OperatorSubsetContractError(f"{label} must be a list of strings.")
    out: list[str] = []
    for idx, item in enumerate(value):
        out.append(_require_non_empty_string(item, f"{label}[{idx}]"))
    return out


def _known_slots() -> set[str]:
    return set(REQUIRED_OPERATOR_BASIS_SLOTS)


def _required_slots() -> set[str]:
    registry = get_operator_basis_registry()
    slots = registry["slots"]
    return {slot for slot, payload in slots.items() if payload.get("required") is True}


def _is_multi_slot(slot: str) -> bool:
    registry = get_operator_basis_registry()
    return registry["slots"][slot]["selection_mode"] == "multi"


def _validate_selection_for_slot(slot: str, value: Any, *, label: str) -> None:
    allowed = set(list_ui_selectable_implementations(slot))
    if _is_multi_slot(slot):
        values = _require_string_list(value, label)
        if not values:
            raise OperatorSubsetContractError(f"{label} must be non-empty for multi-select slot.")
        seen: set[str] = set()
        for selection_id in values:
            if selection_id in seen:
                raise OperatorSubsetContractError(f"{label} has duplicate selection: {selection_id}")
            if selection_id not in allowed:
                raise OperatorSubsetContractError(
                    f"{label} contains unknown selection '{selection_id}'. Allowed: {', '.join(sorted(allowed))}"
                )
            seen.add(selection_id)
    else:
        selection_id = _require_non_empty_string(value, label)
        if selection_id not in allowed:
            raise OperatorSubsetContractError(
                f"{label} must be one of: {', '.join(sorted(allowed))}"
            )


def validate_preset_definition(definition: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate PresetDefinition subset contract."""
    payload = deepcopy(PRESET_DEFINITION_TEMPLATE if definition is None else definition)
    root = _require_dict(payload, "preset_definition")

    _require_non_empty_string(root.get("id"), "preset_definition.id")
    _require_non_empty_string(root.get("label"), "preset_definition.label")
    _require_non_empty_string(root.get("description"), "preset_definition.description")

    operator_subset = _require_dict(root.get("operator_subset"), "preset_definition.operator_subset")
    defaults = root.get("defaults", {})
    defaults = _require_dict(defaults, "preset_definition.defaults")
    locked = set(_require_string_list(root.get("locked", []), "preset_definition.locked"))
    optional = set(_require_string_list(root.get("optional", []), "preset_definition.optional"))

    known_slots = _known_slots()
    required_slots = _required_slots()

    for collection_name, values in (("locked", locked), ("optional", optional)):
        unknown = sorted(slot for slot in values if slot not in known_slots)
        if unknown:
            raise OperatorSubsetContractError(
                f"preset_definition.{collection_name} references unknown slots: {', '.join(unknown)}"
            )

    overlap = sorted(locked.intersection(optional))
    if overlap:
        raise OperatorSubsetContractError(
            f"preset_definition.locked and preset_definition.optional overlap: {', '.join(overlap)}"
        )

    subset_slots = set(operator_subset.keys())
    unknown_subset = sorted(slot for slot in subset_slots if slot not in known_slots)
    if unknown_subset:
        raise OperatorSubsetContractError(
            f"preset_definition.operator_subset references unknown slots: {', '.join(unknown_subset)}"
        )

    missing_required = sorted(required_slots - subset_slots)
    if missing_required:
        raise OperatorSubsetContractError(
            f"preset_definition.operator_subset is missing required slots: {', '.join(missing_required)}"
        )

    for slot, value in operator_subset.items():
        _validate_selection_for_slot(slot, value, label=f"preset_definition.operator_subset.{slot}")

    defaults_slots = set(defaults.keys())
    unknown_defaults = sorted(slot for slot in defaults_slots if slot not in known_slots)
    if unknown_defaults:
        raise OperatorSubsetContractError(
            f"preset_definition.defaults references unknown slots: {', '.join(unknown_defaults)}"
        )
    locked_defaults = sorted(slot for slot in defaults_slots if slot in locked)
    if locked_defaults:
        raise OperatorSubsetContractError(
            f"preset_definition.defaults cannot include locked slots: {', '.join(locked_defaults)}"
        )
    for slot, value in defaults.items():
        _validate_selection_for_slot(slot, value, label=f"preset_definition.defaults.{slot}")

    # Required slots must not be optional and may be locked if intentionally immutable.
    required_optional = sorted(required_slots.intersection(optional))
    if required_optional:
        raise OperatorSubsetContractError(
            f"preset_definition.optional cannot include required slots: {', '.join(required_optional)}"
        )

    return root


def get_preset_definition_template() -> dict[str, Any]:
    """Return validated template PresetDefinition."""
    return validate_preset_definition(PRESET_DEFINITION_TEMPLATE)


def build_registry_generated_ui_universe() -> dict[str, tuple[str, ...]]:
    """Generate UI-selectable universe from registry only."""
    return {
        slot: tuple(list_ui_selectable_implementations(slot))
        for slot in REQUIRED_OPERATOR_BASIS_SLOTS
    }


def validate_registry_generated_ui_universe(
    universe: dict[str, list[str] | tuple[str, ...]] | None = None,
) -> dict[str, tuple[str, ...]]:
    """Validate that a UI universe mapping exactly matches registry-produced values."""
    expected = build_registry_generated_ui_universe()
    actual_input = expected if universe is None else universe
    if not isinstance(actual_input, dict):
        raise OperatorSubsetContractError("ui_universe must be an object of slot -> list/tuple.")

    actual: dict[str, tuple[str, ...]] = {}
    for slot in REQUIRED_OPERATOR_BASIS_SLOTS:
        if slot not in actual_input:
            raise OperatorSubsetContractError(f"ui_universe missing slot: {slot}")
        values = actual_input[slot]
        if not isinstance(values, (list, tuple)):
            raise OperatorSubsetContractError(f"ui_universe.{slot} must be a list/tuple of strings.")
        normalized = tuple(_require_non_empty_string(v, f"ui_universe.{slot}") for v in values)
        actual[slot] = normalized
    extra = sorted(set(actual_input.keys()) - set(REQUIRED_OPERATOR_BASIS_SLOTS))
    if extra:
        raise OperatorSubsetContractError(f"ui_universe has unexpected slots: {', '.join(extra)}")

    for slot in REQUIRED_OPERATOR_BASIS_SLOTS:
        if actual[slot] != expected[slot]:
            raise OperatorSubsetContractError(
                f"ui_universe.{slot} must be registry-generated and exactly match registry order/content."
            )
    return actual


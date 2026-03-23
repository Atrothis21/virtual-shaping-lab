"""Selection compiler from preset subset contracts to frozen compile artifacts."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any

from ui.contracts.operator_assembly_spec import compile_operator_subset_to_assembly_spec
from ui.contracts.operator_basis_schema import REQUIRED_OPERATOR_BASIS_SLOTS
from ui.contracts.operator_legality_engine import (
    OperatorLegalityError,
    validate_operator_legality,
    validate_slot_selection_legality,
)
from ui.contracts.operator_subset_contract import OperatorSubsetContractError, validate_preset_definition


OPERATOR_SELECTION_COMPILER_VERSION = "3.12.5"


class OperatorSelectionCompilerError(ValueError):
    """Raised when selection compile fails."""

    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        self.code = str(code)
        self.details = dict(details or {})
        super().__init__(f"[{self.code}] {message}")


def _stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _stable_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _coerce_mapping(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise OperatorSelectionCompilerError("CMP_E_INVALID_SHAPE", f"{label} must be an object.")
    return dict(value)


def _normalize_selection_ids(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    raise OperatorSelectionCompilerError(
        "CMP_E_INVALID_SHAPE",
        "Selection value must be string/list/null.",
    )


def _enforce_registry_universe(raw_preset: dict[str, Any]) -> None:
    subset = _coerce_mapping(raw_preset.get("operator_subset"), "preset_definition.operator_subset")
    defaults = _coerce_mapping(raw_preset.get("defaults"), "preset_definition.defaults")
    unknown_slots = sorted((set(subset.keys()) | set(defaults.keys())) - set(REQUIRED_OPERATOR_BASIS_SLOTS))
    if unknown_slots:
        raise OperatorSelectionCompilerError(
            "CMP_E_UNKNOWN_SLOT",
            f"Unknown operator slot(s): {', '.join(unknown_slots)}",
            details={"slots": unknown_slots},
        )

    for slot, value in subset.items():
        try:
            validate_slot_selection_legality(slot, value)
        except OperatorLegalityError as exc:
            raise OperatorSelectionCompilerError(
                "CMP_E_UNKNOWN_SELECTION",
                f"operator_subset.{slot} contains non-registry selection.",
                details={"slot": slot, "selection": value, "cause": exc.code},
            ) from exc
    for slot, value in defaults.items():
        try:
            validate_slot_selection_legality(slot, value)
        except OperatorLegalityError as exc:
            raise OperatorSelectionCompilerError(
                "CMP_E_UNKNOWN_SELECTION",
                f"defaults.{slot} contains non-registry selection.",
                details={"slot": slot, "selection": value, "cause": exc.code},
            ) from exc


def compile_operator_selection_artifact(preset_definition: dict[str, Any]) -> dict[str, Any]:
    """Compile subset contract into frozen deterministic artifact."""
    raw = deepcopy(preset_definition)
    _enforce_registry_universe(raw)

    try:
        preset = validate_preset_definition(raw)
    except OperatorSubsetContractError as exc:
        raise OperatorSelectionCompilerError(
            "CMP_E_PRESET_INVALID",
            str(exc),
        ) from exc

    try:
        validate_operator_legality(preset)
    except OperatorLegalityError as exc:
        raise OperatorSelectionCompilerError(
            f"CMP_E_LEGALITY_{exc.code}",
            str(exc),
            details=exc.details,
        ) from exc

    assembly_spec = compile_operator_subset_to_assembly_spec(preset)
    subset = dict(preset.get("operator_subset", {}) or {})
    defaults = dict(preset.get("defaults", {}) or {})

    normalized_slots: dict[str, Any] = {}
    selected_slots: list[str] = []
    for slot in REQUIRED_OPERATOR_BASIS_SLOTS:
        spec_slot = assembly_spec["slots"][slot]
        subset_ids = _normalize_selection_ids(subset.get(slot))
        default_ids = _normalize_selection_ids(defaults.get(slot))
        if subset_ids:
            effective_ids = subset_ids
            source = "subset"
        elif default_ids:
            effective_ids = default_ids
            source = "default"
        else:
            effective_ids = []
            source = "disabled"

        is_selected = len(effective_ids) > 0
        if is_selected:
            selected_slots.append(slot)

        normalized_slots[slot] = {
            "slot_id": slot,
            "selection_mode": spec_slot["selection_mode"],
            "effective_selection_ids": effective_ids,
            "source": source,
            "selected": is_selected,
            "disabled": not is_selected,
        }

    artifact_core = {
        "version": OPERATOR_SELECTION_COMPILER_VERSION,
        "preset_id": preset["id"],
        "assembly_spec": assembly_spec,
        "selected_slots": selected_slots,
        "normalized_slots": normalized_slots,
        "frozen": True,
    }
    artifact = deepcopy(artifact_core)
    artifact["frozen_compiled_hash"] = _stable_hash(artifact_core)
    return artifact


def stable_selection_compile_json(preset_definition: dict[str, Any]) -> str:
    """Return deterministic compile JSON."""
    return _stable_json(compile_operator_selection_artifact(preset_definition))


def stable_selection_compile_hash(preset_definition: dict[str, Any]) -> str:
    """Return deterministic compile hash."""
    return compile_operator_selection_artifact(preset_definition)["frozen_compiled_hash"]


from __future__ import annotations

import copy

import pytest

from ui.contracts.operator_assembly_spec import (
    OperatorAssemblySpecValidationError,
    compile_operator_subset_to_assembly_spec,
    stable_operator_assembly_spec_hash,
    stable_operator_assembly_spec_json,
    validate_operator_assembly_spec,
)
from ui.contracts.operator_subset_contract import PRESET_DEFINITION_TEMPLATE


def test_compile_operator_subset_to_assembly_spec_snapshot_acquisition():
    spec = compile_operator_subset_to_assembly_spec(PRESET_DEFINITION_TEMPLATE)
    assert spec["preset_id"] == "rw_acquisition"
    assert spec["selected_slots"] == ["phi", "p", "delta", "w", "omega", "m"]
    assert spec["slots"]["phi"]["selection_ids"] == ["elemental"]
    assert spec["slots"]["omega"]["selection_ids"] == ["classical_contingency"]
    assert spec["slots"]["m"]["selection_ids"] == ["trial_log", "learning_curve", "final_weights"]
    assert spec["slots"]["delta"]["locked"] is True
    assert spec["slots"]["a"]["optional"] is True


def test_compile_operator_subset_to_assembly_spec_is_deterministic():
    payload = copy.deepcopy(PRESET_DEFINITION_TEMPLATE)
    payload_reordered = {
        "description": payload["description"],
        "id": payload["id"],
        "label": payload["label"],
        "operator_subset": {
            "m": payload["operator_subset"]["m"],
            "omega": payload["operator_subset"]["omega"],
            "w": payload["operator_subset"]["w"],
            "delta": payload["operator_subset"]["delta"],
            "p": payload["operator_subset"]["p"],
            "phi": payload["operator_subset"]["phi"],
        },
        "optional": list(reversed(payload["optional"])),
        "locked": list(payload["locked"]),
        "defaults": dict(payload["defaults"]),
    }
    spec_a = compile_operator_subset_to_assembly_spec(payload)
    spec_b = compile_operator_subset_to_assembly_spec(payload_reordered)
    assert stable_operator_assembly_spec_json(spec_a) == stable_operator_assembly_spec_json(spec_b)
    assert stable_operator_assembly_spec_hash(spec_a) == stable_operator_assembly_spec_hash(spec_b)


def test_operator_assembly_spec_rejects_unknown_registry_id_reference():
    spec = compile_operator_subset_to_assembly_spec(PRESET_DEFINITION_TEMPLATE)
    spec["slots"]["phi"]["selection_ids"] = ["not_real"]
    spec["slots"]["phi"]["selected"] = True
    with pytest.raises(OperatorAssemblySpecValidationError, match="unknown registry id"):
        validate_operator_assembly_spec(spec)


def test_operator_assembly_spec_rejects_internal_builder_family_mismatch():
    spec = compile_operator_subset_to_assembly_spec(PRESET_DEFINITION_TEMPLATE)
    spec["slots"]["w"]["internal_builder_families"] = ["representation"]
    with pytest.raises(OperatorAssemblySpecValidationError, match="internal_builder_families"):
        validate_operator_assembly_spec(spec)


def test_operator_assembly_spec_references_registry_ids_only_for_selections():
    spec = compile_operator_subset_to_assembly_spec(PRESET_DEFINITION_TEMPLATE)
    for slot_payload in spec["slots"].values():
        assert slot_payload["registry_ids_only"] is True
    validate_operator_assembly_spec(spec)


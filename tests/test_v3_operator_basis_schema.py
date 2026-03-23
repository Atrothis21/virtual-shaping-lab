from __future__ import annotations

import copy

import pytest

from ui.contracts.operator_basis_schema import (
    OPERATOR_BASIS_MASTER_TABLE,
    OPERATOR_BASIS_SCHEMA_TEMPLATE,
    REQUIRED_OPERATOR_BASIS_SLOTS,
    OperatorBasisSchemaValidationError,
    get_operator_basis_schema,
    list_operator_basis_slots,
    stable_operator_basis_schema_hash,
    stable_operator_basis_schema_json,
    validate_operator_basis_schema,
)


def test_operator_basis_schema_accepts_canonical_template():
    payload = get_operator_basis_schema()
    assert payload["version"]
    assert payload["preset_id"] == "acquisition"
    assert set(payload["operators"].keys()) == set(REQUIRED_OPERATOR_BASIS_SLOTS)


def test_operator_basis_schema_rejects_missing_required_slot():
    payload = copy.deepcopy(OPERATOR_BASIS_SCHEMA_TEMPLATE)
    del payload["operators"]["omega"]
    with pytest.raises(OperatorBasisSchemaValidationError, match="must contain exactly required slots"):
        validate_operator_basis_schema(payload)


def test_operator_basis_schema_rejects_unknown_selection_value():
    payload = copy.deepcopy(OPERATOR_BASIS_SCHEMA_TEMPLATE)
    payload["operators"]["phi"]["selection"] = "not_real"
    with pytest.raises(OperatorBasisSchemaValidationError, match="must be one of"):
        validate_operator_basis_schema(payload)


def test_operator_basis_schema_rejects_required_operator_disabled():
    payload = copy.deepcopy(OPERATOR_BASIS_SCHEMA_TEMPLATE)
    payload["operators"]["p"]["enabled"] = False
    payload["operators"]["p"]["selection"] = None
    with pytest.raises(OperatorBasisSchemaValidationError, match="is required and cannot be disabled"):
        validate_operator_basis_schema(payload)


def test_operator_basis_schema_rejects_multi_select_duplicates():
    payload = copy.deepcopy(OPERATOR_BASIS_SCHEMA_TEMPLATE)
    payload["operators"]["m"]["selection"] = ["trial_log", "trial_log"]
    with pytest.raises(OperatorBasisSchemaValidationError, match="has duplicate value"):
        validate_operator_basis_schema(payload)


def test_operator_basis_schema_stable_serialization_and_hash():
    payload = copy.deepcopy(OPERATOR_BASIS_SCHEMA_TEMPLATE)
    payload_reordered = {
        "description": payload["description"],
        "label": payload["label"],
        "preset_id": payload["preset_id"],
        "version": payload["version"],
        "program": payload["program"],
        "stimuli": payload["stimuli"],
        "operators": {k: payload["operators"][k] for k in reversed(tuple(payload["operators"].keys()))},
    }

    json_a = stable_operator_basis_schema_json(payload)
    json_b = stable_operator_basis_schema_json(payload_reordered)
    assert json_a == json_b
    assert stable_operator_basis_schema_hash(payload) == stable_operator_basis_schema_hash(payload_reordered)


def test_operator_basis_master_table_covers_all_required_slots():
    assert set(OPERATOR_BASIS_MASTER_TABLE.keys()) == set(REQUIRED_OPERATOR_BASIS_SLOTS)
    assert set(list_operator_basis_slots()) == set(REQUIRED_OPERATOR_BASIS_SLOTS)
    for slot in REQUIRED_OPERATOR_BASIS_SLOTS:
        entry = OPERATOR_BASIS_MASTER_TABLE[slot]
        assert entry["allowed_selections"]
        assert entry["selection_mode"] in {"single", "multi"}


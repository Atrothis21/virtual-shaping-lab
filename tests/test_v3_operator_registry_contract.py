from __future__ import annotations

import copy

import pytest

from ui.contracts.operator_basis_registry import (
    OPERATOR_BASIS_REGISTRY,
    OperatorBasisRegistryValidationError,
    get_internal_builder_family,
    get_operator_basis_registry,
    get_operator_selection_contract,
    list_operator_basis_registry_slots,
    list_ui_selectable_implementations,
    validate_operator_basis_registry,
)
from ui.contracts.operator_basis_schema import REQUIRED_OPERATOR_BASIS_SLOTS
from ui.contracts.operator_basis_schema import OPERATOR_BASIS_MASTER_TABLE


def test_operator_basis_registry_loads_and_covers_all_slots():
    payload = get_operator_basis_registry()
    assert set(payload["slots"].keys()) == set(REQUIRED_OPERATOR_BASIS_SLOTS)
    assert set(list_operator_basis_registry_slots()) == set(REQUIRED_OPERATOR_BASIS_SLOTS)


def test_operator_basis_registry_ui_selectables_match_master_table():
    payload = get_operator_basis_registry()
    for slot in REQUIRED_OPERATOR_BASIS_SLOTS:
        master_allowed = set(OPERATOR_BASIS_MASTER_TABLE[slot]["allowed_selections"])
        selectable = set(list_ui_selectable_implementations(slot))
        assert selectable == master_allowed
        slot_payload = payload["slots"][slot]
        for selection_id in selectable:
            selection = slot_payload["selections"][selection_id]
            assert selection["ui_visible"] is True


def test_operator_basis_registry_selection_contract_has_params_schema_and_builder_family():
    payload = get_operator_basis_registry()
    for slot in REQUIRED_OPERATOR_BASIS_SLOTS:
        for selection_id in payload["slots"][slot]["selections"].keys():
            selection = get_operator_selection_contract(slot, selection_id)
            assert isinstance(selection["params_schema"], dict)
            assert isinstance(selection["internal_builder_family"], str)
            assert selection["internal_builder_family"]


def test_operator_basis_registry_internal_builder_family_routing_is_resolvable():
    payload = get_operator_basis_registry()
    for slot in REQUIRED_OPERATOR_BASIS_SLOTS:
        some_selection = next(iter(payload["slots"][slot]["selections"].keys()))
        builder_family = get_internal_builder_family(slot, some_selection)
        assert isinstance(builder_family, str)
        assert builder_family == payload["slots"][slot]["selections"][some_selection]["internal_builder_family"]


def test_operator_basis_registry_rejects_missing_slot():
    bad = copy.deepcopy(OPERATOR_BASIS_REGISTRY)
    del bad["slots"]["omega"]
    with pytest.raises(OperatorBasisRegistryValidationError, match="must match required basis slots"):
        validate_operator_basis_registry(bad)


def test_operator_basis_registry_rejects_selection_family_mismatch():
    bad = copy.deepcopy(OPERATOR_BASIS_REGISTRY)
    bad["slots"]["phi"]["selections"]["elemental"]["internal_builder_family"] = "learner"
    with pytest.raises(OperatorBasisRegistryValidationError, match="internal_builder_family"):
        validate_operator_basis_registry(bad)


def test_operator_basis_registry_rejects_unknown_selection_lookup():
    with pytest.raises(KeyError, match="Unknown selection"):
        get_operator_selection_contract("phi", "not_real")

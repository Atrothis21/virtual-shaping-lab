from __future__ import annotations

import copy

import pytest

from ui.contracts.arrangement_contract import (
    ARRANGEMENT_CONTRACT,
    REQUIRED_ARRANGEMENT_IDS,
    ArrangementContractValidationError,
    get_arrangement,
    get_arrangement_contract,
    list_arrangement_ids,
    stable_arrangement_contract_hash,
    stable_arrangement_contract_json,
    validate_arrangement_contract,
)


def test_arrangement_contract_accepts_canonical_template():
    payload = get_arrangement_contract()
    assert payload["version"]
    assert set(payload["arrangements"].keys()) == set(REQUIRED_ARRANGEMENT_IDS)
    assert payload["arrangements"]["pavlovian"]["policy_semantics"]["forbids_non_null_policy"] is True
    assert payload["arrangements"]["operant"]["policy_semantics"]["requires_non_null_policy"] is True


def test_arrangement_contract_rejects_unknown_arrangement_id():
    payload = copy.deepcopy(ARRANGEMENT_CONTRACT)
    payload["arrangements"]["hybrid"] = copy.deepcopy(payload["arrangements"]["pavlovian"])
    with pytest.raises(ArrangementContractValidationError, match="must include exactly required IDs"):
        validate_arrangement_contract(payload)


def test_arrangement_contract_rejects_invalid_shape():
    payload = copy.deepcopy(ARRANGEMENT_CONTRACT)
    del payload["arrangements"]["operant"]["policy_semantics"]
    with pytest.raises(ArrangementContractValidationError, match="missing required key: policy_semantics"):
        validate_arrangement_contract(payload)


def test_arrangement_contract_rejects_policy_overlap():
    payload = copy.deepcopy(ARRANGEMENT_CONTRACT)
    payload["arrangements"]["operant"]["policy_semantics"]["allowed_values"] = ["softmax", "none"]
    with pytest.raises(ArrangementContractValidationError, match="allowed/forbidden policy values overlap"):
        validate_arrangement_contract(payload)


def test_arrangement_contract_id_accessors():
    assert list_arrangement_ids() == REQUIRED_ARRANGEMENT_IDS
    pav = get_arrangement("pavlovian")
    assert pav["id"] == "pavlovian"
    with pytest.raises(ArrangementContractValidationError, match="Unknown arrangement_id"):
        get_arrangement("unknown")


def test_arrangement_contract_stable_json_and_hash_snapshot():
    payload = copy.deepcopy(ARRANGEMENT_CONTRACT)
    reordered = {
        "arrangements": {
            "operant": payload["arrangements"]["operant"],
            "pavlovian": payload["arrangements"]["pavlovian"],
        },
        "version": payload["version"],
    }
    assert stable_arrangement_contract_json(payload) == stable_arrangement_contract_json(reordered)
    assert stable_arrangement_contract_hash(payload) == stable_arrangement_contract_hash(reordered)
    assert (
        stable_arrangement_contract_hash(payload)
        == "c1b6b6fb9356836e09518428edcc88ff5d242e5b2a7b64cb06d245f06aa2f585"
    )

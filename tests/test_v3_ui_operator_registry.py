from __future__ import annotations

import copy

import pytest

from ui.contracts.operator_registry import (
    OPERATOR_REGISTRY,
    OperatorRegistryValidationError,
    get_operator,
    get_operator_registry,
    list_operator_ids,
    validate_operator_registry,
)


def test_operator_registry_load_and_baseline_operators_exist():
    payload = get_operator_registry()
    assert payload["version"]
    operators = payload["operators"]
    assert "phi" in operators
    assert "p" in operators
    assert "delta" in operators
    assert "w" in operators


def test_operator_registry_id_list_is_sorted_and_stable():
    ids = list_operator_ids()
    assert isinstance(ids, tuple)
    assert list(ids) == sorted(ids)
    assert "phi" in ids
    assert "delta" in ids


def test_operator_registry_get_operator_success_and_failure():
    op = get_operator("w")
    assert op["id"] == "w"
    assert op["family"] == "update"
    assert "reads_trialstate" in op["runtime"]

    with pytest.raises(KeyError):
        get_operator("not_real")


def test_operator_registry_rejects_unknown_reads_trialstate_field():
    payload = copy.deepcopy(OPERATOR_REGISTRY)
    payload["operators"]["delta"]["runtime"]["reads_trialstate"].append("unknown_field")
    with pytest.raises(OperatorRegistryValidationError, match="references unknown TrialState field"):
        validate_operator_registry(payload)


def test_operator_registry_rejects_unknown_writes_trialstate_field():
    payload = copy.deepcopy(OPERATOR_REGISTRY)
    payload["operators"]["w"]["runtime"]["writes_trialstate"].append("not_a_field")
    with pytest.raises(OperatorRegistryValidationError, match="references unknown TrialState field"):
        validate_operator_registry(payload)


def test_operator_registry_rejects_stage_index_not_positive():
    payload = copy.deepcopy(OPERATOR_REGISTRY)
    payload["operators"]["phi"]["stage_index"] = 0
    with pytest.raises(OperatorRegistryValidationError, match="stage_index must be > 0"):
        validate_operator_registry(payload)


def test_operator_registry_rejects_operator_id_mismatch():
    payload = copy.deepcopy(OPERATOR_REGISTRY)
    payload["operators"]["p"]["id"] = "prediction"
    with pytest.raises(OperatorRegistryValidationError, match="id must match operator key"):
        validate_operator_registry(payload)


def test_operator_registry_rejects_unknown_required_upstream_operator():
    payload = copy.deepcopy(OPERATOR_REGISTRY)
    payload["operators"]["delta"]["runtime"]["required_upstream"] = ["not_real_op"]
    with pytest.raises(OperatorRegistryValidationError, match="references unknown operator id"):
        validate_operator_registry(payload)


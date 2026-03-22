from __future__ import annotations

import copy

import pytest

from ui.contracts.trialstate_registry import (
    REQUIRED_TRIALSTATE_FIELDS,
    REQUIRED_TRIALSTATE_FIELD_GROUPS,
    TRIALSTATE_FIELD_REGISTRY,
    TrialStateRegistryValidationError,
    get_trialstate_field,
    get_trialstate_field_registry,
    list_trialstate_field_ids,
    validate_trialstate_field_registry,
)


def test_trialstate_registry_load_and_required_groups_fields():
    payload = get_trialstate_field_registry()
    assert payload["version"]
    groups = payload["field_groups"]
    fields = payload["fields"]
    for group in REQUIRED_TRIALSTATE_FIELD_GROUPS:
        assert group in groups
    for field_name in REQUIRED_TRIALSTATE_FIELDS:
        assert field_name in fields


def test_trialstate_registry_field_id_list_is_stable_sorted():
    ids = list_trialstate_field_ids()
    assert isinstance(ids, tuple)
    assert list(ids) == sorted(ids)
    assert "stimulus" in ids
    assert "prediction" in ids


def test_trialstate_registry_resolve_field_success_and_failure():
    prediction = get_trialstate_field("prediction")
    assert prediction["id"] == "prediction"
    assert prediction["group"] == "prediction"
    assert prediction["runtime"]["kind"] == "float"

    with pytest.raises(KeyError):
        get_trialstate_field("not_a_real_field")


def test_trialstate_registry_rejects_missing_required_group():
    payload = copy.deepcopy(TRIALSTATE_FIELD_REGISTRY)
    del payload["field_groups"]["metadata"]
    with pytest.raises(TrialStateRegistryValidationError, match="missing required group"):
        validate_trialstate_field_registry(payload)


def test_trialstate_registry_rejects_missing_required_field_key():
    payload = copy.deepcopy(TRIALSTATE_FIELD_REGISTRY)
    del payload["fields"]["prediction"]["runtime"]
    with pytest.raises(TrialStateRegistryValidationError, match="missing required key: runtime"):
        validate_trialstate_field_registry(payload)


def test_trialstate_registry_rejects_unknown_group_reference():
    payload = copy.deepcopy(TRIALSTATE_FIELD_REGISTRY)
    payload["fields"]["prediction"]["group"] = "unknown_group"
    with pytest.raises(TrialStateRegistryValidationError, match="references unknown group"):
        validate_trialstate_field_registry(payload)


def test_trialstate_registry_rejects_non_boolean_visibility_flags():
    payload = copy.deepcopy(TRIALSTATE_FIELD_REGISTRY)
    payload["fields"]["prediction"]["visibility"]["expert_mode"] = "yes"
    with pytest.raises(TrialStateRegistryValidationError, match="expert_mode must be boolean"):
        validate_trialstate_field_registry(payload)


def test_trialstate_registry_rejects_duplicate_field_ids():
    payload = copy.deepcopy(TRIALSTATE_FIELD_REGISTRY)
    payload["fields"]["state"]["id"] = "stimulus"
    with pytest.raises(TrialStateRegistryValidationError, match="duplicate id value"):
        validate_trialstate_field_registry(payload)


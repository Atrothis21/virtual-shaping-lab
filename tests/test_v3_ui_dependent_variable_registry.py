from __future__ import annotations

import copy

import pytest

from ui.contracts.dependent_variable_registry import (
    DEPENDENT_VARIABLE_REGISTRY,
    REQUIRED_DEPENDENT_VARIABLES,
    DependentVariableRegistryValidationError,
    get_dependent_variable,
    get_dependent_variable_registry,
    list_dependent_variable_ids,
    validate_dependent_variable_registry,
    validate_preset_results_contract,
)


def test_dependent_variable_registry_load_and_baseline_variables_exist():
    payload = get_dependent_variable_registry()
    assert payload["version"]
    variables = payload["variables"]
    for variable_id in REQUIRED_DEPENDENT_VARIABLES:
        assert variable_id in variables


def test_dependent_variable_registry_id_list_is_sorted_and_stable():
    ids = list_dependent_variable_ids()
    assert isinstance(ids, tuple)
    assert list(ids) == sorted(ids)
    assert "prediction_error" in ids
    assert "response_probability" in ids


def test_dependent_variable_registry_get_variable_success_and_failure():
    variable = get_dependent_variable("prediction_error")
    assert variable["id"] == "prediction_error"
    assert variable["runtime"]["kind"] == "direct_field"

    with pytest.raises(KeyError):
        get_dependent_variable("not_real")


def test_dependent_variable_registry_rejects_unknown_source_field():
    payload = copy.deepcopy(DEPENDENT_VARIABLE_REGISTRY)
    payload["variables"]["prediction_error"]["runtime"]["source_fields"].append("unknown_field")
    with pytest.raises(
        DependentVariableRegistryValidationError,
        match="source_fields references unknown TrialState field",
    ):
        validate_dependent_variable_registry(payload)


def test_dependent_variable_registry_rejects_unknown_related_operator():
    payload = copy.deepcopy(DEPENDENT_VARIABLE_REGISTRY)
    payload["variables"]["prediction_error"]["explainability"]["related_operators"].append("not_real_operator")
    with pytest.raises(
        DependentVariableRegistryValidationError,
        match="related_operators references unknown operator id",
    ):
        validate_dependent_variable_registry(payload)


def test_dependent_variable_registry_rejects_unknown_related_trialstate_field():
    payload = copy.deepcopy(DEPENDENT_VARIABLE_REGISTRY)
    payload["variables"]["prediction_error"]["explainability"]["related_trialstate_fields"].append("not_real_field")
    with pytest.raises(
        DependentVariableRegistryValidationError,
        match="related_trialstate_fields references unknown TrialState field",
    ):
        validate_dependent_variable_registry(payload)


def test_preset_results_contract_rejects_unknown_variable_id():
    with pytest.raises(
        DependentVariableRegistryValidationError,
        match="primary_dependent_variables\\[0\\] references unknown dependent variable id",
    ):
        validate_preset_results_contract(
            {
                "primary_dependent_variables": ["not_real_variable"],
                "secondary_dependent_variables": [],
                "graph_priority": [],
            }
        )


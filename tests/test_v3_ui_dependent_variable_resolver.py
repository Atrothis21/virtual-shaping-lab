from __future__ import annotations

import copy

import pytest

from ui.contracts.dependent_variable_registry import DEPENDENT_VARIABLE_REGISTRY
from ui.contracts.dependent_variable_resolver import (
    DependentVariableResolverError,
    resolve_dependent_variable,
    resolve_dependent_variable_from_registry_payload,
    resolve_dependent_variables_for_surface,
    resolve_report_variable,
    resolve_results_variable,
)
from ui.contracts.registry_integrity import load_ui_registries


def test_v3_11_entry_criteria_registry_foundation_and_acquisition_stack_available():
    registries = load_ui_registries()
    assert "trialstate_registry" in registries
    assert "operator_registry" in registries
    assert "dependent_variable_registry" in registries
    assert "preset_registry" in registries
    assert "acquisition" in registries["preset_registry"]["presets"]


def test_dependent_variable_resolver_contract_results_surface():
    resolved = resolve_results_variable("associative_strength")
    assert resolved["id"] == "associative_strength"
    assert resolved["label"]
    assert resolved["chart"]
    assert resolved["units"]
    assert isinstance(resolved["related_operators"], list)
    assert isinstance(resolved["related_trialstate_fields"], list)


def test_dependent_variable_resolver_contract_report_surface():
    resolved = resolve_report_variable("predicted_outcome")
    assert resolved["id"] == "predicted_outcome"
    assert resolved["visibility_default"] is True


def test_dependent_variable_resolver_unknown_id_guard():
    with pytest.raises(KeyError):
        resolve_dependent_variable("not_real_variable", surface="results")


def test_dependent_variable_resolver_malformed_metadata_guard():
    payload = copy.deepcopy(DEPENDENT_VARIABLE_REGISTRY)
    payload["variables"]["associative_strength"]["visualization"]["default_chart"] = None

    with pytest.raises(DependentVariableResolverError, match="default_chart must be a non-empty string"):
        resolve_dependent_variable_from_registry_payload(
            "associative_strength",
            registry_payload=payload,
            surface="results",
        )


def test_dependent_variable_resolver_shared_surface_api():
    results_vars = resolve_dependent_variables_for_surface(surface="results")
    report_vars = resolve_dependent_variables_for_surface(surface="report")
    assert results_vars
    assert report_vars
    assert all("id" in item and "label" in item for item in results_vars)
    assert all("id" in item and "label" in item for item in report_vars)

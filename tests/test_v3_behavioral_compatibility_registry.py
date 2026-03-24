from __future__ import annotations

import copy

import pytest

from ui.contracts.behavioral_compatibility_registry import (
    BEHAVIORAL_COMPATIBILITY_REGISTRY,
    BehavioralCompatibilityRegistryValidationError,
    get_behavioral_compatibility_registry,
    validate_behavioral_compatibility_registry,
)


def test_behavioral_compatibility_registry_shape_and_load():
    payload = get_behavioral_compatibility_registry()
    assert payload["version"]
    assert isinstance(payload["entries"], list) and payload["entries"]


def test_behavioral_compatibility_registry_requires_core_coverage():
    payload = copy.deepcopy(BEHAVIORAL_COMPATIBILITY_REGISTRY)
    payload["entries"] = [
        entry
        for entry in payload["entries"]
        if entry["id"] != "pavlovian_extinction_rw_classical_default"
    ]
    with pytest.raises(
        BehavioralCompatibilityRegistryValidationError,
        match="missing required baseline compatibility coverage for core tuples",
    ):
        validate_behavioral_compatibility_registry(payload)


def test_behavioral_compatibility_registry_rejects_invalid_outcome_value():
    payload = copy.deepcopy(BEHAVIORAL_COMPATIBILITY_REGISTRY)
    payload["entries"][0]["outcome"] = "unknown_state"
    with pytest.raises(
        BehavioralCompatibilityRegistryValidationError,
        match="outcome must be one of",
    ):
        validate_behavioral_compatibility_registry(payload)


def test_behavioral_compatibility_registry_edit_conditional_branch_must_be_explicit():
    payload = copy.deepcopy(BEHAVIORAL_COMPATIBILITY_REGISTRY)
    payload["entries"][0]["when"] = {"n_trials": {"lt": 5}}
    with pytest.raises(
        BehavioralCompatibilityRegistryValidationError,
        match="edit-conditional branches must be explicit",
    ):
        validate_behavioral_compatibility_registry(payload)


def test_behavioral_compatibility_registry_novel_requires_rationale_source():
    payload = copy.deepcopy(BEHAVIORAL_COMPATIBILITY_REGISTRY)
    for entry in payload["entries"]:
        if entry["outcome"] == "novel":
            entry.pop("rationale_source", None)
    with pytest.raises(
        BehavioralCompatibilityRegistryValidationError,
        match="rationale_source",
    ):
        validate_behavioral_compatibility_registry(payload)


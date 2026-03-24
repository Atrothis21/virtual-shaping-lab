from __future__ import annotations

import copy

import pytest

from ui.contracts.agent_bundle_registry import (
    AGENT_BUNDLE_REGISTRY,
    AgentBundleRegistryValidationError,
    get_agent_bundle_registry,
    validate_agent_bundle_registry,
)


def test_agent_bundle_registry_declares_primary_declarative_identity_policy():
    payload = get_agent_bundle_registry()
    text = payload["primary_identity_policy"].lower()
    assert "declarative operator selections" in text
    assert "secondary metadata" in text


def test_agent_bundle_registry_requires_registry_generated_selectable_universe():
    payload = copy.deepcopy(AGENT_BUNDLE_REGISTRY)
    payload["bundles"]["rw_classical"]["selectable_universe_source"] = "hand_authored"
    with pytest.raises(AgentBundleRegistryValidationError, match="selectable_universe_source"):
        validate_agent_bundle_registry(payload)


def test_agent_bundle_registry_rejects_builder_family_constraint_drift():
    payload = copy.deepcopy(AGENT_BUNDLE_REGISTRY)
    payload["bundles"]["rw_operant"]["builder_family_constraints"]["agent_control"]["allowed"] = [
        "learner"
    ]
    with pytest.raises(AgentBundleRegistryValidationError, match="contradicts routed family"):
        validate_agent_bundle_registry(payload)


def test_agent_bundle_registry_rejects_missing_core_bundle_selection_slots():
    payload = copy.deepcopy(AGENT_BUNDLE_REGISTRY)
    del payload["bundles"]["rw_classical"]["operator_selections"]["delta"]
    with pytest.raises(AgentBundleRegistryValidationError, match="missing required slots"):
        validate_agent_bundle_registry(payload)


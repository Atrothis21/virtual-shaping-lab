from __future__ import annotations

import copy

import pytest

from ui.contracts.agent_bundle_registry import (
    AGENT_BUNDLE_REGISTRY,
    AgentBundleRegistryValidationError,
    get_agent_bundle,
    get_agent_bundle_registry,
    list_agent_bundle_ids,
    validate_agent_bundle_arrangement_compatibility,
    validate_agent_bundle_registry,
)


def test_agent_bundle_registry_load_and_shape():
    payload = get_agent_bundle_registry()
    assert payload["version"]
    assert "rw_classical" in payload["bundles"]
    assert "rw_operant" in payload["bundles"]


def test_agent_bundle_id_list_is_sorted_and_stable():
    ids = list_agent_bundle_ids()
    assert isinstance(ids, tuple)
    assert list(ids) == sorted(ids)
    assert "rw_classical" in ids


def test_agent_bundle_get_success_and_failure():
    bundle = get_agent_bundle("rw_classical")
    assert bundle["id"] == "rw_classical"
    with pytest.raises(AgentBundleRegistryValidationError, match="Unknown agent bundle id"):
        get_agent_bundle("not_real")


def test_agent_bundle_registry_rejects_unknown_selection():
    payload = copy.deepcopy(AGENT_BUNDLE_REGISTRY)
    payload["bundles"]["rw_classical"]["operator_selections"]["w"] = "not_real"
    with pytest.raises(AgentBundleRegistryValidationError, match="unknown selection"):
        validate_agent_bundle_registry(payload)


def test_agent_bundle_registry_rejects_arrangement_mismatch():
    with pytest.raises(AgentBundleRegistryValidationError, match="not compatible with arrangement"):
        validate_agent_bundle_arrangement_compatibility(
            bundle_id="rw_classical",
            arrangement_id="operant",
        )


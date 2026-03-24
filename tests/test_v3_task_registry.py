from __future__ import annotations

import copy

import pytest

from ui.contracts.preset_registry import get_preset_registry
from ui.contracts.task_registry import (
    REQUIRED_TASK_IDS,
    TASK_REGISTRY,
    TaskRegistryValidationError,
    build_thin_preset_task_reference,
    get_task_implementation,
    get_task_registry,
    list_task_ids,
    list_task_implementation_ids,
    resolve_task_implementation_for_tuple,
    validate_task_registry,
    validate_task_tuple_policy,
)


def test_task_registry_load_and_shape():
    payload = get_task_registry()
    assert payload["version"]
    assert set(payload["phenomena"].keys()) == set(REQUIRED_TASK_IDS)
    assert payload["implementations"]["pavlovian_acquisition"]["protocol_family"] == "acquisition"


def test_task_registry_required_task_ids_present():
    assert list_task_ids() == tuple(sorted(REQUIRED_TASK_IDS))


def test_task_implementation_ids_are_unique_and_stable():
    ids = list_task_implementation_ids()
    assert isinstance(ids, tuple)
    assert list(ids) == sorted(ids)
    assert "pavlovian_acquisition" in ids
    assert "operant_acquisition" in ids


def test_task_registry_rejects_invalid_arrangement_compatibility():
    payload = copy.deepcopy(TASK_REGISTRY)
    payload["implementations"]["operant_acquisition"]["arrangement_id"] = "not_real"
    with pytest.raises(TaskRegistryValidationError, match="arrangement_id is not recognized"):
        validate_task_registry(payload)


def test_task_registry_rejects_duplicate_or_overlapping_operator_sets():
    payload = copy.deepcopy(TASK_REGISTRY)
    payload["implementations"]["pavlovian_acquisition"]["optional_operators"].append("w")
    with pytest.raises(TaskRegistryValidationError, match="required/optional operators overlap"):
        validate_task_registry(payload)


def test_task_tuple_policy_rejects_arrangement_mismatch():
    with pytest.raises(TaskRegistryValidationError, match="task tuple incompatible"):
        validate_task_tuple_policy(
            arrangement_id="operant",
            implementation_id="pavlovian_acquisition",
            agent_bundle_id="rw_classical",
        )


def test_task_tuple_policy_enforces_deferred_and_forbidden_hybrid_policies():
    with pytest.raises(TaskRegistryValidationError, match="deferred by policy"):
        validate_task_tuple_policy(
            arrangement_id="hybrid",
            implementation_id="hybrid_extinction_bridge",
            agent_bundle_id="rw_classical",
        )
    with pytest.raises(TaskRegistryValidationError, match="forbidden by policy"):
        validate_task_tuple_policy(
            arrangement_id="hybrid",
            implementation_id="hybrid_acquisition_transfer",
            agent_bundle_id="legacy_hybrid_bundle",
        )


def test_task_registry_thin_preset_reference_stays_compatible():
    registry = get_preset_registry()
    reference = registry["presets"]["acquisition"]["task_reference"]
    built = build_thin_preset_task_reference("acquisition")
    assert reference == built
    resolved = resolve_task_implementation_for_tuple(
        phenomenon_id=reference["phenomenon_id"],
        arrangement_id=reference["default_arrangement_id"],
    )
    assert resolved["id"] == reference["default_implementation_id"]


def test_get_task_implementation_success_and_failure():
    impl = get_task_implementation("pavlovian_extinction")
    assert impl["phenomenon_id"] == "extinction"
    with pytest.raises(TaskRegistryValidationError, match="Unknown task implementation id"):
        get_task_implementation("unknown")

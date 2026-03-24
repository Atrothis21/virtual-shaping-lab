from __future__ import annotations

from ui.contracts.arrangement_task_agent_composition import (
    compose_arrangement_task_agent_to_operator_subset,
    compose_from_preset_reference,
    stable_arrangement_task_agent_provenance_hash,
    stable_arrangement_task_agent_provenance_json,
)


def test_composition_provenance_shape_and_axis_contributions():
    artifact = compose_arrangement_task_agent_to_operator_subset(
        arrangement_id="pavlovian",
        phenomenon_id="acquisition",
        agent_bundle_id="rw_classical",
    )
    provenance = artifact["provenance"]
    assert provenance["arrangement_id"] == "pavlovian"
    assert provenance["phenomenon_id"] == "acquisition"
    assert provenance["task_implementation_id"] == "pavlovian_acquisition"
    assert provenance["agent_bundle_id"] == "rw_classical"
    assert provenance["axis_to_slot_contribution"]["arrangement"]["required_slots"]
    assert provenance["axis_to_slot_contribution"]["task"]["required_operators"]
    assert provenance["axis_to_slot_contribution"]["agent"]["operator_slots"]


def test_composition_provenance_hash_is_deterministic():
    a = compose_arrangement_task_agent_to_operator_subset(
        arrangement_id="operant",
        phenomenon_id="acquisition",
        agent_bundle_id="rw_operant",
    )["provenance"]
    b = compose_arrangement_task_agent_to_operator_subset(
        arrangement_id="operant",
        phenomenon_id="acquisition",
        agent_bundle_id="rw_operant",
    )["provenance"]
    assert stable_arrangement_task_agent_provenance_json(a) == stable_arrangement_task_agent_provenance_json(b)
    assert stable_arrangement_task_agent_provenance_hash(a) == stable_arrangement_task_agent_provenance_hash(b)
    assert a["composition_hash"] == stable_arrangement_task_agent_provenance_hash(a)


def test_preset_wrapper_composition_compatibility():
    artifact = compose_from_preset_reference(
        preset_id="differential_acquisition",
        agent_bundle_id="rw_classical",
    )
    assert artifact["provenance"]["arrangement_id"] == "pavlovian"
    assert artifact["provenance"]["phenomenon_id"] == "differential_acquisition"
    assert artifact["provenance"]["task_implementation_id"] == "pavlovian_differential_acquisition"


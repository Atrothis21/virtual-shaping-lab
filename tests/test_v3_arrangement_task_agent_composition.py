from __future__ import annotations

import pytest

from ui.contracts.arrangement_task_agent_composition import (
    ArrangementTaskAgentCompositionError,
    compose_arrangement_task_agent_to_operator_subset,
    stable_arrangement_task_agent_composition_hash,
)


def test_arrangement_task_agent_composition_determinism():
    a = compose_arrangement_task_agent_to_operator_subset(
        arrangement_id="pavlovian",
        phenomenon_id="acquisition",
        agent_bundle_id="rw_classical",
    )
    b = compose_arrangement_task_agent_to_operator_subset(
        arrangement_id="pavlovian",
        phenomenon_id="acquisition",
        agent_bundle_id="rw_classical",
    )
    assert a == b
    assert stable_arrangement_task_agent_composition_hash(a) == stable_arrangement_task_agent_composition_hash(b)


def test_arrangement_task_agent_composition_accepts_known_valid_tuple():
    artifact = compose_arrangement_task_agent_to_operator_subset(
        arrangement_id="pavlovian",
        phenomenon_id="extinction",
        agent_bundle_id="rw_classical",
    )
    subset = artifact["operator_subset"]
    assert subset["phi"] == "elemental"
    assert subset["w"] == "rescorla_wagner"
    assert "pi" not in subset
    assert artifact["provenance"]["protocol_family"] == "extinction"


def test_arrangement_task_agent_composition_rejects_known_invalid_tuple_with_machine_code():
    with pytest.raises(
        ArrangementTaskAgentCompositionError,
        match="COMP_E_AGENT_ARRANGEMENT_MISMATCH",
    ):
        compose_arrangement_task_agent_to_operator_subset(
            arrangement_id="pavlovian",
            phenomenon_id="acquisition",
            agent_bundle_id="rw_operant",
        )


def test_arrangement_task_agent_composition_rejects_unknown_arrangement_with_machine_code():
    with pytest.raises(
        ArrangementTaskAgentCompositionError,
        match="COMP_E_UNKNOWN_ARRANGEMENT",
    ):
        compose_arrangement_task_agent_to_operator_subset(
            arrangement_id="hybrid",
            phenomenon_id="acquisition",
            agent_bundle_id="legacy_hybrid_bundle",
        )

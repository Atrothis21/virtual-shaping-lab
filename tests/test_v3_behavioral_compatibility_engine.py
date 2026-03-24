from __future__ import annotations

from ui.contracts.behavioral_compatibility_engine import (
    evaluate_behavioral_compatibility,
)
from ui.contracts.operator_legality_engine import evaluate_operator_legality
from ui.contracts.task_registry import resolve_task_implementation_for_tuple


def test_behavioral_compatibility_engine_is_deterministic_for_same_tuple():
    first = evaluate_behavioral_compatibility(
        arrangement_id="pavlovian",
        phenomenon_id="acquisition",
        agent_bundle_id="rw_classical",
        edits={"n_trials": 20},
    )
    second = evaluate_behavioral_compatibility(
        arrangement_id="pavlovian",
        phenomenon_id="acquisition",
        agent_bundle_id="rw_classical",
        edits={"n_trials": 20},
    )
    assert first == second


def test_behavioral_compatibility_engine_uses_legality_gating():
    result = evaluate_behavioral_compatibility(
        arrangement_id="hybrid",
        phenomenon_id="acquisition",
        agent_bundle_id="legacy_hybrid_bundle",
    )
    assert result["status"] == "structurally_invalid"
    assert result["source"] == "legality_engine"
    assert result["legality"]["is_legal"] is False
    assert result["legality"]["diagnostics"]
    assert result["legality"]["diagnostics"][0]["code"] == "LGL_E_TUPLE_COMPOSITION"


def test_behavioral_compatibility_engine_parity_with_legality_engine_for_invalid_tuple():
    legality = evaluate_operator_legality(
        arrangement_id="hybrid",
        phenomenon_id="acquisition",
        agent_bundle_id="legacy_hybrid_bundle",
    )
    result = evaluate_behavioral_compatibility(
        arrangement_id="hybrid",
        phenomenon_id="acquisition",
        agent_bundle_id="legacy_hybrid_bundle",
    )
    assert result["legality"]["diagnostics"] == legality


def test_behavioral_compatibility_engine_returns_known_tuple_expectation_snapshot():
    result = evaluate_behavioral_compatibility(
        arrangement_id="pavlovian",
        phenomenon_id="acquisition",
        agent_bundle_id="rw_classical",
        edits={"n_trials": 20},
    )
    assert result["status"] == "success"
    assert result["task_implementation_id"] == "pavlovian_acquisition"
    assert result["matched_registry_entry_id"] == "pavlovian_acquisition_rw_classical_default"


def test_behavioral_compatibility_engine_resolves_edit_conditional_partial_branch():
    result = evaluate_behavioral_compatibility(
        arrangement_id="operant",
        phenomenon_id="acquisition",
        agent_bundle_id="rw_operant",
        edits={"n_trials": 3},
    )
    assert result["status"] == "partial"
    assert result["matched_registry_entry_id"] == "operant_acquisition_rw_operant_short_horizon"


def test_behavioral_compatibility_engine_returns_behaviorally_unsupported_for_legal_uncovered_tuple():
    # Legal tuple (operant extinction + rw_operant) intentionally lacks behavioral coverage.
    result = evaluate_behavioral_compatibility(
        arrangement_id="operant",
        phenomenon_id="extinction",
        agent_bundle_id="rw_operant",
    )
    expected_impl = resolve_task_implementation_for_tuple(
        phenomenon_id="extinction",
        arrangement_id="operant",
    )["id"]
    assert result["legality"]["is_legal"] is True
    assert result["status"] == "behaviorally_unsupported"
    assert result["task_implementation_id"] == expected_impl
    assert result["unmet_behavioral_requirements"]


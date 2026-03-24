from __future__ import annotations

from ui.contracts.behavioral_compatibility_engine import evaluate_behavioral_compatibility
from ui.contracts.operator_legality_engine import evaluate_operator_legality


def test_legality_and_behavior_layers_remain_separate_for_invalid_tuple():
    legality = evaluate_operator_legality(
        arrangement_id="hybrid",
        phenomenon_id="acquisition",
        agent_bundle_id="legacy_hybrid_bundle",
    )
    behavioral = evaluate_behavioral_compatibility(
        arrangement_id="hybrid",
        phenomenon_id="acquisition",
        agent_bundle_id="legacy_hybrid_bundle",
    )

    assert legality
    assert behavioral["status"] == "structurally_invalid"
    assert behavioral["legality"]["diagnostics"] == legality


def test_legality_and_behavior_layers_remain_separate_for_legal_tuple():
    legality = evaluate_operator_legality(
        arrangement_id="pavlovian",
        phenomenon_id="acquisition",
        agent_bundle_id="rw_classical",
    )
    behavioral = evaluate_behavioral_compatibility(
        arrangement_id="pavlovian",
        phenomenon_id="acquisition",
        agent_bundle_id="rw_classical",
    )

    assert legality == []
    assert behavioral["legality"]["is_legal"] is True
    assert behavioral["status"] in {"success", "partial", "behaviorally_unsupported", "novel"}
    assert behavioral["source"] != "legality_engine"


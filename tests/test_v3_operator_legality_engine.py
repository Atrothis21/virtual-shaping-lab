from __future__ import annotations

import copy

import pytest

from ui.contracts.operator_legality_engine import (
    OPERATOR_COMPATIBILITY_MATRIX,
    OperatorLegalityError,
    evaluate_operator_legality,
    list_operator_legality_error_codes,
    validate_operator_legality,
    validate_slot_selection_legality,
)
from ui.contracts.operator_subset_contract import PRESET_DEFINITION_TEMPLATE


def _preset() -> dict:
    return copy.deepcopy(PRESET_DEFINITION_TEMPLATE)


def test_legality_engine_accepts_canonical_acquisition_subset():
    payload = _preset()
    validated = validate_operator_legality(payload)
    assert validated["delta"] == "rw_error"
    assert validated["w"] == "rescorla_wagner"


def test_legality_engine_rejects_conditional_requirement_delta_requires_trace():
    payload = _preset()
    payload["operator_subset"]["delta"] = "td_lambda_error"
    payload["operator_subset"]["e"] = "none"
    with pytest.raises(OperatorLegalityError, match="LGL_E_DELTA_REQUIRES_TRACE"):
        validate_operator_legality(payload)


def test_legality_engine_rejects_incompatible_classical_policy_pair():
    payload = _preset()
    payload["operator_subset"]["p"] = "state_action_value"
    payload["operator_subset"]["pi"] = "softmax"
    with pytest.raises(OperatorLegalityError, match="LGL_E_CLASSICAL_POLICY_INCOMPATIBLE"):
        validate_operator_legality(payload)


@pytest.mark.parametrize(
    "patch,expected_code",
    [
        (
            {
                "operator_subset": {"delta": "td_lambda_error", "e": "none"},
            },
            "LGL_E_DELTA_REQUIRES_TRACE",
        ),
        (
            {
                "operator_subset": {"pi": "softmax", "p": "state_value"},
            },
            "LGL_E_POLICY_REQUIRES_ACTION_PREDICTOR",
        ),
        (
            {
                "operator_subset": {"w": "actor_critic_update", "delta": "rw_error"},
            },
            "LGL_E_ACTOR_CRITIC_TRIPLET",
        ),
    ],
)
def test_legality_engine_error_code_snapshots(patch, expected_code):
    payload = _preset()
    payload["operator_subset"].update(patch["operator_subset"])
    diagnostics = evaluate_operator_legality(payload)
    assert diagnostics
    assert diagnostics[0]["code"] == expected_code


def test_legality_matrix_coverage_entries_exercised():
    expected_codes = set(OPERATOR_COMPATIBILITY_MATRIX.keys())
    assert set(list_operator_legality_error_codes()) == expected_codes

    observed: set[str] = set()
    with pytest.raises(OperatorLegalityError) as exc:
        validate_slot_selection_legality("phi", "not_declared")
    observed.add(exc.value.code)

    scenarios = [
        {"operator_subset": {"delta": "td_lambda_error", "e": "none"}},
        {"operator_subset": {"pi": "softmax", "p": "state_value"}},
        {"operator_subset": {"pi": "softmax", "p": "state_action_value"}},
        {"operator_subset": {"w": "actor_critic_update", "delta": "rw_error"}},
        {"operator_subset": {"m": ["action_probabilities"]}},
        {"operator_subset": {"m": ["eligibility_curve"]}},
    ]

    for scenario in scenarios:
        payload = _preset()
        payload["operator_subset"].update(scenario["operator_subset"])
        diagnostics = evaluate_operator_legality(payload)
        observed.update(d["code"] for d in diagnostics)

    assert expected_codes.issubset(observed)

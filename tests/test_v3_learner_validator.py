from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.learning import LearnerSpec, LearnerSpecValidationError, validate_learner_spec


def _legal_spec() -> LearnerSpec:
    return LearnerSpec(
        trace="none",
        predictor="state_value",
        error="rw_error",
        attention="fixed",
        updater="delta_rule",
        policy="none",
    )


def test_validate_learner_spec_accepts_legal_classical_tuple():
    spec = _legal_spec()
    validate_learner_spec(spec)


@pytest.mark.parametrize(
    "patch,code",
    [
        ({"predictor": "state_value", "error": "sarsa_error"}, "LGR_E_ERROR_REQUIRES_Q_PREDICTOR"),
        ({"predictor": "q_value", "policy": "none", "error": "q_error"}, "LGR_E_ERROR_REQUIRES_ACTION_POLICY"),
        ({"trace": "none", "updater": "trace_delta_rule"}, "LGR_E_TRACE_REQUIRED"),
        ({"attention": "pearce_hall", "updater": "delta_rule"}, "LGR_E_ATTENTION_UPDATER_MISMATCH"),
        ({"error": "expected_sarsa_error", "predictor": "q_value", "policy": "greedy"}, "LGR_E_EXPECTED_SARSA_POLICY"),
        ({"predictor": "actor_critic_pair", "error": "td_error", "updater": "actor_critic_update", "policy": "actor_policy"}, "LGR_E_ACTOR_CRITIC_ERROR"),
        (
            {
                "trace": "eligibility",
                "updater": "actor_critic_update",
                "predictor": "q_value",
                "error": "q_error",
                "policy": "epsilon_greedy",
            },
            "LGR_E_ACTOR_CRITIC_UPDATER_REQUIRES_AC_PREDICTOR",
        ),
    ],
)
def test_validate_learner_spec_rejects_illegal_tuples_with_named_error_codes(patch, code):
    payload = _legal_spec().to_dict()
    payload.update(patch)
    with pytest.raises(LearnerSpecValidationError) as exc:
        LearnerSpec.from_dict(payload)
    assert exc.value.code == code

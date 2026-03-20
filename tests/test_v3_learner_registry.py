from __future__ import annotations

from virtual_shaping_lab.vsl.agent.learning import (
    COMPATIBILITY_MATRIX,
    SLOT_REGISTRIES,
    compatibility_matrix,
    learner_registry_hash,
    learner_registry_payload,
    slot_registries,
)
from virtual_shaping_lab.vsl.agent.learning.validation import (
    ACTOR_CRITIC_REQUIRED,
    ATTENTION_TO_UPDATERS_STRICT,
    ATTENTION_VALUES,
    ERROR_VALUES,
    ERROR_REQUIRES_ACTION_POLICY,
    ERROR_REQUIRES_Q_PREDICTOR,
    EXPECTED_SARSA_POLICIES,
    POLICY_VALUES,
    POLICY_NONE_INCOMPATIBLE_PREDICTORS,
    PREDICTOR_TO_ERRORS,
    PREDICTOR_TO_POLICIES,
    PREDICTOR_VALUES,
    TRACE_TO_UPDATERS,
    TRACE_VALUES,
    UPDATER_VALUES,
)


def test_v3_learner_slot_registries_are_machine_readable():
    payload = slot_registries()
    assert set(payload.keys()) == {"trace", "predictor", "error", "attention", "updater", "policy"}
    assert all(isinstance(values, list) for values in payload.values())
    assert payload == SLOT_REGISTRIES


def test_v3_learner_compatibility_matrix_is_machine_readable():
    matrix = compatibility_matrix()
    assert set(matrix.keys()) == {
        "predictor_to_error",
        "predictor_to_policy",
        "trace_to_updater",
        "attention_to_updater_strict",
        "error_requires_q_predictor",
        "error_requires_action_policy",
        "expected_sarsa_policy",
        "policy_none_incompatible_predictors",
        "actor_critic_required",
    }
    assert matrix == COMPATIBILITY_MATRIX


def test_v3_learner_registry_parity_with_validator_constants():
    assert SLOT_REGISTRIES["trace"] == sorted(TRACE_VALUES)
    assert SLOT_REGISTRIES["predictor"] == sorted(PREDICTOR_VALUES)
    assert SLOT_REGISTRIES["error"] == sorted(ERROR_VALUES)
    assert SLOT_REGISTRIES["attention"] == sorted(ATTENTION_VALUES)
    assert SLOT_REGISTRIES["updater"] == sorted(UPDATER_VALUES)
    assert SLOT_REGISTRIES["policy"] == sorted(POLICY_VALUES)

    assert COMPATIBILITY_MATRIX["predictor_to_error"] == {
        key: sorted(values) for key, values in sorted(PREDICTOR_TO_ERRORS.items())
    }
    assert COMPATIBILITY_MATRIX["predictor_to_policy"] == {
        key: sorted(values) for key, values in sorted(PREDICTOR_TO_POLICIES.items())
    }
    assert COMPATIBILITY_MATRIX["trace_to_updater"] == {
        key: sorted(values) for key, values in sorted(TRACE_TO_UPDATERS.items())
    }
    assert COMPATIBILITY_MATRIX["attention_to_updater_strict"] == {
        key: sorted(values) for key, values in sorted(ATTENTION_TO_UPDATERS_STRICT.items())
    }
    assert COMPATIBILITY_MATRIX["error_requires_q_predictor"] == {
        "errors": sorted(ERROR_REQUIRES_Q_PREDICTOR),
        "allowed_predictors": ["nonlinear_q", "q_value"],
    }
    assert COMPATIBILITY_MATRIX["error_requires_action_policy"] == {
        "errors": sorted(ERROR_REQUIRES_ACTION_POLICY),
        "forbidden_policy": ["none"],
    }
    assert COMPATIBILITY_MATRIX["expected_sarsa_policy"] == {
        "error": ["expected_sarsa_error"],
        "allowed_policies": sorted(EXPECTED_SARSA_POLICIES),
    }
    assert COMPATIBILITY_MATRIX["policy_none_incompatible_predictors"] == {
        "predictors": sorted(POLICY_NONE_INCOMPATIBLE_PREDICTORS),
        "policy": ["none"],
    }
    assert COMPATIBILITY_MATRIX["actor_critic_required"] == {
        "predictor": [ACTOR_CRITIC_REQUIRED["predictor"]],
        "error": [ACTOR_CRITIC_REQUIRED["error"]],
        "updater": [ACTOR_CRITIC_REQUIRED["updater"]],
        "policy": [ACTOR_CRITIC_REQUIRED["policy"]],
    }


def test_v3_learner_registry_payload_and_hash_are_stable():
    payload = learner_registry_payload()
    assert payload["version"] == "3.5.0"
    assert payload["slot_registries"] == SLOT_REGISTRIES
    assert payload["compatibility_matrix"] == COMPATIBILITY_MATRIX
    hashes = [learner_registry_hash() for _ in range(20)]
    assert len(set(hashes)) == 1

from experiment.parameters.composer import ParameterComposer, parameters_to_dict
from experiment.parameters.types import (
    EpsilonGreedyPolicyParams,
    ExperimentParameters,
    NullPolicyParams,
)


def _payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {
                    "stimuli": ["tone", "noise"],
                    "contexts": ["A", "B"],
                    "temporal_basis": {
                        "enabled": True,
                        "variant": "identity",
                        "dimension": 1,
                    },
                    "similarity": {
                        "type": "matrix",
                        "stimuli": ["tone", "noise"],
                        "values": [
                            [1.0, 0.2],
                            [0.2, 1.0],
                        ],
                    },
                },
            },
            "prediction_error": {"variant": "rescorla_wagner", "params": {}},
            "attention": {"tone": {"attention": 0.8}, "noise": 0.5},
            "salience": {"tone": 0.9, "noise": 0.6},
            "policy": {"name": "epsilon-greedy", "params": {"epsilon": 0.2, "actions": ["left", "right"]}},
            "runtime": {"seed": 7, "update_mode": "tick", "record_mode": "tick", "strict_records": True},
            "phases": [
                {
                    "name": "Acquisition",
                    "protocol": "Acquisition",
                    "params": {
                        "n_trials": "5",
                        "alpha": 0.2,
                        "gamma": 0.0,
                        "duration_s": 1.0,
                        "dt_s": 0.1,
                        "context": "A",
                    },
                }
            ],
        }
    }


def test_parameter_composer_produces_typed_parameters():
    params = ParameterComposer.compose(_payload())
    assert isinstance(params, ExperimentParameters)
    assert params.learner.algorithm == "rescorla_wagner"
    assert params.learner.prediction_error_rule.variant == "rescorla_wagner"
    assert params.representation.temporal_basis.enabled is True
    assert params.representation.temporal_basis.dimension == 1
    assert params.runtime.update_mode == "tick"
    assert params.units[0].unit_key == "acquisition"
    assert isinstance(params.policy, EpsilonGreedyPolicyParams)
    assert params.policy.epsilon == 0.2


def test_parameter_composer_handles_missing_policy_as_null():
    payload = _payload()
    payload["experiment"].pop("policy")
    params = ParameterComposer.compose(payload)
    assert isinstance(params.policy, NullPolicyParams)


def test_parameters_to_dict_is_deterministic():
    p1 = _payload()
    p2 = _payload()
    # reorder maps intentionally
    p2["experiment"]["salience"] = {"noise": 0.6, "tone": 0.9}
    p2["experiment"]["attention"] = {"noise": 0.5, "tone": {"attention": 0.8}}

    composed_1 = ParameterComposer.compose(p1)
    composed_2 = ParameterComposer.compose(p2)
    assert parameters_to_dict(composed_1) == parameters_to_dict(composed_2)


def test_parameter_composer_defaults_prediction_error_rule_to_algorithm():
    payload = _payload()
    payload["experiment"].pop("prediction_error")
    params = ParameterComposer.compose(payload)
    assert params.learner.prediction_error_rule.variant == "rescorla_wagner"


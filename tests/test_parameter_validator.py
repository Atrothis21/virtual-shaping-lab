import pytest

from experiment.parameters.pipeline import (
    ParameterNormalizerPipeline,
    ParameterValidatorPipeline,
)


def _base_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": ["tone", "noise"], "contexts": ["A", "B"]},
            },
            "attention": {"tone": 0.8},
            "phases": [
                {
                    "protocol": "acquisition",
                    "params": {"n_trials": 5, "duration_s": 1.0, "dt_s": 0.1, "context": "A"},
                }
            ],
        }
    }


def test_parameter_validator_accepts_valid_payload():
    payload = ParameterNormalizerPipeline.normalize(_base_payload())
    ParameterValidatorPipeline.validate(payload)


def test_parameter_validator_rejects_attention_in_representation():
    payload = _base_payload()
    payload["experiment"]["representation"]["params"]["attention"] = {"tone": 0.8}
    with pytest.raises(ValueError, match="must not include attention"):
        ParameterValidatorPipeline.validate(payload)


def test_parameter_validator_rejects_phase_cross_concern_keys():
    payload = _base_payload()
    payload["experiment"]["phases"][0]["params"]["salience"] = {"tone": 0.7}
    with pytest.raises(ValueError, match="forbidden cross-concern keys"):
        ParameterValidatorPipeline.validate(payload)


def test_parameter_validator_rejects_asymmetric_similarity_matrix():
    payload = _base_payload()
    payload["experiment"]["representation"]["params"]["similarity"] = {
        "type": "matrix",
        "values": [
            [1.0, 0.5],
            [0.1, 1.0],
        ],
    }
    with pytest.raises(ValueError, match="must be symmetric"):
        ParameterValidatorPipeline.validate(payload)


def test_parameter_validator_rejects_unknown_attention_keys():
    payload = _base_payload()
    payload["experiment"]["attention"] = {"unknown": 0.6}
    with pytest.raises(ValueError, match="attention keys not in known stimuli"):
        ParameterValidatorPipeline.validate(payload)


def test_parameter_validator_attention_config_contract():
    payload = _base_payload()
    payload["experiment"]["attention_config"] = {"name": "pearce_hall", "params": {"eta": 0.2}}
    ParameterValidatorPipeline.validate(payload)

    payload = _base_payload()
    payload["experiment"]["attention"] = {"name": "mackintosh", "params": {"kappa": 0.1}}
    ParameterValidatorPipeline.validate(payload)

    payload = _base_payload()
    payload["experiment"]["attention_config"] = {"name": "pearce_hall"}
    with pytest.raises(ValueError, match="must include 'name' and 'params'"):
        ParameterValidatorPipeline.validate(payload)

    payload = _base_payload()
    payload["experiment"]["attention_config"] = {"name": "unknown_model", "params": {}}
    with pytest.raises(ValueError, match="Unsupported experiment.attention_config.name"):
        ParameterValidatorPipeline.validate(payload)

    payload = _base_payload()
    payload["experiment"]["attention_config"] = {
        "name": "pearce_hall",
        "params": {"eta": 1.5},
    }
    with pytest.raises(ValueError, match="eta must be in \\[0,1\\]"):
        ParameterValidatorPipeline.validate(payload)

    payload = _base_payload()
    payload["experiment"]["attention_config"] = {
        "name": "static",
        "params": {"overrides": {"tone": -0.1}},
    }
    with pytest.raises(ValueError, match="overrides\\['tone'\\].*\\[0,1\\]"):
        ParameterValidatorPipeline.validate(payload)


def test_parameter_validator_rejects_non_grid_aligned_dt_duration():
    payload = _base_payload()
    payload["experiment"]["phases"][0]["params"]["duration_s"] = 1.0
    payload["experiment"]["phases"][0]["params"]["dt_s"] = 0.3
    with pytest.raises(ValueError, match="dt_s must divide duration_s"):
        ParameterValidatorPipeline.validate(payload)


def test_parameter_validator_rejects_undeclared_context():
    payload = _base_payload()
    payload["experiment"]["phases"][0]["params"]["context"] = "C"
    with pytest.raises(ValueError, match="not declared in representation contexts"):
        ParameterValidatorPipeline.validate(payload)


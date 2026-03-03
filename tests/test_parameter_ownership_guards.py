import pytest

from experiment.assemble import assemble_experiment
from experiment.domain.types import ExperimentPlan
from experiment.runner import Runner
from experiment.parameters import validate_composed_parameter_ownership


def _base_composed():
    return {
        "representation": {
            "context": {"mode": "gated", "contexts": ["A"], "inference_enabled": False},
            "salience": {"default": 1.0, "overrides": {}},
            "similarity": {"enabled": False, "matrix": {}},
        },
        "learner": {
            "algorithm": "rescorla_wagner",
            "alpha": 0.1,
            "gamma": 0.0,
            "attention": {"mode": "none", "default": 1.0, "overrides": {}},
        },
        "policy": {"name": "null"},
        "runtime": {"seed": None, "update_mode": "trial", "record_mode": "trial", "strict_records": False},
        "units": [
            {
                "unit_key": "acquisition",
                "name": "Acq",
                "context_id": "A",
                "n_trials": 1,
                "time": {"duration_s": 1.0, "dt_s": 1.0},
                "contingency": {"n_trials": 1},
                "learning_gate": {"enabled": True},
                "metadata": {"phase_index": 0},
            }
        ],
    }


def test_validate_composed_parameter_ownership_accepts_valid_structure():
    validate_composed_parameter_ownership(_base_composed())


def test_validate_composed_parameter_ownership_rejects_representation_attention():
    composed = _base_composed()
    composed["representation"]["attention"] = {"tone": 0.8}
    with pytest.raises(ValueError, match="representation object must not contain learner-owned keys"):
        validate_composed_parameter_ownership(composed)


def test_validate_composed_parameter_ownership_rejects_learner_representation_keys():
    composed = _base_composed()
    composed["learner"]["salience"] = {"tone": 0.5}
    with pytest.raises(ValueError, match="learner object must not contain representation-owned keys"):
        validate_composed_parameter_ownership(composed)


def test_validate_composed_parameter_ownership_rejects_policy_non_policy_keys():
    composed = _base_composed()
    composed["policy"]["alpha"] = 0.1
    with pytest.raises(ValueError, match="policy object contains non-policy keys"):
        validate_composed_parameter_ownership(composed)


def test_validate_composed_parameter_ownership_rejects_runtime_non_runtime_keys():
    composed = _base_composed()
    composed["runtime"]["epsilon"] = 0.2
    with pytest.raises(ValueError, match="runtime object contains non-runtime keys"):
        validate_composed_parameter_ownership(composed)


def test_validate_composed_parameter_ownership_rejects_unit_contingency_leaks():
    composed = _base_composed()
    composed["units"][0]["contingency"]["attention"] = {"tone": 0.9}
    with pytest.raises(ValueError, match="unit contingency must not contain learner/representation-owned keys"):
        validate_composed_parameter_ownership(composed)


def test_assemble_experiment_fails_fast_on_invalid_composed_parameters():
    plan = ExperimentPlan(
        units=[
            {
                "name": "Acq",
                "protocol": "acquisition",
                "stimuli": {"cs_plus": ["tone"]},
                "params": {"n_trials": 1},
            }
        ],
        settings={
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": ["tone"], "max_compound_size": 2},
            },
            "composed_parameters": {
                "representation": {"attention": {"tone": 0.8}},
            },
        },
    )
    with pytest.raises(ValueError, match="Ownership contract violation"):
        assemble_experiment(plan)


def test_runner_fails_fast_on_invalid_composed_runtime_object():
    with pytest.raises(ValueError, match="runtime object contains non-runtime keys"):
        Runner(
            runtime_units=[],
            settings={
                "composed_parameters": {
                    "runtime": {"update_mode": "trial", "alpha": 0.1},
                }
            },
        )


def test_assemble_experiment_rejects_template_phase_param_ownership_leaks():
    plan = ExperimentPlan(
        units=[
            {
                "name": "Template Acquisition",
                "protocol": "acquisition_template",
                "stimuli": {"cs_plus": ["tone"]},
                "params": {"n_trials": 1, "salience": {"tone": 0.4}},
            }
        ],
        settings={
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": ["tone"], "max_compound_size": 2},
            },
            "policy": None,
            "stimuli": ["tone"],
            "salience": {},
            "attention": {},
            "context_inference": {},
        },
    )
    with pytest.raises(ValueError, match="must not include representation/learner-owned keys"):
        assemble_experiment(plan)

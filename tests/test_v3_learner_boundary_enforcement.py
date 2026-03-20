from __future__ import annotations

import pytest

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from virtual_shaping_lab.vsl.agent.learning import LearnerSpecValidationError


def _base_payload() -> dict:
    return {
        "experiment": {
            "program": {
                "phases": [
                    {
                        "name": "Phase 1",
                        "protocol": "acquisition",
                        "stimuli": {"cs_plus": ["tone"]},
                        "params": {"n_trials": 1, "alpha": 0.2, "gamma": 0.0},
                        "trials": 1,
                    }
                ],
            },
            "agent": {
                "name": "classical_agent",
                "representation": {
                    "name": "vector_elemental",
                    "params": {"stimuli": ["tone"], "max_compound_size": 2},
                },
                "learning": {"rule": "rescorla_wagner", "params": {}},
                "policy": None,
            },
            "runtime": {},
        },
        "report": {"preset": "acquisition"},
    }


def test_v3_learner_enforcement_build_plan_embeds_learner_spec():
    plan = ExperimentConfig.plan_from_payload(_base_payload())
    learner_spec = plan.agent_spec["learning"]["learner_spec"]
    assert learner_spec["trace"] == "none"
    assert learner_spec["predictor"] == "state_value"
    assert learner_spec["error"] == "rw_error"
    assert learner_spec["policy"] == "none"
    assert isinstance(plan.settings.get("learner_spec_hash"), str)


def test_v3_learner_enforcement_build_plan_fails_on_illegal_legacy_tuple():
    payload = _base_payload()
    payload["experiment"]["agent"]["learning"]["rule"] = "q_learner"
    with pytest.raises(LearnerSpecValidationError, match="LGR_E_ERROR_REQUIRES_ACTION_POLICY"):
        ExperimentConfig.plan_from_payload(payload)


def test_v3_learner_enforcement_runtime_assembly_fails_on_invalid_explicit_spec():
    plan = ExperimentConfig.plan_from_payload(_base_payload())
    plan.agent_spec["learning"]["learner_spec"] = {
        "trace": "none",
        "predictor": "state_value",
        "error": "sarsa_error",
        "attention": "fixed",
        "updater": "delta_rule",
        "policy": "none",
        "metadata": {"boundary": "test"},
    }
    with pytest.raises(LearnerSpecValidationError, match="LGR_E_ERROR_REQUIRES_Q_PREDICTOR"):
        assemble_experiment(plan)


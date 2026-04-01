from __future__ import annotations

import pytest

from analysis.report import report as report_module
from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment, RolloutHarness
from virtual_shaping_lab.vsl.program import compile_environment_program


def _compiled_env(*, protocol: str, stimuli: dict, params: dict) -> CompiledProgramTestEnvironment:
    program = compile_environment_program(
        {
            "phases": [
                {
                    "name": "Phase",
                    "protocol": protocol,
                    "stimuli": stimuli,
                    "params": params,
                }
            ]
        }
    )
    return CompiledProgramTestEnvironment(program)


@pytest.mark.parametrize(
    "case_id, protocol, stimuli, params, forced_action, expect_actioned",
    [
        (
            "classical_acquisition",
            "acquisition",
            {"cs_plus": ["tone"]},
            {"n_trials": 2, "outcome": 1.0},
            None,
            False,
        ),
        (
            "actioned_operant",
            "operant_conditioning",
            {"cs_plus": ["lever"]},
            {"n_trials": 2, "reward": 1.0},
            "leverpress",
            True,
        ),
    ],
)
def test_v3_21_20_protocol_integration_matrix_spans_runtime_and_report_surfaces(
    case_id: str,
    protocol: str,
    stimuli: dict,
    params: dict,
    forced_action,
    expect_actioned: bool,
):
    _ = case_id
    env = _compiled_env(protocol=protocol, stimuli=stimuli, params=params)
    records = RolloutHarness().run(env, seed=31, action=forced_action)
    assert records

    for rec in records:
        metadata = rec["metadata"]
        assert isinstance(metadata.get("protocol"), dict)
        assert isinstance(metadata.get("observation"), dict)
        assert isinstance(metadata.get("learner"), dict)
        assert isinstance(metadata.get("policy"), dict)

        protocol_meta = metadata["protocol"]
        assert isinstance(protocol_meta.get("emission"), dict)
        assert isinstance(protocol_meta.get("consequence"), dict)
        assert isinstance(protocol_meta.get("advance"), dict)
        assert isinstance(protocol_meta.get("stop"), dict)
        assert protocol_meta.get("pipeline_order") == ["emit", "consequence", "advance", "stop", "finalize"]

        observation_meta = metadata["observation"]
        assert isinstance(observation_meta.get("output"), dict)
        assert isinstance(observation_meta.get("measurements"), dict)

        learner_meta = metadata["learner"]
        assert "prediction" in learner_meta
        assert "error" in learner_meta
        assert isinstance(learner_meta.get("input_features"), dict)

        policy_meta = metadata["policy"]
        assert "action" in policy_meta
        assert isinstance(policy_meta.get("available_actions"), list)
        assert isinstance(policy_meta.get("action_scores"), dict)
        assert isinstance(policy_meta.get("action_probabilities"), dict)

        normalized = report_module._normalize_record_for_artifact(
            {
                "trial": rec["step_index"],
                "reward": rec["reward"],
                "action": rec["action"],
                "done": rec["done"],
                "metadata": metadata,
            }
        )
        assert isinstance(normalized.get("protocol_emission"), dict)
        assert isinstance(normalized.get("protocol_consequence"), dict)
        assert isinstance(normalized.get("protocol_advance"), dict)
        assert isinstance(normalized.get("protocol_stop"), dict)
        assert isinstance(normalized.get("protocol_timing"), dict)
        assert isinstance(normalized.get("protocol_provenance"), dict)

        assert "representation" in normalized
        assert "prediction" in normalized
        assert "policy_action" in normalized

        emission_actions = normalized["protocol_emission"].get("available_actions", [])
        assert isinstance(emission_actions, list)
        if expect_actioned:
            assert len(emission_actions) > 0

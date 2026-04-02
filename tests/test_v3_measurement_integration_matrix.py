from __future__ import annotations

from copy import deepcopy

import pytest

from analysis.report import report as report_module
from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment, RolloutHarness
from virtual_shaping_lab.vsl.measurement import build_executable_measurement_preset
from virtual_shaping_lab.vsl.program import compile_environment_program
from virtual_shaping_lab.vsl.rollout import ReplayHarness


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
    "case_id, protocol, stimuli, params, forced_action, measurement_preset, expected_metric_keys",
    [
        (
            "classical_acquisition_learning_curve",
            "acquisition",
            {"cs_plus": ["tone"]},
            {"n_trials": 3, "outcome": 1.0},
            None,
            "learning_curve_basic",
            {"trial_count", "mean_reward", "reward_curve", "cumulative_reward_curve"},
        ),
        (
            "actioned_operant_action_learning_curve",
            "operant_conditioning",
            {"cs_plus": ["lever"]},
            {"n_trials": 3, "reward": 1.0},
            "leverpress",
            "action_learning_curve",
            {"trial_count", "mean_reward", "reward_curve", "response_rate"},
        ),
    ],
)
def test_v3_22_20_measurement_integration_matrix_spans_protocol_agent_measurement_and_report(
    case_id: str,
    protocol: str,
    stimuli: dict,
    params: dict,
    forced_action,
    measurement_preset: str,
    expected_metric_keys: set[str],
):
    _ = case_id
    # Runtime integration: protocol + observation + learner + policy surfaces.
    env = _compiled_env(protocol=protocol, stimuli=stimuli, params=params)
    records = RolloutHarness().run(env, seed=41, action=forced_action)
    assert records
    for rec in records:
        metadata = rec["metadata"]
        assert isinstance(metadata.get("protocol"), dict)
        assert isinstance(metadata.get("observation"), dict)
        assert isinstance(metadata.get("learner"), dict)
        assert isinstance(metadata.get("policy"), dict)

    # Measurement integration: deterministic post-run seam.
    env_for_measurement = _compiled_env(protocol=protocol, stimuli=stimuli, params=params)
    replay_records, measurement_out = ReplayHarness().run_with_measurement(
        env_for_measurement,
        rollout_id=f"measurement_matrix_{protocol}",
        episode_id=0,
        seed=41,
        action=forced_action,
        measurement_preset_name=measurement_preset,
    )
    assert replay_records
    assert set(measurement_out.analysis.metrics.keys()) >= expected_metric_keys

    # Phenomenon-signature mapping coverage (behavior_measurement.md alignment).
    assert build_executable_measurement_preset(measurement_preset).preset_name == measurement_preset

    # Report normalization integration: embed promoted measurement traces and normalize.
    enriched_records = deepcopy(records)
    measurement_traces = {
        "metrics": dict(measurement_out.analysis.metrics),
        "figures": list(measurement_out.visualization.figures),
        "summary": dict(measurement_out.report),
        "provenance": {
            "preset_name": measurement_preset,
            "pipeline_order": list(measurement_out.metadata.get("pipeline_order", [])),
        },
    }
    for rec in enriched_records:
        rec.setdefault("metadata", {})
        rec["metadata"]["measurement_traces"] = measurement_traces

    normalized = report_module._normalize_record_for_artifact(
        {
            "trial": enriched_records[0]["step_index"],
            "reward": enriched_records[0]["reward"],
            "action": enriched_records[0]["action"],
            "done": enriched_records[0]["done"],
            "metadata": dict(enriched_records[0]["metadata"]),
        }
    )
    assert isinstance(normalized.get("measurement_metrics"), dict)
    assert isinstance(normalized.get("measurement_figures"), list)
    assert isinstance(normalized.get("measurement_summary"), dict)
    assert isinstance(normalized.get("measurement_provenance"), dict)
    assert set(normalized["measurement_metrics"].keys()) >= expected_metric_keys

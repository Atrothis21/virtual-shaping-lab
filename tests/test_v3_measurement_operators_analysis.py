from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.contracts import Action, Outcome, TaskInput, TrialRecord
from virtual_shaping_lab.vsl.measurement import (
    BlockingDiagnosticsAnalysisOperator,
    LearningCurveBasicAnalysisOperator,
    PolicyDiagnosticsAnalysisOperator,
    PredictionErrorDiagnosticsAnalysisOperator,
)


def _typed_record() -> TrialRecord:
    return TrialRecord(
        trial_index=0,
        task_input=TaskInput(stimuli={"tone": 1.0}, available_actions=("left", "right")),
        action=Action(value="left"),
        outcome=Outcome(reward=1.0, next_stimuli={"tone": 1.0}),
        metadata={
            "prediction_error": 0.25,
            "policy_traces": {"action": "left", "action_probabilities": {"left": 0.8, "right": 0.2}},
            "protocol_traces": {"emission": {"stimulus": {"tone": 1.0}}},
        },
    )


def _mapping_record() -> dict:
    return {
        "trial_index": 1,
        "reward": 0.0,
        "action": "right",
        "task_input": {"stimuli": {"tone": 1.0, "noise": 0.5}, "available_actions": ("left", "right")},
        "metadata": {
            "prediction_error": -0.1,
            "policy_traces": {"action": "right", "action_probabilities": {"left": 0.3, "right": 0.7}},
            "protocol_traces": {"emission": {"stimulus": {"tone": 1.0, "noise": 0.5}}},
        },
    }


def test_v3_22_5_learning_curve_basic_analysis_operator_metrics():
    out = LearningCurveBasicAnalysisOperator().analyze(records=[_typed_record(), _mapping_record()])
    assert out.metadata["variant"] == "learning_curve_basic"
    assert out.metrics["trial_count"] == 2
    assert out.metrics["reward_curve"] == [1.0, 0.0]
    assert out.metrics["cumulative_reward_curve"] == [1.0, 1.0]


def test_v3_22_5_prediction_error_analysis_operator_metrics():
    out = PredictionErrorDiagnosticsAnalysisOperator().analyze(records=[_typed_record(), _mapping_record()])
    assert out.metadata["variant"] == "prediction_error_diagnostics"
    assert out.metrics["prediction_error_curve"] == [0.25, -0.1]
    assert out.metrics["mean_prediction_error"] == pytest.approx(0.075, abs=1e-12)


def test_v3_22_5_policy_diagnostics_analysis_operator_metrics():
    out = PolicyDiagnosticsAnalysisOperator().analyze(records=[_typed_record(), _mapping_record()])
    assert out.metadata["variant"] == "policy_diagnostics"
    assert out.metrics["trial_count"] == 2
    assert out.metrics["action_counts"] == {"left": 1, "right": 1}
    assert len(out.metrics["policy_entropy_curve"]) == 2


def test_v3_22_5_blocking_diagnostics_analysis_operator_metrics():
    out = BlockingDiagnosticsAnalysisOperator().analyze(records=[_typed_record(), _mapping_record()])
    assert out.metadata["variant"] == "blocking_diagnostics"
    assert out.metrics["trial_count"] == 2
    assert "tone" in out.metrics["cue_reward_mean"]
    assert out.metrics["cue_count"]["tone"] == 2

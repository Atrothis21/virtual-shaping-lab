from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.protocol import (
    AdvanceOutput,
    ConsequenceOutput,
    CriterionStopOperator,
    HorizonStopOperator,
    StopOutput,
    TrialCountStopOperator,
)


def test_v3_21_5_trial_count_stop_operator_stops_at_limit():
    op = TrialCountStopOperator(max_trials=3)
    out = op.should_stop(
        state={"t": 2},
        advance=AdvanceOutput(t=3, dt_s=1.0, phase_step=3),
        consequence=ConsequenceOutput(reward=0.0, done=False),
    )
    assert isinstance(out, StopOutput)
    assert out.should_stop is True
    assert out.reason == "trial_count_reached"
    assert out.metadata["variant"] == "stop_on_trial_count"


def test_v3_21_5_horizon_stop_operator_uses_elapsed_plus_dt():
    op = HorizonStopOperator(horizon_s=5.0)
    out = op.should_stop(
        state={"elapsed_s": 4.6},
        advance=AdvanceOutput(t=10, dt_s=0.5, phase_step=10),
        consequence=ConsequenceOutput(reward=0.0, done=False),
    )
    assert out.should_stop is True
    assert out.reason == "horizon_reached"
    assert out.stop_state["elapsed_s"] == pytest.approx(5.1, abs=1e-12)


def test_v3_21_5_criterion_stop_operator_stops_on_reward_threshold():
    op = CriterionStopOperator(reward_threshold=3.0)
    out = op.should_stop(
        state={"cumulative_reward": 2.5},
        advance=AdvanceOutput(t=4, dt_s=1.0, phase_step=4),
        consequence=ConsequenceOutput(reward=0.6, done=False),
    )
    assert out.should_stop is True
    assert out.reason == "criterion_reached"
    assert out.stop_state["cumulative_reward"] == pytest.approx(3.1, abs=1e-12)


def test_v3_21_5_trial_count_stop_operator_rejects_non_positive_limit():
    with pytest.raises(ValueError, match="max_trials"):
        TrialCountStopOperator(max_trials=0)

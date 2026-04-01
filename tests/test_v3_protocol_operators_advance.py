from __future__ import annotations

from virtual_shaping_lab.vsl.protocol import AdvanceOutput, ConsequenceOutput, EventAdvanceOperator, TrialAdvanceOperator


def test_v3_21_5_trial_advance_operator_owns_trial_increment():
    op = TrialAdvanceOperator(dt_s=1.25)
    out = op.advance(
        state={"t": 3, "phase_step": 7},
        consequence=ConsequenceOutput(reward=0.0, done=False),
    )
    assert isinstance(out, AdvanceOutput)
    assert out.t == 4
    assert out.phase_step == 8
    assert out.dt_s == 1.25
    assert out.metadata["variant"] == "trial_increment"


def test_v3_21_5_trial_advance_operator_uses_state_dt_when_present():
    op = TrialAdvanceOperator(dt_s=1.0)
    out = op.advance(
        state={"t": 0, "phase_step": 0, "dt_s": 2.5},
        consequence=ConsequenceOutput(reward=1.0, done=False),
    )
    assert out.dt_s == 2.5


def test_v3_21_5_event_advance_operator_uses_event_dt_and_increments_index():
    op = EventAdvanceOperator(default_event_dt_s=0.1)
    out = op.advance(
        state={"t": 9, "phase_step": 9, "event_dt_s": 0.05},
        consequence=ConsequenceOutput(reward=0.0, done=False),
    )
    assert out.t == 10
    assert out.phase_step == 10
    assert out.dt_s == 0.05
    assert out.metadata["variant"] == "event_increment"

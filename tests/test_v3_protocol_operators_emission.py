from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.protocol import EmissionOutput, FixedEmissionOperator, ScheduledEmissionOperator


def test_v3_21_5_fixed_emission_operator_emits_deterministic_payload():
    op = FixedEmissionOperator(
        stimulus={"tone": 1.0, "noise": 0.2},
        context="A",
        available_actions=("leverpress",),
    )
    out = op.emit(state={"t": 5})
    assert isinstance(out, EmissionOutput)
    assert out.stimulus == {"tone": 1.0, "noise": 0.2}
    assert out.context == "A"
    assert out.available_actions == ("leverpress",)
    assert out.metadata["variant"] == "fixed_emission"


def test_v3_21_5_scheduled_emission_operator_uses_state_time_index():
    op = ScheduledEmissionOperator(
        schedule=(
            {"stimulus": {"tone": 1.0}, "context": "A"},
            {"stimulus": {"noise": 1.0}, "context": "B"},
        )
    )
    out0 = op.emit(state={"t": 0})
    out1 = op.emit(state={"t": 1})
    assert out0.stimulus == {"tone": 1.0}
    assert out1.stimulus == {"noise": 1.0}
    assert out1.context == "B"
    assert out1.metadata["variant"] == "scheduled_emission"


def test_v3_21_5_scheduled_emission_operator_clamps_when_not_looping():
    op = ScheduledEmissionOperator(
        schedule=(
            {"stimulus": {"tone": 1.0}},
            {"stimulus": {"noise": 1.0}},
        ),
        loop=False,
    )
    out = op.emit(state={"t": 8})
    assert out.stimulus == {"noise": 1.0}


def test_v3_21_5_scheduled_emission_operator_rejects_empty_schedule():
    with pytest.raises(ValueError, match="schedule"):
        ScheduledEmissionOperator(schedule=())

from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.learning.operators import (
    AccumulatingEligibilityTraceOperator,
    EligibilityOperator,
    NullEligibilityOperator,
    ReplacingEligibilityTraceOperator,
    reset_eligibility_state,
)


def test_v3_18_10_null_eligibility_operator_is_noop():
    op = NullEligibilityOperator()
    assert isinstance(op, EligibilityOperator)
    state = {"tone": 0.4}
    out = op.apply(
        eligibility_state=state,
        features={"tone": 1.0},
        discount=0.9,
        trace_decay=0.8,
    )
    assert out == state


def test_v3_18_10_accumulating_trace_init_and_carry_over_lifecycle():
    op = AccumulatingEligibilityTraceOperator()
    assert isinstance(op, EligibilityOperator)

    # init path: None state initializes lazily
    s1 = op.apply(
        eligibility_state=None,
        features={"tone": 1.0},
        discount=0.9,
        trace_decay=0.8,
    )
    assert s1 == {"tone": pytest.approx(1.0, abs=1e-12)}

    # carry-over path: previous state reused and decayed
    s2 = op.apply(
        eligibility_state=s1,
        features={"tone": 1.0},
        discount=0.9,
        trace_decay=0.8,
    )
    assert s2 == {"tone": pytest.approx(1.72, abs=1e-12)}


def test_v3_18_10_replacing_trace_replaces_active_feature_after_decay():
    op = ReplacingEligibilityTraceOperator()
    s1 = op.apply(
        eligibility_state={"tone": 0.6, "noise": 0.5},
        features={"tone": 1.0, "noise": 0.0},
        discount=0.9,
        trace_decay=0.8,
    )
    assert s1["tone"] == pytest.approx(1.0, abs=1e-12)
    assert s1["noise"] == pytest.approx(0.36, abs=1e-12)


def test_v3_18_10_eligibility_state_reset_lifecycle():
    state = {"tone": 1.72, "noise": 0.3}
    reset = reset_eligibility_state(state)
    assert reset == {}


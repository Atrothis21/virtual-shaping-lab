from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.learning.operators import (
    ErrorOperator,
    RescorlaWagnerErrorOperator,
    TD0ErrorOperator,
)


def test_v3_18_5_rescorla_wagner_error_operator_contract():
    op = RescorlaWagnerErrorOperator()
    assert isinstance(op, ErrorOperator)
    assert op(reward=1.0, prediction=0.25) == pytest.approx(0.75, abs=1e-12)
    assert op(reward=0.0, prediction=0.6, next_prediction=9.0, done=True) == pytest.approx(
        -0.6,
        abs=1e-12,
    )


def test_v3_18_5_td0_error_operator_bootstrap_and_terminal_paths():
    op = TD0ErrorOperator(gamma=0.9)
    assert isinstance(op, ErrorOperator)
    assert op(
        reward=1.0,
        prediction=0.4,
        next_prediction=0.8,
        done=False,
    ) == pytest.approx(1.32, abs=1e-12)
    assert op(
        reward=1.0,
        prediction=0.4,
        next_prediction=0.8,
        done=True,
    ) == pytest.approx(0.6, abs=1e-12)


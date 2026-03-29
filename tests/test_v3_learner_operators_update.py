from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.learning.operators import (
    RescorlaWagnerUpdateOperator,
    TD0UpdateOperator,
    UpdateOperator,
)


def test_v3_18_5_rescorla_wagner_update_operator_mutates_weights_in_state():
    op = RescorlaWagnerUpdateOperator()
    assert isinstance(op, UpdateOperator)

    state = {"weights": {"tone": 0.2}}
    out = op(
        state=state,
        features={"tone": 1.0, "noise": 0.5},
        error=0.4,
        step_size=0.1,
    )

    assert out is state
    assert state["weights"]["tone"] == pytest.approx(0.24, abs=1e-12)
    assert state["weights"]["noise"] == pytest.approx(0.02, abs=1e-12)


def test_v3_18_5_td0_update_operator_owns_mutation_boundary():
    op = TD0UpdateOperator()
    assert isinstance(op, UpdateOperator)

    state = {"weights": {"tone": 0.3}}
    features = {"tone": 2.0}
    snapshot = dict(features)

    out = op(
        state=state,
        features=features,
        error=-0.5,
        step_size=0.2,
    )

    assert out is state
    assert features == snapshot
    assert state["weights"]["tone"] == pytest.approx(0.1, abs=1e-12)


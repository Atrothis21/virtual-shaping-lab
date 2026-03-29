from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.learning.operators import (
    LinearActionValuePredictionOperator,
    LinearStateValuePredictionOperator,
    PredictionOutput,
    PredictionOperator,
    TabularStateValuePredictionOperator,
)


def test_v3_18_5_prediction_output_contract_state_value():
    out = PredictionOutput.from_state_value(0.75, metadata={"source": "test"})
    assert out.state_value == 0.75
    assert out.action_values == {}
    assert out.metadata["source"] == "test"


def test_v3_18_5_prediction_output_contract_action_values():
    out = PredictionOutput.from_action_values({"left": 0.1, "right": 0.6})
    assert out.state_value == 0.6
    assert out.action_values["left"] == 0.1
    assert out.action_values["right"] == 0.6


def test_v3_18_5_linear_state_value_prediction_operator():
    op = LinearStateValuePredictionOperator()
    state = {"weights": {"tone": 0.5, "noise": 0.2}}
    out = op(features={"tone": 1.0, "noise": 2.0}, state=state)
    assert isinstance(op, PredictionOperator)
    assert isinstance(out, PredictionOutput)
    assert out.state_value == 0.9
    assert out.action_values == {}


def test_v3_18_5_tabular_state_value_prediction_operator_default_and_hit_paths():
    op = TabularStateValuePredictionOperator()
    features = {"tone": 1.0, "noise": 0.0}

    default_out = op(features=features, state={"value_table": {}})
    assert default_out.state_value == 0.0

    state = {
        "state_id": "S0",
        "value_table": {"S0": 1.25},
    }
    hit_out = op(features=features, state=state)
    assert hit_out.state_value == 1.25
    assert hit_out.metadata["state_id"] == "S0"


def test_v3_18_5_linear_action_value_prediction_operator_contract():
    op = LinearActionValuePredictionOperator(actions=["left", "right"])
    state = {
        "weights_by_action": {
            "left": {"tone": 0.4, "noise": 0.1},
            "right": {"tone": 0.2, "noise": 0.3},
        }
    }
    out = op(features={"tone": 1.0, "noise": 2.0}, state=state)
    assert isinstance(out, PredictionOutput)
    assert set(out.action_values.keys()) == {"left", "right"}
    assert out.action_values["left"] == pytest.approx(0.6, abs=1e-12)
    assert out.action_values["right"] == pytest.approx(0.8, abs=1e-12)
    assert out.state_value == pytest.approx(0.8, abs=1e-12)

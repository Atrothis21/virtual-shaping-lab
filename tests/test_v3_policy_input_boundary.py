from __future__ import annotations

from dataclasses import dataclass

import pytest

from virtual_shaping_lab.vsl.agent.policy import PolicyInput, build_policy_input
from virtual_shaping_lab.vsl.contracts import TaskInput


@dataclass
class _ObservationOutput:
    features: list[float]
    feature_names: list[str]
    representation: object | None = None
    context_state: object | None = None
    generalized_state: object | None = None


def test_v3_20_5_build_policy_input_derives_from_typed_boundary():
    task_input = TaskInput(
        stimuli={"tone": 1.0},
        context="A",
        t=3,
        phase="acquisition",
        available_actions=("left", "right"),
    )
    observation_output = _ObservationOutput(
        features=[1.0, 0.2],
        feature_names=["tone", "noise"],
        representation={"kind": "elemental"},
        context_state="A",
        generalized_state={"kind": "identity"},
    )
    prediction = {"state_value": 0.42, "action_values": {"left": 0.6, "right": 0.3}}

    out = build_policy_input(
        task_input=task_input,
        observation_output=observation_output,
        prediction=prediction,
    )
    assert isinstance(out, PolicyInput)
    assert out.observation_features == [1.0, 0.2]
    assert out.observation_feature_names == ["tone", "noise"]
    assert out.prediction == 0.42
    assert out.action_values == {"left": 0.6, "right": 0.3}
    assert out.available_actions == ("left", "right")
    assert out.metadata["source"] == "task_observation_prediction"
    assert out.metadata["task_time"] == 3
    assert out.metadata["task_phase"] == "acquisition"


def test_v3_20_5_build_policy_input_requires_typed_task_input():
    with pytest.raises(TypeError, match="TaskInput"):
        build_policy_input(task_input={"stimuli": {}}, observation_output=_ObservationOutput([], []))  # type: ignore[arg-type]


def test_v3_20_5_policy_input_rejects_disallowed_raw_boundary_metadata_keys():
    with pytest.raises(ValueError, match="disallowed raw/boundary keys"):
        PolicyInput(metadata={"raw_stimulus": {"tone": 1.0}})


def test_v3_20_5_policy_input_roundtrip_mapping():
    original = PolicyInput(
        observation_features=[1.0],
        observation_feature_names=["tone"],
        action_values={"left": 0.4},
        available_actions=("left",),
        metadata={"source": "roundtrip"},
    )
    rebuilt = PolicyInput.from_mapping(original.to_mapping())
    assert rebuilt == original


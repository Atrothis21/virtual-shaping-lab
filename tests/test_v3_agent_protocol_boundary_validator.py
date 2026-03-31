from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.contracts import Action, Outcome, TaskInput, validate_interaction_boundary


def test_v3_interaction_boundary_validator_accepts_typed_inputs():
    validate_interaction_boundary(
        task_input=TaskInput(stimuli={"tone": 1.0}),
        action=Action(value="left"),
        outcome=Outcome(reward=1.0),
    )


def test_v3_interaction_boundary_validator_rejects_untyped_task_input():
    with pytest.raises(TypeError, match="TaskInput"):
        validate_interaction_boundary(
            task_input={"stimuli": {"tone": 1.0}},
            action=Action(value="left"),
            outcome=Outcome(reward=1.0),
        )


def test_v3_interaction_boundary_validator_rejects_untyped_action():
    with pytest.raises(TypeError, match="Action"):
        validate_interaction_boundary(
            task_input=TaskInput(stimuli={"tone": 1.0}),
            action={"value": "left"},
            outcome=Outcome(reward=1.0),
        )


def test_v3_interaction_boundary_validator_rejects_untyped_outcome():
    with pytest.raises(TypeError, match="Outcome"):
        validate_interaction_boundary(
            task_input=TaskInput(stimuli={"tone": 1.0}),
            action=Action(value="left"),
            outcome={"reward": 1.0},
        )


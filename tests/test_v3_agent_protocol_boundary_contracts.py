from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.contracts import Action, Outcome, TaskInput, TrialRecord


def test_v3_interaction_contracts_construct_typed_boundary_objects():
    task_input = TaskInput(stimuli={"tone": 1.0}, context="A", t=1, available_actions=("left", "right"))
    action = Action(value="left", metadata={"confidence": 0.8})
    outcome = Outcome(reward=1.0, next_stimuli={"tone": 0.0}, terminated=False)
    record = TrialRecord(trial_index=0, task_input=task_input, action=action, outcome=outcome)

    assert task_input.stimuli["tone"] == 1.0
    assert action.value == "left"
    assert outcome.reward == 1.0
    assert record.trial_index == 0


def test_v3_interaction_outcome_rejects_internal_learning_keys():
    with pytest.raises(ValueError, match="disallowed"):
        Outcome(reward=1.0, metadata={"prediction_error": 0.1})


def test_v3_interaction_trial_record_requires_non_negative_index():
    with pytest.raises(ValueError, match="non-negative"):
        TrialRecord(
            trial_index=-1,
            task_input=TaskInput(stimuli={}),
            action=Action(value=None),
            outcome=Outcome(reward=0.0),
        )


import pytest

from domain.types import META_CUE_LABELS, META_EVENT_TYPE, Observation, Transition
from experiment.domain.types import (
    LearningGateSpec,
    OperantContingencySpec,
    PavlovianContingencySpec,
    PhaseSpec,
    TrialTimeSpec,
    TrialTypeSpec,
)


def test_observation_time_fields_round_trip():
    obs = Observation(
        stimuli=["tone"],
        context="A",
        t_s=1.0,
        dt_s=0.1,
        trial_step=3,
        trial_id="trial-1",
    )
    assert obs.t_s == 1.0
    assert obs.dt_s == 0.1
    assert obs.trial_step == 3
    assert obs.trial_id == "trial-1"


def test_transition_validates_non_negative_time_step(dummy_agent):
    state = dummy_agent.observe(Observation(stimuli=["tone"], context="A"))
    with pytest.raises(ValueError):
        Transition(s=state, r=1.0, dt_s=-0.1)
    with pytest.raises(ValueError):
        Transition(s=state, r=1.0, trial_step=-1)


def test_metadata_key_constants_are_stable():
    assert META_CUE_LABELS == "cue_labels"
    assert META_EVENT_TYPE == "event_type"


def test_trial_type_spec_and_contingency_specs_validate_contracts():
    trial_type = TrialTypeSpec(label="AX", stimuli=["tone", "light"], weight=1.0)
    assert trial_type.label == "AX"

    pav = PavlovianContingencySpec(us_magnitude=1.0, us_event_type="reward")
    assert pav.us_event_type == "reward"

    op = OperantContingencySpec(
        task_key="operant",
        schedule_runtime={"type": "fixed_ratio", "value": 1},
        action_labels=["left", "right"],
    )
    assert op.task_key == "operant"

    with pytest.raises(ValueError):
        TrialTypeSpec(label="", stimuli=["tone"])
    with pytest.raises(ValueError):
        TrialTypeSpec(label="A", stimuli=[], weight=1.0)
    with pytest.raises(ValueError):
        OperantContingencySpec(task_key="", action_labels=["left"])


def test_phase_spec_requires_valid_components():
    spec = PhaseSpec(
        key="pavlovian",
        name="Acquisition",
        context_id="A",
        n_trials=5,
        time=TrialTimeSpec(duration_s=1.0, dt_s=0.5),
        trial_types=[TrialTypeSpec(label="A", stimuli=["tone"])],
        contingency=PavlovianContingencySpec(us_magnitude=1.0),
        learning=LearningGateSpec(enabled=True),
    )
    assert spec.key == "pavlovian"
    assert spec.n_trials == 5

    with pytest.raises(ValueError):
        PhaseSpec(
            key="",
            name="bad",
            context_id="A",
            n_trials=1,
            time=TrialTimeSpec(duration_s=1.0, dt_s=0.5),
            trial_types=[TrialTypeSpec(label="A", stimuli=["tone"])],
            contingency=PavlovianContingencySpec(),
        )
    with pytest.raises(ValueError):
        PhaseSpec(
            key="pavlovian",
            name="bad",
            context_id="A",
            n_trials=0,
            time=TrialTimeSpec(duration_s=1.0, dt_s=0.5),
            trial_types=[TrialTypeSpec(label="A", stimuli=["tone"])],
            contingency=PavlovianContingencySpec(),
        )

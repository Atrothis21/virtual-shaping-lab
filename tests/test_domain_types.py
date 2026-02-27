import pytest

from domain.types import META_CUE_LABELS, META_EVENT_TYPE, Observation, Transition


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

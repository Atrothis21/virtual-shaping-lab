import pytest

from experiment.domain.types import EventSpec, TrialTimeSpec, WindowSpec


def test_trial_time_spec_validates_positive_duration_and_dt():
    with pytest.raises(ValueError):
        TrialTimeSpec(duration_s=0.0, dt_s=0.1)
    with pytest.raises(ValueError):
        TrialTimeSpec(duration_s=1.0, dt_s=0.0)


def test_trial_time_spec_validates_grid_alignment_by_default():
    with pytest.raises(ValueError):
        TrialTimeSpec(duration_s=1.0, dt_s=0.3, allow_partial_last_step=False)

    spec = TrialTimeSpec(duration_s=1.0, dt_s=0.3, allow_partial_last_step=True)
    assert spec.allow_partial_last_step is True


def test_trial_time_spec_validates_iti_and_event_window_bounds():
    with pytest.raises(ValueError):
        TrialTimeSpec(duration_s=1.0, dt_s=0.1, iti_s=-0.1)

    with pytest.raises(ValueError):
        EventSpec(event_type="cs", start_s=-0.1, end_s=0.2)
    with pytest.raises(ValueError):
        EventSpec(event_type="cs", start_s=0.4, end_s=0.3)

    with pytest.raises(ValueError):
        WindowSpec(start_s=-0.1, end_s=0.2)
    with pytest.raises(ValueError):
        WindowSpec(start_s=0.4, end_s=0.3)

    with pytest.raises(ValueError):
        TrialTimeSpec(
            duration_s=1.0,
            dt_s=0.1,
            events=[EventSpec(event_type="us", start_s=0.9, end_s=1.1)],
        )
    with pytest.raises(ValueError):
        TrialTimeSpec(
            duration_s=1.0,
            dt_s=0.1,
            response_windows=[WindowSpec(start_s=0.8, end_s=1.2)],
        )


def test_trial_time_spec_accepts_valid_schedule():
    spec = TrialTimeSpec(
        duration_s=1.0,
        dt_s=0.1,
        iti_s=0.5,
        events=[EventSpec(event_type="cs", start_s=0.0, end_s=0.6)],
        response_windows=[WindowSpec(start_s=0.2, end_s=0.8, label="operant")],
    )
    assert spec.duration_s == 1.0
    assert spec.dt_s == 0.1
    assert spec.iti_s == 0.5
    assert len(spec.events) == 1
    assert len(spec.response_windows) == 1


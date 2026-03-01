import pytest

from analysis.views import aggregate_ticks_to_trials, tick_view, trial_view


def test_trial_and_tick_views_split_mixed_records():
    records = [
        {"trial": 0, "reward": 1.0},
        {"trial": 1, "tick": 0, "reward": 0.1},
        {"trial": 1, "tick": 1, "reward": 0.2},
    ]
    trials = trial_view(records)
    ticks = tick_view(records)

    assert len(trials) == 1
    assert trials[0]["trial"] == 0
    assert len(ticks) == 2
    assert ticks[0]["tick"] == 0


def test_aggregate_ticks_to_trials_summarizes_reward_action_and_metadata():
    ticks = [
        {"phase": "acq", "trial": 2, "tick": 0, "reward": 0.1, "action": None, "context": "A", "t_s": 0.0},
        {"phase": "acq", "trial": 2, "tick": 1, "reward": 0.2, "action": "press", "context": "A", "t_s": 0.5},
        {"phase": "acq", "trial": 3, "tick": 0, "reward": 1.0, "action": "hold", "context": "B", "t_s": 0.0},
    ]

    out = aggregate_ticks_to_trials(ticks)
    assert len(out) == 2
    assert out[0]["trial"] == 2
    assert out[0]["reward"] == pytest.approx(0.3)
    assert out[0]["action"] == "press"
    assert out[0]["tick_count"] == 2
    assert out[1]["trial"] == 3
    assert out[1]["context"] == "B"

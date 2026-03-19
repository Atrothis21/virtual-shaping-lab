from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment, RolloutHarness, TrialState
from virtual_shaping_lab.vsl.program import compile_environment_program


def _program():
    return compile_environment_program(
        {
            "phases": [
                {
                    "name": "Acq",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 2, "outcome": 1.0},
                }
            ]
        }
    )


def test_trial_state_roundtrip_and_required_coordinates():
    state = TrialState.from_components(
        s={"step": 0},
        x={"cs_plus": ["tone"]},
        z={"context": "A"},
        w={},
        a=[],
        u=None,
        y=1.0,
        persistent={"meta": 1},
        prediction=0.7,
        error=0.3,
    )
    blob = state.to_dict()
    rebuilt = TrialState.from_dict(blob)
    assert rebuilt.to_dict() == blob
    assert rebuilt.persistent_metadata() == {"meta": 1}
    assert rebuilt.derived_outputs() == {"prediction": 0.7, "error": 0.3}

    with pytest.raises(ValueError, match="missing required coordinates"):
        TrialState.from_dict({"s": 1, "x": 2, "z": 3, "w": 4, "a": 5, "u": 6, "y": 7})


def test_trial_state_rejects_derived_outputs_in_persistent_metadata():
    with pytest.raises(ValueError, match="must not contain derived outputs"):
        TrialState(
            s={"step": 0},
            x={"cs_plus": ["tone"]},
            z={"context": "A"},
            w={},
            a=[],
            u=None,
            y=1.0,
            m={"persistent": {"prediction": 0.9}, "derived": {}},
        )

    with pytest.raises(ValueError, match="m.derived may only contain derived outputs"):
        TrialState(
            s={"step": 0},
            x={"cs_plus": ["tone"]},
            z={"context": "A"},
            w={},
            a=[],
            u=None,
            y=1.0,
            m={"persistent": {}, "derived": {"foo": 1}},
        )


def test_rollout_emits_trial_state_coordinates():
    env = CompiledProgramTestEnvironment(_program())
    records = RolloutHarness().run(env, seed=5)
    assert records
    for rec in records:
        ts = rec.get("trial_state")
        assert isinstance(ts, dict)
        assert set(("s", "x", "z", "w", "a", "u", "y", "m")).issubset(ts.keys())
        assert set(("persistent", "derived")).issubset(ts["m"].keys())
        assert set(("prediction", "error")).issubset(ts["m"]["derived"].keys())

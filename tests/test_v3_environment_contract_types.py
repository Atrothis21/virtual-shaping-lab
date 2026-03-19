from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.environment import (
    CompiledProgramTestEnvironment,
    EnvironmentReset,
    EnvironmentStep,
    EnvironmentTermination,
    IEnvironment,
    TrialState,
)
from virtual_shaping_lab.vsl.program import compile_environment_program


def _compiled_program():
    return compile_environment_program(
        {
            "phases": [
                {
                    "name": "Acq",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 1, "outcome": 1.0},
                }
            ]
        }
    )


def test_environment_contract_runtime_checkable():
    env = CompiledProgramTestEnvironment(_compiled_program())
    assert isinstance(env, IEnvironment)


def test_environment_typed_objects_roundtrip_shape():
    reset = EnvironmentReset(seed=7, done=False, metadata={"source": "test"})
    term = EnvironmentTermination(done=True, reason="terminal", metadata={"horizon": True})
    trial_state = TrialState.from_components(
        s={"step": 0},
        x={"cs_plus": ["tone"]},
        z={"context": "A"},
        w={},
        a=[],
        u=None,
        y=1.0,
        persistent={"phase": "acq"},
        prediction=0.5,
        error=0.5,
    )
    step = EnvironmentStep(
        step_index=0,
        segment_key="acquisition_0",
        protocol="acquisition",
        trial_type="acquisition_trial",
        trial_index=0,
        action=None,
        stimulus={"cs_plus": ["tone"]},
        reward=1.0,
        done=True,
        trial_state=trial_state,
        termination=term,
        metadata={"phase_index": 0},
    )
    assert reset.to_dict()["seed"] == 7
    assert step.to_dict()["termination"]["reason"] == "terminal"
    assert set(("s", "x", "z", "w", "a", "u", "y", "m")).issubset(step.to_dict()["trial_state"].keys())
    assert step.to_dict()["trial_state"]["m"]["derived"] == {"prediction": 0.5, "error": 0.5}


def test_environment_step_validation_guards():
    with pytest.raises(ValueError, match="segment_key"):
        EnvironmentStep(
            step_index=0,
            segment_key="",
            protocol="acquisition",
            trial_type="acquisition_trial",
            trial_index=0,
            action=None,
        )

    with pytest.raises(ValueError, match="termination"):
        EnvironmentStep(
            step_index=0,
            segment_key="acquisition_0",
            protocol="acquisition",
            trial_type="acquisition_trial",
            trial_index=0,
            action=None,
            termination="bad",  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="trial_state"):
        EnvironmentStep(
            step_index=0,
            segment_key="acquisition_0",
            protocol="acquisition",
            trial_type="acquisition_trial",
            trial_index=0,
            action=None,
            trial_state="bad",  # type: ignore[arg-type]
        )

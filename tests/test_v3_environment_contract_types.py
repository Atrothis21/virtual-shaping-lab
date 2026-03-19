from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.environment import (
    CompiledProgramTestEnvironment,
    EnvironmentReset,
    EnvironmentStep,
    EnvironmentTermination,
    IEnvironment,
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
        termination=term,
        metadata={"phase_index": 0},
    )
    assert reset.to_dict()["seed"] == 7
    assert step.to_dict()["termination"]["reason"] == "terminal"


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

from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.program import EnvironmentProgram, compile_core_environment_program
from virtual_shaping_lab.vsl.spec import ProgramSpec


def test_compile_core_environment_program_acquisition_family():
    program = ProgramSpec(
        phases=[
            {
                "name": "Phase 1",
                "protocol": "acquisition",
                "stimuli": {"cs_plus": ["tone"]},
                "params": {"alpha": 0.2},
                "trials": 12,
            }
        ]
    )

    compiled = compile_core_environment_program(program)
    assert isinstance(compiled, EnvironmentProgram)
    assert len(compiled.segments) == 1
    segment = compiled.segments[0]
    assert segment.protocol == "acquisition"
    assert segment.metadata["family"] == "acquisition"
    assert segment.trials[0].n_trials == 12
    assert segment.trials[0].stimuli == {"cs_plus": ["tone"]}


@pytest.mark.parametrize(
    "protocol",
    ["nonreinforcement", "nonreinforcement_template", "extinction"],
)
def test_compile_core_environment_program_extinction_family(protocol: str):
    program = {
        "phases": [
            {
                "name": "Phase X",
                "protocol": protocol,
                "stimuli": {"cs_plus": ["tone"]},
                "params": {"gamma": 0.0, "n_trials": 5},
            }
        ]
    }

    compiled = compile_core_environment_program(program)
    segment = compiled.segments[0]
    assert segment.protocol == protocol
    assert segment.metadata["family"] == "extinction"
    assert segment.trials[0].n_trials == 5
    assert segment.trials[0].metadata["family"] == "extinction"


def test_compile_core_environment_program_rejects_unsupported_protocol():
    program = {
        "phases": [
            {
                "name": "Phase 1",
                "protocol": "differential_acquisition",
                "stimuli": {"cs_plus": ["tone"], "cs_minus": ["noise"]},
                "params": {"n_trials": 10},
            }
        ]
    }
    with pytest.raises(ValueError, match="Unsupported protocol"):
        compile_core_environment_program(program)


def test_compile_core_environment_program_is_deterministic_for_identical_input():
    payload = {
        "phases": [
            {
                "name": "Phase 1",
                "protocol": "acquisition",
                "stimuli": {"cs_plus": ["tone"]},
                "params": {"alpha": 0.2, "n_trials": 10},
            },
            {
                "name": "Phase 2",
                "protocol": "extinction",
                "stimuli": {"cs_plus": ["tone"]},
                "params": {"gamma": 0.0},
                "trials": 8,
            },
        ]
    }

    first = compile_core_environment_program(payload).to_dict()
    second = compile_core_environment_program(payload).to_dict()
    assert first == second

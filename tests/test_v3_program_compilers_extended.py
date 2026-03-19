from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.program import compile_extended_environment_program
from virtual_shaping_lab.vsl.spec import ProgramSpec


@pytest.mark.parametrize(
    ("protocol", "family", "stimuli"),
    [
        ("differential_acquisition", "differential", {"cs_plus": ["tone"], "cs_minus": ["noise"]}),
        ("probe", "probe", {"cs_plus": ["tone"]}),
        ("context_shift", "context_shift", {}),
    ],
)
def test_compile_extended_environment_program_supported_families(protocol: str, family: str, stimuli: dict[str, list[str]]):
    payload = {
        "phases": [
            {
                "name": "Extended Phase",
                "protocol": protocol,
                "stimuli": stimuli,
                "params": {"n_trials": 7, "context": "B"},
            }
        ]
    }
    compiled = compile_extended_environment_program(payload)
    segment = compiled.segments[0]
    trial = segment.trials[0]
    assert segment.protocol == protocol
    assert segment.metadata["family"] == family
    assert trial.metadata["family"] == family
    assert trial.n_trials == 7


def test_compile_extended_environment_program_accepts_template_aliases():
    payload = ProgramSpec(
        phases=[
            {"name": "Diff Template", "protocol": "differential_acquisition_template", "stimuli": {}, "trials": 3},
            {"name": "Probe Template", "protocol": "probe_template", "stimuli": {}, "trials": 2},
        ]
    )
    compiled = compile_extended_environment_program(payload)
    assert [segment.protocol for segment in compiled.segments] == [
        "differential_acquisition_template",
        "probe_template",
    ]
    assert compiled.metadata["compiler"] == "v3.2.0-extended"


def test_compile_extended_environment_program_rejects_core_protocols():
    payload = {
        "phases": [
            {
                "name": "Core Phase",
                "protocol": "acquisition",
                "stimuli": {"cs_plus": ["tone"]},
                "params": {"n_trials": 4},
            }
        ]
    }
    with pytest.raises(ValueError, match="Unsupported protocol"):
        compile_extended_environment_program(payload)


def test_compile_extended_environment_program_is_deterministic_for_identical_input():
    payload = {
        "phases": [
            {
                "name": "D1",
                "protocol": "differential_acquisition",
                "stimuli": {"cs_plus": ["tone"], "cs_minus": ["noise"]},
                "params": {"n_trials": 11},
            },
            {
                "name": "P1",
                "protocol": "probe",
                "stimuli": {"cs_plus": ["tone"]},
                "trials": 5,
            },
            {
                "name": "Shift",
                "protocol": "context_shift",
                "stimuli": {},
                "params": {"context": "B"},
                "trials": 1,
            },
        ]
    }
    first = compile_extended_environment_program(payload).to_dict()
    second = compile_extended_environment_program(payload).to_dict()
    assert first == second

from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.program import EnvironmentProgram, EnvironmentSegment, EventSpec, TrialSpec


def _sample_program() -> EnvironmentProgram:
    event = EventSpec(event_type="cs_plus", start_s=0.0, end_s=1.0, magnitude=1.0, metadata={"id": "e1"})
    trial = TrialSpec(
        trial_type="acquisition_trial",
        n_trials=10,
        stimuli={"cs_plus": ["tone"]},
        params={"alpha": 0.2},
        events=[event],
        metadata={"phase_index": 0},
    )
    segment = EnvironmentSegment(
        key="acquisition",
        name="Phase 1",
        protocol="acquisition",
        trials=[trial],
        metadata={"source": "template"},
    )
    return EnvironmentProgram(segments=[segment], metadata={"spec_version": 1})


def test_v3_program_types_roundtrip():
    program = _sample_program()
    blob = program.to_dict()
    rebuilt = EnvironmentProgram.from_dict(blob)
    assert rebuilt.to_dict() == blob


def test_v3_program_types_stable_hash_repeats():
    program = _sample_program()
    hashes = [program.stable_hash() for _ in range(20)]
    assert len(set(hashes)) == 1


def test_v3_program_types_validation():
    with pytest.raises(ValueError, match="EventSpec.event_type"):
        EventSpec(event_type="", start_s=0.0, end_s=1.0)

    with pytest.raises(ValueError, match="TrialSpec.n_trials"):
        TrialSpec(trial_type="x", n_trials=0)

    with pytest.raises(ValueError, match="EnvironmentSegment.trials must be non-empty"):
        EnvironmentSegment(key="k", name="n", protocol="p", trials=[])

    with pytest.raises(ValueError, match="EnvironmentProgram.segments must be non-empty"):
        EnvironmentProgram(segments=[])

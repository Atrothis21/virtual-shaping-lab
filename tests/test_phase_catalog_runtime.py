from __future__ import annotations

import pytest

from experiment.phases.catalog_runtime import (
    PHASE_BUILDERS,
    available_phases,
    build_phase,
    validate_phase_key,
)


class _DummyAgent:
    pass


def test_available_phases_is_sorted_and_nonempty():
    phases = available_phases()
    assert phases
    assert phases == sorted(phases)
    assert set(phases) == set(PHASE_BUILDERS.keys())


def test_validate_phase_key_rejects_unknown():
    with pytest.raises(KeyError):
        validate_phase_key("not_a_real_phase")


def test_build_phase_constructs_template_backed_acquisition():
    phase = build_phase(
        "acquisition",
        agent=_DummyAgent(),
        n_trials=1,
        stimuli=["CS"],
        context="A",
    )
    assert phase.spec.key == "pavlovian_phase_template"
    assert phase.spec.name == "acquisition"


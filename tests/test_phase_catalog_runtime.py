from __future__ import annotations

import pytest

from experiment.phases.catalog import PHASE_CATALOG
from experiment.phases.context_shift import ContextShiftPhase
from experiment.phases.criterion_shift import CriterionShiftPhase
from experiment.phases.catalog_runtime import (
    PHASE_METADATA,
    PHASE_BUILDERS,
    available_phases,
    build_phase,
    get_phase_metadata,
    validate_phase_key,
)
from virtual_shaping_lab.domain.catalog_metadata import UICatalogMetadata, validate_ui_metadata_map


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


def test_runtime_catalog_contains_phase_catalog_keys():
    runtime_keys = set(available_phases())
    phase_catalog_keys = set(PHASE_CATALOG.keys())
    assert phase_catalog_keys.issubset(runtime_keys)


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


def test_control_flow_phase_keys_remain_class_based():
    context_shift = build_phase("context_shift", agent=_DummyAgent())
    criterion_shift = build_phase(
        "criterion_shift",
        agent=_DummyAgent(),
        n_trials=1,
        stimuli={"cs_plus": ["A"], "cs_minus": ["B"]},
        outcome=1.0,
    )
    assert isinstance(context_shift, ContextShiftPhase)
    assert isinstance(criterion_shift, CriterionShiftPhase)


def test_phase_catalog_has_ui_metadata_for_all_keys():
    assert set(PHASE_METADATA.keys()) == set(PHASE_BUILDERS.keys())
    meta = get_phase_metadata("acquisition")
    assert meta.label
    assert meta.description
    assert isinstance(meta.params_schema, dict)
    assert isinstance(meta.defaults, dict)
    assert meta.defaults.get("outcome") == 1.0
    assert "pavlovian_only" in meta.constraints
    assert meta.examples


def test_phase_catalog_operant_metadata_declares_operant_constraints():
    operant_meta = get_phase_metadata("operant_phase_template")
    assert "operant_only" in operant_meta.constraints
    assert operant_meta.defaults.get("schedule_builder_strategy") == "operant"
    assert "available_actions" in operant_meta.params_schema


def test_phase_catalog_metadata_rejects_unknown_constraint_symbol():
    bad_map = {
        "acquisition": UICatalogMetadata(
            label="Acquisition",
            description="bad constraints test",
            constraints=("free_text_constraint",),
        )
    }
    with pytest.raises(ValueError, match="unknown constraints"):
        validate_ui_metadata_map(
            keys={"acquisition"},
            metadata_map=bad_map,
            namespace="test.phase_catalog",
        )

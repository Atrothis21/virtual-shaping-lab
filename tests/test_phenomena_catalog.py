from __future__ import annotations

import pytest

from experiment.phenomena.catalog import (
    PHENOMENA_REGISTRY,
    PhenomenonSpec,
    available_phenomena,
    get_phenomenon,
    validate_phenomena_registry,
    validate_phenomenon_key,
)


def test_phenomena_catalog_is_sorted_and_nonempty():
    keys = available_phenomena()
    assert keys
    assert keys == sorted(keys)
    assert set(keys) == set(PHENOMENA_REGISTRY.keys())


def test_phenomena_catalog_validate_rejects_unknown():
    with pytest.raises(KeyError):
        validate_phenomenon_key("not_real")


def test_phenomena_catalog_entries_have_protocol_backing():
    spec = get_phenomenon("blocking")
    assert spec.protocol_key == "blocking"
    assert spec.expected_signatures
    assert spec.expected_signals
    assert spec.recommended_template_key == "verification_report"
    assert "trial_curve" in spec.recommended_figures
    assert "trial" in spec.default_run_modes


def test_phenomena_catalog_validation_rejects_unknown_protocol():
    bad = dict(PHENOMENA_REGISTRY)
    bad["bad_case"] = PhenomenonSpec(
        key="bad_case",
        name="Bad Case",
        description="invalid protocol test",
        protocol_key="not_a_protocol",
        expected_signatures=("x",),
    )
    with pytest.raises(ValueError, match="references unknown protocol"):
        validate_phenomena_registry(bad)


def test_phenomena_catalog_validation_rejects_invalid_default_run_modes():
    bad = dict(PHENOMENA_REGISTRY)
    bad["bad_modes"] = PhenomenonSpec(
        key="bad_modes",
        name="Bad Modes",
        description="invalid run mode test",
        protocol_key="blocking",
        expected_signatures=("x",),
        expected_signals=("x",),
        default_run_modes=("invalid",),
    )
    with pytest.raises(ValueError, match="default_run_modes"):
        validate_phenomena_registry(bad)

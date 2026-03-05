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

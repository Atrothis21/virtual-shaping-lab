from __future__ import annotations

import pytest

from protocols import catalog
from virtual_shaping_lab.domain.catalog_metadata import UICatalogMetadata, validate_ui_metadata_map


class _DummyProtocol:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_protocol_catalog_has_expected_entries():
    names = catalog.available_protocols()
    assert "extinction" in names
    assert "operant_conditioning" in names


def test_protocol_catalog_validate_rejects_unknown():
    with pytest.raises(KeyError):
        catalog.validate_protocol_name("missing_protocol")


def test_protocol_catalog_build_constructs_protocol(monkeypatch):
    monkeypatch.setattr(catalog, "PROTOCOL_BUILDERS", {"dummy": _DummyProtocol})
    proto = catalog.build_protocol(
        "dummy",
        agent="agent",
        stimuli={"cs_plus": ["tone"]},
        params={"n_trials": 5},
    )
    assert isinstance(proto, _DummyProtocol)
    assert proto.kwargs["agent"] == "agent"
    assert proto.kwargs["stimuli"] == {"cs_plus": ["tone"]}
    assert proto.kwargs["params"] == {"n_trials": 5}


def test_protocol_catalog_normalizes_protocol_keys():
    catalog.validate_protocol_name("Operant-Conditioning")


def test_protocol_catalog_has_ui_metadata_for_all_keys():
    assert set(catalog.PROTOCOL_METADATA.keys()) == set(catalog.PROTOCOL_BUILDERS.keys())
    meta = catalog.get_protocol_metadata("Operant-Conditioning")
    assert meta.label
    assert meta.description
    assert isinstance(meta.params_schema, dict)
    assert isinstance(meta.defaults, dict)
    assert "operant_only" in meta.constraints
    assert "schedule_type" in meta.params_schema
    assert meta.examples


def test_protocol_catalog_extinction_metadata_has_pavlovian_constraint():
    extinction_meta = catalog.get_protocol_metadata("extinction")
    assert "pavlovian_only" in extinction_meta.constraints


def test_protocol_catalog_metadata_rejects_unknown_constraint_symbol():
    bad_map = {
        "extinction": UICatalogMetadata(
            label="Extinction",
            description="bad constraints test",
            constraints=("unknown_free_text_constraint",),
        )
    }
    with pytest.raises(ValueError, match="unknown constraints"):
        validate_ui_metadata_map(
            keys={"extinction"},
            metadata_map=bad_map,
            namespace="test.protocol_catalog",
        )

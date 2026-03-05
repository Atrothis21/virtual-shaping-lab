from __future__ import annotations

from analysis.report.catalog import DEFAULT_TEMPLATE_BY_PROTOCOL, REPORT_TEMPLATE_METADATA
from experiment.phases.catalog_runtime import PHASE_BUILDERS, PHASE_METADATA
from protocols.catalog import PROTOCOL_BUILDERS, PROTOCOL_METADATA


def _assert_metadata_complete(metadata_map, keys: set[str], *, namespace: str) -> None:
    assert set(metadata_map.keys()) == keys, f"{namespace}: metadata keys must match catalog keys."
    for key, meta in metadata_map.items():
        assert meta.label.strip(), f"{namespace}:{key} missing label."
        assert meta.description.strip(), f"{namespace}:{key} missing description."
        assert isinstance(meta.params_schema, dict), f"{namespace}:{key} params_schema must be dict."
        assert isinstance(meta.defaults, dict), f"{namespace}:{key} defaults must be dict."
        assert isinstance(meta.constraints, tuple), f"{namespace}:{key} constraints must be tuple."
        assert isinstance(meta.examples, tuple), f"{namespace}:{key} examples must be tuple."
        assert len(meta.examples) > 0, f"{namespace}:{key} should include at least one example."


def test_phase_catalog_metadata_completeness_guard():
    _assert_metadata_complete(
        PHASE_METADATA,
        set(PHASE_BUILDERS.keys()),
        namespace="phase_catalog",
    )


def test_protocol_catalog_metadata_completeness_guard():
    _assert_metadata_complete(
        PROTOCOL_METADATA,
        set(PROTOCOL_BUILDERS.keys()),
        namespace="protocol_catalog",
    )


def test_report_catalog_metadata_completeness_guard():
    _assert_metadata_complete(
        REPORT_TEMPLATE_METADATA,
        set(DEFAULT_TEMPLATE_BY_PROTOCOL.keys()),
        namespace="report_catalog",
    )

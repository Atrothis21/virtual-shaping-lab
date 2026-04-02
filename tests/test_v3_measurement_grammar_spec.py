from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.measurement import MeasurementSpec, MeasurementSpecValidationError


def _sample_spec() -> MeasurementSpec:
    return MeasurementSpec(
        analysis_ops=["learning_curve_basic"],
        visualization_ops=["line_plot"],
        report_op="markdown_report",
        metadata={"family": "classical", "version": "3.22.0"},
    )


def test_v3_measurement_spec_roundtrip():
    spec = _sample_spec()
    rebuilt = MeasurementSpec.from_dict(spec.to_dict())
    assert rebuilt == spec


def test_v3_measurement_spec_hash_is_stable():
    spec = _sample_spec()
    hashes = [spec.stable_hash() for _ in range(20)]
    assert len(set(hashes)) == 1


@pytest.mark.parametrize("field_name", ["analysis_ops", "visualization_ops"])
def test_v3_measurement_spec_requires_string_lists(field_name: str):
    payload = _sample_spec().to_dict()
    payload[field_name] = [""]
    with pytest.raises(ValueError, match=field_name):
        MeasurementSpec.from_dict(payload)


@pytest.mark.parametrize("field_name", ["report_op", "metadata"])
def test_v3_measurement_spec_requires_non_empty_report_and_object_metadata(field_name: str):
    payload = _sample_spec().to_dict()
    payload[field_name] = "   " if field_name == "report_op" else "bad"
    with pytest.raises(ValueError, match=field_name):
        MeasurementSpec.from_dict(payload)


def test_v3_measurement_spec_fails_fast_for_illegal_tuple():
    with pytest.raises(MeasurementSpecValidationError, match="MEAS_E_REPORT_REQUIRES_VISUALIZATION"):
        MeasurementSpec(
            analysis_ops=["learning_curve_basic"],
            visualization_ops=[],
            report_op="pdf_report",
        )

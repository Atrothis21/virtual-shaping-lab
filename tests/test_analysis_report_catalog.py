import pytest
import warnings

from analysis.report.catalog import (
    DEFAULT_REPORT_BY_PROTOCOL,
    DEFAULT_TEMPLATE_BY_PROTOCOL,
    REPORT_TEMPLATE_METADATA,
    get_default_report_for_protocol,
    get_report_template_metadata,
    get_default_template_for_protocol,
)


def test_report_catalog_has_extinction_and_rapid_reacquisition_mapping():
    assert DEFAULT_REPORT_BY_PROTOCOL["acquisition"] == "verification_report"
    assert DEFAULT_REPORT_BY_PROTOCOL["extinction"] == "verification_report"
    assert DEFAULT_REPORT_BY_PROTOCOL["rapid_reacquisition"] == "verification_report"
    assert DEFAULT_REPORT_BY_PROTOCOL["blocking"] == "verification_report"
    assert DEFAULT_REPORT_BY_PROTOCOL["overshadowing"] == "verification_report"
    assert DEFAULT_REPORT_BY_PROTOCOL["conditioned_inhibition"] == "verification_report"
    assert DEFAULT_REPORT_BY_PROTOCOL["aba_renewal"] == "verification_report"
    assert DEFAULT_REPORT_BY_PROTOCOL["abc_renewal"] == "verification_report"
    assert DEFAULT_REPORT_BY_PROTOCOL["aab_renewal"] == "verification_report"
    assert DEFAULT_REPORT_BY_PROTOCOL["operant_conditioning"] == "verification_report"


def test_report_catalog_falls_back_to_verification_report():
    assert get_default_report_for_protocol("missing_protocol") == "verification_report"


def test_report_catalog_returns_compositional_template():
    template = get_default_template_for_protocol("extinction")
    assert template.report_name == "verification_report"
    assert template.template_version == 1
    assert template.metric_names == ("mean_reward",)
    assert template.figure_names == ("trial_curve", "tick_response_curve", "probe_bar")


def test_report_template_fallback_is_stable():
    with pytest.warns(UserWarning, match="Available mappings:"):
        template = get_default_template_for_protocol("missing_protocol")
    assert template.report_name == "verification_report"
    assert template.template_version == 1
    assert "trial_curve" in template.figure_names


def test_report_catalog_normalizes_protocol_keys():
    assert get_default_report_for_protocol("Operant-Conditioning") == "verification_report"
    template = get_default_template_for_protocol("OPERANT-CONDITIONING")
    assert template.report_name == "verification_report"


def test_report_catalog_has_explicit_acquisition_template_mapping_without_warning():
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        template = get_default_template_for_protocol("acquisition")
    assert template.report_name == "verification_report"
    assert len(captured) == 0


def test_report_catalog_has_ui_metadata_for_all_template_mappings():
    assert set(REPORT_TEMPLATE_METADATA.keys()) == set(DEFAULT_TEMPLATE_BY_PROTOCOL.keys())
    meta = get_report_template_metadata("EXTINCTION")
    assert meta.label
    assert meta.description
    assert isinstance(meta.params_schema, dict)
    assert isinstance(meta.defaults, dict)

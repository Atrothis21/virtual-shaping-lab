from analysis.report.catalog import (
    DEFAULT_REPORT_BY_PROTOCOL,
    get_default_report_for_protocol,
    get_default_template_for_protocol,
)


def test_report_catalog_has_extinction_and_rapid_reacquisition_mapping():
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
    assert template.metric_names == ("mean_reward",)
    assert template.figure_names == ("trial_curve", "tick_response_curve", "probe_bar")


def test_report_template_fallback_is_stable():
    template = get_default_template_for_protocol("missing_protocol")
    assert template.report_name == "verification_report"
    assert "trial_curve" in template.figure_names

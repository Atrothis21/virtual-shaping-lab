import pytest

from analysis.registry import (
    FIGURES,
    METRICS,
    REPORTS,
    build_figure,
    build_metric,
    build_report,
)


def test_analysis_registry_has_verification_components():
    assert "mean_reward" in METRICS
    assert "trial_curve" in FIGURES
    assert "tick_response_curve" in FIGURES
    assert "probe_bar" in FIGURES
    assert "verification_report" in REPORTS


def test_analysis_registry_builders():
    metric = build_metric("mean_reward")
    figure = build_figure("trial_curve")
    report = build_report("verification_report")

    assert metric.name == "mean_reward"
    assert figure.name == "trial_curve"
    assert report.name == "verification_report"


def test_analysis_registry_rejects_unknown_names():
    with pytest.raises(KeyError):
        build_metric("missing_metric")
    with pytest.raises(KeyError):
        build_figure("missing_figure")
    with pytest.raises(KeyError):
        build_report("missing_report")

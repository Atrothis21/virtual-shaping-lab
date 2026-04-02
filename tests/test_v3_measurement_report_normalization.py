from __future__ import annotations

from analysis.report import report as report_module


def test_v3_22_15_report_normalization_promotes_canonical_measurement_trace_fields():
    out = report_module._normalize_record_for_artifact(
        {
            "trial": 0,
            "metadata": {
                "measurement_traces": {
                    "metrics": {"mean_reward": 0.75},
                    "figures": [{"kind": "line_plot"}],
                    "summary": {"format": "markdown", "title": "Summary"},
                    "provenance": {"preset_name": "learning_curve_basic"},
                }
            },
        }
    )

    assert out["measurement_metrics"] == {"mean_reward": 0.75}
    assert out["measurement_figures"] == [{"kind": "line_plot"}]
    assert out["measurement_summary"] == {"format": "markdown", "title": "Summary"}
    assert out["measurement_provenance"] == {"preset_name": "learning_curve_basic"}


def test_v3_22_15_report_normalization_emits_deterministic_measurement_defaults():
    out = report_module._normalize_record_for_artifact(
        {
            "trial": 0,
            "metadata": {},
        }
    )

    assert out["measurement_metrics"] == {}
    assert out["measurement_figures"] == []
    assert out["measurement_summary"] == {}
    assert out["measurement_provenance"] == {}

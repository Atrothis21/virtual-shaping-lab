from __future__ import annotations

from analysis.report import report as report_module


def test_v3_22_15_canonical_measurement_traces_take_precedence_over_legacy_fields():
    out = report_module._normalize_record_for_artifact(
        {
            "trial": 0,
            "measurement_metrics": {"legacy_metric": 1.0},
            "measurement_figures": [{"kind": "legacy"}],
            "measurement_summary": {"legacy": True},
            "measurement_provenance": {"legacy_source": "top_level"},
            "metadata": {
                "measurement_traces": {
                    "metrics": {"canonical_metric": 2.0},
                    "figures": [{"kind": "canonical"}],
                    "summary": {"format": "markdown"},
                    "provenance": {"preset_name": "learning_curve_basic"},
                },
                "measurement": {
                    "metrics": {"legacy_metadata_metric": 3.0},
                    "figures": [{"kind": "legacy_metadata"}],
                    "summary": {"format": "json"},
                    "provenance": {"legacy_source": "metadata"},
                },
            },
        }
    )

    assert out["measurement_metrics"] == {"canonical_metric": 2.0}
    assert out["measurement_figures"] == [{"kind": "canonical"}]
    assert out["measurement_summary"] == {"format": "markdown"}
    assert out["measurement_provenance"] == {"preset_name": "learning_curve_basic"}


def test_v3_22_15_legacy_measurement_bridges_emit_owner_and_expiry_markers():
    out = report_module._normalize_record_for_artifact(
        {
            "trial": 1,
            "measurement_metrics": {"legacy_metric": 1.0},
            "measurement_figures": [{"kind": "legacy_top"}],
            "measurement_summary": {"legacy": "top"},
            "measurement_provenance": {"legacy_source": "top_level"},
            "metadata": {
                "measurement": {
                    "metrics": {"legacy_metadata_metric": 2.0},
                    "figures": [{"kind": "legacy_metadata"}],
                    "summary": {"legacy": "metadata"},
                    "provenance": {"legacy_source": "metadata"},
                },
                "runtime_measurement": {
                    "analysis": {"runtime_metric": 3.0},
                    "visualization": {"figures": [{"kind": "runtime"}]},
                    "report": {"runtime_summary": True},
                    "metadata": {"runtime_source": "runtime_measurement_json"},
                },
            },
        }
    )

    # Legacy bridge precedence (no canonical measurement_traces):
    # top-level -> metadata.measurement -> metadata.runtime_measurement
    assert out["measurement_metrics"] == {"runtime_metric": 3.0}
    assert out["measurement_figures"] == [{"kind": "runtime"}]
    assert out["measurement_summary"] == {"runtime_summary": True}

    bridge_markers = out["measurement_provenance"]["compatibility_bridges"]
    assert [item["bridge"] for item in bridge_markers] == [
        "legacy_top_level_measurement_fields",
        "legacy_metadata_measurement_payload",
        "legacy_runtime_measurement_payload",
    ]
    for item in bridge_markers:
        assert item["owner"] == "v3.22.15"
        assert item["expiry"] == "v3.23.0"

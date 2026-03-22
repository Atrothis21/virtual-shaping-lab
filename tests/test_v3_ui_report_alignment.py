from __future__ import annotations

import json

from analysis.report.config import ReportConfig
from analysis.report import report as report_module
from ui.contracts.dependent_variable_resolver import resolve_report_variable
from ui.contracts.report_alignment import build_report_alignment_contract


class _DummyMetric:
    def compute(self, records):
        return {"n": len(records)}


def test_report_labeling_contract_sources_registry_labels_and_descriptions():
    aligned = build_report_alignment_contract(
        "acquisition",
        metric_names=["prediction_time_series"],
    )
    predicted_outcome = resolve_report_variable("predicted_outcome")

    metric = aligned["metric_labels"]["prediction_time_series"]
    assert metric["source"] == "dependent_variable_registry"
    assert metric["variable_id"] == "predicted_outcome"
    assert metric["label"] == predicted_outcome["label"]
    assert metric["description"] == predicted_outcome["plain_language"]


def test_report_alignment_snapshot_for_selected_acquisition_metrics():
    aligned = build_report_alignment_contract(
        "acquisition",
        metric_names=["prediction_time_series", "mean_prediction_by_stimulus"],
    )
    assert aligned["preset_id"] == "acquisition"
    assert [entry["id"] for entry in aligned["variables"]] == [
        "associative_strength",
        "predicted_outcome",
        "prediction_error",
        "response_strength",
    ]
    assert aligned["metric_labels"] == {
        "prediction_time_series": {
            "label": "Predicted Outcome",
            "description": "Expected outcome before feedback arrives.",
            "variable_id": "predicted_outcome",
            "source": "dependent_variable_registry",
        },
        "mean_prediction_by_stimulus": {
            "label": "Mean Prediction By Stimulus",
            "description": "",
            "variable_id": None,
            "source": "metric_name_fallback",
        },
    }


def test_run_report_emits_registry_driven_alignment_artifact(monkeypatch, tmp_path):
    cfg = ReportConfig(
        metrics=["prediction_time_series", "mean_prediction_by_stimulus"],
        visualizations=[],
        params={},
    )
    monkeypatch.setattr(report_module, "get_report_preset", lambda _name: cfg)
    monkeypatch.setattr(
        report_module,
        "METRIC_REGISTRY",
        {
            "prediction_time_series": _DummyMetric,
            "mean_prediction_by_stimulus": _DummyMetric,
        },
    )

    report_dir = report_module.run_report(
        records=[{"prediction": 0.2, "response": 0.2, "stimulus": "tone"}],
        preset="acquisition",
        output_dir=str(tmp_path),
    )
    alignment_path = report_dir / "report_alignment.json"
    assert alignment_path.exists()

    payload = json.loads(alignment_path.read_text(encoding="utf-8"))
    assert payload["preset_id"] == "acquisition"
    assert payload["metric_labels"]["prediction_time_series"]["label"] == "Predicted Outcome"
    assert payload["metric_labels"]["mean_prediction_by_stimulus"]["label"] == "Mean Prediction By Stimulus"


def test_run_report_metric_pages_use_registry_alignment_label(monkeypatch, tmp_path):
    cfg = ReportConfig(
        metrics=["prediction_time_series"],
        visualizations=[],
        params={},
    )
    monkeypatch.setattr(report_module, "get_report_preset", lambda _name: cfg)
    monkeypatch.setattr(report_module, "METRIC_REGISTRY", {"prediction_time_series": _DummyMetric})

    captured_titles: list[str] = []

    class _DummyPdf:
        def __init__(self, _path):
            self.path = _path

        def add_figure(self, _fig, _title: str):
            pass

        def add_metric_text(self, title: str, _metric_result):
            captured_titles.append(title)

        def close(self):
            pass

    monkeypatch.setattr(report_module, "ReportPDF", _DummyPdf)

    report_module.run_report(
        records=[{"prediction": 0.2, "response": 0.2, "stimulus": "tone"}],
        preset="acquisition",
        output_dir=str(tmp_path),
    )
    assert captured_titles == ["Predicted Outcome"]

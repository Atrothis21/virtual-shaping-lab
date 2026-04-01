import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import pytest

from analysis.report import config as report_config
from analysis.report.config import ReportConfig
from analysis.report import io as report_io
from analysis.report.pdf import ReportPDF
from analysis.report.presets import get_report_preset
from analysis.report import report as report_module


class DummyMetric:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def compute(self, records):
        return {"count": len(records)}


class DummyViz:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.fig = None

    def render(self, records, metrics=None, **kwargs):
        self.fig, ax = plt.subplots()
        ax.plot([0, 1])

    def save(self, path):
        if self.fig is None:
            raise RuntimeError("render must be called before save")
        self.fig.savefig(path)


class DummyVizNoParams:
    def __init__(self):
        self.kwargs = {}


def test_report_config_metric_and_visualization_build(monkeypatch):
    monkeypatch.setitem(report_config.METRIC_REGISTRY, "dummy_metric", DummyMetric)
    monkeypatch.setitem(report_config.VISUALIZATION_REGISTRY, "dummy_viz", DummyViz)
    cfg = ReportConfig(metrics=["dummy_metric"], visualizations=["dummy_viz"], params={"x": 1})
    items = cfg.items
    assert len(items) == 1
    assert isinstance(items[0].metric, DummyMetric)
    assert isinstance(items[0].visualization, DummyViz)


def test_report_config_discrimination_metric(monkeypatch):
    monkeypatch.setitem(report_config.METRIC_REGISTRY, "discrimination_index", DummyMetric)
    monkeypatch.setitem(report_config.VISUALIZATION_REGISTRY, "dummy_viz", DummyViz)
    cfg = ReportConfig(
        metrics=["discrimination_index"],
        visualizations=["dummy_viz"],
        params={"cs_plus": ["tone"], "cs_minus": ["noise"]},
    )
    items = cfg.items
    assert items[0].metric.kwargs["positive_key"] == "tone"


def test_report_config_unknown_metric(monkeypatch):
    monkeypatch.setitem(report_config.METRIC_REGISTRY, "dummy_metric", DummyMetric)
    cfg = ReportConfig(metrics=["missing_metric"], visualizations=["dummy_viz"])
    with pytest.raises(KeyError):
        _ = cfg.items


def test_report_config_unknown_visualization(monkeypatch):
    monkeypatch.setitem(report_config.METRIC_REGISTRY, "dummy_metric", DummyMetric)
    cfg = ReportConfig(metrics=["dummy_metric"], visualizations=["missing_viz"])
    with pytest.raises(KeyError):
        _ = cfg.items


def test_report_config_visualization_fallback(monkeypatch):
    monkeypatch.setitem(report_config.METRIC_REGISTRY, "dummy_metric", DummyMetric)
    monkeypatch.setitem(report_config.VISUALIZATION_REGISTRY, "dummy_viz", DummyVizNoParams)
    cfg = ReportConfig(metrics=["dummy_metric"], visualizations=["dummy_viz"], params={"x": 1})
    items = cfg.items
    assert isinstance(items[0].visualization, DummyVizNoParams)


def test_report_config_length_mismatch():
    cfg = ReportConfig(metrics=["a"], visualizations=["b", "c"])
    with pytest.raises(ValueError):
        _ = cfg.items


def test_create_report_dir_and_save_metric(tmp_path):
    report_dir = report_io.create_report_dir(base_dir=str(tmp_path))
    assert (report_dir / "metrics").exists()
    assert (report_dir / "figures").exists()

    metrics_dir = report_dir / "metrics"
    report_io.save_metric_output("dummy_metric", {"value": 1}, metrics_dir)
    saved = metrics_dir / "dummy_metric.json"
    assert saved.exists()
    assert json.loads(saved.read_text()) == {"value": 1}


def test_report_pdf_writes_pages(tmp_path):
    pdf_path = tmp_path / "report.pdf"
    pdf = ReportPDF(pdf_path)

    fig = plt.figure()
    pdf.add_figure(fig, "Figure Title")
    plt.close(fig)

    pdf.add_metric_text("Metric", {"value": 1})
    pdf.close()

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0


def test_report_preset_unknown_name_raises():
    with pytest.raises(KeyError):
        _ = get_report_preset("missing_preset")


def test_run_report_writes_outputs(monkeypatch, tmp_path):
    cfg = ReportConfig(
        metrics=["dummy_metric"],
        visualizations=["dummy_viz"],
        params={},
    )

    monkeypatch.setattr(report_module, "get_report_preset", lambda name: cfg)
    monkeypatch.setattr(report_module, "METRIC_REGISTRY", {"dummy_metric": DummyMetric})
    monkeypatch.setattr(report_module, "VISUALIZATION_REGISTRY", {"dummy_viz": DummyViz})

    payload = {
        "experiment": {
            "program": {
                "phases": [
                    {
                        "name": "Phase 0",
                        "protocol": "acquisition",
                        "stimuli": {"cs_plus": ["tone"]},
                        "params": {"n_trials": 1},
                        "trials": 1,
                    }
                ]
            },
            "agent": {
                "name": "classical_agent",
                "representation": {
                    "name": "vector_elemental",
                    "params": {"stimuli": ["tone"]},
                },
                "learning": {
                    "rule": "rescorla_wagner",
                    "params": {},
                    "attention": {
                        "initial": {"tone": 0.7},
                        "config": {"name": "static", "params": {"default": 1.0}},
                    },
                },
                "policy": None,
            },
            "runtime": {},
        },
        "report": {"preset": "dummy"},
    }
    payload["provenance"] = {"mechanisms": {"attention_mechanism": {"variant": "static"}}}
    records = [{"prediction": 0.1, "trial": 0}]

    report_dir = report_module.run_report(
        records=records,
        preset="dummy",
        payload=payload,
        output_dir=str(tmp_path),
    )

    assert (report_dir / "records.json").exists()
    assert (report_dir / "payload.json").exists()
    assert (report_dir / "attention_summary.json").exists()
    assert (report_dir / "mechanism_provenance.json").exists()
    assert (report_dir / "artifact_identity.json").exists()
    assert (report_dir / "report.pdf").exists()
    assert (report_dir / "metrics" / "dummy_metric.json").exists()

    stored_payload = json.loads((report_dir / "payload.json").read_text())
    assert set(stored_payload["experiment"].keys()) == {"program", "agent", "runtime"}
    stored_records = json.loads((report_dir / "records.json").read_text())
    assert stored_records[0]["trial"] == 0
    assert "step" in stored_records[0]
    assert "tick" in stored_records[0]
    assert "stimulus" in stored_records[0]
    assert "action" in stored_records[0]
    assert "reward" in stored_records[0]
    assert "prediction" in stored_records[0]
    assert "prediction_error" in stored_records[0]
    assert "policy_state" in stored_records[0]
    attention = json.loads((report_dir / "attention_summary.json").read_text())
    assert attention == {"tone": 0.7}
    mechanism_provenance = json.loads((report_dir / "mechanism_provenance.json").read_text())
    assert mechanism_provenance == {"attention_mechanism": {"variant": "static"}}
    artifact_identity = json.loads((report_dir / "artifact_identity.json").read_text())
    assert isinstance(artifact_identity.get("engine_version"), str) and artifact_identity["engine_version"]
    assert artifact_identity.get("record_schema_version") == "v1"
    assert isinstance(artifact_identity.get("mechanism_identity"), dict)

    fig_path = report_dir / "dummy_viz.png"
    assert fig_path.exists()


def test_run_report_unknown_metric(monkeypatch, tmp_path):
    cfg = ReportConfig(metrics=["missing_metric"], visualizations=[], params={})
    monkeypatch.setattr(report_module, "get_report_preset", lambda name: cfg)
    monkeypatch.setattr(report_module, "METRIC_REGISTRY", {})

    with pytest.raises(KeyError):
        report_module.run_report(
            records=[{"prediction": 0.1}],
            preset="dummy",
            output_dir=str(tmp_path),
        )


def test_run_report_unknown_visualization(monkeypatch, tmp_path):
    cfg = ReportConfig(metrics=[], visualizations=["missing_viz"], params={})
    monkeypatch.setattr(report_module, "get_report_preset", lambda name: cfg)
    monkeypatch.setattr(report_module, "VISUALIZATION_REGISTRY", {})

    with pytest.raises(KeyError):
        report_module.run_report(
            records=[{"prediction": 0.1}],
            preset="dummy",
            output_dir=str(tmp_path),
        )


def test_normalize_record_for_artifact_promotes_learner_traces():
    out = report_module._normalize_record_for_artifact(
        {
            "trial": 0,
            "metadata": {
                "learner": {
                    "prediction": 0.2,
                    "error": -0.1,
                    "update_features": {"tone": 1.0},
                    "attention_state": {"tone": 0.8},
                    "eligibility_state": {"tone": 0.5},
                }
            },
        }
    )
    assert out["prediction"] == pytest.approx(0.2)
    assert out["prediction_error"] == pytest.approx(-0.1)
    assert out["v"] == pytest.approx(0.2)
    assert out["delta"] == pytest.approx(-0.1)
    assert out["theta"] == {"tone": 1.0}
    assert out["attention"] == {"tone": 0.8}
    assert out["memory"] == {"tone": 0.5}


def test_normalize_record_for_artifact_promotes_observation_traces():
    out = report_module._normalize_record_for_artifact(
        {
            "trial": 0,
            "metadata": {
                "observation_traces": {
                    "representation": {"tone": 1.0},
                    "context_state": "A",
                    "generalized_state": {"kind": "identity"},
                    "features": [1.0, 0.0],
                    "feature_names": ["tone", "ctx:A"],
                    "provenance": {
                        "runtime_observation": {"preset_name": "identity_observation"},
                    },
                }
            },
        }
    )
    assert out["representation"] == {"tone": 1.0}
    assert out["context_state"] == "A"
    assert out["generalized_state"] == {"kind": "identity"}
    assert out["features"] == [1.0, 0.0]
    assert out["observation_provenance"] == {
        "runtime_observation": {"preset_name": "identity_observation"},
    }


def test_normalize_record_for_artifact_promotes_policy_traces():
    out = report_module._normalize_record_for_artifact(
        {
            "trial": 0,
            "metadata": {
                "policy_traces": {
                    "action": "leverpress",
                    "available_actions": ["leverpress", "no_press"],
                    "action_scores": {"leverpress": 0.9, "no_press": 0.2},
                    "action_probabilities": {"leverpress": 0.8, "no_press": 0.2},
                    "provenance": {"variant": "epsilon_greedy"},
                }
            },
        }
    )
    assert out["action"] == "leverpress"
    assert out["policy_action"] == "leverpress"
    assert out["policy_available_actions"] == ["leverpress", "no_press"]
    assert out["policy_action_scores"] == {"leverpress": 0.9, "no_press": 0.2}
    assert out["policy_action_probabilities"] == {"leverpress": 0.8, "no_press": 0.2}
    assert out["policy_provenance"] == {"variant": "epsilon_greedy"}
    assert out["policy_state"] == {
        "action_scores": {"leverpress": 0.9, "no_press": 0.2},
        "action_probabilities": {"leverpress": 0.8, "no_press": 0.2},
    }


def test_normalize_record_for_artifact_promotes_protocol_traces():
    out = report_module._normalize_record_for_artifact(
        {
            "trial": 0,
            "metadata": {
                "protocol_traces": {
                    "emission": {
                        "stimulus": {"lever": 1.0},
                        "context": "A",
                        "available_actions": ["leverpress", "no_press"],
                    },
                    "consequence": {"reward": 1.0, "done": False},
                    "advance": {"t": 3, "phase_step": 3, "dt_s": 1.0},
                    "stop": {"should_stop": False, "reason": None},
                    "timing": {"t": 3, "phase_step": 3, "dt_s": 1.0},
                    "provenance": {
                        "preset_name": "operant_protocol",
                        "pipeline_order": ["emit", "consequence", "advance", "stop", "finalize"],
                    },
                }
            },
        }
    )
    assert out["protocol_emission"] == {
        "stimulus": {"lever": 1.0},
        "context": "A",
        "available_actions": ["leverpress", "no_press"],
    }
    assert out["protocol_consequence"] == {"reward": 1.0, "done": False}
    assert out["protocol_advance"] == {"t": 3, "phase_step": 3, "dt_s": 1.0}
    assert out["protocol_stop"] == {"should_stop": False, "reason": None}
    assert out["protocol_timing"] == {"t": 3, "phase_step": 3, "dt_s": 1.0}
    assert out["protocol_provenance"] == {
        "preset_name": "operant_protocol",
        "pipeline_order": ["emit", "consequence", "advance", "stop", "finalize"],
    }

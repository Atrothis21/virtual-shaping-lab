from pathlib import Path

from analysis.domain.types import ReportResult
from analysis.public import (
    get_protocol_default_template,
    list_protocol_default_templates,
    run_default_protocol_report,
    run_preset_report,
)


def _trial_records():
    return [
        {"trial": 0, "reward": 0.0, "prediction": 0.1, "stimulus": "tone", "context": "A"},
        {"trial": 1, "reward": 1.0, "prediction": 0.5, "stimulus": "tone", "context": "A"},
        {"trial": 2, "reward": 1.0, "prediction": 0.8, "stimulus": "noise", "context": "A"},
    ]


def test_list_protocol_default_templates_from_public_facade():
    templates = list_protocol_default_templates()
    assert isinstance(templates, dict)
    assert "blocking" in templates
    assert "report_name" in templates["blocking"]
    assert "template_version" in templates["blocking"]


def test_get_protocol_default_template_from_public_facade():
    spec = get_protocol_default_template("blocking")
    assert hasattr(spec, "report_name")
    assert hasattr(spec, "template_version")
    assert hasattr(spec, "metric_names")
    assert hasattr(spec, "figure_names")


def test_run_default_protocol_report_from_public_facade(tmp_path):
    out = run_default_protocol_report(
        protocol_name="blocking",
        records=_trial_records(),
        out_dir=str(tmp_path),
    )
    assert isinstance(out, ReportResult)
    assert Path(out.output_dir).exists()


def test_run_preset_report_from_public_facade(tmp_path):
    out_dir = run_preset_report(
        records=_trial_records(),
        preset="acquisition",
        payload={
            "experiment": {
                "program": {
                    "phases": [
                        {
                            "name": "Acquisition",
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
                    },
                    "policy": None,
                },
                "runtime": {},
            },
            "report": {"preset": "acquisition"},
        },
        output_dir=str(tmp_path),
    )
    assert Path(out_dir).exists()

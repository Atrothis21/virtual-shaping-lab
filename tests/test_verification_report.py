from pathlib import Path
import warnings

from analysis.domain.types import AnalysisContext
from analysis.registry import run_report_template

_TICKLABEL_WARNING_FRAGMENT = "set_ticklabels() should only be used with a fixed number of ticks"


def _trial_records():
    return [
        {"trial": 0, "reward": 0.0, "prediction": 0.1, "stimulus": "tone", "context": "A"},
        {"trial": 1, "reward": 1.0, "prediction": 0.5, "stimulus": "tone", "context": "A"},
        {"trial": 2, "reward": 1.0, "prediction": 0.8, "stimulus": "noise", "context": "A"},
    ]


def _tick_records():
    return [
        {"trial": 0, "tick": 0, "reward": 0.0, "action": None, "context": "A", "t_s": 0.0, "dt_s": 0.5},
        {"trial": 0, "tick": 1, "reward": 1.0, "action": "press", "context": "A", "t_s": 0.5, "dt_s": 0.5},
        {"trial": 1, "tick": 0, "reward": 0.0, "action": None, "context": "A", "t_s": 0.0, "dt_s": 0.5},
        {"trial": 1, "tick": 1, "reward": 1.0, "action": "press", "context": "A", "t_s": 0.5, "dt_s": 0.5},
    ]


def test_verification_report_generates_artifacts_for_trial_records(tmp_path):
    out = run_report_template("verification_report", _trial_records(), str(tmp_path))
    assert out.name == "verification_report"
    assert Path(out.output_dir).exists()
    assert "mean_reward" in out.artifacts["metrics"]
    assert len(out.artifacts["figures"]) == 3
    for p in out.artifacts["figures"]:
        assert Path(p).exists()


def test_verification_report_generates_tick_curve_when_ticks_present(tmp_path):
    ctx = AnalysisContext(record_mode="tick")
    out = run_report_template("verification_report", _tick_records(), str(tmp_path), ctx=ctx)
    assert len(out.artifacts["figures"]) == 3
    tick_fig = [p for p in out.artifacts["figures"] if p.endswith("tick_response_curve.png")]
    assert len(tick_fig) == 1
    assert Path(tick_fig[0]).exists()


def test_verification_report_emits_no_ticklabel_warnings(tmp_path):
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        run_report_template("verification_report", _trial_records(), str(tmp_path))

    ticklabel_warnings = [
        w for w in captured if _TICKLABEL_WARNING_FRAGMENT in str(w.message)
    ]
    assert ticklabel_warnings == []

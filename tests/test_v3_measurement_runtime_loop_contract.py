from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v3_22_10_environment_step_loop_has_no_runtime_measurement_dispatch():
    text = (ROOT / "virtual_shaping_lab" / "vsl" / "rollout" / "harness.py").read_text(encoding="utf-8")
    assert "build_runtime_measurement_adapter(" not in text
    assert "measurement_adapter.step(" not in text
    assert ".run_with_measurement(" not in text


def test_v3_22_10_replay_harness_dispatches_measurement_after_rollout_completion():
    text = (ROOT / "virtual_shaping_lab" / "vsl" / "rollout" / "replay_harness.py").read_text(encoding="utf-8")
    assert "def run_with_measurement(" in text
    assert "records = self.run(" in text
    assert "measurement_result = adapter.step(" in text
    assert text.find("records = self.run(") < text.find("measurement_result = adapter.step(")


def test_v3_22_10_report_measurement_runs_on_finalized_records_not_runtime_loop():
    text = (ROOT / "virtual_shaping_lab" / "analysis" / "report" / "report.py").read_text(encoding="utf-8")
    assert "build_runtime_measurement_adapter(" in text
    assert "_to_runtime_measurement_records(records)" in text
    assert "environment.step(" not in text

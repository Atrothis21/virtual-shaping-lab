from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTION_SERVICE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "preset_action_service.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_action_service_exports_workflow_boundary():
    text = _read(ACTION_SERVICE)
    assert "window.VSLReact.presetActionService" in text
    assert "createPresetActionService" in text
    assert "resolvePresetFromSelection" in text
    assert "resolveAndRunPresetFromSelection" in text
    assert "resolveRunReportPresetFromSelection" in text


def test_action_service_contains_plan_run_report_side_effects():
    text = _read(ACTION_SERVICE)
    assert "apiClient.postJson(\"plan\", payload)" in text
    assert "apiClient.postJson(\"run\", runPayload)" in text
    assert "apiClient.postJson(`runs/${encodeURIComponent(runId)}/report`, {})" in text
    assert "type: stateApi.UI_EVENTS.PLAN_RESOLVE_REQUESTED" in text
    assert "type: stateApi.UI_EVENTS.RUN_START_REQUESTED" in text
    assert "type: stateApi.UI_EVENTS.REPORT_REQUESTED" in text


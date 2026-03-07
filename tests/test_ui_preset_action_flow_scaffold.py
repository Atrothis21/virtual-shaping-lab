from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
ACTION_SERVICE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "preset_action_service.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_preset_action_flow_has_plan_then_run_sequence():
    text = _read(ACTION_SERVICE)
    assert "const resolved = await resolvePresetFromSelection(presetItem);" in text
    assert "if (!resolved.ok) return resolved;" in text
    assert "expected_plan_hash" in text
    assert "setActionState({" in text
    assert "message: \"Starting preset run...\"" in text


def test_preset_action_flow_exposes_workflow_callbacks_to_route_container():
    text = _read(INDEX_APP)
    assert "onResolvePresetAction={resolvePresetFromSelection}" in text
    assert "onResolveRunAction={resolveAndRunPresetFromSelection}" in text
    assert "onResolveRunReportAction={resolveRunReportPresetFromSelection}" in text
    assert "actionState={presetActionState}" in text


def test_preset_action_flow_has_run_readiness_before_report_creation():
    text = _read(ACTION_SERVICE)
    assert "waitForRunReportReadiness" in text
    assert "Waiting for run readiness before report..." in text
    assert "isRunTerminalFromPayload" in text
    assert "Run not report-ready yet. Continue from Run route when complete." in text
    assert "apiClient.postJson(`runs/${encodeURIComponent(runId)}/report`, {})" in text
    assert "type: stateApi.UI_EVENTS.REPORT_REQUESTED" in text
    assert "type: stateApi.UI_EVENTS.REPORT_SUCCEEDED" in text
    assert "type: stateApi.UI_EVENTS.REPORT_FAILED" in text


def test_preset_action_flow_has_hash_mismatch_recovery_message():
    text = _read(ACTION_SERVICE)
    assert "isPlanHashMismatchError" in text
    assert "Plan hash mismatch detected. Re-resolve preset and retry run." in text


def test_index_app_uses_action_service_handlers():
    text = _read(INDEX_APP)
    assert "window.VSLReact.presetActionService" in text
    assert "presetActionHandlers" in text
    assert "presetActionHandlers.resolvePresetFromSelection" in text
    assert "presetActionHandlers.resolveAndRunPresetFromSelection" in text
    assert "presetActionHandlers.resolveRunReportPresetFromSelection" in text

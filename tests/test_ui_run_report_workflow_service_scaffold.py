from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "run_report_workflow_service.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_run_report_workflow_service_exports_boundary():
    text = _read(SERVICE)
    assert "window.VSLReact.runReportWorkflowService" in text
    assert "createRunReportWorkflowService" in text
    assert "startRunFromResolvedPlan" in text
    assert "refreshActiveRunStatus" in text
    assert "pollActiveRunStatus" in text
    assert "createReportFromActiveRun" in text


def test_run_report_workflow_service_owns_run_and_report_side_effects():
    text = _read(SERVICE)
    assert 'apiClient.postJson("run", runPayload)' in text
    assert 'apiClient.getJson(`runs/${encodeURIComponent(runId)}`)' in text
    assert 'apiClient.postJson(`runs/${encodeURIComponent(runId)}/report`, {})' in text
    assert "type: stateApi.UI_EVENTS.RUN_START_REQUESTED" in text
    assert "type: stateApi.UI_EVENTS.RUN_STATUS_UPDATED" in text
    assert "type: stateApi.UI_EVENTS.REPORT_REQUESTED" in text

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_run_route_has_start_and_polling_controls():
    text = _read(INDEX_APP)
    assert "function RunRouteContainer(" in text
    assert "Start Run" in text
    assert "Refresh Status" in text
    assert "startRunFromResolvedPlan" in text
    assert "refreshActiveRunStatus" in text


def test_run_route_renders_lifecycle_and_provenance_summary():
    text = _read(INDEX_APP)
    assert "selectRunLifecycleViewModel" in text
    assert "buildLifecycleInstrumentView" in text
    assert "Request Status:" in text
    assert "Active Run ID:" in text
    assert "Plan Hash:" in text
    assert "Polling Updated:" in text
    assert "isRunTerminalLifecycle" in text
    assert "lifecycle-instrument" in text
    assert "lifecycle-meter" in text


def test_run_route_wires_run_create_and_polling_events():
    text = _read(INDEX_APP)
    assert "window.VSLReact.lifecycleViewModels" in text
    assert "selectRunLifecycleViewModelFn" in text
    assert "buildLifecycleInstrumentViewFn" in text
    assert "runReportWorkflowService" in text
    assert "createRunReportWorkflowService" in text
    assert "runReportWorkflowHandlers.startRunFromResolvedPlan" in text
    assert "runReportWorkflowHandlers.refreshActiveRunStatus" in text
    assert "runReportWorkflowHandlers.pollActiveRunStatus" in text
    assert "window.setInterval" in text


def test_run_lifecycle_styles_exist():
    text = _read(INDEX_HTML)
    assert ".run-lifecycle-card" in text
    assert ".run-lifecycle-summary" in text
    assert ".lifecycle-badge" in text
    assert ".lifecycle-instrument" in text
    assert ".lifecycle-meter" in text
    assert ".lifecycle-caption" in text
    assert ".run-action-message" in text
    assert ".run-action-error" in text

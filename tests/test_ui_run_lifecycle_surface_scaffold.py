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
    assert "Request Status:" in text
    assert "Active Run ID:" in text
    assert "Plan Hash:" in text
    assert "Polling Updated:" in text
    assert "isRunTerminalLifecycle" in text


def test_run_route_wires_run_create_and_polling_events():
    text = _read(INDEX_APP)
    assert "stateApi.UI_EVENTS.RUN_START_REQUESTED" in text
    assert "stateApi.UI_EVENTS.RUN_START_SUCCEEDED" in text
    assert "stateApi.UI_EVENTS.RUN_START_FAILED" in text
    assert "stateApi.UI_EVENTS.RUN_STATUS_UPDATED" in text
    assert "window.setInterval" in text
    assert "runs/${encodeURIComponent(runState.activeRunId)}" in text


def test_run_lifecycle_styles_exist():
    text = _read(INDEX_HTML)
    assert ".run-lifecycle-card" in text
    assert ".run-lifecycle-summary" in text
    assert ".run-action-message" in text
    assert ".run-action-error" in text


from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"
REPORT_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "report_route.jsx"
LIFECYCLE_VIEW_MODELS = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "lifecycle_view_models.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_report_route_has_create_report_action_and_lifecycle_summary():
    text = _read(REPORT_ROUTE)
    assert "function ReportRouteContainer(" in text
    assert "Generate Report" in text
    assert "Refresh Run Status" in text
    assert "selectReportLifecycleViewModel" in text
    assert "buildLifecycleInstrumentView" in text
    assert "Run ID:" in text
    assert "Lifecycle:" in text
    assert "Next Actions:" in text
    assert "report-provenance-summary" in text
    assert "source_run_id:" in text
    assert "template_version_used:" in text
    assert "lifecycle-instrument" in text
    assert "lifecycle-meter" in text


def test_report_route_wires_report_events_and_report_endpoint():
    text = _read(REPORT_ROUTE) + _read(INDEX_APP) + _read(LIFECYCLE_VIEW_MODELS)
    assert "createReportFromActiveRun" in text
    assert "window.VSLReact.lifecycleViewModels" in text
    assert "selectReportLifecycleViewModelFn" in text
    assert "selectReportArtifactViewModelFn" in text
    assert "detectReportVersionMismatchesFn" in text
    assert "runReportWorkflowService" in text
    assert "runReportWorkflowHandlers.createReportFromActiveRun" in text
    assert "isPlanFresh={isPlanFreshForCurrentDraft}" in text
    assert "Plan is stale for current draft. Re-resolve plan before generating report." in text
    assert "reportActionStatus={reportActionStatus}" in text
    assert "RouteNotice={RouteNotice}" in text
    assert "selectReportArtifactViewModel" in text
    assert "inferFigureSemanticTone" in text
    assert "detectReportVersionMismatches" in text
    assert "Degraded mode active for" in text
    assert "report-plot-legend" in text
    assert "report-figure-grid" in text
    assert "report-figure-card" in text


def test_report_lifecycle_styles_exist():
    text = _read(INDEX_CSS)
    assert ".report-lifecycle-card" in text
    assert ".report-lifecycle-summary" in text
    assert ".report-provenance-summary" in text
    assert ".report-degraded-note" in text
    assert ".report-artifact-grid" in text
    assert ".report-artifact-card" in text
    assert ".report-artifact-missing" in text
    assert ".report-plot-legend" in text
    assert ".report-figure-grid" in text
    assert ".report-figure-card" in text
    assert ".report-figure-card.accent-cs-plus::before" in text
    assert ".report-figure-card.accent-cs-minus::before" in text
    assert ".report-figure-card.accent-probe::before" in text
    assert ".report-figure-card.accent-compound::before" in text
    assert ".report-figure-card.accent-learning::before" in text
    assert ".report-figure-title" in text
    assert ".report-figure-tone" in text
    assert ".report-figure-list" in text
    assert ".report-action-message" in text
    assert ".report-action-error" in text

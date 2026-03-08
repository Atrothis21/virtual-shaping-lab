from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_PRIMITIVES = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "ui_primitives.jsx"
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
PRESETS_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "presets_route.jsx"
RUN_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "run_route.jsx"
REPORT_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "report_route.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ui_primitives_export_shared_route_notice():
    text = _read(UI_PRIMITIVES)
    assert "function RouteNotice(" in text
    assert "route-notice" in text
    assert "RouteNotice," in text


def test_index_app_routes_use_shared_route_notice_for_non_happy_paths():
    app_text = _read(INDEX_APP)
    presets_text = _read(PRESETS_ROUTE)
    run_text = _read(RUN_ROUTE)
    report_text = _read(REPORT_ROUTE)
    assert "const RouteNotice = uiPrimitives.RouteNotice" in app_text
    assert "className=\"preset-action-error\"" in presets_text
    assert "className=\"run-action-error\"" in run_text
    assert "className=\"report-action-error\"" in report_text
    assert "className=\"run-blocking-note\"" in run_text
    assert "className=\"report-degraded-note\"" in report_text


def test_route_notice_styles_exist():
    text = _read(INDEX_CSS)
    assert ".route-notice" in text
    assert ".route-notice.info" in text
    assert ".route-notice.warning" in text
    assert ".route-notice.error" in text

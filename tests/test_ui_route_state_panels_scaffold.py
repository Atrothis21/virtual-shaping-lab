from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_PRIMITIVES = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "ui_primitives.jsx"
PRESETS_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "presets_route.jsx"
BUILDER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "builder_route.jsx"
RUN_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "run_route.jsx"
REPORT_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "report_route.jsx"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ui_primitives_export_route_state_panel():
    text = _read(UI_PRIMITIVES)
    assert "function RouteStatePanel(" in text
    assert "route-state-panel" in text
    assert "RouteStatePanel," in text


def test_routes_use_route_state_panels_for_loading_empty_success_completion():
    presets = _read(PRESETS_ROUTE)
    builder = _read(BUILDER_ROUTE)
    run = _read(RUN_ROUTE)
    report = _read(REPORT_ROUTE)
    assert "RouteStatePanel" in presets
    assert "RouteStatePanel" in builder
    assert "RouteStatePanel" in run
    assert "RouteStatePanel" in report
    assert 'state: "loading"' in presets + builder + run + report
    assert 'state: "empty"' in presets + builder + run + report
    assert 'state: "success"' in presets + builder + run + report
    assert 'state: "completed"' in presets + builder + run + report


def test_route_state_panel_styles_exist():
    text = _read(INDEX_CSS)
    assert ".route-state-panel" in text
    assert ".route-state-panel.loading" in text
    assert ".route-state-panel.empty" in text
    assert ".route-state-panel.success" in text
    assert ".route-state-panel.completed" in text

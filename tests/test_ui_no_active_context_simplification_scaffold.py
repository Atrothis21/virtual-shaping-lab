from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "run_route.jsx"
REPORT_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "report_route.jsx"
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_run_route_has_compact_no_active_context_mode_with_single_nav_action():
    text = _read(RUN_ROUTE)
    assert "if (!vm.activeRunId)" in text
    assert "run-empty-compact" in text
    assert "No active run" in text
    assert "Go to presets" in text
    assert "onNavigate" in text


def test_report_route_has_compact_no_active_context_mode_with_single_nav_action():
    text = _read(REPORT_ROUTE)
    assert "if (!vm.effectiveRunId)" in text
    assert "report-empty-compact" in text
    assert "No report context" in text
    assert "Go to runs" in text
    assert "onNavigate" in text


def test_index_app_wires_navigation_keys_to_run_and_report_routes():
    text = _read(INDEX_APP)
    assert "onNavigate={navigateTo}" in text
    assert "routeKeys={{ presets: routes.presets.key }}" in text
    assert "routeKeys={{ run: routes.run.key }}" in text


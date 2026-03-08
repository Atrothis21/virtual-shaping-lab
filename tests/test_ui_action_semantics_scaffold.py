from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRESETS_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "presets_route.jsx"
BUILDER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "builder_route.jsx"
RUN_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "run_route.jsx"
REPORT_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "report_route.jsx"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_primary_secondary_action_classes_are_present_in_routes():
    presets = _read(PRESETS_ROUTE)
    builder = _read(BUILDER_ROUTE)
    run = _read(RUN_ROUTE)
    report = _read(REPORT_ROUTE)
    text = presets + builder + run + report
    assert "route-action-primary" in text
    assert "route-action-secondary" in text


def test_primary_actions_use_consistent_verbs():
    text = _read(PRESETS_ROUTE) + _read(BUILDER_ROUTE) + _read(RUN_ROUTE) + _read(REPORT_ROUTE)
    assert "Resolve Plan" in text
    assert "Start Run" in text
    assert "Generate Report" in text
    assert "Resolve Preset" in text


def test_action_semantic_styles_exist():
    css = _read(INDEX_CSS)
    assert ".route-action-primary" in css
    assert ".route-action-secondary" in css

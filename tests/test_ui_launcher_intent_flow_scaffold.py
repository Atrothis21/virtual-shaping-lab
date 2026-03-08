from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "launcher_route.jsx"
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_launcher_route_has_featured_and_recent_sections_with_caps():
    text = _read(LAUNCHER_ROUTE)
    assert "selectFeaturedPresetItems(catalogState, 4)" in text
    assert "buildRecentActivityItems(runState, reportState, 3)" in text
    assert "Featured presets" in text
    assert "Recent activity" in text


def test_launcher_route_wires_quick_actions_to_shared_handlers():
    text = _read(LAUNCHER_ROUTE) + _read(INDEX_APP)
    assert "onResolveRunAction" in text
    assert "onResolveRunReportAction" in text
    assert "handleQuickRun" in text
    assert "handleQuickRunReport" in text
    assert "onResolveRunAction={resolveAndRunPresetFromSelection}" in text
    assert "onResolveRunReportAction={resolveRunReportPresetFromSelection}" in text


def test_launcher_route_keeps_builder_and_presets_navigation_entrypoints():
    text = _read(LAUNCHER_ROUTE)
    assert "onRunPreset={() => typeof onNavigate === \"function\" && onNavigate(toPresets)}" in text
    assert "onBuildExperiment={() => {" in text
    assert "onStartGuidedBuilder" in text
    assert "onNavigate(toBuilder)" in text

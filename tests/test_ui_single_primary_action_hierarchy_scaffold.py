from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRESETS_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "presets_route.jsx"
LAUNCHER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "launcher_route.jsx"
LAUNCHER_CARD = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "features" / "launcher" / "LauncherCard.jsx"
BUILDER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "builder_route.jsx"
RUN_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "run_route.jsx"
REPORT_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "report_route.jsx"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_preset_detail_uses_single_primary_quick_success_action():
    text = _read(PRESETS_ROUTE)
    assert "className=\"route-action route-action-primary\" onClick={() => typeof onResolveRun === \"function\" && onResolveRun(item)}>Run preset</button>" in text
    assert "className=\"route-action route-action-secondary\" onClick={() => typeof onResolvePreset === \"function\" && onResolvePreset(item)}>Prepare preset</button>" in text
    assert "className=\"route-action route-action-secondary\" onClick={() => typeof onResolveRunReport === \"function\" && onResolveRunReport(item)}>Run preset + report</button>" in text


def test_legacy_and_tertiary_actions_are_demoted_consistently():
    joined = (
        _read(BUILDER_ROUTE)
        + _read(RUN_ROUTE)
        + _read(REPORT_ROUTE)
        + _read(PRESETS_ROUTE)
        + _read(LAUNCHER_ROUTE)
    )
    assert "route-action route-action-tertiary" in joined
    assert "Open Legacy Builder" in joined
    assert "Open Legacy Console" in joined
    assert "Open Legacy Results" in joined
    assert "Open Legacy Presets" in joined
    assert "More presets" in joined


def test_launcher_primary_hierarchy_is_owned_by_intent_cards():
    text = _read(LAUNCHER_CARD)
    assert 'tone === "dominant" ? "route-action route-action-primary" : "route-action route-action-secondary"' in text


def test_tertiary_action_styles_exist():
    css = _read(INDEX_CSS)
    assert ".route-action-tertiary" in css
    assert ".route-action-tertiary:hover" in css

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
PRESETS_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "presets_route.jsx"
BUILDER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "builder_route.jsx"
RUN_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "run_route.jsx"
REPORT_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "report_route.jsx"
CATALOG_HELP_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "catalog_help_route.jsx"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_routes_avoid_inline_style_except_lifecycle_width_meter():
    run_text = _read(RUN_ROUTE)
    report_text = _read(REPORT_ROUTE)
    presets_text = _read(PRESETS_ROUTE)
    builder_text = _read(BUILDER_ROUTE)
    catalog_help_text = _read(CATALOG_HELP_ROUTE)
    app_text = _read(INDEX_APP)
    assert 'style={{ width: `${lifecycleInstrument.progressPct}%` }}' in run_text
    assert 'style={{ width: `${lifecycleInstrument.progressPct}%` }}' in report_text
    assert "style={{" not in presets_text
    assert "style={{" not in builder_text
    assert "style={{" not in catalog_help_text
    assert "style={{" not in app_text


def test_theme_consistency_classes_exist_for_shell_and_preset_polish():
    text = _read(INDEX_CSS)
    assert ".shell-subtitle-compact" in text
    assert ".shell-nav-version-readout" in text
    assert ".preset-meta-row" in text
    assert ".preset-meta-row-signals" in text
    assert ".preset-action-step" in text
    assert ".phenomenon-scope-note" in text
    assert ".preset-quick-select-card" in text
    assert ".preset-quick-select-copy" in text

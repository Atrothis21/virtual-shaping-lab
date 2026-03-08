from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_PRIMITIVES = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "ui_primitives.jsx"
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
LAUNCHER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "launcher_route.jsx"
BUILDER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "builder_route.jsx"
RUN_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "run_route.jsx"
REPORT_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "report_route.jsx"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ui_primitives_export_shared_recovery_action_row():
    text = _read(UI_PRIMITIVES)
    assert "function RecoveryActionRow(" in text
    assert "Retry" in text
    assert "Go to presets" in text
    assert "Go to builder" in text
    assert "RecoveryActionRow," in text


def test_launcher_builder_run_report_use_shared_recovery_actions():
    text = (
        _read(LAUNCHER_ROUTE)
        + _read(BUILDER_ROUTE)
        + _read(RUN_ROUTE)
        + _read(REPORT_ROUTE)
    )
    assert "RecoveryActionRow" in text
    assert "onGoPresets" in text
    assert "onGoBuilder" in text


def test_route_wiring_passes_navigation_and_retry_for_recovery_rows():
    text = _read(INDEX_APP)
    assert "onRetryCatalog={refreshCatalog}" in text
    assert "onNavigate={navigateTo}" in text
    assert "routeKeys={{ presets: routes.presets.key, builder: routes.builder.key }}" in text
    assert "routeKeys={{ run: routes.run.key, presets: routes.presets.key, builder: routes.builder.key }}" in text


def test_recovery_action_styles_exist():
    text = _read(INDEX_CSS)
    assert ".route-recovery-actions" in text

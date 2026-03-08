from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_PRIMITIVES = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "ui_primitives.jsx"
BUILDER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "builder_route.jsx"
RUN_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "run_route.jsx"
REPORT_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "report_route.jsx"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ui_primitives_export_shared_constraint_components():
    text = _read(UI_PRIMITIVES)
    assert "function buildConstraintChips(" in text
    assert "function ConstraintStateChips(" in text
    assert "function ConstraintMessage(" in text
    assert "ConstraintStateChips," in text
    assert "ConstraintMessage," in text


def test_builder_uses_shared_constraint_components():
    text = _read(BUILDER_ROUTE)
    assert "VSLReact.uiPrimitives" in text
    assert "ConstraintStateChips" in text
    assert "ConstraintMessage" in text
    assert "classNamePrefix=\"builder-constraint\"" in text


def test_run_report_use_shared_constraint_badges_for_disabled_states():
    run_text = _read(RUN_ROUTE)
    report_text = _read(REPORT_ROUTE)
    assert "ConstraintStateChips" in run_text
    assert "classNamePrefix=\"route-constraint\"" in run_text
    assert "runConstraintState" in run_text
    assert "ConstraintStateChips" in report_text
    assert "classNamePrefix=\"route-constraint\"" in report_text
    assert "reportConstraintState" in report_text


def test_route_constraint_styles_exist():
    text = _read(INDEX_CSS)
    assert ".route-constraint-states" in text
    assert ".route-constraint-chip" in text
    assert ".route-constraint-chip.is-disabled" in text
    assert ".route-constraint-chip.is-warning" in text

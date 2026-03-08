from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
BUILDER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "builder_route.jsx"
PLAN_WORKFLOW = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "plan_workflow_service.js"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_builder_plan_resolve_errors_use_banner_and_inline_treatment():
    text = _read(INDEX_APP) + _read(BUILDER_ROUTE)
    assert "buildPlanResolveErrorView" in text
    assert "extractFieldHintsFromReason" in text
    assert "Plan validation failed" in text
    assert "Invalid fields:" in text
    assert "Retry Resolve" in text
    assert "plan-resolve-inline-error" in text


def test_builder_plan_resolve_errors_show_actionable_recovery_guidance():
    text = _read(INDEX_APP) + _read(BUILDER_ROUTE) + _read(PLAN_WORKFLOW)
    assert "Likely Fields:" in text
    assert "Recovery:" in text
    assert "Edit draft fields, revalidate, and retry plan resolution." in text
    assert "resolvePlanFromBuilderContext" in text


def test_builder_plan_resolve_inline_error_styles_exist():
    text = _read(INDEX_CSS)
    assert ".plan-resolve-inline-error" in text
    assert ".plan-resolve-inline-error code" in text
    assert ".plan-resolve-inline-error ul" in text


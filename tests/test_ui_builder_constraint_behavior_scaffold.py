from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSTRAINTS = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "builder_constraint_controls.js"
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
BUILDER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "builder_route.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_builder_constraint_module_exports_canonical_actions():
    text = _read(CONSTRAINTS)
    assert 'HIDE: "hide"' in text
    assert 'DISABLE: "disable"' in text
    assert 'WARN: "warn"' in text
    assert 'AUTO_CORRECT: "auto-correct"' in text
    assert "deriveBuilderConstraintState" in text
    assert "evaluateConstraintBehavior" in text
    assert "NON_SEMANTIC_AUTOCORRECT_FIELDS" in text
    assert "Semantic auto-correct blocked; explicit user update required." in text


def test_builder_constraints_are_catalog_derived_not_local_ad_hoc():
    text = _read(CONSTRAINTS)
    assert "catalogState.extensions" in text
    assert "extensions.protocols" in text
    assert "extensions.report_templates" in text


def test_builder_route_uses_shared_constraint_state_for_controls():
    text = _read(BUILDER_ROUTE)
    assert "builderConstraintControls" in text
    assert "deriveBuilderConstraintState" in text
    assert "evaluateConstraintBehavior" in text
    assert "protocolConstraint" in text
    assert "templateConstraint" in text
    assert "runModeConstraint" in text
    assert "advancedConstraint" in text
    assert "renderConstraintStates" in text
    assert "builder-constraint-states" in text
    assert "builder-constraint-chip" in text
    assert "autoCorrectBlocked" in text
    assert "builder-constraint-warning" in text
    assert "builder-constraint-note" in text


def test_builder_constraint_styles_exist():
    text = _read(INDEX_CSS)
    assert ".builder-constraint-warning" in text
    assert ".builder-constraint-note" in text
    assert ".builder-constraint-states" in text
    assert ".builder-constraint-chip" in text
    assert ".builder-constraint-chip.is-hidden" in text
    assert ".builder-constraint-chip.is-disabled" in text
    assert ".builder-constraint-chip.is-warning" in text
    assert ".builder-constraint-chip.is-autocorrect" in text
    assert ".builder-constraint-chip.is-blocked" in text

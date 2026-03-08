from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
BUILDER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "builder_route.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"
CONSTRAINTS = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "builder_constraint_controls.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_builder_route_shows_autocorrect_before_after_reason_and_undo():
    text = _read(BUILDER_ROUTE)
    assert "builder-autocorrect-notice" in text
    assert "Auto-correct applied:" in text
    assert "Before:" in text
    assert "After:" in text
    assert "Reason:" in text
    assert "Undo Auto-correct" in text


def test_builder_autocorrect_is_restricted_to_non_semantic_fields():
    text = _read(CONSTRAINTS)
    assert "NON_SEMANTIC_AUTOCORRECT_FIELDS" in text
    assert '"template_key"' in text
    assert "autoCorrectBlocked" in text


def test_builder_autocorrect_notice_styles_exist():
    text = _read(INDEX_CSS)
    assert ".builder-autocorrect-notice" in text
    assert ".builder-autocorrect-notice code" in text

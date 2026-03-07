from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"
FORM_SCHEMA = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "builder_form_schema.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_builder_route_has_scoped_section_layout():
    text = _read(INDEX_APP)
    schema_text = _read(FORM_SCHEMA)
    assert "builder-sections-grid" in text
    assert "Overview" in text
    assert "Protocol/Seed Selection" in schema_text
    assert "Phases" in schema_text
    assert "Runtime" in schema_text
    assert "Report" in schema_text
    assert "Advanced/Debug" in text


def test_builder_route_does_not_expose_raw_payload_editor_surface():
    text = _read(INDEX_APP)
    assert "Raw Payload" not in text
    assert "JSON editor" not in text


def test_builder_section_styles_exist():
    text = _read(INDEX_HTML)
    assert ".builder-sections-grid" in text
    assert ".builder-section-panel" in text
    assert ".builder-section-panel-muted" in text
    assert "border-style: dashed" in text
    assert "filter: saturate(0.72)" in text
    assert ".builder-section-header" in text
    assert ".builder-section-subheading" in text
    assert ".builder-section-index" in text
    assert ".builder-section-heading" in text
    assert ".builder-section-overview::before" in text
    assert ".builder-section-runtime::before" in text
    assert ".builder-section-report::before" in text
    assert ".builder-kv" in text
    assert ".builder-control-group" in text
    assert ".builder-readout" in text


def test_builder_sections_render_console_hierarchy_markers():
    text = _read(INDEX_APP)
    schema_text = _read(FORM_SCHEMA)
    assert "builder-section-overview" in text
    assert "builder-section-protocol" in schema_text
    assert "builder-section-phases" in schema_text
    assert "builder-section-runtime" in schema_text
    assert "builder-section-report" in schema_text
    assert "builder-section-advanced" in text
    assert "builder-section-index" in text
    assert "builder-control-group" in text
    assert "builder-readout" in text

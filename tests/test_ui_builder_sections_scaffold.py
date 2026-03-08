from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
BUILDER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "builder_route.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"
FORM_SCHEMA = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "builder_form_schema.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_builder_route_has_scoped_section_layout():
    text = _read(BUILDER_ROUTE)
    schema_text = _read(FORM_SCHEMA)
    assert "builder-sections-grid" in text
    assert "Overview" in text
    assert "Protocol/Seed Selection" in schema_text
    assert "Phases" in schema_text
    assert "Runtime" in schema_text
    assert "Report" in schema_text
    assert "Advanced/Debug" in text


def test_builder_route_does_not_expose_raw_payload_editor_surface():
    text = _read(BUILDER_ROUTE)
    assert "Raw Payload" not in text
    assert "JSON editor" not in text


def test_builder_section_styles_exist():
    text = _read(INDEX_CSS)
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
    assert ".builder-advanced-wrapper" in text
    assert ".builder-advanced-toggle" in text
    assert ".builder-advanced-content" in text
    assert ".builder-debug-summary" in text
    assert ".builder-debug-details-toggle" in text
    assert ".builder-debug-details" in text


def test_builder_sections_render_console_hierarchy_markers():
    text = _read(BUILDER_ROUTE)
    schema_text = _read(FORM_SCHEMA)
    assert "builder-section-overview" in text
    assert "builder-section-protocol" in schema_text
    assert "builder-section-phases" in schema_text
    assert "builder-section-runtime" in schema_text
    assert "builder-section-report" in schema_text
    assert "builder-section-advanced" in text
    assert "Show Advanced Diagnostics" in text
    assert "Hide Advanced Diagnostics" in text
    assert "builder-advanced-toggle" in text
    assert "builder-advanced-content" in text
    assert "builder-section-index" in text
    assert "builder-control-group" in text
    assert "builder-readout" in text


def test_builder_advanced_access_model_defaults_to_hidden():
    text = _read(BUILDER_ROUTE)
    assert "const [advancedVisible, setAdvancedVisible] = React.useState(false);" in text
    assert "const [debugDetailsVisible, setDebugDetailsVisible] = React.useState(false);" in text
    assert "aria-expanded={advancedVisible ? \"true\" : \"false\"}" in text
    assert "{advancedVisible ? (" in text
    assert "Show Debug Details" in text
    assert "Hide Debug Details" in text
    assert "render_cap_rows" in text
    assert "sample_every_n_ticks" in text
    assert "cap_policy: \"backend-cap-aware\"" in text

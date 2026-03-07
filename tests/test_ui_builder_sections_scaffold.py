from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_builder_route_has_scoped_section_layout():
    text = _read(INDEX_APP)
    assert "builder-sections-grid" in text
    assert "Overview" in text
    assert "Protocol/Seed Selection" in text
    assert "Phases" in text
    assert "Runtime" in text
    assert "Report" in text
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
    assert ".builder-section-heading" in text
    assert ".builder-kv" in text

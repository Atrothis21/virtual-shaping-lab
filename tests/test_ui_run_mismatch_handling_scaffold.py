from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_run_surface_has_provenance_view_model_and_mismatch_detection():
    text = _read(INDEX_APP)
    assert "selectRunProvenanceViewModel" in text
    assert "detectRunVersionMismatches" in text
    assert "record_schema_version" in text
    assert "template_version_used" in text
    assert "plan_hash" in text


def test_run_surface_uses_shared_banner_and_blocking_panel_for_mismatches():
    text = _read(INDEX_APP)
    assert "Version mismatch detected" in text
    assert "Incompatible data version" in text
    assert "GlobalBanner" in text
    assert "BlockingPanel" in text
    assert "Refresh Run Status" in text


def test_run_surface_renders_provenance_context():
    text = _read(INDEX_APP)
    assert "Run Provenance" in text
    assert "run_id:" in text
    assert "plan_hash:" in text
    assert "record_schema_version:" in text
    assert "template_version_used:" in text
    assert "next_actions:" in text


def test_run_provenance_styles_exist():
    text = _read(INDEX_HTML)
    assert ".run-provenance-summary" in text
    assert ".run-provenance-summary code" in text
    assert ".run-blocking-note" in text


from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FOUNDATION = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "ui_foundation_primitives.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_foundation_primitives_export_expected_components():
    text = _read(FOUNDATION)
    assert "function PageRegion" in text
    assert "function SurfacePanel" in text
    assert "function StatusBadge" in text
    assert "function PrimaryButton" in text
    assert "function SecondaryButton" in text
    assert "window.VSLReact.foundationPrimitives" in text


def test_index_css_defines_foundation_primitive_styles():
    text = _read(INDEX_HTML)
    assert ".vsl-page-region" in text
    assert ".vsl-surface-panel" in text
    assert ".vsl-status-badge" in text
    assert ".vsl-btn" in text
    assert ".vsl-btn-primary" in text
    assert ".vsl-btn-secondary" in text

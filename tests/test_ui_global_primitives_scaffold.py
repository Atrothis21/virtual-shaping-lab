from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_PRIMITIVES = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "ui_primitives.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ui_primitives_exports_shared_components():
    text = _read(UI_PRIMITIVES)
    assert "function NotificationStack" in text
    assert "function GlobalBanner" in text
    assert "function BlockingPanel" in text
    assert "window.VSLReact.uiPrimitives" in text


def test_ui_primitives_includes_catalog_mismatch_banner_helper():
    text = _read(UI_PRIMITIVES)
    assert "function buildCatalogMismatchBanner" in text
    assert 'versionMismatch.field !== "catalog_version"' in text
    assert "Catalog version mismatch detected" in text

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_builder_lazy_loading_has_explicit_fallback_retry_controls():
    text = _read(INDEX_APP)
    assert 'if (activeRoute === routes.builder.key) {' in text
    assert "Builder modules failed to load." in text
    assert "Loading builder modules..." in text
    assert "Retry" in text
    assert "Go to presets" in text


def test_builder_lazy_loading_resets_loading_state_when_route_changes():
    text = _read(INDEX_APP)
    assert "if (activeRoute === routes.builder.key) return;" in text
    assert "if (!prev.loading) return prev;" in text
    assert "return { ...prev, loading: false };" in text

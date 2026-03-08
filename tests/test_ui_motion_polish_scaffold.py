from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_motion_polish_transitions_exist_for_key_surfaces():
    text = _read(INDEX_CSS)
    assert ".route-card" in text
    assert ".global-banner" in text
    assert ".route-notice" in text
    assert ".route-state-panel" in text
    assert "transition: border-color 180ms ease" in text


def test_motion_polish_has_lifecycle_and_panel_reveal_animation():
    text = _read(INDEX_CSS)
    assert "@keyframes vsl-fade-slide-in" in text
    assert ".builder-advanced-content" in text
    assert ".builder-debug-details" in text
    assert "animation: vsl-fade-slide-in 180ms ease-out;" in text
    assert ".lifecycle-meter span" in text
    assert "transition: width 220ms ease-out;" in text


def test_motion_polish_respects_prefers_reduced_motion():
    text = _read(INDEX_CSS)
    assert "@media (prefers-reduced-motion: reduce)" in text
    assert "animation-duration: 0.01ms !important;" in text
    assert "transition-duration: 0.01ms !important;" in text

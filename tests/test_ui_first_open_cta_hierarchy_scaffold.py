from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_CARD = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "features" / "launcher" / "LauncherCard.jsx"
LAUNCHER_VIEW = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "features" / "launcher" / "LauncherView.jsx"
CSS = ROOT / "virtual_shaping_lab" / "ui" / "css" / "index.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_launcher_assigns_dominant_and_secondary_tones():
    view = _read(LAUNCHER_VIEW)
    assert 'tone="dominant"' in view
    assert 'title="Run a preset"' in view
    assert 'tone="secondary"' in view
    assert 'title="Build an experiment"' in view


def test_launcher_card_maps_tone_to_action_hierarchy_classes():
    card = _read(LAUNCHER_CARD)
    assert 'tone === "dominant" ? "route-action route-action-primary" : "route-action route-action-secondary"' in card
    assert "data-launcher-tone" in card


def test_css_defines_dominant_visual_priority():
    css = _read(CSS)
    assert ".launcher-card-dominant" in css
    assert ".launcher-card-secondary" in css
    assert "grid-column: span 2;" in css

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "virtual_shaping_lab" / "ui" / "js" / "react"
INDEX_APP = ROOT / "index_app.jsx"
LAUNCHER_VIEW = ROOT / "features" / "launcher" / "LauncherView.jsx"
LAUNCHER_ROUTE = ROOT / "routes" / "launcher_route.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_first_open_primary_nav_is_intent_scoped():
    text = _read(INDEX_APP)
    assert 'const PRIMARY_NAV_KEYS = ["home", "presets", "builder", "run", "report"];' in text
    assert "return ROUTES.home.key;" in text
    assert 'if (normalized.startsWith("#/home")) return ROUTES.home.key;' in text


def test_launcher_view_keeps_two_intent_cards_only():
    text = _read(LAUNCHER_VIEW)
    assert "title=\"Run a preset\"" in text
    assert "title=\"Build an experiment\"" in text
    assert "tone=\"dominant\"" in text
    assert "tone=\"secondary\"" in text
    # Guard against reintroducing dense launcher card walls.
    assert text.count("<LauncherCard") == 2


def test_launcher_route_keeps_first_open_density_caps():
    text = _read(LAUNCHER_ROUTE)
    assert "selectFeaturedPresetItems(catalogState, 4)" in text
    assert "buildRecentActivityItems(runState, reportState, 3)" in text
    assert "Featured presets" in text
    assert "Recent activity" in text


from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_CARD = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "features" / "launcher" / "LauncherCard.jsx"
LAUNCHER_VIEW = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "features" / "launcher" / "LauncherView.jsx"
LAUNCHER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "launcher_route.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_launcher_feature_modules_exist_and_register():
    card = _read(LAUNCHER_CARD)
    view = _read(LAUNCHER_VIEW)
    route = _read(LAUNCHER_ROUTE)

    assert "launcherFeature.LauncherCard" in card
    assert "launcherFeature.LauncherView" in view
    assert "routeContainers.LauncherRouteContainer" in route


def test_launcher_view_exposes_two_primary_intent_cards():
    view = _read(LAUNCHER_VIEW)
    assert "Run a preset" in view
    assert "Build an experiment" in view
    assert "LauncherCard" in view
    assert "actionLabel=\"Run preset\"" in view
    assert "actionLabel=\"Build experiment\"" in view


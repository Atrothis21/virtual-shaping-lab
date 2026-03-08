from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELECTOR = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "features" / "launcher" / "first_open_state_selector.js"
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
ROUTER_STATE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "router_state.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_first_open_selector_policy_is_explicit():
    text = _read(SELECTOR)
    assert "function selectFirstOpenState" in text
    assert "initialRouteKey: \"home\"" in text
    assert "showRecentStrip: recentItems.length > 0" in text
    assert "first-time/no-history: show launcher" in text
    assert "has recent activity: still show launcher with recent strip visible" in text


def test_index_app_consumes_first_open_selector_for_no_hash_boot():
    text = _read(INDEX_APP)
    assert "launcherFeature.selectFirstOpenState" in text
    assert "const currentHash = window.location.hash;" in text
    assert "if (currentHash) return parseRouteFromHash(currentHash);" in text
    assert "selectFirstOpenState({ recentItems: [], hasVisitedLauncher: false })" in text


def test_router_state_home_is_default_and_primary_nav_intent_exists():
    router = _read(ROUTER_STATE)
    index = _read(INDEX_APP)
    assert "home: { key: \"home\"" in router
    assert "return ROUTES.home.key;" in router
    assert "const PRIMARY_NAV_KEYS = [\"home\", \"presets\", \"builder\", \"run\", \"report\"];" in index


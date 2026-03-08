from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "launcher_route.jsx"
STATE_DOMAINS = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "state_domains.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_recent_activity_builder_enforces_cap_and_deterministic_ordering():
    text = _read(LAUNCHER_ROUTE)
    assert "function buildRecentActivityItems(runState, reportState, maxItems)" in text
    assert "const ranked = rows.sort((a, b) => {" in text
    assert "const timeDelta = Number(b.atMs || 0) - Number(a.atMs || 0);" in text
    assert "return String(a.key).localeCompare(String(b.key));" in text
    assert "return ranked.slice(0, cap);" in text
    assert "buildRecentActivityItems(runState, reportState, 3)" in text


def test_recent_activity_uses_run_and_report_timestamps():
    launcher = _read(LAUNCHER_ROUTE)
    state = _read(STATE_DOMAINS)
    assert "atMs: toEpochMs(runState.lastPollAtMs)" in launcher
    assert "toEpochMs(reportState.lastUpdatedAtMs)" in launcher
    assert "generated_at_ms" in launcher
    assert "lastUpdatedAtMs: null" in state
    assert "next[DOMAIN_KEYS.report].lastUpdatedAtMs = payload.atMs || Date.now();" in state

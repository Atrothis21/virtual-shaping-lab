from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
PRESETS_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "presets_route.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_preset_seed_builder_handoff_is_explicit():
    text = _read(INDEX_APP) + _read(PRESETS_ROUTE)
    assert "handleSeedToBuilder" in text
    assert "onSeedDraftFromPreset(item)" in text
    assert "onNavigate(keys.builder)" in text


def test_preset_seed_resolve_handoff_is_explicit():
    text = _read(INDEX_APP) + _read(PRESETS_ROUTE)
    assert "handleResolvePreset" in text
    assert "onNavigate(keys.run)" in text
    assert "handleResolveRunReport" in text
    assert "onNavigate(keys.report)" in text


def test_seed_uses_builder_draft_event_boundary():
    text = _read(INDEX_APP)
    assert "type: stateApi.UI_EVENTS.DRAFT_EDITED" in text
    assert "payload: { draft: draftSeed }" in text
    assert "buildConstrainedDraftSeedFromPreset(presetItem)" in text


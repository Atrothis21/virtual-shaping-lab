from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_presets_route_has_catalog_view_model_selector():
    text = _read(INDEX_APP)
    assert "function selectPresetCatalogViewModel" in text
    assert "extensions.phenomena" in text
    assert "expectedSignals" in text
    assert "defaultTemplate" in text
    assert "runModes" in text
    assert "getSignalSemanticTone" in text
    assert "getProtocolAccentTone" in text
    assert "PresetSignalChips" in text


def test_presets_route_has_browser_controls():
    text = _read(INDEX_APP)
    assert "function PresetsRouteContainer" in text
    assert "Search" in text
    assert "Run Mode" in text
    assert "Sort" in text
    assert "setSearchQuery" in text
    assert "setRunModeFilter" in text
    assert "setSortBy" in text
    assert "filter((item)" in text
    assert "localeCompare" in text


def test_presets_route_renders_grid_component():
    text = _read(INDEX_APP)
    assert "function PresetBrowserGrid" in text
    assert "Use In Builder" in text
    assert "Open Legacy Presets" in text
    assert "onUseInBuilder(item)" in text
    assert "accent-${getProtocolAccentTone(item.protocolKey)}" in text
    assert "vsl-status-badge semantic" in text


def test_presets_route_has_detail_panel_and_primary_actions():
    text = _read(INDEX_APP)
    assert "function PresetDetailPanel" in text
    assert "Preset Detail" in text
    assert "Resolve Preset" in text
    assert "Resolve + Run" in text
    assert "Resolve + Run + Report" in text
    assert "onResolvePreset(item)" in text
    assert "onResolveRun(item)" in text
    assert "onResolveRunReport(item)" in text
    assert "setSelectedPresetKey" in text
    assert "selectedPreset" in text
    assert "Preset Key:" in text


def test_presets_route_has_seeded_draft_initialization_handoff():
    text = _read(INDEX_APP)
    assert "buildConstrainedDraftSeedFromPreset" in text
    assert "seed_source: \"preset-catalog\"" in text
    assert "seedDraftFromPreset" in text
    assert "stateApi.UI_EVENTS.DRAFT_EDITED" in text
    assert "onSeedDraftFromPreset={seedDraftFromPreset}" in text
    assert "onNavigate={navigateTo}" in text
    assert "Seeded: ${seed.seed_source}" in text


def test_presets_route_wires_resolve_and_run_actions_to_api():
    text = _read(INDEX_APP)
    assert "buildPresetApiPayload" in text
    assert "apiClient.postJson(\"plan\", payload)" in text
    assert "apiClient.postJson(\"run\", runPayload)" in text
    assert "resolvePresetFromSelection" in text
    assert "resolveAndRunPresetFromSelection" in text
    assert "stateApi.UI_EVENTS.PLAN_RESOLVE_REQUESTED" in text
    assert "stateApi.UI_EVENTS.PLAN_RESOLVE_SUCCEEDED" in text
    assert "stateApi.UI_EVENTS.PLAN_RESOLVE_FAILED" in text
    assert "stateApi.UI_EVENTS.RUN_START_REQUESTED" in text
    assert "stateApi.UI_EVENTS.RUN_START_SUCCEEDED" in text
    assert "stateApi.UI_EVENTS.RUN_START_FAILED" in text


def test_presets_route_renders_action_level_status_and_errors():
    text = _read(INDEX_APP)
    assert "Action Status:" in text
    assert "presetActionState" in text
    assert "Preset plan resolve failed." in text
    assert "Preset run failed." in text


def test_presets_route_has_lightweight_phenomenon_support_panel():
    text = _read(INDEX_APP)
    assert "function PhenomenonSupportPanel" in text
    assert "Phenomenon Support" in text
    assert "metadata-only" in text
    assert "Expected Signals:" in text
    assert "lightweight support surface" in text
    assert "Support Mode:" in text
    assert "setup-guidance" in text
    assert "signal_count" in text
    assert "PresetSignalChips signals={item.expectedSignals}" in text


def test_index_css_has_presets_browser_layout_styles():
    text = _read(INDEX_HTML)
    assert ".preset-controls" in text
    assert ".preset-grid" in text
    assert ".preset-card" in text
    assert ".preset-detail" in text
    assert ".phenomenon-support" in text
    assert ".phenomenon-signal-list" in text
    assert ".preset-detail-selectors" in text
    assert ".preset-action-status" in text
    assert ".preset-action-message" in text
    assert ".preset-action-error" in text
    assert ".vsl-status-badge.semantic.cs-plus" in text
    assert ".preset-card::before" in text
    assert ".preset-card.accent-cs-plus::before" in text
    assert ".preset-signal-chip-row" in text
    assert ".preset-signal-chip.cs-plus" in text
    assert ".preset-meta-line" in text
    assert ".phenomenon-support::before" in text
    assert ".phenomenon-support.accent-cs-plus::before" in text
    assert ".phenomenon-meta-line" in text

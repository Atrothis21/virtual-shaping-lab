from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_DOMAINS_JS = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "state_domains.js"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_state_domains_module_defines_required_domain_keys():
    text = _read(STATE_DOMAINS_JS)
    assert 'builderDraft: "builderDraftState"' in text
    assert 'plan: "planState"' in text
    assert 'run: "runState"' in text
    assert 'report: "reportState"' in text
    assert 'catalogCache: "catalogCacheState"' in text
    assert 'debugAdvanced: "debugAdvancedState"' in text


def test_state_domains_exports_initializers_and_selectors():
    text = _read(STATE_DOMAINS_JS)
    assert "UI_EVENTS" in text
    assert "createInitialUIState" in text
    assert "createBuilderDraftState" in text
    assert "createPlanState" in text
    assert "createRunState" in text
    assert "createReportState" in text
    assert "createCatalogCacheState" in text
    assert "createDebugAdvancedState" in text
    assert "selectBuilderDraftState" in text
    assert "selectPlanState" in text
    assert "selectRunState" in text
    assert "selectReportState" in text
    assert "selectCatalogCacheState" in text
    assert "selectDebugAdvancedState" in text
    assert "applyUIEvent" in text
    assert "isPlanFreshForCurrentDraft" in text
    assert "canRunFromState" in text


def test_state_domains_script_is_loaded_before_index_app():
    html = _read(INDEX_HTML)
    state_idx = html.find('/ui/js/react/state_domains.js')
    app_idx = html.find('/ui/js/react/index_app.jsx')
    assert state_idx != -1
    assert app_idx != -1
    assert state_idx < app_idx


def test_index_app_uses_state_domain_initializer():
    text = _read(INDEX_APP)
    assert "window.VSLReact.stateDomains" in text
    assert "createInitialUIState()" in text


def test_state_domains_defines_core_transition_events():
    text = _read(STATE_DOMAINS_JS)
    assert 'DRAFT_EDITED: "DRAFT_EDITED"' in text
    assert 'PLAN_RESOLVE_SUCCEEDED: "PLAN_RESOLVE_SUCCEEDED"' in text
    assert 'RUN_START_SUCCEEDED: "RUN_START_SUCCEEDED"' in text
    assert 'REPORT_SUCCEEDED: "REPORT_SUCCEEDED"' in text
    assert 'CATALOG_REFRESH_SUCCEEDED: "CATALOG_REFRESH_SUCCEEDED"' in text


def test_state_domains_encodes_plan_invalidation_and_reset_semantics():
    text = _read(STATE_DOMAINS_JS)
    # Draft edits invalidate resolved plan and report readiness.
    assert "if (type === UI_EVENTS.DRAFT_EDITED)" in text
    assert 'next[DOMAIN_KEYS.plan].resolvedPlan = null;' in text
    assert 'next[DOMAIN_KEYS.plan].stableHash = "";' in text
    assert 'next[DOMAIN_KEYS.plan].isFreshForDraftVersion = null;' in text
    assert 'next[DOMAIN_KEYS.report].reportData = null;' in text
    # New run start resets report context.
    assert "if (type === UI_EVENTS.RUN_START_SUCCEEDED)" in text
    assert 'next[DOMAIN_KEYS.report].runId = "";' in text
    assert 'next[DOMAIN_KEYS.report].requestStatus = "idle";' in text


def test_state_domains_exposes_freshness_gates_for_run_report_actions():
    text = _read(STATE_DOMAINS_JS)
    assert "function isPlanFreshForCurrentDraft(state)" in text
    assert "function canRunFromState(state)" in text
    assert "plan.isFreshForDraftVersion === draft.draftVersion" in text


def test_state_domains_encodes_catalog_drift_plan_invalidation():
    text = _read(STATE_DOMAINS_JS)
    assert "hasVersionDrift" in text
    assert 'field: "catalog_version"' in text
    assert "if (hasVersionDrift)" in text
    assert 'next[DOMAIN_KEYS.plan].resolvedPlan = null;' in text

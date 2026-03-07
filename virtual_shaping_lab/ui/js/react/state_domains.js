window.VSLReact = window.VSLReact || {};

const DOMAIN_KEYS = Object.freeze({
  builderDraft: "builderDraftState",
  plan: "planState",
  run: "runState",
  report: "reportState",
  catalogCache: "catalogCacheState",
  debugAdvanced: "debugAdvancedState",
});

const OWNERSHIP = Object.freeze({
  LOCAL: "local-authoritative",
  SERVER: "server-derived",
  DERIVED: "derived-transient",
});

const UI_EVENTS = Object.freeze({
  DRAFT_EDITED: "DRAFT_EDITED",
  DRAFT_VALIDATION_UPDATED: "DRAFT_VALIDATION_UPDATED",
  PLAN_RESOLVE_REQUESTED: "PLAN_RESOLVE_REQUESTED",
  PLAN_RESOLVE_SUCCEEDED: "PLAN_RESOLVE_SUCCEEDED",
  PLAN_RESOLVE_FAILED: "PLAN_RESOLVE_FAILED",
  RUN_START_REQUESTED: "RUN_START_REQUESTED",
  RUN_START_SUCCEEDED: "RUN_START_SUCCEEDED",
  RUN_START_FAILED: "RUN_START_FAILED",
  RUN_STATUS_UPDATED: "RUN_STATUS_UPDATED",
  REPORT_REQUESTED: "REPORT_REQUESTED",
  REPORT_SUCCEEDED: "REPORT_SUCCEEDED",
  REPORT_FAILED: "REPORT_FAILED",
  CATALOG_REFRESH_REQUESTED: "CATALOG_REFRESH_REQUESTED",
  CATALOG_REFRESH_SUCCEEDED: "CATALOG_REFRESH_SUCCEEDED",
  CATALOG_REFRESH_FAILED: "CATALOG_REFRESH_FAILED",
});

function createBuilderDraftState() {
  return {
    ownership: OWNERSHIP.LOCAL,
    draft: null,
    draftVersion: 0,
    validationErrors: [],
    isReady: false,
    dirty: false,
  };
}

function createPlanState() {
  return {
    ownership: OWNERSHIP.SERVER,
    requestStatus: "idle",
    resolvedPlan: null,
    stableHash: "",
    isFreshForDraftVersion: null,
    lastError: null,
  };
}

function createRunState() {
  return {
    ownership: OWNERSHIP.SERVER,
    requestStatus: "idle",
    activeRunId: "",
    lifecycleState: "idle",
    runData: null,
    lastPollAtMs: null,
    lastError: null,
  };
}

function createReportState() {
  return {
    ownership: OWNERSHIP.SERVER,
    requestStatus: "idle",
    runId: "",
    reportData: null,
    selectedView: "summary",
    lastError: null,
  };
}

function createCatalogCacheState() {
  return {
    ownership: OWNERSHIP.SERVER,
    requestStatus: "idle",
    extensions: null,
    versions: {
      catalog_version: null,
      record_schema_version: null,
      template_version_used: null,
    },
    fetchedAtMs: null,
    isStale: false,
    versionMismatch: null,
    lastError: null,
  };
}

function createDebugAdvancedState() {
  return {
    ownership: OWNERSHIP.LOCAL,
    visible: false,
    mode: "off",
    maxRows: 200,
    sampled: false,
    sampleEveryNTicks: null,
  };
}

function createInitialUIState() {
  return {
    [DOMAIN_KEYS.builderDraft]: createBuilderDraftState(),
    [DOMAIN_KEYS.plan]: createPlanState(),
    [DOMAIN_KEYS.run]: createRunState(),
    [DOMAIN_KEYS.report]: createReportState(),
    [DOMAIN_KEYS.catalogCache]: createCatalogCacheState(),
    [DOMAIN_KEYS.debugAdvanced]: createDebugAdvancedState(),
  };
}

function cloneState(state) {
  return {
    ...state,
    [DOMAIN_KEYS.builderDraft]: { ...state[DOMAIN_KEYS.builderDraft] },
    [DOMAIN_KEYS.plan]: { ...state[DOMAIN_KEYS.plan] },
    [DOMAIN_KEYS.run]: { ...state[DOMAIN_KEYS.run] },
    [DOMAIN_KEYS.report]: { ...state[DOMAIN_KEYS.report] },
    [DOMAIN_KEYS.catalogCache]: {
      ...state[DOMAIN_KEYS.catalogCache],
      versions: { ...(state[DOMAIN_KEYS.catalogCache].versions || {}) },
    },
    [DOMAIN_KEYS.debugAdvanced]: { ...state[DOMAIN_KEYS.debugAdvanced] },
  };
}

function isRunTerminal(lifecycleState) {
  return lifecycleState === "completed" || lifecycleState === "failed";
}

function applyUIEvent(prevState, event) {
  const current = prevState || createInitialUIState();
  const next = cloneState(current);
  const type = event && event.type ? event.type : "";
  const payload = event && event.payload ? event.payload : {};

  if (type === UI_EVENTS.DRAFT_EDITED) {
    next[DOMAIN_KEYS.builderDraft].dirty = true;
    next[DOMAIN_KEYS.builderDraft].draft = payload.draft || next[DOMAIN_KEYS.builderDraft].draft;
    next[DOMAIN_KEYS.builderDraft].draftVersion += 1;
    next[DOMAIN_KEYS.plan].resolvedPlan = null;
    next[DOMAIN_KEYS.plan].stableHash = "";
    next[DOMAIN_KEYS.plan].isFreshForDraftVersion = null;
    next[DOMAIN_KEYS.plan].requestStatus = "idle";
    next[DOMAIN_KEYS.report].runId = "";
    next[DOMAIN_KEYS.report].reportData = null;
    next[DOMAIN_KEYS.report].requestStatus = "idle";
    return next;
  }

  if (type === UI_EVENTS.DRAFT_VALIDATION_UPDATED) {
    next[DOMAIN_KEYS.builderDraft].validationErrors = Array.isArray(payload.validationErrors)
      ? payload.validationErrors
      : [];
    next[DOMAIN_KEYS.builderDraft].isReady = Boolean(payload.isReady);
    return next;
  }

  if (type === UI_EVENTS.PLAN_RESOLVE_REQUESTED) {
    next[DOMAIN_KEYS.plan].requestStatus = "loading";
    next[DOMAIN_KEYS.plan].lastError = null;
    return next;
  }

  if (type === UI_EVENTS.PLAN_RESOLVE_SUCCEEDED) {
    next[DOMAIN_KEYS.plan].requestStatus = "success";
    next[DOMAIN_KEYS.plan].resolvedPlan = payload.resolvedPlan || null;
    next[DOMAIN_KEYS.plan].stableHash = payload.stableHash || "";
    next[DOMAIN_KEYS.plan].isFreshForDraftVersion = next[DOMAIN_KEYS.builderDraft].draftVersion;
    return next;
  }

  if (type === UI_EVENTS.PLAN_RESOLVE_FAILED) {
    next[DOMAIN_KEYS.plan].requestStatus = "error";
    next[DOMAIN_KEYS.plan].lastError = payload.error || null;
    return next;
  }

  if (type === UI_EVENTS.RUN_START_REQUESTED) {
    next[DOMAIN_KEYS.run].requestStatus = "loading";
    next[DOMAIN_KEYS.run].lastError = null;
    return next;
  }

  if (type === UI_EVENTS.RUN_START_SUCCEEDED) {
    next[DOMAIN_KEYS.run].requestStatus = "success";
    next[DOMAIN_KEYS.run].activeRunId = payload.runId || "";
    next[DOMAIN_KEYS.run].lifecycleState = payload.lifecycleState || "running";
    next[DOMAIN_KEYS.run].runData = payload.runData || null;
    next[DOMAIN_KEYS.run].lastPollAtMs = payload.atMs || Date.now();
    next[DOMAIN_KEYS.report].runId = "";
    next[DOMAIN_KEYS.report].reportData = null;
    next[DOMAIN_KEYS.report].requestStatus = "idle";
    return next;
  }

  if (type === UI_EVENTS.RUN_START_FAILED) {
    next[DOMAIN_KEYS.run].requestStatus = "error";
    next[DOMAIN_KEYS.run].lastError = payload.error || null;
    return next;
  }

  if (type === UI_EVENTS.RUN_STATUS_UPDATED) {
    next[DOMAIN_KEYS.run].runData = payload.runData || next[DOMAIN_KEYS.run].runData;
    next[DOMAIN_KEYS.run].lifecycleState = payload.lifecycleState || next[DOMAIN_KEYS.run].lifecycleState;
    next[DOMAIN_KEYS.run].lastPollAtMs = payload.atMs || Date.now();
    if (isRunTerminal(next[DOMAIN_KEYS.run].lifecycleState)) {
      next[DOMAIN_KEYS.run].requestStatus = "success";
    }
    return next;
  }

  if (type === UI_EVENTS.REPORT_REQUESTED) {
    next[DOMAIN_KEYS.report].requestStatus = "loading";
    next[DOMAIN_KEYS.report].lastError = null;
    next[DOMAIN_KEYS.report].runId = payload.runId || next[DOMAIN_KEYS.run].activeRunId || "";
    return next;
  }

  if (type === UI_EVENTS.REPORT_SUCCEEDED) {
    next[DOMAIN_KEYS.report].requestStatus = "success";
    next[DOMAIN_KEYS.report].runId = payload.runId || next[DOMAIN_KEYS.report].runId;
    next[DOMAIN_KEYS.report].reportData = payload.reportData || null;
    return next;
  }

  if (type === UI_EVENTS.REPORT_FAILED) {
    next[DOMAIN_KEYS.report].requestStatus = "error";
    next[DOMAIN_KEYS.report].lastError = payload.error || null;
    return next;
  }

  if (type === UI_EVENTS.CATALOG_REFRESH_REQUESTED) {
    next[DOMAIN_KEYS.catalogCache].requestStatus = "loading";
    next[DOMAIN_KEYS.catalogCache].lastError = null;
    return next;
  }

  if (type === UI_EVENTS.CATALOG_REFRESH_SUCCEEDED) {
    const previousVersions = next[DOMAIN_KEYS.catalogCache].versions || {};
    const nextVersions = payload.versions || {};
    const hasVersionDrift =
      previousVersions.catalog_version != null &&
      nextVersions.catalog_version != null &&
      previousVersions.catalog_version !== nextVersions.catalog_version;
    next[DOMAIN_KEYS.catalogCache].requestStatus = "success";
    next[DOMAIN_KEYS.catalogCache].extensions = payload.extensions || null;
    next[DOMAIN_KEYS.catalogCache].versions = {
      ...previousVersions,
      ...nextVersions,
    };
    next[DOMAIN_KEYS.catalogCache].fetchedAtMs = payload.atMs || Date.now();
    next[DOMAIN_KEYS.catalogCache].isStale = false;
    next[DOMAIN_KEYS.catalogCache].versionMismatch = hasVersionDrift
      ? {
          field: "catalog_version",
          expected: previousVersions.catalog_version,
          received: nextVersions.catalog_version,
        }
      : null;
    if (hasVersionDrift) {
      next[DOMAIN_KEYS.plan].resolvedPlan = null;
      next[DOMAIN_KEYS.plan].stableHash = "";
      next[DOMAIN_KEYS.plan].isFreshForDraftVersion = null;
    }
    return next;
  }

  if (type === UI_EVENTS.CATALOG_REFRESH_FAILED) {
    next[DOMAIN_KEYS.catalogCache].requestStatus = "error";
    next[DOMAIN_KEYS.catalogCache].lastError = payload.error || null;
    next[DOMAIN_KEYS.catalogCache].isStale = true;
    return next;
  }

  return current;
}

function isPlanFreshForCurrentDraft(state) {
  const plan = selectPlanState(state);
  const draft = selectBuilderDraftState(state);
  if (!plan || !draft) return false;
  return plan.isFreshForDraftVersion != null && plan.isFreshForDraftVersion === draft.draftVersion;
}

function canRunFromState(state) {
  const plan = selectPlanState(state);
  const draft = selectBuilderDraftState(state);
  return Boolean(
    plan &&
    draft &&
    plan.requestStatus === "success" &&
    plan.stableHash &&
    plan.isFreshForDraftVersion === draft.draftVersion
  );
}

function selectBuilderDraftState(state) {
  return state ? state[DOMAIN_KEYS.builderDraft] : undefined;
}

function selectPlanState(state) {
  return state ? state[DOMAIN_KEYS.plan] : undefined;
}

function selectRunState(state) {
  return state ? state[DOMAIN_KEYS.run] : undefined;
}

function selectReportState(state) {
  return state ? state[DOMAIN_KEYS.report] : undefined;
}

function selectCatalogCacheState(state) {
  return state ? state[DOMAIN_KEYS.catalogCache] : undefined;
}

function selectDebugAdvancedState(state) {
  return state ? state[DOMAIN_KEYS.debugAdvanced] : undefined;
}

window.VSLReact.stateDomains = {
  DOMAIN_KEYS,
  OWNERSHIP,
  UI_EVENTS,
  createInitialUIState,
  createBuilderDraftState,
  createPlanState,
  createRunState,
  createReportState,
  createCatalogCacheState,
  createDebugAdvancedState,
  applyUIEvent,
  isPlanFreshForCurrentDraft,
  canRunFromState,
  selectBuilderDraftState,
  selectPlanState,
  selectRunState,
  selectReportState,
  selectCatalogCacheState,
  selectDebugAdvancedState,
};

const TAB_KEYS = ["plan", "run", "report"];
const RUN_POLL_INTERVAL_MS = 1500;
const {
  REQUEST_STATUS,
  makeRequestState,
  requestLoading,
  requestSuccess,
  requestError,
  ErrorEnvelopePanel,
} = window.VSLReact;

const UI_LIFECYCLE = {
  PLAN_DRAFT: "PlanDraft",
  PLAN_RESOLVED: "PlanResolved",
  RUN_IN_PROGRESS: "RunInProgress",
  RUN_COMPLETE: "RunComplete",
  REPORT_COMPLETE: "ReportComplete",
};

const UI_LIFECYCLE_EVENT = {
  PLAN_EDITED: "PLAN_EDITED",
  PLAN_RESOLVED: "PLAN_RESOLVED",
  RUN_STARTED: "RUN_STARTED",
  RUN_COMPLETED: "RUN_COMPLETED",
  REPORT_COMPLETED: "REPORT_COMPLETED",
};

const UI_LIFECYCLE_TRANSITIONS = {
  [UI_LIFECYCLE.PLAN_DRAFT]: {
    [UI_LIFECYCLE_EVENT.PLAN_EDITED]: UI_LIFECYCLE.PLAN_DRAFT,
    [UI_LIFECYCLE_EVENT.PLAN_RESOLVED]: UI_LIFECYCLE.PLAN_RESOLVED,
  },
  [UI_LIFECYCLE.PLAN_RESOLVED]: {
    [UI_LIFECYCLE_EVENT.PLAN_EDITED]: UI_LIFECYCLE.PLAN_DRAFT,
    [UI_LIFECYCLE_EVENT.PLAN_RESOLVED]: UI_LIFECYCLE.PLAN_RESOLVED,
    [UI_LIFECYCLE_EVENT.RUN_STARTED]: UI_LIFECYCLE.RUN_IN_PROGRESS,
  },
  [UI_LIFECYCLE.RUN_IN_PROGRESS]: {
    [UI_LIFECYCLE_EVENT.PLAN_EDITED]: UI_LIFECYCLE.PLAN_DRAFT,
    [UI_LIFECYCLE_EVENT.RUN_COMPLETED]: UI_LIFECYCLE.RUN_COMPLETE,
  },
  [UI_LIFECYCLE.RUN_COMPLETE]: {
    [UI_LIFECYCLE_EVENT.PLAN_EDITED]: UI_LIFECYCLE.PLAN_DRAFT,
    [UI_LIFECYCLE_EVENT.RUN_STARTED]: UI_LIFECYCLE.RUN_IN_PROGRESS,
    [UI_LIFECYCLE_EVENT.REPORT_COMPLETED]: UI_LIFECYCLE.REPORT_COMPLETE,
  },
  [UI_LIFECYCLE.REPORT_COMPLETE]: {
    [UI_LIFECYCLE_EVENT.PLAN_EDITED]: UI_LIFECYCLE.PLAN_DRAFT,
    [UI_LIFECYCLE_EVENT.RUN_STARTED]: UI_LIFECYCLE.RUN_IN_PROGRESS,
    [UI_LIFECYCLE_EVENT.REPORT_COMPLETED]: UI_LIFECYCLE.REPORT_COMPLETE,
  },
};

const TERMINAL_RUN_STATES = new Set([
  "completed",
  "complete",
  "failed",
  "error",
  "cancelled",
  "canceled",
  "report_complete",
]);

function transitionLifecycle(currentState, eventName) {
  const from = UI_LIFECYCLE_TRANSITIONS[currentState] || {};
  return from[eventName] || currentState;
}

function canResolvePlan(lifecycleState) {
  return lifecycleState !== UI_LIFECYCLE.RUN_IN_PROGRESS;
}

function canRunLifecycle(lifecycleState) {
  return lifecycleState === UI_LIFECYCLE.PLAN_RESOLVED || lifecycleState === UI_LIFECYCLE.RUN_COMPLETE || lifecycleState === UI_LIFECYCLE.REPORT_COMPLETE;
}

function canCreateReportLifecycle(lifecycleState) {
  return lifecycleState === UI_LIFECYCLE.RUN_COMPLETE || lifecycleState === UI_LIFECYCLE.REPORT_COMPLETE;
}

function createLifecycleStore(lifecycleState, transition) {
  return {
    state: lifecycleState,
    canResolvePlan: canResolvePlan(lifecycleState),
    canRun: canRunLifecycle(lifecycleState),
    canCreateReport: canCreateReportLifecycle(lifecycleState),
    markPlanEdited: () => transition(UI_LIFECYCLE_EVENT.PLAN_EDITED),
    markPlanResolved: () => transition(UI_LIFECYCLE_EVENT.PLAN_RESOLVED),
    markRunStarted: () => transition(UI_LIFECYCLE_EVENT.RUN_STARTED),
    markRunCompleted: () => transition(UI_LIFECYCLE_EVENT.RUN_COMPLETED),
    markReportCompleted: () => transition(UI_LIFECYCLE_EVENT.REPORT_COMPLETED),
  };
}

const DEFAULT_PLAN_DRAFT = JSON.stringify(
  {
    experiment: {
      learner: "rescorla_wagner",
      agent: "classical_agent",
      representation: {
        name: "vector_elemental",
        params: { stimuli: ["tone"], max_compound_size: 2 },
      },
      phases: [
        {
          name: "Acquisition",
          protocol: "acquisition",
          stimuli: { cs_plus: ["tone"] },
          params: { n_trials: 20, alpha: 0.2, gamma: 0.0 },
        },
      ],
    },
    report: { preset: "acquisition" },
  },
  null,
  2
);

const LIFECYCLE_PRESETS = {
  acquisition_demo: {
    label: "Acquisition Demo",
    payload: JSON.parse(DEFAULT_PLAN_DRAFT),
  },
  extinction_demo: {
    label: "Extinction Demo",
    payload: {
      experiment: {
        learner: "rescorla_wagner",
        agent: "classical_agent",
        representation: {
          name: "vector_elemental",
          params: { stimuli: ["tone"], max_compound_size: 2 },
        },
        phases: [
          {
            name: "Acquisition",
            protocol: "acquisition",
            stimuli: { cs_plus: ["tone"] },
            params: { n_trials: 20, alpha: 0.2, gamma: 0.0 },
          },
          {
            name: "Extinction",
            protocol: "extinction",
            stimuli: { cs_plus: ["tone"] },
            params: { n_trials: 20, alpha: 0.2, gamma: 0.0 },
          },
        ],
      },
      report: { preset: "extinction" },
    },
  },
};

function normalizeTab(tab) {
  const key = String(tab || "").toLowerCase().trim();
  return TAB_KEYS.includes(key) ? key : "plan";
}

function getTabFromHash() {
  const raw = window.location.hash.replace(/^#\/?/, "");
  return normalizeTab(raw);
}

function tabLabel(tab) {
  if (tab === "plan") return "Plan";
  if (tab === "run") return "Run";
  return "Report";
}

function Panel({ tab }) {
  const endpointByTab = {
    plan: "POST /plan",
    run: "POST /run + GET /runs/{run_id}",
    report: "POST /runs/{run_id}/report",
  };
  const noteByTab = {
    plan: "Resolve payload drafts into stable, hashable plans.",
    run: "Create runs and track lifecycle progression.",
    report: "Generate report artifacts and provenance output.",
  };

  return (
    <div className="panel">
      <h2>{tabLabel(tab)} Console</h2>
      <p>{noteByTab[tab]}</p>
      <div className="api-card">
        <div><strong>Primary Endpoint:</strong></div>
        <code>{endpointByTab[tab]}</code>
      </div>
    </div>
  );
}

function updateDraftField(draft, updater) {
  try {
    const payload = JSON.parse(draft);
    const nextPayload = updater(payload);
    return {
      ok: true,
      value: JSON.stringify(nextPayload, null, 2),
    };
  } catch (_err) {
    return { ok: false };
  }
}

function clonePayload(payload) {
  return JSON.parse(JSON.stringify(payload));
}

function PlanPane({
  draft,
  setDraft,
  resolveState,
  onResolve,
  onPresetSelect,
  onPresetResolveRun,
  onPresetResolveRunReport,
  presetKey,
  setPresetKey,
  presetFlowState,
  catalogExtensions,
  lifecycle,
}) {
  const resolveData = resolveState.data || null;
  const stableHash = resolveData && resolveData.stable_hash ? resolveData.stable_hash : "";
  const resolvedPlan = resolveData && resolveData.plan ? resolveData.plan : null;
  const summary = React.useMemo(() => summarizePlan(resolvedPlan), [resolvedPlan]);
  const protocols = catalogExtensions && Array.isArray(catalogExtensions.protocols) ? catalogExtensions.protocols : [];
  const learners = catalogExtensions && Array.isArray(catalogExtensions.learners) ? catalogExtensions.learners : [];
  const policies = catalogExtensions && Array.isArray(catalogExtensions.policies) ? catalogExtensions.policies : [];
  const representations =
    catalogExtensions && Array.isArray(catalogExtensions.representations)
      ? catalogExtensions.representations
      : [];
  const presetEntries = Object.entries(LIFECYCLE_PRESETS);

  function setProtocol(protocolName) {
    const updated = updateDraftField(draft, (payload) => {
      const next = { ...payload };
      const experiment = { ...(next.experiment || {}) };
      const phases = Array.isArray(experiment.phases) ? [...experiment.phases] : [];
      if (phases.length === 0) {
        phases.push({ name: "Phase 1", protocol: protocolName, params: {}, stimuli: {} });
      } else {
        phases[0] = { ...(phases[0] || {}), protocol: protocolName };
      }
      experiment.phases = phases;
      next.experiment = experiment;
      return next;
    });
    if (updated.ok) setDraft(updated.value);
  }

  function setLearner(learnerName) {
    const updated = updateDraftField(draft, (payload) => {
      const next = { ...payload };
      const experiment = { ...(next.experiment || {}), learner: learnerName };
      next.experiment = experiment;
      return next;
    });
    if (updated.ok) setDraft(updated.value);
  }

  function setPolicy(policyName) {
    const updated = updateDraftField(draft, (payload) => {
      const next = { ...payload };
      const experiment = { ...(next.experiment || {}), policy: policyName };
      next.experiment = experiment;
      return next;
    });
    if (updated.ok) setDraft(updated.value);
  }

  function setRepresentation(reprName) {
    const updated = updateDraftField(draft, (payload) => {
      const next = { ...payload };
      const experiment = { ...(next.experiment || {}) };
      const representation = { ...(experiment.representation || {}), name: reprName };
      experiment.representation = representation;
      next.experiment = experiment;
      return next;
    });
    if (updated.ok) setDraft(updated.value);
  }

  const parsedDraft = React.useMemo(() => {
    try {
      return JSON.parse(draft);
    } catch (_err) {
      return null;
    }
  }, [draft]);
  const phaseRows =
    parsedDraft &&
    parsedDraft.experiment &&
    Array.isArray(parsedDraft.experiment.phases)
      ? parsedDraft.experiment.phases
      : [];

  function mutatePhases(mutator) {
    const updated = updateDraftField(draft, (payload) => {
      const next = { ...payload };
      const experiment = { ...(next.experiment || {}) };
      const phases = Array.isArray(experiment.phases) ? [...experiment.phases] : [];
      const nextPhases = mutator(phases).map((phase, idx) => {
        const base = phase && typeof phase === "object" ? { ...phase } : {};
        const params = base.params && typeof base.params === "object" ? { ...base.params } : {};
        if (!Number.isFinite(Number(params.n_trials))) {
          params.n_trials = 20;
        }
        return {
          name: base.name || `Phase ${idx + 1}`,
          protocol: base.protocol || "acquisition",
          stimuli: base.stimuli && typeof base.stimuli === "object" ? base.stimuli : {},
          params,
        };
      });
      experiment.phases = nextPhases;
      next.experiment = experiment;
      return next;
    });
    if (updated.ok) setDraft(updated.value);
  }

  function addPhase() {
    mutatePhases((phases) => [
      ...phases,
      {
        name: `Phase ${phases.length + 1}`,
        protocol: "acquisition",
        stimuli: {},
        params: { n_trials: 20 },
      },
    ]);
  }

  function removePhase(index) {
    mutatePhases((phases) => phases.filter((_, idx) => idx !== index));
  }

  function movePhase(index, direction) {
    mutatePhases((phases) => {
      const target = index + direction;
      if (target < 0 || target >= phases.length) return phases;
      const next = [...phases];
      const tmp = next[index];
      next[index] = next[target];
      next[target] = tmp;
      return next;
    });
  }

  function patchPhase(index, patcher) {
    mutatePhases((phases) =>
      phases.map((phase, idx) => (idx === index ? patcher(phase || {}) : phase))
    );
  }

  function patchPayload(patcher) {
    const updated = updateDraftField(draft, patcher);
    if (updated.ok) setDraft(updated.value);
  }

  const runtimeSettings =
    parsedDraft && parsedDraft.settings && typeof parsedDraft.settings === "object"
      ? parsedDraft.settings
      : {};
  const firstPhase = phaseRows.length ? phaseRows[0] : null;
  const firstPhaseParams =
    firstPhase && firstPhase.params && typeof firstPhase.params === "object"
      ? firstPhase.params
      : {};

  function setRuntimeMode(key, value) {
    patchPayload((payload) => {
      const next = { ...payload };
      const settings = { ...(next.settings || {}) };
      settings[key] = value;
      next.settings = settings;
      return next;
    });
  }

  function setFirstPhaseContext(value) {
    if (!phaseRows.length) return;
    patchPhase(0, (p) => ({ ...p, context: value }));
  }

  function setFirstPhaseNumericParam(key, value) {
    if (!phaseRows.length) return;
    patchPhase(0, (p) => ({
      ...p,
      params: {
        ...(p.params || {}),
        [key]: Number(value),
      },
    }));
  }

  function setRewardScheduleName(value) {
    if (!phaseRows.length) return;
    patchPhase(0, (p) => {
      const params = { ...(p.params || {}) };
      const clean = String(value || "").trim();
      if (!clean) {
        delete params.reward_schedule;
      } else {
        params.reward_schedule = clean;
      }
      return { ...p, params };
    });
  }

  function setRewardScheduleParamsJson(rawText) {
    if (!phaseRows.length) return;
    const clean = String(rawText || "").trim();
    if (!clean) {
      patchPhase(0, (p) => {
        const params = { ...(p.params || {}) };
        delete params.reward_schedule_params;
        return { ...p, params };
      });
      return;
    }
    try {
      const parsed = JSON.parse(clean);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return;
      patchPhase(0, (p) => ({
        ...p,
        params: {
          ...(p.params || {}),
          reward_schedule_params: parsed,
        },
      }));
    } catch (_err) {
      // Keep draft unchanged while JSON is invalid; user can continue editing.
    }
  }

  return (
    <div style={{ marginTop: "1rem" }}>
      <div className="panel">
        <h2>Plan Draft</h2>
        <p>Edit payload JSON and resolve through <code>POST /plan</code>.</p>
        <div className="api-card" style={{ marginTop: "0.75rem" }}>
          <div><strong>Preset Quick Start</strong></div>
          <p style={{ marginTop: "0.45rem" }}>
            Execute lifecycle in one action: load preset, resolve plan, and run.
          </p>
          <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", alignItems: "center" }}>
            <select
              value={presetKey}
              onChange={(e) => setPresetKey(e.target.value)}
              style={{ minWidth: "220px" }}
            >
              {presetEntries.map(([key, preset]) => (
                <option key={key} value={key}>{preset.label}</option>
              ))}
            </select>
            <button className="tab" onClick={onPresetSelect}>Load Preset</button>
            <button
              className="tab"
              onClick={onPresetResolveRun}
              disabled={presetFlowState.status === REQUEST_STATUS.LOADING}
            >
              {presetFlowState.status === REQUEST_STATUS.LOADING ? "Running Preset..." : "Resolve + Run Preset"}
            </button>
            <button
              className="tab"
              onClick={onPresetResolveRunReport}
              disabled={presetFlowState.status === REQUEST_STATUS.LOADING}
            >
              {presetFlowState.status === REQUEST_STATUS.LOADING ? "Generating..." : "Resolve + Run + Report Preset"}
            </button>
            <span>
              <strong>Preset Status:</strong> <code>{presetFlowState.status}</code>
            </span>
          </div>
          <ErrorEnvelopePanel error={presetFlowState.error} />
        </div>
        <div className="api-card" style={{ marginTop: "0.75rem" }}>
          <div><strong>Catalog-backed quick selectors</strong></div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "0.6rem",
              marginTop: "0.6rem",
            }}
          >
            <label>
              <div><strong>Protocol (phase 1)</strong></div>
              <select
                style={{ width: "100%", marginTop: "0.25rem" }}
                defaultValue=""
                onChange={(e) => {
                  if (e.target.value) setProtocol(e.target.value);
                }}
              >
                <option value="">Select protocol</option>
                {protocols.map((name) => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
            </label>
            <label>
              <div><strong>Learner</strong></div>
              <select
                style={{ width: "100%", marginTop: "0.25rem" }}
                defaultValue=""
                onChange={(e) => {
                  if (e.target.value) setLearner(e.target.value);
                }}
              >
                <option value="">Select learner</option>
                {learners.map((name) => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
            </label>
            <label>
              <div><strong>Policy</strong></div>
              <select
                style={{ width: "100%", marginTop: "0.25rem" }}
                defaultValue=""
                onChange={(e) => {
                  if (e.target.value) setPolicy(e.target.value);
                }}
              >
                <option value="">Select policy</option>
                {policies.map((name) => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
            </label>
            <label>
              <div><strong>Representation</strong></div>
              <select
                style={{ width: "100%", marginTop: "0.25rem" }}
                defaultValue=""
                onChange={(e) => {
                  if (e.target.value) setRepresentation(e.target.value);
                }}
              >
                <option value="">Select representation</option>
                {representations.map((name) => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
            </label>
          </div>
        </div>
        <div className="api-card" style={{ marginTop: "0.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.6rem", flexWrap: "wrap" }}>
            <strong>Minimal Phase Builder</strong>
            <button className="tab" onClick={addPhase}>Add Phase</button>
          </div>
          {!parsedDraft ? (
            <p style={{ marginTop: "0.55rem", color: "#b45309" }}>
              Fix JSON syntax to use the phase builder.
            </p>
          ) : null}
          {parsedDraft && !phaseRows.length ? (
            <p style={{ marginTop: "0.55rem" }}><code>No phases configured.</code></p>
          ) : null}
          {phaseRows.length ? (
            <div style={{ marginTop: "0.6rem", display: "flex", flexDirection: "column", gap: "0.65rem" }}>
              {phaseRows.map((phase, idx) => (
                <div key={`phase-builder-${idx}`} style={{ border: "1px solid #cbd5e1", borderRadius: "8px", padding: "0.6rem" }}>
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
                    <strong>{`Phase ${idx + 1}`}</strong>
                    <button className="tab" onClick={() => movePhase(idx, -1)} disabled={idx === 0}>Up</button>
                    <button className="tab" onClick={() => movePhase(idx, 1)} disabled={idx === phaseRows.length - 1}>Down</button>
                    <button className="tab" onClick={() => removePhase(idx)}>Remove</button>
                  </div>
                  <div
                    style={{
                      marginTop: "0.55rem",
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))",
                      gap: "0.55rem",
                    }}
                  >
                    <label>
                      <div><strong>Name</strong></div>
                      <input
                        type="text"
                        value={phase && phase.name ? String(phase.name) : ""}
                        onChange={(e) =>
                          patchPhase(idx, (p) => ({ ...p, name: e.target.value }))
                        }
                        style={{ width: "100%", marginTop: "0.25rem" }}
                      />
                    </label>
                    <label>
                      <div><strong>Protocol</strong></div>
                      <select
                        value={phase && phase.protocol ? String(phase.protocol) : "acquisition"}
                        onChange={(e) =>
                          patchPhase(idx, (p) => ({ ...p, protocol: e.target.value }))
                        }
                        style={{ width: "100%", marginTop: "0.25rem" }}
                      >
                        {protocols.length ? (
                          protocols.map((name) => (
                            <option key={`phase-${idx}-${name}`} value={name}>{name}</option>
                          ))
                        ) : (
                          <option value="acquisition">acquisition</option>
                        )}
                      </select>
                    </label>
                    <label>
                      <div><strong>n_trials</strong></div>
                      <input
                        type="number"
                        min="1"
                        step="1"
                        value={
                          phase &&
                          phase.params &&
                          Number.isFinite(Number(phase.params.n_trials))
                            ? Number(phase.params.n_trials)
                            : 20
                        }
                        onChange={(e) =>
                          patchPhase(idx, (p) => ({
                            ...p,
                            params: {
                              ...(p.params || {}),
                              n_trials: Math.max(1, Number(e.target.value || 1)),
                            },
                          }))
                        }
                        style={{ width: "100%", marginTop: "0.25rem" }}
                      />
                    </label>
                  </div>
                </div>
              ))}
            </div>
          ) : null}
        </div>
        <div className="api-card" style={{ marginTop: "0.75rem" }}>
          <div><strong>Typed Parameter Bridge</strong></div>
          <p style={{ marginTop: "0.45rem" }}>
            Basic typed editors for context/timing/runtime and operant schedule stubs.
          </p>
          <p style={{ marginTop: "0.35rem", color: "#475569" }}>
            These controls only edit draft payload fields. Schedule semantics and validation are backend-owned.
          </p>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "0.6rem",
              marginTop: "0.6rem",
            }}
          >
            <label>
              <div><strong>settings.update_mode</strong></div>
              <select
                value={runtimeSettings.update_mode || "trial"}
                onChange={(e) => setRuntimeMode("update_mode", e.target.value)}
                style={{ width: "100%", marginTop: "0.25rem" }}
              >
                <option value="trial">trial</option>
                <option value="tick">tick</option>
              </select>
            </label>
            <label>
              <div><strong>settings.record_mode</strong></div>
              <select
                value={runtimeSettings.record_mode || "trial"}
                onChange={(e) => setRuntimeMode("record_mode", e.target.value)}
                style={{ width: "100%", marginTop: "0.25rem" }}
              >
                <option value="trial">trial</option>
                <option value="tick">tick</option>
              </select>
            </label>
            <label>
              <div><strong>phases[0].context</strong></div>
              <input
                type="text"
                value={firstPhase && firstPhase.context ? String(firstPhase.context) : ""}
                onChange={(e) => setFirstPhaseContext(e.target.value)}
                style={{ width: "100%", marginTop: "0.25rem" }}
                disabled={!phaseRows.length}
              />
            </label>
            <label>
              <div><strong>phases[0].params.dt_s</strong></div>
              <input
                type="number"
                min="0"
                step="0.01"
                value={Number.isFinite(Number(firstPhaseParams.dt_s)) ? Number(firstPhaseParams.dt_s) : ""}
                onChange={(e) => setFirstPhaseNumericParam("dt_s", e.target.value || 0)}
                style={{ width: "100%", marginTop: "0.25rem" }}
                disabled={!phaseRows.length}
              />
            </label>
            <label>
              <div><strong>phases[0].params.duration_s</strong></div>
              <input
                type="number"
                min="0"
                step="0.1"
                value={Number.isFinite(Number(firstPhaseParams.duration_s)) ? Number(firstPhaseParams.duration_s) : ""}
                onChange={(e) => setFirstPhaseNumericParam("duration_s", e.target.value || 0)}
                style={{ width: "100%", marginTop: "0.25rem" }}
                disabled={!phaseRows.length}
              />
            </label>
            <label>
              <div><strong>phases[0].params.reward_schedule</strong></div>
              <input
                type="text"
                value={firstPhaseParams.reward_schedule ? String(firstPhaseParams.reward_schedule) : ""}
                onChange={(e) => setRewardScheduleName(e.target.value)}
                style={{ width: "100%", marginTop: "0.25rem" }}
                disabled={!phaseRows.length}
                placeholder="opaque schedule key"
              />
            </label>
            <label style={{ gridColumn: "1 / -1" }}>
              <div><strong>phases[0].params.reward_schedule_params (JSON object)</strong></div>
              <textarea
                value={
                  firstPhaseParams.reward_schedule_params &&
                  typeof firstPhaseParams.reward_schedule_params === "object" &&
                  !Array.isArray(firstPhaseParams.reward_schedule_params)
                    ? JSON.stringify(firstPhaseParams.reward_schedule_params, null, 2)
                    : ""
                }
                onChange={(e) => setRewardScheduleParamsJson(e.target.value)}
                style={{
                  width: "100%",
                  minHeight: "88px",
                  marginTop: "0.25rem",
                  fontFamily: "Consolas, 'Courier New', monospace",
                  fontSize: "0.85rem",
                  boxSizing: "border-box",
                }}
                disabled={!phaseRows.length}
                placeholder='{"key": "value"}'
              />
            </label>
          </div>
        </div>
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          style={{
            width: "100%",
            minHeight: "260px",
            marginTop: "0.75rem",
            padding: "0.65rem",
            borderRadius: "8px",
            border: "1px solid #cbd5e1",
            fontFamily: "Consolas, 'Courier New', monospace",
            fontSize: "0.87rem",
            boxSizing: "border-box",
          }}
        />
        <div style={{ marginTop: "0.75rem", display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
          <button className="tab" onClick={onResolve} disabled={!lifecycle.canResolvePlan || resolveState.status === REQUEST_STATUS.LOADING}>
            {resolveState.status === REQUEST_STATUS.LOADING ? "Resolving..." : "Resolve Plan"}
          </button>
          <span>
            <strong>Status:</strong> <code>{resolveState.status}</code>
          </span>
        </div>
        {!lifecycle.canResolvePlan ? (
          <div style={{ marginTop: "0.5rem", color: "#b45309" }}>
            Plan resolve is disabled while a run is in progress.
          </div>
        ) : null}
        <ErrorEnvelopePanel error={resolveState.error} />
      </div>

      {stableHash ? (
        <div className="panel" style={{ marginTop: "1rem" }}>
          <h2>Resolved Plan</h2>
          <p><strong>Stable Hash:</strong> <code>{stableHash}</code></p>
          <div className="api-card" style={{ marginTop: "0.75rem" }}>
            <div><strong>Plan Summary</strong></div>
            <div style={{ marginTop: "0.4rem" }}>
              <div><strong>Unit Count:</strong> {summary.unitCount}</div>
              <div><strong>Protocol/Phase Flow:</strong> {summary.flow || "n/a"}</div>
              <div><strong>Total Trials:</strong> {summary.totalTrials}</div>
              <div><strong>Timing Mode:</strong> {summary.timingMode}</div>
              <div><strong>Update/Record Mode:</strong> {summary.runtimeMode}</div>
            </div>
          </div>
          <details style={{ marginTop: "0.6rem" }}>
            <summary>View resolved plan JSON</summary>
            <pre style={{ whiteSpace: "pre-wrap", marginTop: "0.6rem" }}>
              {JSON.stringify(resolvedPlan, null, 2)}
            </pre>
          </details>
        </div>
      ) : null}
    </div>
  );
}

function RunPane({ lifecycle, runState, onRun }) {
  const runData = runState.data || null;
  const runLifecycle = runData && runData.lifecycle ? runData.lifecycle : null;
  const metadata = runData && runData.metadata ? runData.metadata : null;
  const artifacts = runData && runData.artifacts ? runData.artifacts : null;
  const runError = runState.error || null;
  const mismatchReason =
    runError &&
    runError.envelope &&
    runError.envelope.details &&
    typeof runError.envelope.details.reason === "string"
      ? runError.envelope.details.reason
      : "";
  const isPlanHashMismatch =
    (runError &&
      runError.envelope &&
      runError.envelope.code === "validation_error" &&
      /plan hash mismatch/i.test(String(runError.envelope.message || ""))) ||
    /plan hash mismatch/i.test(mismatchReason);
  const planHash = metadata && metadata.plan_hash ? String(metadata.plan_hash) : "";
  const recordSchemaVersion = metadata && metadata.record_schema_version ? String(metadata.record_schema_version) : "";
  const templateVersionUsed =
    metadata && Number.isFinite(Number(metadata.template_version_used))
      ? Number(metadata.template_version_used)
      : null;
  const regenerationMode = metadata && metadata.regeneration_mode ? String(metadata.regeneration_mode) : "";
  const sourceRunId = metadata && metadata.source_run_id ? String(metadata.source_run_id) : "";
  const sourceMetadataComplete =
    metadata && Object.prototype.hasOwnProperty.call(metadata, "source_metadata_complete")
      ? Boolean(metadata.source_metadata_complete)
      : null;
  const missingSourceMetadata =
    metadata && Array.isArray(metadata.missing_source_metadata)
      ? metadata.missing_source_metadata
      : [];

  return (
    <div style={{ marginTop: "1rem" }}>
      <div className="panel">
        <h2>Run Console</h2>
        <p>Create a run via <code>POST /run</code>. A resolved plan is required.</p>
        <div style={{ marginTop: "0.75rem", display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
          <button className="tab" onClick={onRun} disabled={!lifecycle.canRun || runState.status === REQUEST_STATUS.LOADING}>
            {runState.status === REQUEST_STATUS.LOADING ? "Running..." : "Run"}
          </button>
          <span>
            <strong>Status:</strong> <code>{runState.status}</code>
          </span>
          {!lifecycle.canRun ? (
            <span style={{ color: "#b45309" }}>Resolve a plan first.</span>
          ) : null}
        </div>
        <ErrorEnvelopePanel error={runState.error} />
        {isPlanHashMismatch ? (
          <div style={{ marginTop: "0.5rem", color: "#b45309" }}>
            Run was blocked by plan drift guard. Resolve the plan again and rerun to refresh `stable_hash`.
          </div>
        ) : null}
      </div>

      {runData ? (
        <div className="panel" style={{ marginTop: "1rem" }}>
          <h2>Run Result</h2>
          <div><strong>Run ID:</strong> <code>{runData.run_id || "n/a"}</code></div>
          <div><strong>State:</strong> <code>{runData.state || "n/a"}</code></div>
          {runLifecycle ? (
            <>
              <div><strong>Lifecycle:</strong> <code>{runLifecycle.state || "n/a"}</code></div>
              <div>
                <strong>Next Actions:</strong>{" "}
                <code>{Array.isArray(runLifecycle.next_actions) ? runLifecycle.next_actions.join(", ") : "n/a"}</code>
              </div>
            </>
          ) : null}
          {metadata ? (
            <div className="api-card" style={{ marginTop: "0.75rem" }}>
              <div><strong>Provenance</strong></div>
              <div style={{ marginTop: "0.5rem" }}>
                <div><strong>plan_hash:</strong> <code>{planHash || "n/a"}</code></div>
                <div><strong>record_schema_version:</strong> <code>{recordSchemaVersion || "n/a"}</code></div>
                <div>
                  <strong>template_version_used:</strong>{" "}
                  <code>{templateVersionUsed === null ? "n/a" : String(templateVersionUsed)}</code>
                </div>
              </div>
            </div>
          ) : null}
          {metadata ? (
            <div className="api-card" style={{ marginTop: "0.75rem" }}>
              <div><strong>Metadata</strong></div>
              <pre style={{ whiteSpace: "pre-wrap", marginTop: "0.5rem" }}>{JSON.stringify(metadata, null, 2)}</pre>
            </div>
          ) : null}
          {artifacts ? (
            <div className="api-card" style={{ marginTop: "0.75rem" }}>
              <div><strong>Artifacts</strong></div>
              <pre style={{ whiteSpace: "pre-wrap", marginTop: "0.5rem" }}>{JSON.stringify(artifacts, null, 2)}</pre>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function ReportPane({ runId, setRunId, reportState, onCreateReport, lifecycle }) {
  const reportData = reportState.data || null;
  const reportLifecycle = reportData && reportData.lifecycle ? reportData.lifecycle : null;
  const metadata = reportData && reportData.metadata ? reportData.metadata : null;
  const artifacts = reportData && reportData.artifacts ? reportData.artifacts : null;
  const figureList = artifacts && Array.isArray(artifacts.figures) ? artifacts.figures : [];
  const pdfPath = artifacts && artifacts.pdf ? String(artifacts.pdf) : "";
  const metaView = React.useMemo(() => {
    const raw = metadata && typeof metadata === "object" ? metadata : null;
    return {
      raw,
      planHash: raw && raw.plan_hash ? String(raw.plan_hash) : "",
      recordSchemaVersion: raw && raw.record_schema_version ? String(raw.record_schema_version) : "",
      templateVersionUsed:
        raw && Number.isFinite(Number(raw.template_version_used))
          ? Number(raw.template_version_used)
          : null,
      regenerationMode: raw && raw.regeneration_mode ? String(raw.regeneration_mode) : "",
      sourceRunId: raw && raw.source_run_id ? String(raw.source_run_id) : "",
      sourceMetadataComplete:
        raw && Object.prototype.hasOwnProperty.call(raw, "source_metadata_complete")
          ? Boolean(raw.source_metadata_complete)
          : null,
      missingSourceMetadata:
        raw && Array.isArray(raw.missing_source_metadata)
          ? raw.missing_source_metadata
          : [],
    };
  }, [metadata]);

  function renderPath(pathValue) {
    const raw = String(pathValue || "");
    if (!raw) return <code>n/a</code>;
    const isHttp = /^https?:\/\//i.test(raw);
    const isRoot = raw.startsWith("/");
    if (isHttp || isRoot) {
      return (
        <a href={raw} target="_blank" rel="noreferrer">
          {raw}
        </a>
      );
    }
    return <code>{raw}</code>;
  }

  return (
    <div style={{ marginTop: "1rem" }}>
      <div className="panel">
        <h2>Report Console</h2>
        <p>Create a report via <code>POST /runs/{`{run_id}`}/report</code>.</p>
        <div style={{ marginTop: "0.75rem" }}>
          <label htmlFor="report-run-id"><strong>Run ID</strong></label>
          <input
            id="report-run-id"
            type="text"
            value={runId}
            onChange={(e) => setRunId(e.target.value)}
            placeholder="Enter run id"
            style={{
              display: "block",
              width: "100%",
              marginTop: "0.4rem",
              padding: "0.55rem",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              boxSizing: "border-box",
            }}
          />
        </div>
        <div style={{ marginTop: "0.75rem", display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
          <button className="tab" onClick={onCreateReport} disabled={!lifecycle.canCreateReport || reportState.status === REQUEST_STATUS.LOADING}>
            {reportState.status === REQUEST_STATUS.LOADING ? "Creating..." : "Create Report"}
          </button>
          <span>
            <strong>Status:</strong> <code>{reportState.status}</code>
          </span>
        </div>
        {!lifecycle.canCreateReport ? (
          <div style={{ marginTop: "0.5rem", color: "#b45309" }}>
            Report creation is enabled after a completed run.
          </div>
        ) : null}
        <ErrorEnvelopePanel error={reportState.error} />
      </div>

      {reportData ? (
        <div className="panel" style={{ marginTop: "1rem" }}>
          <h2>Report Result</h2>
          <div><strong>Status:</strong> <code>{reportData.status || "n/a"}</code></div>
          <div><strong>Report Run ID:</strong> <code>{reportData.run_id || "n/a"}</code></div>
          {reportLifecycle ? (
            <>
              <div><strong>Lifecycle:</strong> <code>{reportLifecycle.state || "n/a"}</code></div>
              <div>
                <strong>Next Actions:</strong>{" "}
                <code>{Array.isArray(reportLifecycle.next_actions) ? reportLifecycle.next_actions.join(", ") : "n/a"}</code>
              </div>
            </>
          ) : null}
          <div className="api-card" style={{ marginTop: "0.75rem" }}>
            <div><strong>Artifacts</strong></div>
            <div style={{ marginTop: "0.5rem" }}>
              <div><strong>PDF:</strong> {renderPath(pdfPath)}</div>
              <div style={{ marginTop: "0.45rem" }}><strong>Figures:</strong></div>
              {figureList.length ? (
                <ul style={{ margin: "0.35rem 0 0.2rem 1.2rem", padding: 0 }}>
                  {figureList.map((pathValue, idx) => (
                    <li key={`${pathValue}-${idx}`}>{renderPath(pathValue)}</li>
                  ))}
                </ul>
              ) : (
                <div><code>none</code></div>
              )}
            </div>
          </div>
          <div className="api-card" style={{ marginTop: "0.75rem" }}>
            <div><strong>Provenance</strong></div>
            <div style={{ marginTop: "0.5rem" }}>
              <div><strong>plan_hash:</strong> <code>{metaView.planHash || "n/a"}</code></div>
              <div><strong>record_schema_version:</strong> <code>{metaView.recordSchemaVersion || "n/a"}</code></div>
              <div>
                <strong>template_version_used:</strong>{" "}
                <code>{metaView.templateVersionUsed === null ? "n/a" : String(metaView.templateVersionUsed)}</code>
              </div>
            </div>
          </div>
          <div className="api-card" style={{ marginTop: "0.75rem" }}>
            <div><strong>Regeneration Metadata</strong></div>
            <div style={{ marginTop: "0.5rem" }}>
              <div><strong>regeneration_mode:</strong> <code>{metaView.regenerationMode || "n/a"}</code></div>
              <div><strong>source_run_id:</strong> <code>{metaView.sourceRunId || "n/a"}</code></div>
              <div>
                <strong>source_metadata_complete:</strong>{" "}
                <code>
                  {metaView.sourceMetadataComplete === null ? "n/a" : metaView.sourceMetadataComplete ? "true" : "false"}
                </code>
              </div>
              <div>
                <strong>missing_source_metadata:</strong>{" "}
                <code>{metaView.missingSourceMetadata.length ? metaView.missingSourceMetadata.join(", ") : "none"}</code>
              </div>
            </div>
          </div>
          {metaView.raw ? (
            <div className="api-card" style={{ marginTop: "0.75rem" }}>
              <div><strong>Metadata</strong></div>
              <pre style={{ whiteSpace: "pre-wrap", marginTop: "0.5rem" }}>{JSON.stringify(metaView.raw, null, 2)}</pre>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function SessionRunHistory({ runs, selectedRunId, onSelect }) {
  return (
    <div className="panel" style={{ marginTop: "1rem" }}>
      <h2>Session Runs</h2>
      <p>Runs created in this browser session.</p>
      {!runs.length ? (
        <div><code>No runs yet.</code></div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.45rem", marginTop: "0.6rem" }}>
          {runs.map((run) => {
            const isSelected = selectedRunId === run.runId;
            return (
              <button
                key={run.runId}
                className={`tab ${isSelected ? "active" : ""}`}
                onClick={() => onSelect(run.runId)}
                style={{ textAlign: "left" }}
              >
                <div><strong>{run.runId}</strong></div>
                <div style={{ fontSize: "0.82rem", color: "#475569" }}>
                  state: <code>{run.state || "n/a"}</code>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function CatalogSummary({ catalogState, onRefresh }) {
  const ext = catalogState.data && catalogState.data.extensions ? catalogState.data.extensions : null;
  const protocols = ext && Array.isArray(ext.protocols) ? ext.protocols.length : 0;
  const learners = ext && Array.isArray(ext.learners) ? ext.learners.length : 0;
  const policies = ext && Array.isArray(ext.policies) ? ext.policies.length : 0;
  const representations = ext && Array.isArray(ext.representations) ? ext.representations.length : 0;
  const reportTemplates =
    ext && ext.report_templates && typeof ext.report_templates === "object"
      ? Object.keys(ext.report_templates).length
      : 0;

  return (
    <div className="api-card" style={{ marginTop: "1rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
        <strong>Extension Catalog</strong>
        <button className="tab" onClick={onRefresh} disabled={catalogState.status === REQUEST_STATUS.LOADING}>
          {catalogState.status === REQUEST_STATUS.LOADING ? "Refreshing..." : "Refresh"}
        </button>
        <span>
          <strong>Status:</strong> <code>{catalogState.status}</code>
        </span>
      </div>

      {ext ? (
        <div style={{ marginTop: "0.55rem" }}>
          <div><strong>protocols:</strong> {protocols}</div>
          <div><strong>learners:</strong> {learners}</div>
          <div><strong>policies:</strong> {policies}</div>
          <div><strong>representations:</strong> {representations}</div>
          <div><strong>report_templates:</strong> {reportTemplates}</div>
        </div>
      ) : null}
      <ErrorEnvelopePanel error={catalogState.error} />
    </div>
  );
}

function getRunStateValue(runData) {
  if (!runData || typeof runData !== "object") return "";
  const lifecycle = runData.lifecycle;
  if (lifecycle && typeof lifecycle === "object" && lifecycle.state) {
    return String(lifecycle.state).toLowerCase();
  }
  if (runData.state) {
    return String(runData.state).toLowerCase();
  }
  return "";
}

function getRunIdValue(runData) {
  if (!runData || typeof runData !== "object" || !runData.run_id) return "";
  return String(runData.run_id);
}

function isRunTerminal(runData) {
  if (!runData || typeof runData !== "object") return false;
  if (runData.done === true) return true;
  const lifecycle = runData.lifecycle;
  if (lifecycle && typeof lifecycle === "object" && lifecycle.done === true) {
    return true;
  }
  return TERMINAL_RUN_STATES.has(getRunStateValue(runData));
}

function summarizePlan(plan) {
  if (!plan || typeof plan !== "object") {
    return {
      unitCount: 0,
      flow: "",
      totalTrials: 0,
      timingMode: "n/a",
      runtimeMode: "n/a",
    };
  }

  const units = Array.isArray(plan.units) ? plan.units : [];
  const settings = plan.settings && typeof plan.settings === "object" ? plan.settings : {};

  const flowParts = [];
  let totalTrials = 0;
  let sawTickTiming = false;

  for (const unit of units) {
    if (!unit || typeof unit !== "object") continue;
    const key = unit.protocol || unit.unit_key || unit.name || "unit";
    flowParts.push(String(key));

    const params = unit.params && typeof unit.params === "object" ? unit.params : {};
    const unitTrials = Number.isFinite(Number(params.n_trials)) ? Number(params.n_trials) : 0;
    totalTrials += unitTrials;

    const dt = params.dt_s;
    if (Number.isFinite(Number(dt)) && Number(dt) > 0 && Number(dt) < 1) {
      sawTickTiming = true;
    }
  }

  let runtimeMode = "trial/trial";
  if (settings && typeof settings === "object") {
    const updateMode = settings.update_mode || "trial";
    const recordMode = settings.record_mode || "trial";
    runtimeMode = `${updateMode}/${recordMode}`;
    if (updateMode === "tick" || recordMode === "tick") {
      sawTickTiming = true;
    }
  }

  return {
    unitCount: units.length,
    flow: flowParts.join(" -> "),
    totalTrials,
    timingMode: sawTickTiming ? "tick-capable" : "trial",
    runtimeMode,
  };
}

function ConsoleApp() {
  const [tab, setTab] = React.useState(getTabFromHash);
  const [apiBase] = React.useState("");
  const [client] = React.useState(() => window.VSLApi.createApiClient({ baseUrl: apiBase }));
  const [catalogState, setCatalogState] = React.useState(() => makeRequestState());
  const [planDraft, setPlanDraft] = React.useState(DEFAULT_PLAN_DRAFT);
  const [planResolveState, setPlanResolveState] = React.useState(() => makeRequestState());
  const [runCreateState, setRunCreateState] = React.useState(() => makeRequestState());
  const [runStatusState, setRunStatusState] = React.useState(() => makeRequestState());
  const [activeRunId, setActiveRunId] = React.useState("");
  const [reportRunId, setReportRunId] = React.useState("");
  const [reportCreateState, setReportCreateState] = React.useState(() => makeRequestState());
  const [lifecycleState, setLifecycleState] = React.useState(UI_LIFECYCLE.PLAN_DRAFT);
  const [sessionRuns, setSessionRuns] = React.useState([]);
  const [presetKey, setPresetKey] = React.useState("acquisition_demo");
  const [presetFlowState, setPresetFlowState] = React.useState(() => makeRequestState());
  const catalogExtensions =
    catalogState.data && catalogState.data.extensions && typeof catalogState.data.extensions === "object"
      ? catalogState.data.extensions
      : null;
  const transitionLifecycleState = React.useCallback((eventName) => {
    setLifecycleState((prev) => transitionLifecycle(prev, eventName));
  }, []);
  const lifecycle = React.useMemo(
    () => createLifecycleStore(lifecycleState, transitionLifecycleState),
    [lifecycleState, transitionLifecycleState]
  );

  React.useEffect(() => {
    function onHashChange() {
      setTab(getTabFromHash());
    }
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  function selectTab(nextTab) {
    const clean = normalizeTab(nextTab);
    window.location.hash = clean;
    setTab(clean);
  }

  const loadCatalog = React.useCallback(async function loadCatalog() {
    setCatalogState((prev) => requestLoading(prev.data));
    try {
      const data = await client.getJson("catalog/extensions");
      setCatalogState(requestSuccess(data));
    } catch (err) {
      setCatalogState((prev) => requestError(err, prev.data));
    }
  }, [client]);

  React.useEffect(() => {
    if (catalogState.status !== REQUEST_STATUS.IDLE) return;
    loadCatalog();
  }, [catalogState.status, loadCatalog]);

  async function resolvePlan() {
    if (!lifecycle.canResolvePlan) {
      setPlanResolveState(
        requestError({
          status: 0,
          message: "Plan resolve unavailable while run is in progress.",
          envelope: {
            code: "ui_plan_resolve_blocked",
            message: "Wait for run completion before resolving another plan.",
            details: {},
          },
        })
      );
      return;
    }

    let payload;
    try {
      payload = JSON.parse(planDraft);
    } catch (err) {
      setPlanResolveState(
        requestError({
          status: 0,
          message: "Invalid JSON in draft payload.",
          envelope: {
            code: "ui_invalid_json",
            message: "Payload is not valid JSON.",
            details: { reason: String(err && err.message ? err.message : err) },
          },
        })
      );
      return;
    }

    await resolvePlanWithPayload(payload);
  }

  function parseDraftPayload() {
    try {
      return { ok: true, value: JSON.parse(planDraft) };
    } catch (err) {
      return {
        ok: false,
        error: {
          status: 0,
          message: "Invalid JSON in draft payload.",
          envelope: {
            code: "ui_invalid_json",
            message: "Payload is not valid JSON.",
            details: { reason: String(err && err.message ? err.message : err) },
          },
        },
      };
    }
  }

  async function executeRunWithPayload(payload) {
    setRunCreateState((prev) => requestLoading(prev.data));
    lifecycle.markRunStarted();
    try {
      const resolvedStableHash =
        planResolveState.data &&
        typeof planResolveState.data.stable_hash === "string" &&
        planResolveState.data.stable_hash
          ? planResolveState.data.stable_hash
          : null;
      const runPayload = resolvedStableHash
        ? { ...payload, expected_plan_hash: resolvedStableHash }
        : payload;

      const data = await client.postJson("run", runPayload);
      setRunCreateState(requestSuccess(data));
      setRunStatusState(requestSuccess(data));
      const nextRunId = data && data.run_id ? String(data.run_id) : "";
      setActiveRunId(nextRunId);
      setReportRunId(nextRunId);
      if (nextRunId) {
        const nextState = getRunStateValue(data) || "created";
        setSessionRuns((prev) => {
          const existing = prev.find((item) => item.runId === nextRunId);
          if (existing) {
            return prev.map((item) =>
              item.runId === nextRunId ? { ...item, state: nextState } : item
            );
          }
          return [{ runId: nextRunId, state: nextState }, ...prev];
        });
      }
      return data;
    } catch (err) {
      setRunCreateState((prev) => requestError(err, prev.data));
      throw err;
    }
  }

  async function resolvePlanWithPayload(payload) {
    setPlanResolveState((prev) => requestLoading(prev.data));
    try {
      const data = await client.postJson("plan", payload);
      setPlanResolveState(requestSuccess(data));
      lifecycle.markPlanResolved();
      return { ok: true, data };
    } catch (err) {
      setPlanResolveState((prev) => requestError(err, prev.data));
      return { ok: false, error: err };
    }
  }

  async function createRun() {
    const parsed = parseDraftPayload();
    if (!parsed.ok) {
      setRunCreateState(requestError(parsed.error));
      return;
    }
    if (!lifecycle.canRun) {
      setRunCreateState(
        requestError({
          status: 0,
          message: "Resolve plan before running.",
          envelope: {
            code: "ui_plan_not_resolved",
            message: "Plan must be resolved before creating a run.",
            details: {},
          },
        })
      );
      return;
    }
    await executeRunWithPayload(parsed.value);
  }

  function loadSelectedPreset() {
    const preset = LIFECYCLE_PRESETS[presetKey];
    if (!preset) return;
    const payload = clonePayload(preset.payload);
    setPlanDraft(JSON.stringify(payload, null, 2));
    lifecycle.markPlanEdited();
  }

  async function resolveAndRunSelectedPreset() {
    const preset = LIFECYCLE_PRESETS[presetKey];
    if (!preset) return;

    const payload = clonePayload(preset.payload);
    setPresetFlowState((prev) => requestLoading(prev.data));
    setPlanDraft(JSON.stringify(payload, null, 2));
    lifecycle.markPlanEdited();

    const resolved = await resolvePlanWithPayload(payload);
    if (!resolved.ok) {
      setPresetFlowState((prev) => requestError(resolved.error, prev.data));
      return;
    }

    try {
      await executeRunWithPayload(payload);
      setPresetFlowState(requestSuccess({ preset: presetKey }));
    } catch (err) {
      setPresetFlowState((prev) => requestError(err, prev.data));
    }
  }

  async function resolveRunAndReportSelectedPreset() {
    const preset = LIFECYCLE_PRESETS[presetKey];
    if (!preset) return;

    const payload = clonePayload(preset.payload);
    setPresetFlowState((prev) => requestLoading(prev.data));
    setPlanDraft(JSON.stringify(payload, null, 2));
    lifecycle.markPlanEdited();

    const resolved = await resolvePlanWithPayload(payload);
    if (!resolved.ok) {
      setPresetFlowState((prev) => requestError(resolved.error, prev.data));
      return;
    }

    try {
      const runData = await executeRunWithPayload(payload);
      const runId = runData && runData.run_id ? String(runData.run_id) : "";
      const reportResult = await createReportForRunId(runId, false);
      if (!reportResult.ok) {
        setPresetFlowState((prev) => requestError(reportResult.error, prev.data));
        return;
      }
      setPresetFlowState(
        requestSuccess({
          preset: presetKey,
          run_id: runId,
          report_run_id: reportResult.data && reportResult.data.run_id ? reportResult.data.run_id : "",
        })
      );
      selectTab("report");
    } catch (err) {
      setPresetFlowState((prev) => requestError(err, prev.data));
    }
  }

  async function loadRunDetail(runId) {
    const cleanRunId = String(runId || "").trim();
    if (!cleanRunId) return;

    setRunStatusState((prev) => requestLoading(prev.data));
    try {
      const data = await client.getJson(`runs/${encodeURIComponent(cleanRunId)}`);
      setRunStatusState(requestSuccess(data));
      const nextState = getRunStateValue(data) || "unknown";
      setSessionRuns((prev) => {
        const existing = prev.find((item) => item.runId === cleanRunId);
        if (existing) {
          return prev.map((item) =>
            item.runId === cleanRunId ? { ...item, state: nextState } : item
          );
        }
        return [{ runId: cleanRunId, state: nextState }, ...prev];
      });
      if (isRunTerminal(data)) {
        lifecycle.markRunCompleted();
      }
    } catch (err) {
      setRunStatusState((prev) => requestError(err, prev.data));
    }
  }

  async function createReportForRunId(runId, enforceLifecycle) {
    const cleanRunId = String(runId || "").trim();
    const mustEnforce = enforceLifecycle !== false;
    if (!cleanRunId) {
      const err = {
        status: 0,
        message: "Run ID is required.",
        envelope: {
          code: "ui_missing_run_id",
          message: "Provide a run ID before creating a report.",
          details: {},
        },
      };
      setReportCreateState(requestError(err));
      return { ok: false, error: err };
    }
    if (mustEnforce && !lifecycle.canCreateReport) {
      const err = {
        status: 0,
        message: "Run must complete before report creation.",
        envelope: {
          code: "ui_run_not_complete",
          message: "Report generation is only enabled after run completion.",
          details: {},
        },
      };
      setReportCreateState(requestError(err));
      return { ok: false, error: err };
    }

    setReportCreateState((prev) => requestLoading(prev.data));
    try {
      const data = await client.postJson(`runs/${encodeURIComponent(cleanRunId)}/report`, {});
      setReportCreateState(requestSuccess(data));
      lifecycle.markReportCompleted();
      return { ok: true, data };
    } catch (err) {
      setReportCreateState((prev) => requestError(err, prev.data));
      return { ok: false, error: err };
    }
  }

  async function createReport() {
    const runId = String(reportRunId || "").trim();
    await createReportForRunId(runId, true);
  }

  React.useEffect(() => {
    if (!activeRunId) return undefined;

    const runStatusId = getRunIdValue(runStatusState.data);
    const runCreateId = getRunIdValue(runCreateState.data);
    const current =
      runStatusId === activeRunId
        ? runStatusState.data
        : runCreateId === activeRunId
        ? runCreateState.data
        : null;
    if (isRunTerminal(current)) return undefined;

    let cancelled = false;

    async function pollRunStatus() {
      setRunStatusState((prev) => requestLoading(prev.data));
      try {
        const data = await client.getJson(`runs/${encodeURIComponent(activeRunId)}`);
        if (cancelled) return;
        setRunStatusState(requestSuccess(data));
        const nextState = getRunStateValue(data) || "unknown";
        setSessionRuns((prev) =>
          prev.map((item) =>
            item.runId === activeRunId ? { ...item, state: nextState } : item
          )
        );
        if (isRunTerminal(data)) {
          lifecycle.markRunCompleted();
        }
      } catch (err) {
        if (cancelled) return;
        setRunStatusState((prev) => requestError(err, prev.data));
      }
    }

    const intervalId = window.setInterval(pollRunStatus, RUN_POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, [activeRunId, client, lifecycle, runCreateState.data, runStatusState.data]);

  return (
    <div className="shell">
      <div className="top">
        <div>
          <h1 style={{ margin: 0 }}>VSL Lifecycle Console</h1>
          <small style={{ color: "#475569" }}>
            Thin UI around plan/run/report lifecycle APIs.
          </small>
        </div>
        <a href="/ui/index.html">Back to Menu</a>
      </div>

      <div className="tabs">
        {TAB_KEYS.map((key) => (
          <button
            key={key}
            className={`tab ${tab === key ? "active" : ""}`}
            onClick={() => selectTab(key)}
          >
            {tabLabel(key)}
          </button>
        ))}
      </div>

      <Panel tab={tab} />
      <div className="api-card" style={{ marginTop: "1rem" }}>
        <div><strong>Lifecycle State:</strong> <code>{lifecycle.state}</code></div>
      </div>
      {tab === "plan" ? (
        <PlanPane
          draft={planDraft}
          setDraft={(next) => {
            setPlanDraft(next);
            lifecycle.markPlanEdited();
          }}
          resolveState={planResolveState}
          onResolve={resolvePlan}
          onPresetSelect={loadSelectedPreset}
          onPresetResolveRun={resolveAndRunSelectedPreset}
          onPresetResolveRunReport={resolveRunAndReportSelectedPreset}
          presetKey={presetKey}
          setPresetKey={setPresetKey}
          presetFlowState={presetFlowState}
          catalogExtensions={catalogExtensions}
          lifecycle={lifecycle}
        />
      ) : null}
      {tab === "run" ? (
        <RunPane
          lifecycle={lifecycle}
          runState={
            getRunIdValue(runStatusState.data) === activeRunId
              ? {
                  status: runStatusState.status,
                  data: runStatusState.data,
                  error: runStatusState.error,
                }
              : runCreateState
          }
          onRun={createRun}
        />
      ) : null}
      {tab === "report" ? (
        <ReportPane
          runId={reportRunId}
          setRunId={setReportRunId}
          reportState={reportCreateState}
          onCreateReport={createReport}
          lifecycle={lifecycle}
        />
      ) : null}

      <div className="api-card" style={{ marginTop: "1rem" }}>
        <div><strong>API Client:</strong> initialized</div>
        <code>{client.buildUrl("catalog/extensions")}</code>
      </div>
      <CatalogSummary catalogState={catalogState} onRefresh={loadCatalog} />
      <SessionRunHistory
        runs={sessionRuns}
        selectedRunId={activeRunId}
        onSelect={(runId) => {
          setActiveRunId(runId);
          setReportRunId(runId);
          loadRunDetail(runId);
        }}
      />
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<ConsoleApp />);

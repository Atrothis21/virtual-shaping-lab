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

const TERMINAL_RUN_STATES = new Set([
  "completed",
  "complete",
  "failed",
  "error",
  "cancelled",
  "canceled",
  "report_complete",
]);

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

function PlanPane({ draft, setDraft, resolveState, onResolve }) {
  const resolveData = resolveState.data || null;
  const stableHash = resolveData && resolveData.stable_hash ? resolveData.stable_hash : "";
  const resolvedPlan = resolveData && resolveData.plan ? resolveData.plan : null;
  const summary = React.useMemo(() => summarizePlan(resolvedPlan), [resolvedPlan]);

  return (
    <div style={{ marginTop: "1rem" }}>
      <div className="panel">
        <h2>Plan Draft</h2>
        <p>Edit payload JSON and resolve through <code>POST /plan</code>.</p>
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
          <button className="tab" onClick={onResolve} disabled={resolveState.status === REQUEST_STATUS.LOADING}>
            {resolveState.status === REQUEST_STATUS.LOADING ? "Resolving..." : "Resolve Plan"}
          </button>
          <span>
            <strong>Status:</strong> <code>{resolveState.status}</code>
          </span>
        </div>
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

function RunPane({ canRun, runState, onRun }) {
  const runData = runState.data || null;
  const lifecycle = runData && runData.lifecycle ? runData.lifecycle : null;
  const metadata = runData && runData.metadata ? runData.metadata : null;
  const artifacts = runData && runData.artifacts ? runData.artifacts : null;

  return (
    <div style={{ marginTop: "1rem" }}>
      <div className="panel">
        <h2>Run Console</h2>
        <p>Create a run via <code>POST /run</code>. A resolved plan is required.</p>
        <div style={{ marginTop: "0.75rem", display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
          <button className="tab" onClick={onRun} disabled={!canRun || runState.status === REQUEST_STATUS.LOADING}>
            {runState.status === REQUEST_STATUS.LOADING ? "Running..." : "Run"}
          </button>
          <span>
            <strong>Status:</strong> <code>{runState.status}</code>
          </span>
          {!canRun ? (
            <span style={{ color: "#b45309" }}>Resolve a plan first.</span>
          ) : null}
        </div>
        <ErrorEnvelopePanel error={runState.error} />
      </div>

      {runData ? (
        <div className="panel" style={{ marginTop: "1rem" }}>
          <h2>Run Result</h2>
          <div><strong>Run ID:</strong> <code>{runData.run_id || "n/a"}</code></div>
          <div><strong>State:</strong> <code>{runData.state || "n/a"}</code></div>
          {lifecycle ? (
            <>
              <div><strong>Lifecycle:</strong> <code>{lifecycle.state || "n/a"}</code></div>
              <div>
                <strong>Next Actions:</strong>{" "}
                <code>{Array.isArray(lifecycle.next_actions) ? lifecycle.next_actions.join(", ") : "n/a"}</code>
              </div>
            </>
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

  async function loadCatalog() {
    setCatalogState((prev) => requestLoading(prev.data));
    try {
      const data = await client.getJson("catalog/extensions");
      setCatalogState(requestSuccess(data));
    } catch (err) {
      setCatalogState((prev) => requestError(err, prev.data));
    }
  }

  async function resolvePlan() {
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

    setPlanResolveState((prev) => requestLoading(prev.data));
    try {
      const data = await client.postJson("plan", payload);
      setPlanResolveState(requestSuccess(data));
    } catch (err) {
      setPlanResolveState((prev) => requestError(err, prev.data));
    }
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

  async function createRun() {
    const parsed = parseDraftPayload();
    if (!parsed.ok) {
      setRunCreateState(requestError(parsed.error));
      return;
    }
    if (planResolveState.status !== REQUEST_STATUS.SUCCESS) {
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

    setRunCreateState((prev) => requestLoading(prev.data));
    try {
      const data = await client.postJson("run", parsed.value);
      setRunCreateState(requestSuccess(data));
      setRunStatusState(requestSuccess(data));
      setActiveRunId(data && data.run_id ? String(data.run_id) : "");
    } catch (err) {
      setRunCreateState((prev) => requestError(err, prev.data));
    }
  }

  React.useEffect(() => {
    if (!activeRunId) return undefined;

    const current = runStatusState.data || runCreateState.data;
    if (isRunTerminal(current)) return undefined;

    let cancelled = false;

    async function pollRunStatus() {
      setRunStatusState((prev) => requestLoading(prev.data));
      try {
        const data = await client.getJson(`runs/${encodeURIComponent(activeRunId)}`);
        if (cancelled) return;
        setRunStatusState(requestSuccess(data));
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
  }, [activeRunId, client, runCreateState.data, runStatusState.data]);

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
      {tab === "plan" ? (
        <PlanPane
          draft={planDraft}
          setDraft={setPlanDraft}
          resolveState={planResolveState}
          onResolve={resolvePlan}
        />
      ) : null}
      {tab === "run" ? (
        <RunPane
          canRun={planResolveState.status === REQUEST_STATUS.SUCCESS}
          runState={
            runStatusState.data
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

      <div className="api-card" style={{ marginTop: "1rem" }}>
        <div><strong>API Client:</strong> initialized</div>
        <code>{client.buildUrl("plan")}</code>
        <div style={{ marginTop: "0.65rem", display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
          <button className="tab" onClick={loadCatalog}>Test API: /catalog/extensions</button>
          <span>
            <strong>Status:</strong>{" "}
            <code>{catalogState.status}</code>
          </span>
          {catalogState.status === REQUEST_STATUS.SUCCESS && catalogState.data ? (
            <span style={{ color: "#0f766e" }}>Catalog loaded</span>
          ) : null}
        </div>
        <ErrorEnvelopePanel error={catalogState.error} />
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<ConsoleApp />);

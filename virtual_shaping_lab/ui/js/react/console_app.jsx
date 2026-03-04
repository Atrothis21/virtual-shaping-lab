const TAB_KEYS = ["plan", "run", "report"];
const {
  REQUEST_STATUS,
  makeRequestState,
  requestLoading,
  requestSuccess,
  requestError,
  ErrorEnvelopePanel,
} = window.VSLReact;

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

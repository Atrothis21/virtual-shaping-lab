const TAB_KEYS = ["plan", "run", "report"];

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

function ConsoleApp() {
  const [tab, setTab] = React.useState(getTabFromHash);
  const [apiBase] = React.useState("");
  const [client] = React.useState(() => window.VSLApi.createApiClient({ baseUrl: apiBase }));

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
        <div><strong>API Client:</strong> initialized</div>
        <code>{client.buildUrl("plan")}</code>
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<ConsoleApp />);

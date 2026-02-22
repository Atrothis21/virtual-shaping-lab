window.VSLReact = window.VSLReact || {};

const {
  buildDefaultPhase,
  createInitialPayload,
  normalizePayload,
} = window.VSLReact.builderState;

const BuilderPhaseList = window.VSLReact.BuilderPhaseList;

function BuilderShellApp() {
  const [payload, setPayload] = React.useState(createInitialPayload);
  const [activePhaseIndex, setActivePhaseIndex] = React.useState(0);
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);

  const normalizedPayload = React.useMemo(() => normalizePayload(payload), [payload]);
  const phases = payload.experiment.phases;
  const active = phases[activePhaseIndex];

  const addPhase = () => {
    setPayload((prev) => {
      const next = JSON.parse(JSON.stringify(prev));
      next.experiment.phases.push(buildDefaultPhase(next.experiment.phases.length));
      return next;
    });
    setActivePhaseIndex(phases.length);
  };

  const updateActive = (updater) => {
    setPayload((prev) => {
      const next = JSON.parse(JSON.stringify(prev));
      updater(next.experiment.phases[activePhaseIndex]);
      return next;
    });
  };

  const onRun = async () => {
    setRunError(false);
    setRunOutput("Running...");

    const res = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(normalizedPayload),
    });
    const result = await res.json();

    if (result.status === "success" && result.run_id) {
      window.location.href = `/ui/results.html?run_id=${result.run_id}`;
      return;
    }

    setRunOutput(JSON.stringify(result, null, 2));
    setRunError(true);
  };

  return (
    <>
      <h1>Virtual Shaping Lab - Builder</h1>
      <p>React builder (phase 4 slice). Advanced controls remain available in legacy fallback.</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/index.html"; }}>
          Back to Menu
        </button>
        <a className="btn secondary" href="/ui/builder_legacy.html">Open Legacy Builder</a>
      </div>

      <BuilderPhaseList
        phases={phases}
        activePhaseIndex={activePhaseIndex}
        onSelectPhase={setActivePhaseIndex}
        onAddPhase={addPhase}
      />

      <div className="panel">
        <h3>Active Phase</h3>
        <label>Protocol</label>
        <select
          value={active.protocol}
          onChange={(e) => updateActive((p) => { p.protocol = e.target.value; })}
        >
          <option value="acquisition">acquisition</option>
          <option value="nonreinforcement">nonreinforcement</option>
          <option value="compound_acquisition">compound_acquisition</option>
          <option value="differential_acquisition">differential_acquisition</option>
        </select>

        <label>Trials</label>
        <input
          type="range"
          min="1"
          max="500"
          value={active.params.n_trials || 100}
          onChange={(e) => updateActive((p) => { p.params.n_trials = +e.target.value; })}
        />
        <div>{active.params.n_trials || 100}</div>

        <label>Alpha</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={active.params.alpha ?? 0.2}
          onChange={(e) => updateActive((p) => { p.params.alpha = +e.target.value; })}
        />
        <div>{active.params.alpha ?? 0.2}</div>

        <label>Gamma</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={active.params.gamma ?? 0.0}
          onChange={(e) => updateActive((p) => { p.params.gamma = +e.target.value; })}
        />
        <div>{active.params.gamma ?? 0.0}</div>
      </div>

      <div className="panel">
        <h3>Payload</h3>
        <pre style={{ background: "#f5f5f5", padding: "1rem", borderRadius: "6px", overflowX: "auto" }}>
          {JSON.stringify(normalizedPayload, null, 2)}
        </pre>
      </div>

      <div className="panel">
        <button className="btn" onClick={onRun}>Run Experiment</button>
        <pre className={runError ? "error" : ""}>{runOutput}</pre>
      </div>

      <details className="panel">
        <summary>Legacy Builder (Advanced Controls)</summary>
        <iframe
          title="legacy-builder"
          src="/ui/builder_legacy.html"
          style={{ width: "100%", minHeight: "78vh", border: "1px solid #ddd", borderRadius: "6px", marginTop: "0.8rem" }}
        />
      </details>
      <div className="panel">
        <small>
          This slice keeps payload/run parity while advanced schema-driven editors remain in the legacy fallback.
        </small>
      </div>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<BuilderShellApp />);

window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click", "lever"];
const KNOWN_PRESETS = new Set([
  "aab_renewal",
  "aba_renewal",
  "abc_renewal",
  "acquisition",
  "basic_learning_curve",
  "blocking",
  "compound_acquisition",
  "conditioned_inhibition",
  "custom_protocol",
  "differential_acquisition",
  "extinction",
  "matching_law",
  "occasion_setting",
  "operant_conditioning",
  "rapid_reacquisition",
]);

function buildDefaultPhase(index) {
  return {
    name: `Phase ${index + 1}`,
    protocol: "acquisition",
    stimuli: { cs_plus: ["tone"] },
    params: { n_trials: 100, alpha: 0.2, gamma: 0.0 },
  };
}

function createInitialPayload() {
  return {
    experiment: {
      learner: "rescorla_wagner",
      agent: "classical_agent",
      representation: {
        name: "vector_elemental",
        params: { stimuli: STIMULI, max_compound_size: 2 },
      },
      context_inference: { enabled: false, max_contexts: 3 },
      salience: {},
      attention: {},
      phases: [buildDefaultPhase(0)],
    },
    report: { preset: "acquisition" },
  };
}

function normalizePayload(inputPayload) {
  const payload = JSON.parse(JSON.stringify(inputPayload));
  if (!payload.report) payload.report = { preset: "custom_protocol" };

  if (payload?.experiment?.attention) {
    Object.entries(payload.experiment.attention).forEach(([key, value]) => {
      if (value == null) return;
      if (typeof value === "number") {
        payload.experiment.attention[key] = { attention: value };
        return;
      }
      if (typeof value === "object" && typeof value.attention === "number") return;
      if (typeof value === "object" && value.attention == null && value.value != null) {
        payload.experiment.attention[key] = { attention: +value.value };
      }
    });
  }

  const phases = payload?.experiment?.phases || [];
  if (phases.length === 1) {
    const proto = phases[0].protocol;
    payload.report.preset = KNOWN_PRESETS.has(proto) ? proto : "custom_protocol";
  } else {
    payload.report.preset = "custom_protocol";
  }

  phases.forEach((phase) => {
    if (phase.protocol === "context_shift" && phase.stimuli) {
      delete phase.stimuli;
    }
  });

  return payload;
}

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

      <div className="panel">
        <h3>Phases</h3>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "0.7rem" }}>
          {phases.map((phase, idx) => (
            <button
              key={`${phase.name}-${idx}`}
              className="btn"
              onClick={() => setActivePhaseIndex(idx)}
              style={{ background: idx === activePhaseIndex ? "#dbeafe" : "#fff" }}
            >
              {phase.name}
            </button>
          ))}
        </div>
        <button className="btn" onClick={addPhase}>Add Phase</button>
      </div>

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

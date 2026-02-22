window.VSLReact = window.VSLReact || {};

const {
  buildDefaultPhase,
  createInitialPayload,
  normalizePayload,
  getAvailableStimuli,
  coercePhaseShape,
} = window.VSLReact.builderState;

const BuilderPhaseList = window.VSLReact.BuilderPhaseList;

function BuilderShellApp() {
  const [payload, setPayload] = React.useState(createInitialPayload);
  const [activePhaseIndex, setActivePhaseIndex] = React.useState(0);
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);

  const availableStimuli = React.useMemo(() => getAvailableStimuli(payload), [payload]);
  const normalizedPayload = React.useMemo(() => normalizePayload(payload), [payload]);
  const phases = payload.experiment.phases;
  const active = phases[activePhaseIndex] || phases[0];

  const addPhase = () => {
    setPayload((prev) => {
      const next = JSON.parse(JSON.stringify(prev));
      const stim = getAvailableStimuli(next);
      next.experiment.phases.push(buildDefaultPhase(next.experiment.phases.length, stim));
      return next;
    });
    setActivePhaseIndex(phases.length);
  };

  const updateActive = (updater) => {
    setPayload((prev) => {
      const next = JSON.parse(JSON.stringify(prev));
      const idx = Math.min(activePhaseIndex, next.experiment.phases.length - 1);
      updater(next.experiment.phases[idx], getAvailableStimuli(next));
      next.experiment.phases[idx] = coercePhaseShape(next.experiment.phases[idx], getAvailableStimuli(next));
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

  const protocol = active?.protocol || "acquisition";
  const isCompound = protocol === "compound_acquisition";
  const isDifferential = protocol === "differential_acquisition";
  const csPlus = active?.stimuli?.cs_plus?.[0] || availableStimuli[0];
  const csMinus = active?.stimuli?.cs_minus?.[0] || availableStimuli[1] || availableStimuli[0];
  const comp1 = active?.stimuli?.compound?.[0] || availableStimuli[0];
  const comp2 = active?.stimuli?.compound?.[1] || availableStimuli[1] || availableStimuli[0];

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
          value={protocol}
          onChange={(e) => updateActive((p, stim) => {
            p.protocol = e.target.value;
            p.stimuli = coercePhaseShape({ protocol: e.target.value, stimuli: p.stimuli, params: p.params, name: p.name }, stim).stimuli;
            p.params = coercePhaseShape({ protocol: e.target.value, stimuli: p.stimuli, params: p.params, name: p.name }, stim).params;
          })}
        >
          <option value="acquisition">acquisition</option>
          <option value="nonreinforcement">nonreinforcement</option>
          <option value="compound_acquisition">compound_acquisition</option>
          <option value="differential_acquisition">differential_acquisition</option>
        </select>

        {!isCompound && !isDifferential && (
          <>
            <label>CS+</label>
            <select
              value={csPlus}
              onChange={(e) => updateActive((p) => { p.stimuli = { cs_plus: [e.target.value] }; })}
            >
              {availableStimuli.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </>
        )}

        {isDifferential && (
          <>
            <label>CS+</label>
            <select
              value={csPlus}
              onChange={(e) => updateActive((p, stim) => {
                const plus = e.target.value;
                const fallback = (stim.find((x) => x !== plus) || plus);
                const minus = p.stimuli?.cs_minus?.[0] === plus ? fallback : (p.stimuli?.cs_minus?.[0] || fallback);
                p.stimuli = { cs_plus: [plus], cs_minus: [minus] };
              })}
            >
              {availableStimuli.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>

            <label>CS-</label>
            <select
              value={csMinus}
              onChange={(e) => updateActive((p, stim) => {
                const minus = e.target.value;
                const plus = p.stimuli?.cs_plus?.[0] || stim[0];
                p.stimuli = { cs_plus: [plus], cs_minus: [minus === plus ? (stim.find((x) => x !== plus) || plus) : minus] };
              })}
            >
              {availableStimuli.map((s) => <option key={s} value={s} disabled={s === csPlus}>{s}</option>)}
            </select>
          </>
        )}

        {isCompound && (
          <>
            <label>Compound Stimulus 1</label>
            <select
              value={comp1}
              onChange={(e) => updateActive((p, stim) => {
                const first = e.target.value;
                const second = p.stimuli?.compound?.[1] === first ? (stim.find((x) => x !== first) || first) : (p.stimuli?.compound?.[1] || stim[1] || first);
                p.stimuli = { compound: [first, second] };
              })}
            >
              {availableStimuli.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>

            <label>Compound Stimulus 2</label>
            <select
              value={comp2}
              onChange={(e) => updateActive((p, stim) => {
                const second = e.target.value;
                const first = p.stimuli?.compound?.[0] || stim[0];
                p.stimuli = { compound: [first, second === first ? (stim.find((x) => x !== first) || first) : second] };
              })}
            >
              {availableStimuli.map((s) => <option key={s} value={s} disabled={s === comp1}>{s}</option>)}
            </select>
          </>
        )}

        <label>Trials</label>
        <input
          type="range"
          min="1"
          max="500"
          value={active?.params?.n_trials || 100}
          onChange={(e) => updateActive((p) => { p.params.n_trials = +e.target.value; })}
        />
        <div>{active?.params?.n_trials || 100}</div>

        {!isCompound && (
          <>
            <label>Alpha</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={active?.params?.alpha ?? 0.2}
              onChange={(e) => updateActive((p) => { p.params.alpha = +e.target.value; })}
            />
            <div>{active?.params?.alpha ?? 0.2}</div>
          </>
        )}

        {isCompound && (
          <>
            <label>Alpha CS1</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={active?.params?.alpha_cs1 ?? 0.2}
              onChange={(e) => updateActive((p) => { p.params.alpha_cs1 = +e.target.value; })}
            />
            <div>{active?.params?.alpha_cs1 ?? 0.2}</div>

            <label>Alpha CS2</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={active?.params?.alpha_cs2 ?? 0.2}
              onChange={(e) => updateActive((p) => { p.params.alpha_cs2 = +e.target.value; })}
            />
            <div>{active?.params?.alpha_cs2 ?? 0.2}</div>
          </>
        )}

        <label>Gamma</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={active?.params?.gamma ?? 0.0}
          onChange={(e) => updateActive((p) => { p.params.gamma = +e.target.value; })}
        />
        <div>{active?.params?.gamma ?? 0.0}</div>
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

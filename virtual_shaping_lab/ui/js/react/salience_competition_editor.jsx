window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click"];

function buildPayload(params) {
  const compound = [params.stim_1, params.stim_2];
  return {
    experiment: {
      learner: "rescorla_wagner",
      agent: "classical_agent",
      representation: {
        name: params.representation,
        params: { stimuli: STIMULI, max_compound_size: 2 },
      },
      context_inference: { enabled: false, max_contexts: 3 },
      phases: [
        {
          name: "Salience Competition",
          protocol: "compound_acquisition",
          stimuli: { compound },
          params: {
            n_trials: params.n_trials,
            alpha_cs1: params.alpha_cs1,
            alpha_cs2: params.alpha_cs2,
            gamma: params.gamma,
          },
        },
      ],
      salience: {
        [params.stim_1]: { salience: params.salience_cs1 },
        [params.stim_2]: { salience: params.salience_cs2 },
      },
      attention: {
        [params.stim_1]: { attention: 1.0 },
        [params.stim_2]: { attention: 1.0 },
      },
    },
    report: { preset: "custom_protocol" },
  };
}

function validate(params) {
  if (params.n_trials < 1) throw new Error("n_trials must be at least 1");
  if (params.alpha_cs1 < 0 || params.alpha_cs1 > 1) throw new Error("alpha_cs1 must be 0-1");
  if (params.alpha_cs2 < 0 || params.alpha_cs2 > 1) throw new Error("alpha_cs2 must be 0-1");
  if (params.gamma < 0 || params.gamma > 1) throw new Error("gamma must be 0-1");
  if (params.salience_cs1 < 0 || params.salience_cs1 > 1) throw new Error("salience_cs1 must be 0-1");
  if (params.salience_cs2 < 0 || params.salience_cs2 > 1) throw new Error("salience_cs2 must be 0-1");
  if (params.stim_1 === params.stim_2) throw new Error("Stimulus A and B must be different");
}

function SalienceCompetitionApp() {
  const [params, setParams] = React.useState({
    n_trials: 160,
    alpha_cs1: 0.2,
    alpha_cs2: 0.2,
    gamma: 0.0,
    salience_cs1: 1.0,
    salience_cs2: 0.15,
    stim_1: "tone",
    stim_2: "noise",
    representation: "vector_elemental",
  });
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);
  const payload = React.useMemo(() => buildPayload(params), [params]);

  const onRun = async () => {
    setRunError(false);
    try {
      validate(params);
    } catch (err) {
      setRunError(true);
      setRunOutput(err.message);
      return;
    }

    setRunOutput("Running...");
    const res = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (res.ok && data.run_id) {
      window.location.href = `/ui/results.html?run_id=${data.run_id}`;
      return;
    }
    setRunOutput(JSON.stringify(data, null, 2));
    setRunError(true);
  };

  return (
    <>
      <h1>Salience-Driven Competition Preset</h1>
      <p>Compound acquisition with strong salience asymmetry to drive cue competition.</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>
          Back to Presets
        </button>
      </div>

      <div className="panel">
        <h3>Trials</h3>
        <label>Trials: <span>{params.n_trials}</span></label>
        <input type="range" min="1" max="500" value={params.n_trials} onChange={(e) => setParams((p) => ({ ...p, n_trials: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Learning</h3>
        <label>Alpha Cue A: <span>{params.alpha_cs1}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.alpha_cs1} onChange={(e) => setParams((p) => ({ ...p, alpha_cs1: +e.target.value }))} />
        <label>Alpha Cue B: <span>{params.alpha_cs2}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.alpha_cs2} onChange={(e) => setParams((p) => ({ ...p, alpha_cs2: +e.target.value }))} />
        <label>Gamma: <span>{params.gamma}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.gamma} onChange={(e) => setParams((p) => ({ ...p, gamma: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Salience</h3>
        <label>Cue A Salience: <span>{params.salience_cs1}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.salience_cs1} onChange={(e) => setParams((p) => ({ ...p, salience_cs1: +e.target.value }))} />
        <label>Cue B Salience: <span>{params.salience_cs2}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.salience_cs2} onChange={(e) => setParams((p) => ({ ...p, salience_cs2: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Stimuli</h3>
        <label>Cue A</label>
        <select value={params.stim_1} onChange={(e) => setParams((p) => ({ ...p, stim_1: e.target.value }))}>
          {STIMULI.map((s) => <option key={s} value={s} disabled={s === params.stim_2}>{s}</option>)}
        </select>
        <label>Cue B</label>
        <select value={params.stim_2} onChange={(e) => setParams((p) => ({ ...p, stim_2: e.target.value }))}>
          {STIMULI.map((s) => <option key={s} value={s} disabled={s === params.stim_1}>{s}</option>)}
        </select>
      </div>

      <h2>Generated Payload</h2>
      <pre>{JSON.stringify(payload, null, 2)}</pre>

      <button onClick={onRun}>Run Experiment</button>
      <pre className={runError ? "error" : ""}>{runOutput}</pre>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<SalienceCompetitionApp />);

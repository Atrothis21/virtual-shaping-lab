window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click"];

function buildPayload(params) {
  const compound = [params.stim_1, params.stim_2];
  const attentionMap = {
    [params.stim_1]: { attention: 1.0 },
    [params.stim_2]: { attention: 1.0 },
  };

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
          name: "Overexpectation: Acquisition",
          protocol: "acquisition",
          stimuli: { cs_plus: [params.stim_1, params.stim_2] },
          params: {
            n_trials: params.n_trials_1,
            alpha: params.alpha_1,
            gamma: params.gamma,
          },
        },
        {
          name: "Overexpectation: Compound",
          protocol: "compound_acquisition",
          stimuli: { compound },
          params: {
            n_trials: params.n_trials_2,
            alpha_cs1: params.alpha_cs1,
            alpha_cs2: params.alpha_cs2,
            gamma: params.gamma,
          },
        },
      ],
      attention: attentionMap,
    },
    report: { preset: "custom_protocol" },
  };
}

function validate(params) {
  if (params.n_trials_1 < 1) throw new Error("n_trials (phase 1) must be at least 1");
  if (params.n_trials_2 < 1) throw new Error("n_trials (phase 2) must be at least 1");
  if (params.alpha_1 < 0 || params.alpha_1 > 1) throw new Error("alpha (phase 1) must be 0-1");
  if (params.alpha_cs1 < 0 || params.alpha_cs1 > 1) throw new Error("alpha_cs1 must be 0-1");
  if (params.alpha_cs2 < 0 || params.alpha_cs2 > 1) throw new Error("alpha_cs2 must be 0-1");
  if (params.gamma < 0 || params.gamma > 1) throw new Error("gamma must be 0-1");
  if (params.stim_1 === params.stim_2) throw new Error("CS1 and CS2 must be different");
}

function OverexpectationApp() {
  const [params, setParams] = React.useState({
    n_trials_1: 80,
    n_trials_2: 80,
    alpha_1: 0.2,
    alpha_cs1: 0.2,
    alpha_cs2: 0.2,
    gamma: 0.0,
    stim_1: "tone",
    stim_2: "noise",
    representation: "vector_elemental",
  });
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);

  const payload = React.useMemo(() => buildPayload(params), [params]);

  const onStim1Change = (nextStim1) => {
    let nextStim2 = params.stim_2;
    if (nextStim1 === nextStim2) {
      nextStim2 = STIMULI.find((s) => s !== nextStim1) || nextStim2;
    }
    setParams((prev) => ({ ...prev, stim_1: nextStim1, stim_2: nextStim2 }));
  };

  const onStim2Change = (nextStim2) => {
    let nextStim1 = params.stim_1;
    if (nextStim2 === nextStim1) {
      nextStim1 = STIMULI.find((s) => s !== nextStim2) || nextStim1;
    }
    setParams((prev) => ({ ...prev, stim_1: nextStim1, stim_2: nextStim2 }));
  };

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
      <h1>Overexpectation Preset</h1>
      <p>Two-phase design: A+ and B+ intermixed, then AB+ compound.</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>Back to Presets</button>
      </div>

      <div className="panel">
        <h3>Trials</h3>
        <label>Phase 1 Trials: <span>{params.n_trials_1}</span></label>
        <input type="range" min="1" max="500" value={params.n_trials_1} onChange={(e) => setParams((p) => ({ ...p, n_trials_1: +e.target.value }))} />
        <label>Phase 2 Trials: <span>{params.n_trials_2}</span></label>
        <input type="range" min="1" max="500" value={params.n_trials_2} onChange={(e) => setParams((p) => ({ ...p, n_trials_2: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Learning</h3>
        <label>Alpha (Phase 1): <span>{params.alpha_1}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.alpha_1} onChange={(e) => setParams((p) => ({ ...p, alpha_1: +e.target.value }))} />
        <label>Alpha CS1 (Phase 2): <span>{params.alpha_cs1}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.alpha_cs1} onChange={(e) => setParams((p) => ({ ...p, alpha_cs1: +e.target.value }))} />
        <label>Alpha CS2 (Phase 2): <span>{params.alpha_cs2}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.alpha_cs2} onChange={(e) => setParams((p) => ({ ...p, alpha_cs2: +e.target.value }))} />
        <label>Discount (gamma): <span>{params.gamma}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.gamma} onChange={(e) => setParams((p) => ({ ...p, gamma: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Stimuli</h3>
        <label>CS1 (A)</label>
        <select value={params.stim_1} onChange={(e) => onStim1Change(e.target.value)}>
          {STIMULI.map((s) => <option key={s} value={s} disabled={s === params.stim_2}>{s}</option>)}
        </select>
        <label>CS2 (B)</label>
        <select value={params.stim_2} onChange={(e) => onStim2Change(e.target.value)}>
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
root.render(<OverexpectationApp />);

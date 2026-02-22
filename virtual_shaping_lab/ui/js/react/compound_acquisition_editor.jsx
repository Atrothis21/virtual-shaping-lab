window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click"];

function buildPayload(params) {
  const salienceMap = {
    [params.stim_1]: { salience: params.alpha_cs1 },
    [params.stim_2]: { salience: params.alpha_cs2 },
  };
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
          name: "Compound Acquisition",
          protocol: "compound_acquisition",
          stimuli: { compound: [params.stim_1, params.stim_2] },
          params: {
            n_trials: params.n_trials,
            alpha_cs1: params.alpha_cs1,
            alpha_cs2: params.alpha_cs2,
            gamma: params.gamma,
          },
        },
      ],
      salience: salienceMap,
      attention: attentionMap,
    },
    report: { preset: "compound_acquisition" },
  };
}

function validate(params) {
  if (params.n_trials < 1) throw new Error("n_trials must be at least 1");
  if (params.alpha_cs1 < 0 || params.alpha_cs1 > 1) throw new Error("alpha_cs1 must be 0-1");
  if (params.alpha_cs2 < 0 || params.alpha_cs2 > 1) throw new Error("alpha_cs2 must be 0-1");
  if (params.gamma < 0 || params.gamma > 1) throw new Error("gamma must be 0-1");
  if (params.stim_1 === params.stim_2) throw new Error("CS1 and CS2 must be different");
}

function CompoundAcquisitionApp() {
  const [params, setParams] = React.useState({
    n_trials: 100,
    alpha_cs1: 0.2,
    alpha_cs2: 0.12,
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
      <h1>Compound Acquisition Preset</h1>
      <p>Two stimuli are presented together on every trial (CS1 + CS2 -&gt; US).</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>
          Back to Presets
        </button>
        <a className="btn secondary" href="/ui/presets/compound_acquisition_legacy.html">Legacy Editor</a>
      </div>

      <div className="panel">
        <h3>Trials</h3>
        <label>Number of Trials: <span>{params.n_trials}</span></label>
        <input
          type="range"
          min="1"
          max="500"
          value={params.n_trials}
          onChange={(e) => setParams((prev) => ({ ...prev, n_trials: +e.target.value }))}
        />
      </div>

      <div className="panel">
        <h3>Learning</h3>
        <label>Alpha CS1 (salience): <span>{params.alpha_cs1}</span></label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={params.alpha_cs1}
          onChange={(e) => setParams((prev) => ({ ...prev, alpha_cs1: +e.target.value }))}
        />

        <label>Alpha CS2 (salience): <span>{params.alpha_cs2}</span></label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={params.alpha_cs2}
          onChange={(e) => setParams((prev) => ({ ...prev, alpha_cs2: +e.target.value }))}
        />

        <label>Discount (gamma): <span>{params.gamma}</span></label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={params.gamma}
          onChange={(e) => setParams((prev) => ({ ...prev, gamma: +e.target.value }))}
        />
      </div>

      <div className="panel">
        <h3>Stimuli</h3>
        <label>CS1</label>
        <select value={params.stim_1} onChange={(e) => onStim1Change(e.target.value)}>
          {STIMULI.map((s) => (
            <option key={s} value={s} disabled={s === params.stim_2}>{s}</option>
          ))}
        </select>

        <label>CS2</label>
        <select value={params.stim_2} onChange={(e) => onStim2Change(e.target.value)}>
          {STIMULI.map((s) => (
            <option key={s} value={s} disabled={s === params.stim_1}>{s}</option>
          ))}
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
root.render(<CompoundAcquisitionApp />);

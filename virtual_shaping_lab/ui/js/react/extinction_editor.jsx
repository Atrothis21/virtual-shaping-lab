window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click"];

function buildPayload(params) {
  const salienceMap = {};
  params.cs_plus.forEach((s) => {
    salienceMap[s] = { salience: params.salience };
  });

  const attentionMap = {};
  params.cs_plus.forEach((s) => {
    attentionMap[s] = { attention: 1.0 };
  });

  return {
    experiment: {
      learner: "rescorla_wagner",
      agent: "classical_agent",
      representation: {
        name: params.representation,
        params: { stimuli: STIMULI, max_compound_size: 2 },
      },
      context_inference: { enabled: false, max_contexts: 3 },
      protocol: "extinction",
      stimuli: { cs_plus: params.cs_plus },
      params: {
        n_acquisition_trials: params.n_acq,
        n_extinction_trials: params.n_ext,
        alpha: params.alpha,
        gamma: params.gamma,
      },
      salience: salienceMap,
      attention: attentionMap,
    },
    report: { preset: "extinction" },
  };
}

function validate(params) {
  if (params.n_acq < 1) throw new Error("n_acquisition_trials must be at least 1");
  if (params.n_ext < 1) throw new Error("n_extinction_trials must be at least 1");
  if (params.alpha < 0 || params.alpha > 1) throw new Error("alpha must be 0-1");
  if (params.gamma < 0 || params.gamma > 1) throw new Error("gamma must be 0-1");
  if (!params.cs_plus.length) throw new Error("Select at least one CS+ stimulus");
}

function ExtinctionApp() {
  const [params, setParams] = React.useState({
    n_acq: 50,
    n_ext: 50,
    alpha: 0.2,
    gamma: 0.0,
    cs_plus: ["tone"],
    salience: 1.0,
    representation: "vector_elemental",
  });
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);

  const payload = React.useMemo(() => buildPayload(params), [params]);

  const onCSPlusChange = (e) => {
    const next = Array.from(e.target.selectedOptions).map((o) => o.value);
    setParams((prev) => ({ ...prev, cs_plus: next }));
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
      <h1>Extinction Preset</h1>
      <p>Protocol: Acquisition (A+) followed by Nonreinforcement (A-).</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>
          Back to Presets
        </button>
      </div>

      <div className="panel">
        <h3>Trials</h3>
        <label>Acquisition Trials: <span>{params.n_acq}</span></label>
        <input
          type="range"
          min="1"
          max="500"
          value={params.n_acq}
          onChange={(e) => setParams((prev) => ({ ...prev, n_acq: +e.target.value }))}
        />

        <label>Extinction Trials: <span>{params.n_ext}</span></label>
        <input
          type="range"
          min="1"
          max="500"
          value={params.n_ext}
          onChange={(e) => setParams((prev) => ({ ...prev, n_ext: +e.target.value }))}
        />
      </div>

      <div className="panel">
        <h3>Learning</h3>
        <label>Learning Rate (alpha): <span>{params.alpha}</span></label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={params.alpha}
          onChange={(e) => setParams((prev) => ({ ...prev, alpha: +e.target.value }))}
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
        <label>CS</label>
        <select multiple value={params.cs_plus} onChange={onCSPlusChange}>
          {STIMULI.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        <label>Salience (applies to selected CS): <span>{params.salience}</span></label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={params.salience}
          onChange={(e) => setParams((prev) => ({ ...prev, salience: +e.target.value }))}
        />
      </div>

      <div className="panel">
        <h3>Representation</h3>
        <label>Type</label>
        <select
          value={params.representation}
          onChange={(e) => setParams((prev) => ({ ...prev, representation: e.target.value }))}
        >
          <option value="vector_elemental">vector_elemental</option>
          <option value="vector_configural">vector_configural</option>
          <option value="vector_hybrid">vector_hybrid</option>
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
root.render(<ExtinctionApp />);

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
      phases: [
        {
          name: "Salience-Dependent Acquisition",
          protocol: "acquisition",
          stimuli: { cs_plus: params.cs_plus },
          params: {
            n_trials: params.n_trials,
            alpha: params.alpha,
            gamma: params.gamma,
          },
        },
      ],
      salience: salienceMap,
      attention: attentionMap,
    },
    report: { preset: "custom_protocol" },
  };
}

function validate(params) {
  if (params.n_trials < 1) throw new Error("n_trials must be at least 1");
  if (params.alpha < 0 || params.alpha > 1) throw new Error("alpha must be 0-1");
  if (params.gamma < 0 || params.gamma > 1) throw new Error("gamma must be 0-1");
  if (params.salience < 0 || params.salience > 1) throw new Error("salience must be 0-1");
  if (!params.cs_plus.length) throw new Error("Select at least one CS+ stimulus");
}

function SalienceAcquisitionRateApp() {
  const [params, setParams] = React.useState({
    n_trials: 120,
    alpha: 0.2,
    gamma: 0.0,
    cs_plus: ["tone"],
    salience: 0.7,
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
      <h1>Salience-Dependent Acquisition Rate Preset</h1>
      <p>Acquisition preset focused on salience-driven differences in learning speed.</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>
          Back to Presets
        </button>
      </div>

      <div className="panel">
        <h3>Trials</h3>
        <label>Number of Trials: <span>{params.n_trials}</span></label>
        <input type="range" min="1" max="500" value={params.n_trials} onChange={(e) => setParams((prev) => ({ ...prev, n_trials: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Learning</h3>
        <label>Learning Rate (alpha): <span>{params.alpha}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.alpha} onChange={(e) => setParams((prev) => ({ ...prev, alpha: +e.target.value }))} />
        <label>Discount (gamma): <span>{params.gamma}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.gamma} onChange={(e) => setParams((prev) => ({ ...prev, gamma: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Stimuli</h3>
        <label>CS</label>
        <select multiple value={params.cs_plus} onChange={(e) => setParams((prev) => ({ ...prev, cs_plus: Array.from(e.target.selectedOptions).map((o) => o.value) }))}>
          {STIMULI.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <label>Salience (selected CS): <span>{params.salience}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.salience} onChange={(e) => setParams((prev) => ({ ...prev, salience: +e.target.value }))} />
      </div>

      <h2>Generated Payload</h2>
      <pre>{JSON.stringify(payload, null, 2)}</pre>

      <button onClick={onRun}>Run Experiment</button>
      <pre className={runError ? "error" : ""}>{runOutput}</pre>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<SalienceAcquisitionRateApp />);

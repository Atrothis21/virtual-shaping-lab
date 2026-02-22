window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click"];
const CONTEXTS = ["A", "B", "C"];

function buildPayload(params) {
  const salienceMap = {};
  salienceMap[params.cs_plus] = { salience: params.salience };
  const attentionMap = {};
  attentionMap[params.cs_plus] = { attention: 1.0 };

  return {
    experiment: {
      learner: "rescorla_wagner",
      agent: "classical_agent",
      representation: {
        name: "vector_hybrid",
        params: {
          stimuli: [...STIMULI],
          max_compound_size: 2,
          include_global: true,
          include_context: true,
        },
      },
      context_inference: { enabled: false, max_contexts: 3 },
      protocol: "aba_renewal",
      stimuli: {
        cs_plus: [params.cs_plus],
        cs_minus: [],
      },
      params: {
        n_acquisition_trials: params.n_acq,
        n_extinction_trials: params.n_ext,
        n_probe_trials: params.n_probe,
        alpha: params.alpha,
        gamma: params.gamma,
        context_a: params.context_a,
        context_b: params.context_b,
      },
      salience: salienceMap,
      attention: attentionMap,
    },
    report: { preset: "aba_renewal" },
  };
}

function validate(params) {
  if (params.n_acq < 1) throw new Error("n_acquisition_trials must be at least 1");
  if (params.n_ext < 1) throw new Error("n_extinction_trials must be at least 1");
  if (params.n_probe < 1) throw new Error("n_probe_trials must be at least 1");
  if (params.alpha < 0 || params.alpha > 1) throw new Error("alpha must be 0-1");
  if (params.gamma < 0 || params.gamma > 1) throw new Error("gamma must be 0-1");
  if (!params.cs_plus) throw new Error("Select a CS stimulus");
  if (!params.context_a) throw new Error("Context A is required");
  if (!params.context_b) throw new Error("Context B is required");
}

function ABARenewalApp() {
  const [params, setParams] = React.useState({
    n_acq: 50,
    n_ext: 50,
    n_probe: 20,
    alpha: 0.2,
    gamma: 0.0,
    cs_plus: "tone",
    salience: 1.0,
    context_a: "A",
    context_b: "B",
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
      <h1>ABA Renewal Preset</h1>
      <p>Protocol: Acquisition in A -&gt; Extinction in B -&gt; Probe in A.</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>Back to Presets</button>
      </div>

      <div className="panel">
        <h3>Trials</h3>
        <label>Acquisition Trials: <span>{params.n_acq}</span></label>
        <input type="range" min="1" max="500" value={params.n_acq} onChange={(e) => setParams((p) => ({ ...p, n_acq: +e.target.value }))} />
        <label>Extinction Trials: <span>{params.n_ext}</span></label>
        <input type="range" min="1" max="500" value={params.n_ext} onChange={(e) => setParams((p) => ({ ...p, n_ext: +e.target.value }))} />
        <label>Probe Trials: <span>{params.n_probe}</span></label>
        <input type="range" min="1" max="200" value={params.n_probe} onChange={(e) => setParams((p) => ({ ...p, n_probe: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Learning</h3>
        <label>Learning Rate (alpha): <span>{params.alpha}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.alpha} onChange={(e) => setParams((p) => ({ ...p, alpha: +e.target.value }))} />
        <label>Discount (gamma): <span>{params.gamma}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.gamma} onChange={(e) => setParams((p) => ({ ...p, gamma: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Stimuli</h3>
        <label>CS (single select)</label>
        <select value={params.cs_plus} onChange={(e) => setParams((p) => ({ ...p, cs_plus: e.target.value }))}>
          {STIMULI.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <label>Salience (applies to CS): <span>{params.salience}</span></label>
        <input type="range" min="0" max="1" step="0.05" value={params.salience} onChange={(e) => setParams((p) => ({ ...p, salience: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Context</h3>
        <label>Context A</label>
        <select value={params.context_a} onChange={(e) => setParams((p) => ({ ...p, context_a: e.target.value }))}>
          {CONTEXTS.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <label>Context B</label>
        <select value={params.context_b} onChange={(e) => setParams((p) => ({ ...p, context_b: e.target.value }))}>
          {CONTEXTS.map((c) => <option key={c} value={c}>{c}</option>)}
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
root.render(<ABARenewalApp />);


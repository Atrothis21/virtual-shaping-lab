window.VSLReact = window.VSLReact || {};
const STIMULI = ["tone", "noise", "light", "click"];

function buildPayload(params) {
  const attentionOverrides = {};
  params.cs_plus.forEach((s) => { attentionOverrides[s] = params.attention; });
  return {
    experiment: {
      learner: "rescorla_wagner",
      agent: "classical_agent",
      representation: { name: "vector_elemental", params: { stimuli: STIMULI, max_compound_size: 2 } },
      context_inference: { enabled: false, max_contexts: 3 },
      phases: [
        {
          name: "Hall-Pearce: Weak Acquisition",
          protocol: "acquisition",
          stimuli: { cs_plus: params.cs_plus },
          params: { n_trials: params.weak_n_trials, alpha: params.alpha, gamma: params.gamma, outcome: params.weak_outcome },
        },
        {
          name: "Hall-Pearce: Strong Acquisition",
          protocol: "acquisition",
          stimuli: { cs_plus: params.cs_plus },
          params: { n_trials: params.strong_n_trials, alpha: params.alpha, gamma: params.gamma, outcome: params.strong_outcome },
        },
      ],
      attention_config: {
        name: "pearce_hall",
        params: { default: 1.0, overrides: attentionOverrides, eta: 0.2 },
      },
    },
    report: { preset: "custom_protocol" },
  };
}

function validate(params) {
  if (params.weak_n_trials < 1 || params.strong_n_trials < 1) throw new Error("Trial counts must be at least 1");
  if (params.alpha < 0 || params.alpha > 1) throw new Error("alpha must be 0-1");
  if (params.gamma < 0 || params.gamma > 1) throw new Error("gamma must be 0-1");
  if (params.attention < 0 || params.attention > 1) throw new Error("attention must be 0-1");
  if (!params.cs_plus.length) throw new Error("Select at least one CS stimulus");
}

function App() {
  const [params, setParams] = React.useState({
    weak_n_trials: 60, strong_n_trials: 120, weak_outcome: 0.3, strong_outcome: 1.0, alpha: 0.2, gamma: 0.0, attention: 0.4, cs_plus: ["tone"],
  });
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);
  const payload = React.useMemo(() => buildPayload(params), [params]);

  const onRun = async () => {
    setRunError(false);
    try { validate(params); } catch (err) { setRunError(true); setRunOutput(err.message); return; }
    setRunOutput("Running...");
    const res = await fetch("/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const data = await res.json();
    if (res.ok && data.run_id) { window.location.href = `/ui/results.html?run_id=${data.run_id}`; return; }
    setRunOutput(JSON.stringify(data, null, 2)); setRunError(true);
  };

  return (
    <>
      <h1>Hall-Pearce Negative Transfer (Attention) Preset</h1>
      <p>Weak acquisition followed by strong acquisition on the same cue.</p>
      <div className="actions"><button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>Back to Presets</button></div>
      <div className="panel"><h3>What This Preset Shows</h3><p>Weak initial training can lower attention and slow later strong learning.</p></div>
      <div className="panel"><h3>Attention</h3><p><strong>All other parameters held constant.</strong></p><p>CS ({params.cs_plus.join(", ")}) Attention: <strong>{params.attention}</strong></p></div>
      <div className="panel"><h3>Stimuli</h3><label>CS</label><select multiple value={params.cs_plus} onChange={(e) => setParams((p) => ({ ...p, cs_plus: Array.from(e.target.selectedOptions).map((o) => o.value) }))}>{STIMULI.map((s) => <option key={s} value={s}>{s}</option>)}</select></div>
      <h2>Generated Payload</h2>
      <pre>{JSON.stringify(payload, null, 2)}</pre>
      <button onClick={onRun}>Run Experiment</button>
      <pre className={runError ? "error" : ""}>{runOutput}</pre>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);

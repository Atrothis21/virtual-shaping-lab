window.VSLReact = window.VSLReact || {};
const STIMULI = ["tone", "noise", "light", "click"];

function buildPayload(params) {
  const attentionOverrides = {
    [params.stim_1]: params.attention_cs1,
    [params.stim_2]: params.attention_cs2,
  };
  const payload = {
    experiment: {
      learner: "rescorla_wagner",
      agent: "classical_agent",
      representation: { name: "vector_elemental", params: { stimuli: STIMULI, max_compound_size: 2 } },
      context_inference: { enabled: false, max_contexts: 3 },
      phases: [
        { name: "Associability Shift: Acquisition", protocol: "acquisition", stimuli: { cs_plus: [params.stim_1] }, params: { n_trials: params.acq_n_trials, alpha: params.alpha, gamma: params.gamma } },
        { name: "Associability Shift: Compound", protocol: "compound_acquisition", stimuli: { compound: [params.stim_1, params.stim_2] }, params: { n_trials: params.comp_n_trials, alpha_cs1: params.alpha, alpha_cs2: params.alpha, gamma: params.gamma } },
      ],
      attention_config: {
        name: "mackintosh",
        params: { default: 1.0, overrides: attentionOverrides, kappa: 0.1 },
      },
    },
    report: { preset: "custom_protocol" },
  };

  return window.VSLReact.toCanonicalPayload(payload);
}

function validate(params) {
  if (params.acq_n_trials < 1 || params.comp_n_trials < 1) throw new Error("Trial counts must be at least 1");
  if (params.alpha < 0 || params.alpha > 1) throw new Error("alpha must be 0-1");
  if (params.gamma < 0 || params.gamma > 1) throw new Error("gamma must be 0-1");
  if (params.attention_cs1 < 0 || params.attention_cs1 > 1) throw new Error("attention_cs1 must be 0-1");
  if (params.attention_cs2 < 0 || params.attention_cs2 > 1) throw new Error("attention_cs2 must be 0-1");
  if (params.stim_1 === params.stim_2) throw new Error("Stimulus A and B must be different");
}

function App() {
  const [params, setParams] = React.useState({
    acq_n_trials: 100, comp_n_trials: 120, alpha: 0.2, gamma: 0.0, attention_cs1: 1.0, attention_cs2: 0.5, stim_1: "tone", stim_2: "noise",
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
      <h1>Associability Shifts (Attention) Preset</h1>
      <p>Single-cue acquisition followed by compound acquisition.</p>
      <div className="actions"><button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>Back to Presets</button></div>
      <div className="panel"><h3>What This Preset Shows</h3><p>Attention can redistribute as learning transitions from a single cue to a cue compound.</p></div>
      <div className="panel"><h3>Attention</h3><p><strong>All other parameters held constant.</strong></p><p>Cue A ({params.stim_1}) Attention: <strong>{params.attention_cs1}</strong></p><p>Cue B ({params.stim_2}) Attention: <strong>{params.attention_cs2}</strong></p></div>
      <div className="panel">
        <h3>Stimuli</h3>
        <label>Cue A</label>
        <select value={params.stim_1} onChange={(e) => {
          const nextStim1 = e.target.value;
          const nextStim2 = nextStim1 === params.stim_2 ? (STIMULI.find((s) => s !== nextStim1) || params.stim_2) : params.stim_2;
          setParams((p) => ({ ...p, stim_1: nextStim1, stim_2: nextStim2 }));
        }}>
          {STIMULI.map((s) => <option key={s} value={s} disabled={s === params.stim_2}>{s}</option>)}
        </select>
        <label>Cue B</label>
        <select value={params.stim_2} onChange={(e) => {
          const nextStim2 = e.target.value;
          const nextStim1 = nextStim2 === params.stim_1 ? (STIMULI.find((s) => s !== nextStim2) || params.stim_1) : params.stim_1;
          setParams((p) => ({ ...p, stim_1: nextStim1, stim_2: nextStim2 }));
        }}>
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
root.render(<App />);

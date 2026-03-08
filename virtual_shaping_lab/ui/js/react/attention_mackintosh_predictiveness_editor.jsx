window.VSLReact = window.VSLReact || {};
const STIMULI = ["tone", "noise", "light", "click"];

function buildPayload(params) {
  const attention = {};
  params.cs_plus.forEach((s) => { attention[s] = { attention: params.attention_plus }; });
  params.cs_minus.forEach((s) => { attention[s] = { attention: params.attention_minus }; });
  return {
    experiment: {
      learner: "rescorla_wagner",
      agent: "classical_agent",
      representation: { name: "vector_elemental", params: { stimuli: STIMULI, max_compound_size: 2 } },
      context_inference: { enabled: false, max_contexts: 3 },
      phases: [{ name: "Mackintosh Predictiveness", protocol: "differential_acquisition", stimuli: { cs_plus: params.cs_plus, cs_minus: params.cs_minus }, params: { n_trials: params.n_trials, alpha: params.alpha } }],
      attention,
    },
    report: { preset: "custom_protocol" },
  };
}

function validate(params) {
  if (params.n_trials < 1) throw new Error("n_trials must be at least 1");
  if (params.alpha < 0 || params.alpha > 1) throw new Error("alpha must be 0-1");
  if (params.attention_plus < 0 || params.attention_plus > 1) throw new Error("CS+ attention must be 0-1");
  if (params.attention_minus < 0 || params.attention_minus > 1) throw new Error("CS- attention must be 0-1");
  if (!params.cs_plus.length || !params.cs_minus.length) throw new Error("Select CS+ and CS- stimuli");
}

function App() {
  const [params, setParams] = React.useState({ n_trials: 140, alpha: 0.2, attention_plus: 1.0, attention_minus: 0.35, cs_plus: ["tone"], cs_minus: ["noise"] });
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);
  const payload = React.useMemo(() => buildPayload(params), [params]);
  const onCSPlus = (e) => { const plus = Array.from(e.target.selectedOptions).map((o) => o.value); setParams((p) => ({ ...p, cs_plus: plus, cs_minus: p.cs_minus.filter((s) => !plus.includes(s)) })); };
  const onCSMinus = (e) => { const minus = Array.from(e.target.selectedOptions).map((o) => o.value); setParams((p) => ({ ...p, cs_minus: minus, cs_plus: p.cs_plus.filter((s) => !minus.includes(s)) })); };
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
      <h1>Mackintosh Predictiveness Effect (Attention) Preset</h1>
      <p>Differential acquisition with predictive vs nonpredictive cue attention bias.</p>
      <div className="actions"><button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>Back to Presets</button></div>
      <div className="panel"><h3>What This Preset Shows</h3><p>Predictive cues can gain more attention than nonpredictive alternatives.</p></div>
      <div className="panel"><h3>Attention</h3><p><strong>All other parameters held constant.</strong></p><p>CS+ ({params.cs_plus.join(", ")}) Attention: <strong>{params.attention_plus}</strong></p><p>CS- ({params.cs_minus.join(", ")}) Attention: <strong>{params.attention_minus}</strong></p></div>
      <div className="panel"><h3>Stimuli</h3><label>CS+ Stimuli</label><select multiple value={params.cs_plus} onChange={onCSPlus}>{STIMULI.map((s) => <option key={s} value={s} disabled={params.cs_minus.includes(s)}>{s}</option>)}</select><br /><br /><label>CS- Stimuli</label><select multiple value={params.cs_minus} onChange={onCSMinus}>{STIMULI.map((s) => <option key={s} value={s} disabled={params.cs_plus.includes(s)}>{s}</option>)}</select></div>
      <h2>Generated Payload</h2>
      <pre>{JSON.stringify(payload, null, 2)}</pre>
      <button onClick={onRun}>Run Experiment</button>
      <pre className={runError ? "error" : ""}>{runOutput}</pre>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);

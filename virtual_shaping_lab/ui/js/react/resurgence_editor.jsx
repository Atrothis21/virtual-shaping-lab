window.VSLReact = window.VSLReact || {};

const STIMULI = ["lever", "tone", "noise", "light", "click"];

function buildPayload(params) {
  return {
    experiment: {
      learner: "q_learner",
      agent: "operant_agent",
      policy: {
        name: "softmax",
        params: {
          actions: [params.action_left, params.action_right],
          temperature: params.temperature,
        },
      },
      representation: {
        name: "vector_elemental",
        params: { stimuli: STIMULI, max_compound_size: 2 },
      },
      context_inference: { enabled: false, max_contexts: 3 },
      protocol: "resurgence",
      stimuli: { cs_plus: [params.cs_plus] },
      params: {
        n_acquisition_trials: params.n_acquisition_trials,
        n_suppression_trials: params.n_suppression_trials,
        n_resurgence_trials: params.n_resurgence_trials,
        acquisition_schedule: { type: "fixed_ratio", value: params.acq_fr, reward: 1.0 },
        suppression_schedule: { type: "fixed_ratio", value: 1, reward: 0.0 },
        resurgence_schedule: { type: "fixed_ratio", value: params.resurgence_fr, reward: 1.0 },
      },
    },
    report: { preset: "resurgence" },
  };
}

function ResurgenceApp() {
  const [params, setParams] = React.useState({
    cs_plus: "lever",
    n_acquisition_trials: 40,
    n_suppression_trials: 40,
    n_resurgence_trials: 30,
    acq_fr: 1,
    resurgence_fr: 1,
    action_left: "left",
    action_right: "right",
    temperature: 0.8,
  });
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);

  const payload = React.useMemo(() => buildPayload(params), [params]);

  const onRun = async () => {
    setRunError(false);
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
      <h1>Resurgence Preset</h1>
      <p>Reinforcement, suppression, and recovery blocks for operant response return.</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>
          Back to Presets
        </button>
      </div>

      <div className="panel">
        <h3>Stimulus</h3>
        <label>CS+</label>
        <select value={params.cs_plus} onChange={(e) => setParams((p) => ({ ...p, cs_plus: e.target.value }))}>
          {STIMULI.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="panel">
        <h3>Actions</h3>
        <label>Action Label 1</label>
        <input type="text" value={params.action_left} onChange={(e) => setParams((p) => ({ ...p, action_left: e.target.value || "left" }))} />
        <label>Action Label 2</label>
        <input type="text" value={params.action_right} onChange={(e) => setParams((p) => ({ ...p, action_right: e.target.value || "right" }))} />
        <label>Softmax Temperature: <span>{params.temperature}</span></label>
        <input type="range" min="0.1" max="3" step="0.1" value={params.temperature} onChange={(e) => setParams((p) => ({ ...p, temperature: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Block Trials</h3>
        <label>Acquisition: <span>{params.n_acquisition_trials}</span></label>
        <input type="range" min="10" max="150" value={params.n_acquisition_trials} onChange={(e) => setParams((p) => ({ ...p, n_acquisition_trials: +e.target.value }))} />
        <label>Suppression: <span>{params.n_suppression_trials}</span></label>
        <input type="range" min="10" max="150" value={params.n_suppression_trials} onChange={(e) => setParams((p) => ({ ...p, n_suppression_trials: +e.target.value }))} />
        <label>Recovery: <span>{params.n_resurgence_trials}</span></label>
        <input type="range" min="10" max="150" value={params.n_resurgence_trials} onChange={(e) => setParams((p) => ({ ...p, n_resurgence_trials: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Reinforcement Demand</h3>
        <label>Acquisition FR: <span>{params.acq_fr}</span></label>
        <input type="range" min="1" max="10" value={params.acq_fr} onChange={(e) => setParams((p) => ({ ...p, acq_fr: +e.target.value }))} />
        <label>Recovery FR: <span>{params.resurgence_fr}</span></label>
        <input type="range" min="1" max="10" value={params.resurgence_fr} onChange={(e) => setParams((p) => ({ ...p, resurgence_fr: +e.target.value }))} />
      </div>

      <h2>Generated Payload</h2>
      <pre>{JSON.stringify(payload, null, 2)}</pre>

      <button onClick={onRun}>Run Experiment</button>
      <pre className={runError ? "error" : ""}>{runOutput}</pre>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<ResurgenceApp />);

window.VSLReact = window.VSLReact || {};

const STIMULI = ["lever", "tone", "noise", "light", "click"];
const OPERANT_ACTIONS = window.VSLReact.OPERANT_ACTIONS || ["nosepoke_L", "nosepoke_R", "leverpress", "keypeck"];

function buildPayload(params) {
  const payload = {
    experiment: {
      learner: "q_learner",
      agent: "operant_agent",
      policy: {
        name: "softmax",
        params: {
          actions: [params.action],
          temperature: params.temperature,
        },
      },
      representation: {
        name: "vector_hybrid",
        params: {
          stimuli: STIMULI,
          max_compound_size: 2,
          include_context: true,
          include_global: true,
        },
      },
      context_inference: { enabled: false, max_contexts: 3 },
      protocol: "spontaneous_recovery",
      params: {
        n_acquisition_trials: params.n_acquisition_trials,
        n_extinction_trials: params.n_extinction_trials,
        n_probe_trials: params.n_probe_trials,
        context_a: params.context_a,
        context_b: params.context_b,
        acquisition_schedule: { type: "fixed_ratio", value: params.acq_fr, reward: 1.0 },
        extinction_schedule: { type: "fixed_ratio", value: params.ext_fr, reward: 0.0 },
        probe_schedule: { type: "fixed_ratio", value: params.probe_fr, reward: 0.0 },
      },
    },
    report: { preset: "spontaneous_recovery" },
  };

  return window.VSLReact.toCanonicalPayload(payload);
}

function SpontaneousRecoveryApp() {
  const [params, setParams] = React.useState({
    n_acquisition_trials: 40,
    n_extinction_trials: 40,
    n_probe_trials: 30,
    acq_fr: 1,
    ext_fr: 1,
    probe_fr: 1,
    context_a: "A",
    context_b: "B",
    action: "leverpress",
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
      <h1>Spontaneous Recovery Preset</h1>
      <p>Operant acquisition and extinction across contexts with recovery probe.</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>
          Back to Presets
        </button>
      </div>

      <div className="panel">
        <h3>Actions</h3>
        <label>Action</label>
        <select value={params.action} onChange={(e) => setParams((p) => ({ ...p, action: e.target.value }))}>
          {OPERANT_ACTIONS.map((action) => <option key={action} value={action}>{action}</option>)}
        </select>
        <label>Softmax Temperature: <span>{params.temperature}</span></label>
        <input type="range" min="0.1" max="3" step="0.1" value={params.temperature} onChange={(e) => setParams((p) => ({ ...p, temperature: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Contexts</h3>
        <label>Acquisition/Probe Context</label>
        <select value={params.context_a} onChange={(e) => setParams((p) => ({ ...p, context_a: e.target.value }))}>
          <option value="A">A</option>
          <option value="B">B</option>
          <option value="C">C</option>
        </select>
        <label>Extinction Context</label>
        <select value={params.context_b} onChange={(e) => setParams((p) => ({ ...p, context_b: e.target.value }))}>
          <option value="A">A</option>
          <option value="B">B</option>
          <option value="C">C</option>
        </select>
      </div>

      <div className="panel">
        <h3>Block Trials</h3>
        <label>Acquisition: <span>{params.n_acquisition_trials}</span></label>
        <input type="range" min="10" max="200" value={params.n_acquisition_trials} onChange={(e) => setParams((p) => ({ ...p, n_acquisition_trials: +e.target.value }))} />
        <label>Extinction: <span>{params.n_extinction_trials}</span></label>
        <input type="range" min="10" max="200" value={params.n_extinction_trials} onChange={(e) => setParams((p) => ({ ...p, n_extinction_trials: +e.target.value }))} />
        <label>Probe: <span>{params.n_probe_trials}</span></label>
        <input type="range" min="10" max="150" value={params.n_probe_trials} onChange={(e) => setParams((p) => ({ ...p, n_probe_trials: +e.target.value }))} />
      </div>

      <h2>Generated Payload</h2>
      <pre>{JSON.stringify(payload, null, 2)}</pre>

      <button onClick={onRun}>Run Experiment</button>
      <pre className={runError ? "error" : ""}>{runOutput}</pre>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<SpontaneousRecoveryApp />);

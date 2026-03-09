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
        name: "vector_elemental",
        params: { stimuli: STIMULI, max_compound_size: 2 },
      },
      context_inference: { enabled: false, max_contexts: 3 },
      protocol: "superextinction",
      params: {
        n_acquisition_trials: params.n_acquisition_trials,
        n_superextinction_trials: params.n_superextinction_trials,
        acquisition_schedule: { type: "fixed_ratio", value: params.acq_fr, reward: 1.0 },
        superextinction_schedule: { type: "fixed_ratio", value: params.punish_fr, reward: params.punishment_reward },
      },
    },
    report: { preset: "superextinction" },
  };

  return window.VSLReact.toCanonicalPayload(payload);
}

function SuperextinctionApp() {
  const [params, setParams] = React.useState({
    n_acquisition_trials: 50,
    n_superextinction_trials: 50,
    acq_fr: 1,
    punish_fr: 1,
    punishment_reward: -1.0,
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
      <h1>Superextinction Preset</h1>
      <p>Acquisition followed by explicit punishment-driven suppression.</p>

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
        <h3>Block Trials</h3>
        <label>Acquisition: <span>{params.n_acquisition_trials}</span></label>
        <input type="range" min="10" max="200" value={params.n_acquisition_trials} onChange={(e) => setParams((p) => ({ ...p, n_acquisition_trials: +e.target.value }))} />
        <label>Punishment: <span>{params.n_superextinction_trials}</span></label>
        <input type="range" min="10" max="200" value={params.n_superextinction_trials} onChange={(e) => setParams((p) => ({ ...p, n_superextinction_trials: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Contingencies</h3>
        <label>Acquisition FR: <span>{params.acq_fr}</span></label>
        <input type="range" min="1" max="10" value={params.acq_fr} onChange={(e) => setParams((p) => ({ ...p, acq_fr: +e.target.value }))} />
        <label>Punishment FR: <span>{params.punish_fr}</span></label>
        <input type="range" min="1" max="10" value={params.punish_fr} onChange={(e) => setParams((p) => ({ ...p, punish_fr: +e.target.value }))} />
        <label>Punishment Reward: <span>{params.punishment_reward.toFixed(1)}</span></label>
        <input type="range" min="-3" max="-0.1" step="0.1" value={params.punishment_reward} onChange={(e) => setParams((p) => ({ ...p, punishment_reward: +e.target.value }))} />
      </div>

      <h2>Generated Payload</h2>
      <pre>{JSON.stringify(payload, null, 2)}</pre>

      <button onClick={onRun}>Run Experiment</button>
      <pre className={runError ? "error" : ""}>{runOutput}</pre>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<SuperextinctionApp />);

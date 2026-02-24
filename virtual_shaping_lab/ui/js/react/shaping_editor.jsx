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
      protocol: "shaping",
      stimuli: { cs_plus: [params.cs_plus] },
      params: {
        n_stage_1_trials: params.n_stage_1_trials,
        n_stage_2_trials: params.n_stage_2_trials,
        schedule_stage_1: { type: "fixed_ratio", value: params.fr_stage_1, reward: 1.0 },
        schedule_stage_2: { type: "fixed_ratio", value: params.fr_stage_2, reward: 1.0 },
      },
    },
    report: { preset: "shaping" },
  };
}

function ShapingApp() {
  const [params, setParams] = React.useState({
    cs_plus: "lever",
    n_stage_1_trials: 60,
    n_stage_2_trials: 60,
    fr_stage_1: 1,
    fr_stage_2: 5,
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
      <h1>Shaping Preset</h1>
      <p>Two-stage operant shaping with increasing fixed-ratio demand.</p>

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
        <h3>Stage 1</h3>
        <label>Trials: <span>{params.n_stage_1_trials}</span></label>
        <input type="range" min="10" max="200" value={params.n_stage_1_trials} onChange={(e) => setParams((p) => ({ ...p, n_stage_1_trials: +e.target.value }))} />
        <label>FR Value: <span>{params.fr_stage_1}</span></label>
        <input type="range" min="1" max="10" value={params.fr_stage_1} onChange={(e) => setParams((p) => ({ ...p, fr_stage_1: +e.target.value }))} />
      </div>

      <div className="panel">
        <h3>Stage 2</h3>
        <label>Trials: <span>{params.n_stage_2_trials}</span></label>
        <input type="range" min="10" max="200" value={params.n_stage_2_trials} onChange={(e) => setParams((p) => ({ ...p, n_stage_2_trials: +e.target.value }))} />
        <label>FR Value: <span>{params.fr_stage_2}</span></label>
        <input type="range" min="2" max="20" value={params.fr_stage_2} onChange={(e) => setParams((p) => ({ ...p, fr_stage_2: +e.target.value }))} />
      </div>

      <h2>Generated Payload</h2>
      <pre>{JSON.stringify(payload, null, 2)}</pre>

      <button onClick={onRun}>Run Experiment</button>
      <pre className={runError ? "error" : ""}>{runOutput}</pre>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<ShapingApp />);

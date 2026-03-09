window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click"];
const FIXED_PARAMS = Object.freeze({
  n_acq: 50,
  n_comp: 50,
  alpha: 0.2,
  stim_a: "tone",
  stim_x: "noise",
  salience_a: 1.0,
  salience_x: 0.5,
  representation: "vector_elemental",
});

function buildPayload(params) {
  const salienceMap = {
    [params.stim_a]: { salience: params.salience_a },
    [params.stim_x]: { salience: params.salience_x },
  };
  const attentionMap = {};
  Object.keys(salienceMap).forEach((s) => {
    attentionMap[s] = { attention: 1.0 };
  });

  const payload = {
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
          name: "Blocking Acquisition",
          protocol: "acquisition",
          stimuli: { cs_plus: [params.stim_a] },
          params: {
            n_trials: params.n_acq,
            alpha: params.alpha,
          },
        },
        {
          name: "Blocking Compound",
          protocol: "compound_acquisition",
          stimuli: { compound: [params.stim_a, params.stim_x] },
          params: {
            n_trials: params.n_comp,
            alpha: params.alpha,
          },
        },
      ],
      salience: salienceMap,
      attention: attentionMap,
    },
    report: { preset: "blocking" },
  };

  return window.VSLReact.toCanonicalPayload(payload);
}

function validate(params) {
  if (params.n_acq < 1) throw new Error("n_acquisition_trials must be at least 1");
  if (params.n_comp < 1) throw new Error("n_compound_trials must be at least 1");
  if (params.alpha < 0 || params.alpha > 1) throw new Error("alpha must be 0-1");
  if (!params.stim_a || !params.stim_x) throw new Error("Select A and X");
  if (params.stim_a === params.stim_x) throw new Error("A and X must be different");
}

function BlockingApp() {
  const params = FIXED_PARAMS;
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);

  const payload = React.useMemo(() => buildPayload(params), []);

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
      <h1>Blocking Preset</h1>
      <p>Protocol: A+ acquisition followed by AX+ compound acquisition (blocking).</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>
          Back to Presets
        </button>
      </div>

      <div className="panel">
        <h3>Phase Composition (Read-Only)</h3>
        <p><strong>All other parameters held constant.</strong></p>
        <p><strong>Phase 1:</strong> acquisition ({params.stim_a}+) for {params.n_acq} trials</p>
        <p><strong>Phase 2:</strong> compound_acquisition ({params.stim_a}{params.stim_x}+) for {params.n_comp} trials</p>
      </div>

      <div className="panel">
        <h3>Fixed Parameters (Read-Only)</h3>
        <p>Representation: <strong>{params.representation}</strong></p>
        <p>Learning Rate (alpha): <strong>{params.alpha}</strong></p>
      </div>

      <div className="panel">
        <h3>Stimuli</h3>
        <label>CS+ A (Read-Only)</label>
        <select value={params.stim_a} disabled>
          {STIMULI.map((s) => (
            <option key={s} value={s} disabled={s === params.stim_x}>{s}</option>
          ))}
        </select>

        <label>CS+ X (Read-Only)</label>
        <select value={params.stim_x} disabled>
          {STIMULI.map((s) => (
            <option key={s} value={s} disabled={s === params.stim_a}>{s}</option>
          ))}
        </select>

        <p>Salience (A): <strong>{params.salience_a}</strong></p>
        <p>Salience (X): <strong>{params.salience_x}</strong></p>
      </div>

      <h2>Generated Payload</h2>
      <pre>{JSON.stringify(payload, null, 2)}</pre>

      <button onClick={onRun}>Run Experiment</button>
      <pre className={runError ? "error" : ""}>{runOutput}</pre>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<BlockingApp />);

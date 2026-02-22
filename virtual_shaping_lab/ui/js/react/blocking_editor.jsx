window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click"];

function buildPayload(params) {
  const salienceMap = {
    [params.stim_a]: { salience: params.salience_a },
    [params.stim_x]: { salience: params.salience_x },
  };
  const attentionMap = {};
  Object.keys(salienceMap).forEach((s) => {
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
      protocol: "blocking",
      stimuli: {
        cs_plus: [params.stim_a, params.stim_x],
      },
      params: {
        n_acquisition_trials: params.n_acq,
        n_compound_trials: params.n_comp,
        alpha: params.alpha,
      },
      salience: salienceMap,
      attention: attentionMap,
    },
    report: { preset: "blocking" },
  };
}

function validate(params) {
  if (params.n_acq < 1) throw new Error("n_acquisition_trials must be at least 1");
  if (params.n_comp < 1) throw new Error("n_compound_trials must be at least 1");
  if (params.alpha < 0 || params.alpha > 1) throw new Error("alpha must be 0-1");
  if (!params.stim_a || !params.stim_x) throw new Error("Select A and X");
  if (params.stim_a === params.stim_x) throw new Error("A and X must be different");
}

function BlockingApp() {
  const [params, setParams] = React.useState({
    n_acq: 50,
    n_comp: 50,
    alpha: 0.2,
    stim_a: "tone",
    stim_x: "noise",
    salience_a: 1.0,
    salience_x: 1.0,
    representation: "vector_elemental",
  });
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);

  const payload = React.useMemo(() => buildPayload(params), [params]);

  const onStimAChange = (nextA) => {
    let nextX = params.stim_x;
    if (nextA === nextX) {
      nextX = STIMULI.find((s) => s !== nextA) || nextX;
    }
    setParams((prev) => ({ ...prev, stim_a: nextA, stim_x: nextX }));
  };

  const onStimXChange = (nextX) => {
    let nextA = params.stim_a;
    if (nextX === nextA) {
      nextA = STIMULI.find((s) => s !== nextX) || nextA;
    }
    setParams((prev) => ({ ...prev, stim_a: nextA, stim_x: nextX }));
  };

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
        <a className="btn secondary" href="/ui/presets/blocking_legacy.html">Legacy Editor</a>
      </div>

      <div className="panel">
        <h3>Trials</h3>
        <label>Acquisition Trials (A+): <span>{params.n_acq}</span></label>
        <input
          type="range"
          min="1"
          max="500"
          value={params.n_acq}
          onChange={(e) => setParams((prev) => ({ ...prev, n_acq: +e.target.value }))}
        />

        <label>Compound Trials (AX+): <span>{params.n_comp}</span></label>
        <input
          type="range"
          min="1"
          max="500"
          value={params.n_comp}
          onChange={(e) => setParams((prev) => ({ ...prev, n_comp: +e.target.value }))}
        />
      </div>

      <div className="panel">
        <h3>Learning</h3>
        <label>Learning Rate (alpha): <span>{params.alpha}</span></label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={params.alpha}
          onChange={(e) => setParams((prev) => ({ ...prev, alpha: +e.target.value }))}
        />
      </div>

      <div className="panel">
        <h3>Stimuli</h3>
        <label>CS+ A</label>
        <select value={params.stim_a} onChange={(e) => onStimAChange(e.target.value)}>
          {STIMULI.map((s) => (
            <option key={s} value={s} disabled={s === params.stim_x}>{s}</option>
          ))}
        </select>

        <label>CS+ X</label>
        <select value={params.stim_x} onChange={(e) => onStimXChange(e.target.value)}>
          {STIMULI.map((s) => (
            <option key={s} value={s} disabled={s === params.stim_a}>{s}</option>
          ))}
        </select>

        <label>Salience (A): <span>{params.salience_a}</span></label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={params.salience_a}
          onChange={(e) => setParams((prev) => ({ ...prev, salience_a: +e.target.value }))}
        />

        <label>Salience (X): <span>{params.salience_x}</span></label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={params.salience_x}
          onChange={(e) => setParams((prev) => ({ ...prev, salience_x: +e.target.value }))}
        />
      </div>

      <div className="panel">
        <h3>Representation</h3>
        <label>Type</label>
        <select
          value={params.representation}
          onChange={(e) => setParams((prev) => ({ ...prev, representation: e.target.value }))}
        >
          <option value="vector_elemental">vector_elemental</option>
          <option value="vector_configural">vector_configural</option>
          <option value="vector_hybrid">vector_hybrid</option>
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
root.render(<BlockingApp />);

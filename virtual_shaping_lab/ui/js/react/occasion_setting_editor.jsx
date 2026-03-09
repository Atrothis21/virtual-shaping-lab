window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click"];

function buildPayload(params) {
  const salienceMap = {
    [params.occasion_setter]: { salience: params.salience_s },
    [params.target]: { salience: params.salience_x },
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
        name: "vector_hybrid",
        params: {
          stimuli: [...STIMULI],
          max_compound_size: 2,
          include_global: true,
          include_context: true,
        },
      },
      context_inference: { enabled: false, max_contexts: 3 },
      protocol: "occasion_setting",
      stimuli: {
        occasion_setter: [params.occasion_setter],
        target: [params.target],
      },
      params: {
        n_training_trials: params.n_training_trials,
        n_probe_trials: params.n_probe_trials,
        alpha: params.alpha,
      },
      salience: salienceMap,
      attention: attentionMap,
    },
    report: { preset: "occasion_setting" },
  };

  return window.VSLReact.toCanonicalPayload(payload);
}

function validate(params) {
  if (params.n_training_trials < 1) throw new Error("n_training_trials must be at least 1");
  if (params.n_probe_trials < 1) throw new Error("n_probe_trials must be at least 1");
  if (params.alpha < 0 || params.alpha > 1) throw new Error("alpha must be 0-1");
  if (!params.occasion_setter || !params.target) throw new Error("Select S and X");
  if (params.occasion_setter === params.target) throw new Error("S and X must be different");
}

function OccasionSettingApp() {
  const [params, setParams] = React.useState({
    n_training_trials: 100,
    n_probe_trials: 20,
    alpha: 0.2,
    occasion_setter: "tone",
    target: "noise",
    salience_s: 1.0,
    salience_x: 1.0,
  });
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);

  const payload = React.useMemo(() => buildPayload(params), [params]);

  const onOccasionSetterChange = (nextS) => {
    let nextX = params.target;
    if (nextS === nextX) {
      nextX = STIMULI.find((s) => s !== nextS) || nextX;
    }
    setParams((prev) => ({ ...prev, occasion_setter: nextS, target: nextX }));
  };

  const onTargetChange = (nextX) => {
    let nextS = params.occasion_setter;
    if (nextX === nextS) {
      nextS = STIMULI.find((s) => s !== nextX) || nextS;
    }
    setParams((prev) => ({ ...prev, occasion_setter: nextS, target: nextX }));
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
      <h1>Occasion Setting Preset</h1>
      <p>Train S+X -> US and X alone -> no US. Probe compares X vs S+X.</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>
          Back to Presets
        </button>
      </div>

      <div className="panel">
        <h3>Trials</h3>
        <label>Training Trials: <span>{params.n_training_trials}</span></label>
        <input
          type="range"
          min="1"
          max="500"
          value={params.n_training_trials}
          onChange={(e) => setParams((prev) => ({ ...prev, n_training_trials: +e.target.value }))}
        />

        <label>Probe Trials: <span>{params.n_probe_trials}</span></label>
        <input
          type="range"
          min="1"
          max="200"
          value={params.n_probe_trials}
          onChange={(e) => setParams((prev) => ({ ...prev, n_probe_trials: +e.target.value }))}
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
        <label>Occasion Setter (S)</label>
        <select value={params.occasion_setter} onChange={(e) => onOccasionSetterChange(e.target.value)}>
          {STIMULI.map((s) => (
            <option key={s} value={s} disabled={s === params.target}>{s}</option>
          ))}
        </select>

        <label>Target (X)</label>
        <select value={params.target} onChange={(e) => onTargetChange(e.target.value)}>
          {STIMULI.map((s) => (
            <option key={s} value={s} disabled={s === params.occasion_setter}>{s}</option>
          ))}
        </select>

        <label>Salience (S): <span>{params.salience_s}</span></label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={params.salience_s}
          onChange={(e) => setParams((prev) => ({ ...prev, salience_s: +e.target.value }))}
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

      <h2>Generated Payload</h2>
      <pre>{JSON.stringify(payload, null, 2)}</pre>

      <button onClick={onRun}>Run Experiment</button>
      <pre className={runError ? "error" : ""}>{runOutput}</pre>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<OccasionSettingApp />);

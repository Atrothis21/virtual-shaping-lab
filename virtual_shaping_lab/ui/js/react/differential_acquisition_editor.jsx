window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click"];

function buildPayload(params) {
  const salienceMap = {};
  params.cs_plus.forEach((s) => {
    salienceMap[s] = { salience: params.salience };
  });

  const attentionMap = {};
  [...params.cs_plus, ...params.cs_minus].forEach((s) => {
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
      phases: [
        {
          name: "Differential Acquisition",
          protocol: "differential_acquisition",
          stimuli: {
            cs_plus: params.cs_plus,
            cs_minus: params.cs_minus,
          },
          params: {
            n_trials: params.n_trials,
            alpha: params.alpha,
          },
        },
      ],
      salience: salienceMap,
      attention: attentionMap,
    },
    report: { preset: "differential_acquisition" },
  };
}

function validate(params) {
  if (params.n_trials < 1) throw new Error("n_trials must be at least 1");
  if (params.alpha < 0 || params.alpha > 1) throw new Error("alpha must be 0-1");
  if (!params.cs_plus.length) throw new Error("Select at least one CS+ stimulus");
  if (!params.cs_minus.length) throw new Error("Select at least one CS- stimulus");
}

function DifferentialAcquisitionApp() {
  const [params, setParams] = React.useState({
    n_trials: 100,
    alpha: 0.2,
    salience: 1.0,
    cs_plus: ["tone"],
    cs_minus: ["noise"],
    representation: "vector_elemental",
  });
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);

  const payload = React.useMemo(() => buildPayload(params), [params]);

  const onCSPlusChange = (e) => {
    const nextPlus = Array.from(e.target.selectedOptions).map((o) => o.value);
    const nextMinus = params.cs_minus.filter((s) => !nextPlus.includes(s));
    setParams((prev) => ({ ...prev, cs_plus: nextPlus, cs_minus: nextMinus }));
  };

  const onCSMinusChange = (e) => {
    const nextMinus = Array.from(e.target.selectedOptions).map((o) => o.value);
    const nextPlus = params.cs_plus.filter((s) => !nextMinus.includes(s));
    setParams((prev) => ({ ...prev, cs_plus: nextPlus, cs_minus: nextMinus }));
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
      <h1>Differential Acquisition Preset</h1>
      <p>CS+ reinforced and CS- nonreinforced within a single phase.</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>
          Back to Presets
        </button>
        <a className="btn secondary" href="/ui/presets/differential_acquisition_legacy.html">Legacy Editor</a>
      </div>

      <div className="panel">
        <h3>Trials</h3>
        <label>Number of Trials: <span>{params.n_trials}</span></label>
        <input
          type="range"
          min="1"
          max="500"
          value={params.n_trials}
          onChange={(e) => setParams((prev) => ({ ...prev, n_trials: +e.target.value }))}
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
        <label>Salience (applies to selected CS+): <span>{params.salience}</span></label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={params.salience}
          onChange={(e) => setParams((prev) => ({ ...prev, salience: +e.target.value }))}
        />
      </div>

      <div className="panel">
        <h3>Stimuli</h3>
        <label>CS+ Stimuli</label>
        <select multiple value={params.cs_plus} onChange={onCSPlusChange}>
          {STIMULI.map((s) => (
            <option key={s} value={s} disabled={params.cs_minus.includes(s)}>{s}</option>
          ))}
        </select>

        <br /><br />

        <label>CS- Stimuli</label>
        <select multiple value={params.cs_minus} onChange={onCSMinusChange}>
          {STIMULI.map((s) => (
            <option key={s} value={s} disabled={params.cs_plus.includes(s)}>{s}</option>
          ))}
        </select>
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
root.render(<DifferentialAcquisitionApp />);

window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click"];

function buildPayload(params) {
  const attentionMap = {};
  [...params.cs_plus, ...params.cs_minus].forEach((s) => {
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
      protocol: "conditioned_inhibition",
      stimuli: {
        cs_plus: params.cs_plus,
        cs_minus: params.cs_minus,
      },
      params: {
        n_acquisition_trials: params.n_acq,
        n_inhibition_trials: params.n_inh,
        n_retardation_trials: params.n_ret,
        alpha: params.alpha,
      },
      attention: attentionMap,
    },
    report: { preset: "conditioned_inhibition" },
  };

  return window.VSLReact.toCanonicalPayload(payload);
}

function validate(params) {
  if (params.n_acq < 1) throw new Error("n_acquisition_trials must be at least 1");
  if (params.n_inh < 1) throw new Error("n_inhibition_trials must be at least 1");
  if (params.n_ret < 1) throw new Error("n_retardation_trials must be at least 1");
  if (params.alpha < 0 || params.alpha > 1) throw new Error("alpha must be 0-1");
  if (!params.cs_plus.length) throw new Error("Select at least one CS+ stimulus");
  if (!params.cs_minus.length) throw new Error("Select at least one CS- stimulus");
}

function ConditionedInhibitionApp() {
  const [params, setParams] = React.useState({
    n_acq: 50,
    n_inh: 50,
    n_ret: 20,
    alpha: 0.2,
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
      <h1>Conditioned Inhibition Preset</h1>
      <p>Acquisition (A+), compound nonreinforcement (AX-), summation, and retardation tests.</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>
          Back to Presets
        </button>
      </div>

      <div className="panel">
        <h3>Trials</h3>
        <label>Acquisition Trials: <span>{params.n_acq}</span></label>
        <input
          type="range"
          min="1"
          max="200"
          value={params.n_acq}
          onChange={(e) => setParams((prev) => ({ ...prev, n_acq: +e.target.value }))}
        />

        <label>Inhibition Trials: <span>{params.n_inh}</span></label>
        <input
          type="range"
          min="1"
          max="200"
          value={params.n_inh}
          onChange={(e) => setParams((prev) => ({ ...prev, n_inh: +e.target.value }))}
        />

        <label>Retardation Trials: <span>{params.n_ret}</span></label>
        <input
          type="range"
          min="1"
          max="200"
          value={params.n_ret}
          onChange={(e) => setParams((prev) => ({ ...prev, n_ret: +e.target.value }))}
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
        <label>CS+ (Excitor A)</label>
        <select multiple value={params.cs_plus} onChange={onCSPlusChange}>
          {STIMULI.map((s) => (
            <option key={s} value={s} disabled={params.cs_minus.includes(s)}>{s}</option>
          ))}
        </select>

        <br /><br />

        <label>CS- (Inhibitor X)</label>
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
root.render(<ConditionedInhibitionApp />);

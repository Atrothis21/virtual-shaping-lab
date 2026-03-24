window.VSLReact = window.VSLReact || {};

function buildBasisAuthoringPayload(params) {
  return {
    preset_id: "acquisition",
    operator_subset: {
      phi: params.phi,
      w: params.w,
    },
    edits: {
      n_trials: params.n_trials,
      cs_plus: params.cs_plus,
      learning_rule: params.learning_rule,
    },
  };
}

function validate(params) {
  if (params.n_trials < 1) throw new Error("n_trials must be at least 1");
  if (!params.cs_plus.length) throw new Error("Select at least one CS+ stimulus");
}

function AcquisitionApp() {
  const [contract, setContract] = React.useState(null);
  const [loadError, setLoadError] = React.useState("");
  const [params, setParams] = React.useState({
    n_trials: 50,
    cs_plus: ["tone"],
    learning_rule: "rescorla_wagner",
    phi: "elemental",
    w: "rescorla_wagner",
  });
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);

  React.useEffect(() => {
    let active = true;
    (async () => {
      try {
        const res = await fetch("/catalog/presets/acquisition/basis-authoring");
        const data = await res.json();
        if (!res.ok) {
          throw new Error((data && data.detail && data.detail.message) || "Failed to load acquisition authoring contract.");
        }
        if (!active) return;
        setContract(data);
        setParams((prev) => ({
          ...prev,
          n_trials: data.defaults.editable.n_trials,
          cs_plus: data.defaults.editable.cs_plus,
          learning_rule: data.defaults.editable.learning_rule,
          phi: data.defaults.operator_subset.phi,
          w: data.defaults.operator_subset.w,
        }));
      } catch (err) {
        if (active) setLoadError(err.message || "Failed to load authoring contract.");
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  React.useEffect(() => {
    setParams((prev) => {
      if (prev.learning_rule === "temporal_difference") return { ...prev, w: "td0_update" };
      return { ...prev, w: "rescorla_wagner" };
    });
  }, [params.learning_rule]);

  const payload = React.useMemo(() => buildBasisAuthoringPayload(params), [params]);

  const onCSPlusChange = (e) => {
    const next = Array.from(e.target.selectedOptions).map((o) => o.value);
    setParams((prev) => ({ ...prev, cs_plus: next }));
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

    const materializeRes = await fetch("/catalog/presets/acquisition/materialize-basis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const materialized = await materializeRes.json();
    if (!materializeRes.ok) {
      setRunOutput(JSON.stringify(materialized, null, 2));
      setRunError(true);
      return;
    }

    const res = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(materialized),
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
      <h1>Acquisition Preset</h1>
      <p>Classical acquisition with a CS+ stimulus.</p>
      {loadError ? <pre className="error">{loadError}</pre> : null}
      {!contract && !loadError ? <pre>Loading basis authoring contract...</pre> : null}

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/presets.html"; }}>
          Back to Presets
        </button>
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
        <h3>Learner Rule</h3>
        <label>Rule</label>
        <select
          value={params.learning_rule}
          onChange={(e) => setParams((prev) => ({ ...prev, learning_rule: e.target.value }))}
        >
          <option value="rescorla_wagner">rescorla_wagner</option>
          <option value="temporal_difference">temporal_difference</option>
        </select>
      </div>

      <div className="panel">
        <h3>Stimuli</h3>
        <label>CS</label>
        <select multiple value={params.cs_plus} onChange={onCSPlusChange}>
          {(contract?.defaults?.stimuli_catalog || ["tone", "noise"]).map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      <div className="panel">
        <h3>Representation Operator (phi)</h3>
        <label>Selection</label>
        <select
          value={params.phi}
          onChange={(e) => setParams((prev) => ({ ...prev, phi: e.target.value }))}
        >
          {(contract?.operator_choices?.phi || []).map((choice) => (
            <option key={choice} value={choice}>{choice}</option>
          ))}
        </select>
      </div>

      <h2>Basis Authoring Payload</h2>
      <pre>{JSON.stringify(payload, null, 2)}</pre>

      <button onClick={onRun}>Run Experiment</button>
      <pre className={runError ? "error" : ""}>{runOutput}</pre>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<AcquisitionApp />);

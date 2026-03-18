window.VSLReact = window.VSLReact || {};

const {
  buildDefaultPhase,
  migratePhaseProtocol,
  createInitialPayload,
  validateBeforeRun,
  getAvailableStimuli,
} = window.VSLReact.builderState;

const BuilderPhaseList = window.VSLReact.BuilderPhaseList;

const PROTOCOL_OPTIONS = [
  { value: "acquisition", label: "Acquisition" },
  { value: "nonreinforcement", label: "Nonreinforcement" },
  { value: "compound_acquisition", label: "Compound Acquisition" },
  { value: "compound_nonreinforcement", label: "Compound Nonreinforcement" },
  { value: "differential_acquisition", label: "Differential Acquisition" },
  { value: "probe", label: "Probe" },
  { value: "context_shift", label: "Context Shift" },
  { value: "criterion_shift", label: "Criterion Shift" },
];

function StimulusChipPicker({ options, selected, onToggle, disabledSet = new Set() }) {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginTop: "0.4rem" }}>
      {options.map((s) => {
        const active = selected.includes(s);
        const disabled = disabledSet.has(s);
        return (
          <button
            key={`chip-${s}`}
            type="button"
            className={`btn ${active ? "" : "secondary"}`}
            disabled={disabled}
            onClick={() => onToggle(s)}
            style={{
              marginTop: 0,
              opacity: disabled ? 0.45 : 1,
              borderColor: active ? "#2563eb" : undefined,
              background: active ? "#2563eb" : undefined,
              color: active ? "#fff" : undefined,
            }}
          >
            {s}
          </button>
        );
      })}
    </div>
  );
}

function isIdentitySimilarity(similarity) {
  if (!similarity) return true;
  const values = similarity?.values;
  if (!Array.isArray(values) || !values.length) return true;
  for (let i = 0; i < values.length; i += 1) {
    const row = values[i];
    if (!Array.isArray(row) || row.length !== values.length) return false;
    for (let j = 0; j < row.length; j += 1) {
      const v = Number(row[j]);
      if (!Number.isFinite(v)) return false;
      if (i === j && Math.abs(v - 1.0) > 1e-9) return false;
      if (i !== j && Math.abs(v) > 1e-9) return false;
    }
  }
  return true;
}

function isNeutralParamMap(mapObj, field, neutralValue) {
  if (!mapObj || typeof mapObj !== "object") return true;
  const entries = Object.values(mapObj);
  if (!entries.length) return true;
  return entries.every((raw) => {
    if (typeof raw === "number") return Math.abs(raw - neutralValue) < 1e-9;
    if (raw && typeof raw[field] === "number") return Math.abs(raw[field] - neutralValue) < 1e-9;
    return true;
  });
}

function BuilderShellApp() {
  const [payload, setPayload] = React.useState(createInitialPayload);
  const [activePhaseIndex, setActivePhaseIndex] = React.useState(0);
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);
  const [runStatus, setRunStatus] = React.useState("Idle");
  const [seedNotice, setSeedNotice] = React.useState("");

  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search || "");
    if (params.get("from") === "preset") {
      setSeedNotice("Loaded payload from preset. You can now customize it in Builder.");
    }
  }, []);

  const availableStimuli = React.useMemo(() => getAvailableStimuli(payload), [payload]);
  const phases =
    payload &&
    payload.experiment &&
    payload.experiment.program &&
    Array.isArray(payload.experiment.program.phases)
      ? payload.experiment.program.phases
      : [];
  const active = phases[activePhaseIndex] || phases[0];

  const protocol = active?.protocol || "acquisition";
  const isCompound = protocol === "compound_acquisition" || protocol === "compound_nonreinforcement";
  const isCompoundAcq = protocol === "compound_acquisition";
  const isDifferential = protocol === "differential_acquisition";
  const isContextShift = protocol === "context_shift";
  const isProbe = protocol === "probe";
  const isCriterion = protocol === "criterion_shift";

  const csPlusList = Array.isArray(active?.stimuli?.cs_plus) && active.stimuli.cs_plus.length
    ? active.stimuli.cs_plus
    : [availableStimuli[0]];
  const csMinusList = Array.isArray(active?.stimuli?.cs_minus) && active.stimuli.cs_minus.length
    ? active.stimuli.cs_minus
    : [availableStimuli[1] || availableStimuli[0]];
  const comp1 = active?.stimuli?.compound?.[0] || availableStimuli[0];
  const comp2 = active?.stimuli?.compound?.[1] || availableStimuli[1] || availableStimuli[0];

  const showSingleCs = !isCompound && !isDifferential && !isContextShift;
  const showTrials = !isContextShift;
  const showAlpha = !isCompoundAcq && !isContextShift && !isProbe;
  const showGamma = !isContextShift && !isProbe;
  const showOutcome = protocol === "acquisition";
  const contextValue = active?.params?.context || "A";
  const trialsMax = protocol === "probe" ? 200 : 500;

  const baselineCompatible = React.useMemo(() => {
    const salienceNeutral = isNeutralParamMap(payload?.experiment?.agent?.representation?.salience, "salience", 1.0);
    const attentionNeutral = isNeutralParamMap(payload?.experiment?.agent?.learning?.attention?.initial, "attention", 1.0);
    const similarityNeutral = isIdentitySimilarity(payload?.experiment?.agent?.representation?.params?.similarity || null);
    const contextInferenceEnabled = Boolean(payload?.experiment?.runtime?.context_inference?.enabled);
    return salienceNeutral && attentionNeutral && similarityNeutral && !contextInferenceEnabled;
  }, [payload]);

  const addPhase = () => {
    setPayload((prev) => {
      const next = JSON.parse(JSON.stringify(prev));
      const stim = getAvailableStimuli(next);
      if (!next.experiment.program || !Array.isArray(next.experiment.program.phases)) {
        next.experiment.program = { phases: [] };
      }
      next.experiment.program.phases.push(buildDefaultPhase(next.experiment.program.phases.length, stim));
      return next;
    });
    setActivePhaseIndex(phases.length);
  };

  const updateActive = (updater) => {
    setPayload((prev) => {
      const next = JSON.parse(JSON.stringify(prev));
      const phaseRows =
        next.experiment && next.experiment.program && Array.isArray(next.experiment.program.phases)
          ? next.experiment.program.phases
          : [];
      const idx = Math.min(activePhaseIndex, phaseRows.length - 1);
      updater(phaseRows[idx], getAvailableStimuli(next));
      return next;
    });
  };

  const resetBuilder = () => {
    setPayload(createInitialPayload());
    setActivePhaseIndex(0);
    setRunOutput("Not run yet.");
    setRunError(false);
  };

  const onRun = async () => {
    setRunError(false);
    setRunStatus("Validating");
    setRunOutput("Validating payload...");

    let runPayload;
    try {
      runPayload = validateBeforeRun(payload);
    } catch (err) {
      setRunError(true);
      setRunStatus("Validation Error");
      setRunOutput(`Validation error: ${err.message}`);
      return;
    }

    try {
      setRunStatus("Running");
      setRunOutput("Submitting run request...");

      const res = await fetch("/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(runPayload),
      });
      const result = await res.json();

      if (result.status === "success" && result.run_id) {
        setRunStatus("Completed");
        window.location.href = `/ui/results.html?run_id=${result.run_id}`;
        return;
      }

      setRunStatus("Run Error");
      setRunOutput(JSON.stringify(result, null, 2));
      setRunError(true);
    } catch (err) {
      setRunStatus("Run Error");
      setRunOutput(`Run failed: ${err.message}`);
      setRunError(true);
    }
  };

  return (
    <>
      <h1>Virtual Shaping Lab - Builder</h1>
      <p>Constrained builder with pre-allowed parameter controls.</p>
      <div style={{ color: "#555", marginBottom: "0.45rem" }}>
        <strong>Navigation:</strong> <a href="/ui/index.html">Menu</a> / Builder
      </div>
      {seedNotice && (
        <div
          style={{
            marginBottom: "0.6rem",
            background: "#eff6ff",
            border: "1px solid #bfdbfe",
            color: "#1e3a8a",
            borderRadius: "6px",
            padding: "0.45rem 0.6rem",
            fontSize: "0.9rem",
          }}
        >
          {seedNotice}
        </div>
      )}

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/index.html"; }}>
          Back to Menu
        </button>
        <button className="btn secondary" onClick={resetBuilder}>Reset Builder</button>
      </div>

      <div className="panel">
        <h3>Baseline Compatibility</h3>
        <div
          style={{
            position: "sticky",
            top: "0.4rem",
            zIndex: 5,
            display: "inline-block",
            padding: "0.2rem 0.5rem",
            borderRadius: "999px",
            background: baselineCompatible ? "#ecfdf5" : "#fff7ed",
            border: `1px solid ${baselineCompatible ? "#86efac" : "#fdba74"}`,
          }}
        >
          <strong>Status:</strong>{" "}
          {baselineCompatible ? "Baseline-Compatible" : "Customized"}
        </div>
        <div style={{ color: "#555", marginTop: "0.2rem" }}>
          Baseline = salience 1.0, attention 1.0, identity similarity, context inference off.
        </div>
      </div>

      <BuilderPhaseList
        phases={phases}
        activePhaseIndex={activePhaseIndex}
        onSelectPhase={setActivePhaseIndex}
        onAddPhase={addPhase}
      />

      <div className="panel">
        <h3>Active Phase</h3>

        <label>Phase</label>
        <select
          value={protocol}
          onChange={(e) => updateActive((p, stim) => {
            const migrated = migratePhaseProtocol(p, e.target.value, stim);
            p.protocol = migrated.protocol;
            p.stimuli = migrated.stimuli;
            p.params = migrated.params;
          })}
        >
          {PROTOCOL_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>

        {showTrials && (
          <div className="panel">
            <h4>Trials</h4>
            <label>Trials</label>
            <div style={{ color: "#666", fontSize: "0.86rem" }}>More trials increase learning/expression stability.</div>
            <input
              type="range"
              min="1"
              max={trialsMax}
              value={active?.params?.n_trials || 100}
              onChange={(e) => updateActive((p) => {
                if (!p.params) p.params = {};
                p.params.n_trials = +e.target.value;
              })}
            />
            <div>{active?.params?.n_trials || 100}</div>
          </div>
        )}

        <div className="panel">
          <h4>Learning</h4>

          {showAlpha && (
            <>
              <label>Learning Rate (alpha)</label>
              <div style={{ color: "#666", fontSize: "0.86rem" }}>Higher alpha updates associations faster per trial.</div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={active?.params?.alpha ?? 0.2}
                onChange={(e) => updateActive((p) => {
                  if (!p.params) p.params = {};
                  p.params.alpha = +e.target.value;
                })}
              />
              <div>{active?.params?.alpha ?? 0.2}</div>
            </>
          )}

          {isCompoundAcq && (
            <>
              <label>Alpha CS1</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={active?.params?.alpha_cs1 ?? 0.2}
                onChange={(e) => updateActive((p) => {
                  if (!p.params) p.params = {};
                  p.params.alpha_cs1 = +e.target.value;
                })}
              />
              <div>{active?.params?.alpha_cs1 ?? 0.2}</div>

              <label>Alpha CS2</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={active?.params?.alpha_cs2 ?? 0.2}
                onChange={(e) => updateActive((p) => {
                  if (!p.params) p.params = {};
                  p.params.alpha_cs2 = +e.target.value;
                })}
              />
              <div>{active?.params?.alpha_cs2 ?? 0.2}</div>
            </>
          )}

          {showGamma && (
            <>
              <label>Discount (gamma)</label>
              <div style={{ color: "#666", fontSize: "0.86rem" }}>Gamma controls future-value carryover (usually low in classical tasks).</div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={active?.params?.gamma ?? 0.0}
                onChange={(e) => updateActive((p) => {
                  if (!p.params) p.params = {};
                  p.params.gamma = +e.target.value;
                })}
              />
              <div>{active?.params?.gamma ?? 0.0}</div>
            </>
          )}

          {showOutcome && (
            <>
              <label>Outcome</label>
              <div style={{ color: "#666", fontSize: "0.86rem" }}>Outcome is the target reinforcement magnitude.</div>
              <input
                type="range"
                min="0"
                max="2"
                step="0.05"
                value={active?.params?.outcome ?? 1.0}
                onChange={(e) => updateActive((p) => {
                  if (!p.params) p.params = {};
                  p.params.outcome = +e.target.value;
                })}
              />
              <div>{active?.params?.outcome ?? 1.0}</div>
            </>
          )}
        </div>

        {!isContextShift && (
          <div className="panel">
            <h4>Stimuli</h4>

            {showSingleCs && (
              <>
                <label>CS+</label>
                <div style={{ color: "#666", fontSize: "0.86rem" }}>Click chips to add/remove stimuli for this phase.</div>
                <StimulusChipPicker
                  options={availableStimuli}
                  selected={csPlusList}
                  onToggle={(value) => updateActive((p, stim) => {
                    const current = Array.isArray(p.stimuli?.cs_plus) && p.stimuli.cs_plus.length ? p.stimuli.cs_plus : [stim[0]];
                    const has = current.includes(value);
                    const nextPlus = has ? current.filter((s) => s !== value) : [...current, value];
                    p.stimuli = { cs_plus: nextPlus.length ? nextPlus : [stim[0]] };
                  })}
                />
              </>
            )}

            {isDifferential && (
              <>
                <label>CS+</label>
                <div style={{ color: "#666", fontSize: "0.86rem" }}>Select one or more reinforced cues.</div>
                <StimulusChipPicker
                  options={availableStimuli}
                  selected={csPlusList}
                  onToggle={(value) => updateActive((p, stim) => {
                    const current = Array.isArray(p.stimuli?.cs_plus) && p.stimuli.cs_plus.length ? p.stimuli.cs_plus : [stim[0]];
                    const has = current.includes(value);
                    const nextPlusRaw = has ? current.filter((s) => s !== value) : [...current, value];
                    const nextPlus = nextPlusRaw.length ? nextPlusRaw : [stim[0]];
                    const currentMinus = Array.isArray(p.stimuli?.cs_minus) ? p.stimuli.cs_minus : [stim[1] || stim[0]];
                    const nextMinus = currentMinus.filter((s) => !nextPlus.includes(s));
                    const fallbackMinus = stim.find((x) => !nextPlus.includes(x)) || nextPlus[0];
                    p.stimuli = {
                      cs_plus: nextPlus,
                      cs_minus: nextMinus.length ? nextMinus : [fallbackMinus],
                    };
                  })}
                />

                <br /><br />
                <label>CS-</label>
                <div style={{ color: "#666", fontSize: "0.86rem" }}>Select nonreinforced cues (cannot overlap with CS+).</div>
                <StimulusChipPicker
                  options={availableStimuli}
                  selected={csMinusList}
                  disabledSet={new Set(csPlusList)}
                  onToggle={(value) => updateActive((p, stim) => {
                    const plus = Array.isArray(p.stimuli?.cs_plus) && p.stimuli.cs_plus.length ? p.stimuli.cs_plus : [stim[0]];
                    if (plus.includes(value)) return;
                    const current = Array.isArray(p.stimuli?.cs_minus) && p.stimuli.cs_minus.length
                      ? p.stimuli.cs_minus.filter((s) => !plus.includes(s))
                      : [stim[1] || stim[0]].filter((s) => !plus.includes(s));
                    const has = current.includes(value);
                    const nextRaw = has ? current.filter((s) => s !== value) : [...current, value];
                    const fallbackMinus = stim.find((x) => !plus.includes(x)) || plus[0];
                    p.stimuli = {
                      cs_plus: plus,
                      cs_minus: nextRaw.length ? nextRaw : [fallbackMinus],
                    };
                  })}
                />
              </>
            )}

            {isCompound && (
              <>
                <label>Compound Stimulus (two cues)</label>
                <select
                  style={{ width: "100%" }}
                  value={comp1}
                  onChange={(e) => updateActive((p, stim) => {
                    const first = e.target.value;
                    const second = p.stimuli?.compound?.[1] === first
                      ? (stim.find((x) => x !== first) || first)
                      : (p.stimuli?.compound?.[1] || stim[1] || first);
                    p.stimuli = { compound: [first, second] };
                  })}
                >
                  {availableStimuli.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>

                <br />
                <select
                  style={{ width: "100%" }}
                  value={comp2}
                  onChange={(e) => updateActive((p, stim) => {
                    const second = e.target.value;
                    const first = p.stimuli?.compound?.[0] || stim[0];
                    p.stimuli = { compound: [first, second === first ? (stim.find((x) => x !== first) || first) : second] };
                  })}
                >
                  {availableStimuli.map((s) => <option key={s} value={s} disabled={s === comp1}>{s}</option>)}
                </select>
              </>
            )}
          </div>
        )}

        {(isContextShift || isProbe || isCriterion) && (
          <div className="panel">
            <h4>Context</h4>
            <label>Context</label>
            <select
              value={contextValue}
              onChange={(e) => updateActive((p) => {
                if (!p.params) p.params = {};
                p.params.context = e.target.value;
              })}
            >
              <option value="A">A</option>
              <option value="B">B</option>
              <option value="C">C</option>
            </select>
          </div>
        )}

        {isProbe && (
          <>
            <label style={{ marginTop: "0.7rem", display: "block" }}>
              <input
                type="checkbox"
                checked={Boolean(active?.params?.deliver_reward)}
                onChange={(e) => updateActive((p) => {
                  if (!p.params) p.params = {};
                  p.params.deliver_reward = e.target.checked;
                })}
              />{" "}
              Deliver reward during probe
            </label>

            <label>Reward Value</label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.05"
              value={active?.params?.reward_value ?? 0.0}
              disabled={!active?.params?.deliver_reward}
              onChange={(e) => updateActive((p) => {
                if (!p.params) p.params = {};
                p.params.reward_value = +e.target.value;
              })}
            />
            <div>{active?.params?.reward_value ?? 0.0}</div>
          </>
        )}

        {isCriterion && (
          <>
            <label>Criterion Threshold</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={active?.params?.criterion?.threshold ?? 0.8}
              onChange={(e) => updateActive((p) => {
                if (!p.params) p.params = {};
                if (!p.params.criterion) p.params.criterion = { type: "prediction_threshold", threshold: 0.8, window: 10 };
                p.params.criterion.type = "prediction_threshold";
                p.params.criterion.threshold = +e.target.value;
              })}
            />
            <div>{active?.params?.criterion?.threshold ?? 0.8}</div>

            <label>Criterion Window</label>
            <input
              type="range"
              min="1"
              max="100"
              step="1"
              value={active?.params?.criterion?.window ?? 10}
              onChange={(e) => updateActive((p) => {
                if (!p.params) p.params = {};
                if (!p.params.criterion) p.params.criterion = { type: "prediction_threshold", threshold: 0.8, window: 10 };
                p.params.criterion.type = "prediction_threshold";
                p.params.criterion.window = +e.target.value;
              })}
            />
            <div>{active?.params?.criterion?.window ?? 10}</div>

            <label>Safety Cap (blank disables)</label>
            <input
              type="number"
              min="1"
              value={active?.params?.safety_cap ?? ""}
              onChange={(e) => updateActive((p) => {
                if (!p.params) p.params = {};
                const raw = e.target.value;
                p.params.safety_cap = raw === "" ? null : Math.max(1, Math.round(+raw));
              })}
            />
          </>
        )}
      </div>

      <div className="panel">
        <div style={{ marginBottom: "0.5rem" }}>
          <strong>Run Status:</strong> {runStatus}
        </div>
        <button className="btn" onClick={onRun}>Run Experiment</button>
        <pre className={runError ? "error" : ""}>{runOutput}</pre>
      </div>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<BuilderShellApp />);

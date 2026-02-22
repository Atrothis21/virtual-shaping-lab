window.VSLReact = window.VSLReact || {};

const {
  STIMULI: KNOWN_STIMULI,
  buildDefaultPhase,
  migratePhaseProtocol,
  createInitialPayload,
  validateBeforeRun,
  getAvailableStimuli,
} = window.VSLReact.builderState;

const BuilderPhaseList = window.VSLReact.BuilderPhaseList;

function collectReferencedStimuli(phases) {
  const refs = new Set();
  (phases || []).forEach((phase) => {
    if (Array.isArray(phase?.stimuli?.cs_plus)) phase.stimuli.cs_plus.forEach((s) => refs.add(s));
    if (Array.isArray(phase?.stimuli?.cs_minus)) phase.stimuli.cs_minus.forEach((s) => refs.add(s));
    if (Array.isArray(phase?.stimuli?.compound)) phase.stimuli.compound.forEach((s) => refs.add(s));
  });
  return refs;
}

function collectActivePhaseStimuli(phase) {
  const out = [];
  if (Array.isArray(phase?.stimuli?.cs_plus)) out.push(...phase.stimuli.cs_plus);
  if (Array.isArray(phase?.stimuli?.cs_minus)) out.push(...phase.stimuli.cs_minus);
  if (Array.isArray(phase?.stimuli?.compound)) out.push(...phase.stimuli.compound);
  return Array.from(new Set(out));
}

function readParamMapValue(mapObj, key, field, fallback) {
  const raw = mapObj?.[key];
  if (typeof raw === "number") return raw;
  if (raw && typeof raw[field] === "number") return raw[field];
  return fallback;
}

function buildDefaultSimilarity(stimuli, offdiag) {
  const values = stimuli.map((_, i) =>
    stimuli.map((__, j) => (i === j ? 1.0 : offdiag))
  );
  return {
    type: "matrix",
    stimuli: [...stimuli],
    values,
  };
}

function inferOffdiagFromSimilarity(similarity, fallback) {
  const values = similarity?.values;
  if (!Array.isArray(values) || !values.length) return fallback;
  for (let i = 0; i < values.length; i += 1) {
    for (let j = 0; j < values[i].length; j += 1) {
      if (i !== j && Number.isFinite(+values[i][j])) return +values[i][j];
    }
  }
  return fallback;
}

function BuilderShellApp() {
  const [payload, setPayload] = React.useState(createInitialPayload);
  const [activePhaseIndex, setActivePhaseIndex] = React.useState(0);
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);
  const [newStimulus, setNewStimulus] = React.useState(KNOWN_STIMULI[0] || "tone");
  const [showAdvanced, setShowAdvanced] = React.useState(false);
  const [similarityOffdiag, setSimilarityOffdiag] = React.useState(0.2);

  const availableStimuli = React.useMemo(() => getAvailableStimuli(payload), [payload]);
  const phases = payload.experiment.phases;
  const active = phases[activePhaseIndex] || phases[0];
  const referencedStimuli = React.useMemo(() => collectReferencedStimuli(phases), [phases]);
  const activePhaseStimuli = React.useMemo(() => collectActivePhaseStimuli(active), [active]);

  const addPhase = () => {
    setPayload((prev) => {
      const next = JSON.parse(JSON.stringify(prev));
      const stim = getAvailableStimuli(next);
      next.experiment.phases.push(buildDefaultPhase(next.experiment.phases.length, stim));
      return next;
    });
    setActivePhaseIndex(phases.length);
  };

  const updateActive = (updater) => {
    setPayload((prev) => {
      const next = JSON.parse(JSON.stringify(prev));
      const idx = Math.min(activePhaseIndex, next.experiment.phases.length - 1);
      updater(next.experiment.phases[idx], getAvailableStimuli(next));
      return next;
    });
  };

  const applySimilarity = (offdiag) => {
    const nextOffdiag = Math.max(0, Math.min(1, +offdiag || 0));
    const stimuli = repStimuli;
    if (!stimuli.length) return;

    setPayload((prev) => {
      const next = JSON.parse(JSON.stringify(prev));
      if (!next.experiment.representation) next.experiment.representation = { name: "vector_elemental", params: {} };
      if (!next.experiment.representation.params) next.experiment.representation.params = {};
      next.experiment.representation.params.similarity = buildDefaultSimilarity(stimuli, nextOffdiag);
      return next;
    });
  };

  const setSimilarityEnabled = (enabled) => {
    if (enabled) {
      applySimilarity(similarityOffdiag);
      return;
    }
    setPayload((prev) => {
      const next = JSON.parse(JSON.stringify(prev));
      if (next?.experiment?.representation?.params) {
        delete next.experiment.representation.params.similarity;
      }
      return next;
    });
  };

  const updateRepresentationStimuli = (nextStimuli) => {
    const deduped = Array.from(new Set((nextStimuli || []).filter(Boolean)));
    if (!deduped.length) return;

    setPayload((prev) => {
      const next = JSON.parse(JSON.stringify(prev));
      if (!next.experiment.representation) next.experiment.representation = { name: "vector_elemental", params: {} };
      if (!next.experiment.representation.params) next.experiment.representation.params = {};
      next.experiment.representation.params.stimuli = deduped;

      const trimMap = (obj, field) => {
        const out = {};
        deduped.forEach((s) => {
          const val = obj?.[s];
          if (val == null) return;
          if (typeof val === "number") {
            out[s] = { [field]: val };
            return;
          }
          if (typeof val[field] === "number") {
            out[s] = { [field]: val[field] };
          }
        });
        return out;
      };

      next.experiment.salience = trimMap(next.experiment.salience || {}, "salience");
      next.experiment.attention = trimMap(next.experiment.attention || {}, "attention");
      if (next.experiment.representation.params.similarity) {
        next.experiment.representation.params.similarity = buildDefaultSimilarity(
          deduped,
          inferOffdiagFromSimilarity(next.experiment.representation.params.similarity, similarityOffdiag)
        );
      }
      return next;
    });
  };

  const onRun = async () => {
    setRunError(false);
    setRunOutput("Running...");

    let runPayload;
    try {
      runPayload = validateBeforeRun(payload);
    } catch (err) {
      setRunError(true);
      setRunOutput(`Validation error: ${err.message}`);
      return;
    }

    const res = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(runPayload),
    });
    const result = await res.json();

    if (result.status === "success" && result.run_id) {
      window.location.href = `/ui/results.html?run_id=${result.run_id}`;
      return;
    }

    setRunOutput(JSON.stringify(result, null, 2));
    setRunError(true);
  };

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

  const repStimuli = availableStimuli;
  const addableStimuli = KNOWN_STIMULI.filter((s) => !repStimuli.includes(s));
  const selectedAddStimulus = addableStimuli.includes(newStimulus) ? newStimulus : (addableStimuli[0] || "");
  const similarity = payload?.experiment?.representation?.params?.similarity || null;
  const similarityEnabled = Boolean(similarity);

  React.useEffect(() => {
    if (!similarity) return;
    setSimilarityOffdiag(inferOffdiagFromSimilarity(similarity, 0.2));
  }, [similarity]);

  return (
    <>
      <h1>Virtual Shaping Lab - Builder</h1>
      <p>React builder (phase 4.7 slice). Core advanced controls are now native; legacy remains as fallback.</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/index.html"; }}>
          Back to Menu
        </button>
        <a className="btn secondary" href="/ui/builder_legacy.html">Open Legacy Builder</a>
        <button className="btn secondary" onClick={() => setShowAdvanced((v) => !v)}>
          {showAdvanced ? "Hide Advanced Controls" : "Show Advanced Controls"}
        </button>
      </div>

      {showAdvanced && (
      <div className="panel">
        <h3>Advanced Controls</h3>
        <label>Representation Stimuli</label>
        <div style={{ display: "grid", gap: "0.4rem", marginBottom: "0.8rem" }}>
          {repStimuli.map((s) => {
            const isReferenced = referencedStimuli.has(s);
            const canRemove = repStimuli.length > 1 && !isReferenced;
            return (
              <div key={s} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.6rem" }}>
                <span>{s}{isReferenced ? " (in use)" : ""}</span>
                <button
                  className="btn"
                  disabled={!canRemove}
                  onClick={() => updateRepresentationStimuli(repStimuli.filter((x) => x !== s))}
                >
                  Remove
                </button>
              </div>
            );
          })}
        </div>

        <label>Add Known Stimulus</label>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap", marginBottom: "0.8rem" }}>
          <select
            value={selectedAddStimulus}
            onChange={(e) => setNewStimulus(e.target.value)}
            disabled={!addableStimuli.length}
          >
            {addableStimuli.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <button
            className="btn"
            disabled={!selectedAddStimulus}
            onClick={() => updateRepresentationStimuli([...repStimuli, selectedAddStimulus])}
          >
            Add Stimulus
          </button>
        </div>

        <label style={{ marginTop: "0.6rem", display: "block" }}>
          <input
            type="checkbox"
            checked={Boolean(payload?.experiment?.context_inference?.enabled)}
            onChange={(e) => setPayload((prev) => {
              const next = JSON.parse(JSON.stringify(prev));
              if (!next.experiment.context_inference) next.experiment.context_inference = { enabled: false, max_contexts: 3 };
              next.experiment.context_inference.enabled = e.target.checked;
              return next;
            })}
          />{" "}
          Enable Context Inference
        </label>

        <label>Max Contexts</label>
        <input
          type="range"
          min="1"
          max="3"
          step="1"
          value={payload?.experiment?.context_inference?.max_contexts ?? 3}
          disabled={!payload?.experiment?.context_inference?.enabled}
          onChange={(e) => setPayload((prev) => {
            const next = JSON.parse(JSON.stringify(prev));
            if (!next.experiment.context_inference) next.experiment.context_inference = { enabled: false, max_contexts: 3 };
            next.experiment.context_inference.max_contexts = +e.target.value;
            return next;
          })}
        />
        <div>{payload?.experiment?.context_inference?.max_contexts ?? 3}</div>

        <h4 style={{ marginTop: "1rem", marginBottom: "0.4rem" }}>Similarity (Optional)</h4>
        <label style={{ display: "block" }}>
          <input
            type="checkbox"
            checked={similarityEnabled}
            onChange={(e) => setSimilarityEnabled(e.target.checked)}
          />{" "}
          Enable similarity matrix
        </label>

        <label>Off-diagonal Similarity: {similarityOffdiag.toFixed(2)}</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={similarityOffdiag}
          onChange={(e) => {
            const nextVal = +e.target.value;
            setSimilarityOffdiag(nextVal);
            if (similarityEnabled) applySimilarity(nextVal);
          }}
        />

        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.5rem" }}>
          <button className="btn" onClick={() => setSimilarityEnabled(true)}>
            Apply Default Matrix
          </button>
          <button className="btn secondary" onClick={() => {
            setSimilarityOffdiag(0.0);
            applySimilarity(0.0);
          }}>
            Reset to Identity
          </button>
        </div>

        {similarityEnabled && similarity?.stimuli?.length > 0 && (
          <div style={{ marginTop: "0.8rem", overflowX: "auto" }}>
            <table style={{ borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th />
                  {similarity.stimuli.map((label) => (
                    <th key={`sim-head-${label}`} style={{ padding: "4px 6px" }}>{label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {similarity.stimuli.map((rowLabel, i) => (
                  <tr key={`sim-row-${rowLabel}`}>
                    <th style={{ padding: "4px 6px" }}>{rowLabel}</th>
                    {similarity.stimuli.map((colLabel, j) => {
                      const cellValue = similarity?.values?.[i]?.[j] ?? (i === j ? 1.0 : 0.0);
                      return (
                        <td key={`sim-cell-${rowLabel}-${colLabel}`} style={{ padding: "2px 4px" }}>
                          <input
                            type="number"
                            min="0"
                            max="1"
                            step="0.05"
                            value={cellValue}
                            disabled={i === j}
                            style={{ width: "64px" }}
                            onChange={(e) => {
                              const v = Math.max(0, Math.min(1, parseFloat(e.target.value) || 0));
                              setPayload((prev) => {
                                const next = JSON.parse(JSON.stringify(prev));
                                const sim = next?.experiment?.representation?.params?.similarity;
                                if (!sim || !Array.isArray(sim.values)) return next;
                                sim.values[i][j] = v;
                                sim.values[j][i] = v;
                                return next;
                              });
                            }}
                          />
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
            <pre style={{ marginTop: "0.6rem" }}>
              {JSON.stringify(similarity, null, 2)}
            </pre>
          </div>
        )}

        <h4 style={{ marginTop: "1rem", marginBottom: "0.4rem" }}>Phase Stimulus Salience</h4>
        {activePhaseStimuli.length === 0 && (
          <div>No phase stimuli selected for this protocol.</div>
        )}
        {activePhaseStimuli.map((s) => {
          const value = readParamMapValue(payload?.experiment?.salience || {}, s, "salience", 0.2);
          return (
            <div key={`salience-${s}`} style={{ marginBottom: "0.4rem" }}>
              <label>{s}: {value.toFixed(2)}</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={value}
                onChange={(e) => setPayload((prev) => {
                  const next = JSON.parse(JSON.stringify(prev));
                  if (!next.experiment.salience) next.experiment.salience = {};
                  next.experiment.salience[s] = { salience: +e.target.value };
                  return next;
                })}
              />
            </div>
          );
        })}

        <h4 style={{ marginTop: "1rem", marginBottom: "0.4rem" }}>Phase Stimulus Attention</h4>
        {activePhaseStimuli.length === 0 && (
          <div>No phase stimuli selected for this protocol.</div>
        )}
        {activePhaseStimuli.map((s) => {
          const value = readParamMapValue(payload?.experiment?.attention || {}, s, "attention", 1.0);
          return (
            <div key={`attention-${s}`} style={{ marginBottom: "0.4rem" }}>
              <label>{s}: {value.toFixed(2)}</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={value}
                onChange={(e) => setPayload((prev) => {
                  const next = JSON.parse(JSON.stringify(prev));
                  if (!next.experiment.attention) next.experiment.attention = {};
                  next.experiment.attention[s] = { attention: +e.target.value };
                  return next;
                })}
              />
            </div>
          );
        })}
      </div>
      )}

      <BuilderPhaseList
        phases={phases}
        activePhaseIndex={activePhaseIndex}
        onSelectPhase={setActivePhaseIndex}
        onAddPhase={addPhase}
      />

      <div className="panel">
        <h3>Active Phase</h3>
        <label>Protocol</label>
        <select
          value={protocol}
          onChange={(e) => updateActive((p, stim) => {
            const migrated = migratePhaseProtocol(p, e.target.value, stim);
            p.protocol = migrated.protocol;
            p.stimuli = migrated.stimuli;
            p.params = migrated.params;
          })}
        >
          <option value="acquisition">acquisition</option>
          <option value="nonreinforcement">nonreinforcement</option>
          <option value="differential_acquisition">differential_acquisition</option>
          <option value="compound_acquisition">compound_acquisition</option>
          <option value="compound_nonreinforcement">compound_nonreinforcement</option>
          <option value="probe">probe</option>
          <option value="context_shift">context_shift</option>
          <option value="criterion_shift">criterion_shift</option>
        </select>

        {showSingleCs && (
          <>
            <label>CS+</label>
            <select
              multiple
              size="5"
              value={csPlusList}
              onChange={(e) => updateActive((p, stim) => {
                const nextPlus = Array.from(e.target.selectedOptions).map((o) => o.value);
                p.stimuli = { cs_plus: nextPlus.length ? nextPlus : [stim[0]] };
              })}
            >
              {availableStimuli.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </>
        )}

        {isDifferential && (
          <>
            <label>CS+</label>
            <select
              multiple
              size="5"
              value={csPlusList}
              onChange={(e) => updateActive((p, stim) => {
                const nextPlusRaw = Array.from(e.target.selectedOptions).map((o) => o.value);
                const nextPlus = nextPlusRaw.length ? nextPlusRaw : [stim[0]];
                const currentMinus = Array.isArray(p.stimuli?.cs_minus) ? p.stimuli.cs_minus : [stim[1] || stim[0]];
                const nextMinus = currentMinus.filter((s) => !nextPlus.includes(s));
                const fallbackMinus = stim.find((x) => !nextPlus.includes(x)) || nextPlus[0];
                p.stimuli = {
                  cs_plus: nextPlus,
                  cs_minus: nextMinus.length ? nextMinus : [fallbackMinus],
                };
              })}
            >
              {availableStimuli.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>

            <label>CS-</label>
            <select
              multiple
              size="5"
              value={csMinusList}
              onChange={(e) => updateActive((p, stim) => {
                const plus = Array.isArray(p.stimuli?.cs_plus) && p.stimuli.cs_plus.length
                  ? p.stimuli.cs_plus
                  : [stim[0]];
                const nextMinusRaw = Array.from(e.target.selectedOptions).map((o) => o.value);
                const filtered = nextMinusRaw.filter((s) => !plus.includes(s));
                const fallbackMinus = stim.find((x) => !plus.includes(x)) || plus[0];
                p.stimuli = {
                  cs_plus: plus,
                  cs_minus: filtered.length ? filtered : [fallbackMinus],
                };
              })}
            >
              {availableStimuli.map((s) => <option key={s} value={s} disabled={csPlusList.includes(s)}>{s}</option>)}
            </select>
          </>
        )}

        {isCompound && (
          <>
            <label>Compound Stimulus 1</label>
            <select
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

            <label>Compound Stimulus 2</label>
            <select
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

        {(isContextShift || isProbe || isCriterion) && (
          <>
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
          </>
        )}

        {showTrials && (
          <>
            <label>Trials</label>
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
          </>
        )}

        {showAlpha && (
          <>
            <label>Alpha</label>
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
            <label>Gamma</label>
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
        <h3>Payload</h3>
        <pre style={{ background: "#f5f5f5", padding: "1rem", borderRadius: "6px", overflowX: "auto" }}>
          {JSON.stringify(payload, null, 2)}
        </pre>
      </div>

      <div className="panel">
        <button className="btn" onClick={onRun}>Run Experiment</button>
        <pre className={runError ? "error" : ""}>{runOutput}</pre>
      </div>

      <details className="panel">
        <summary>Legacy Builder (Advanced Controls)</summary>
        <iframe
          title="legacy-builder"
          src="/ui/builder_legacy.html"
          style={{ width: "100%", minHeight: "78vh", border: "1px solid #ddd", borderRadius: "6px", marginTop: "0.8rem" }}
        />
      </details>
      <div className="panel">
        <small>
          Native advanced controls are now available here. Keep legacy fallback for remaining edge-case parity checks.
        </small>
      </div>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<BuilderShellApp />);

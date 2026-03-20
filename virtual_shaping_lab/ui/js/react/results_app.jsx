const KNOWN_FIGURES = [
  "line_plot.png",
  "dual_time_series_plot.png",
  "summation_plot.png",
  "retardation_curve_plot.png",
  "stimulus_bar_plot.png",
  "discrimination_curve_plot.png",
  "cumulative_response_plot.png",
  "cumulative_reward_plot.png",
  "reward_time_series_plot.png",
  "outcome_type_bar_plot.png",
  "phase_reward_bar_plot.png",
  "action_distribution_plot.png",
  "extinction_curve_plot.png",
  "probe_bar_plot.png",
  "auto_time_series_plot.png",
];

const KNOWN_METRICS = [
  "prediction_time_series.json",
  "reward_time_series.json",
  "cumulative_responses.json",
  "cumulative_rewards.json",
  "outcome_type_counts.json",
  "phase_reward_summary.json",
  "action_counts.json",
];

function inferFigureTags(fileName) {
  const file = String(fileName || "").toLowerCase();
  const tags = [];

  if (file.includes("probe")) tags.push("Probe");
  if (file.includes("compound") || file.includes("summation")) tags.push("Compound");
  if (file.includes("discrimination")) tags.push("CS+ / CS-");
  if (file.includes("extinction")) tags.push("Extinction");
  if (file.includes("curve") || file.includes("time_series") || file.includes("line_plot")) tags.push("Learning");
  if (file.includes("bar_plot") || file.includes("distribution")) tags.push("Distribution");
  return tags;
}

function inferMetricTags(fileName) {
  const file = String(fileName || "").toLowerCase();
  const tags = [];
  if (file.includes("time_series")) tags.push("Time Series");
  if (file.includes("counts")) tags.push("Counts");
  if (file.includes("summary")) tags.push("Summary");
  if (file.includes("reward")) tags.push("Reward");
  if (file.includes("prediction")) tags.push("Prediction");
  return tags;
}

function getRunId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("run_id");
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch ${url}`);
  }
  return res.json();
}

function valueToString(v) {
  if (v && typeof v === "object") {
    return JSON.stringify(v);
  }
  return String(v);
}

function operantConsequenceClass(mode) {
  if (mode === "positive_reinforcement" || mode === "negative_reinforcement") return "appetitive (+)";
  if (mode === "positive_punishment" || mode === "negative_punishment") return "aversive (-)";
  return "n/a";
}

function normalizeNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function operatorPipelineForRecord(payload, record) {
  const recordIdentity = record?.operator_pipeline_identity;
  if (recordIdentity && Array.isArray(recordIdentity.stage_keys) && recordIdentity.stage_keys.length) {
    return recordIdentity.stage_keys;
  }
  const payloadIdentity = payload?.metadata?.operator_pipeline_identity;
  if (payloadIdentity && Array.isArray(payloadIdentity.stage_keys) && payloadIdentity.stage_keys.length) {
    return payloadIdentity.stage_keys;
  }
  return ["Phi", "C", "K", "S", "P", "E", "U", "Policy"];
}

function behaviorToOperatorExplanation(payload, record, trialIndex) {
  const prediction = normalizeNumber(record?.prediction);
  const reward = normalizeNumber(record?.reward);
  const error = normalizeNumber(record?.prediction_error);
  const action = record?.action ?? "none";
  const operatorStages = operatorPipelineForRecord(payload, record);

  const lines = [];
  lines.push(`Trial ${trialIndex + 1}: action=${valueToString(action)}`);
  if (prediction !== null) lines.push(`Prediction (P): ${prediction.toFixed(6)}`);
  if (reward !== null) lines.push(`Outcome/Reward (r): ${reward.toFixed(6)}`);
  if (error !== null) {
    lines.push(`Prediction Error (E): ${error.toFixed(6)}`);
  } else if (prediction !== null && reward !== null) {
    lines.push(`Prediction Error (E): ${(reward - prediction).toFixed(6)} (derived)`);
  } else {
    lines.push("Prediction Error (E): unavailable");
  }
  lines.push(`Pipeline hooks: ${operatorStages.join(" -> ")}`);

  return {
    prediction,
    reward,
    error,
    action,
    operatorStages,
    summary: lines.join("\n"),
  };
}

function Summary({ payload, runId }) {
  const exp = payload?.experiment || {};
  const program = exp?.program || {};
  const agent = exp?.agent || {};
  const learning = agent?.learning || {};
  const runtime = exp?.runtime || {};
  const report = payload?.report || {};
  const representation = typeof agent.representation === "string"
    ? agent.representation
    : agent.representation?.name;
  const policy = agent.policy || {};
  const policyName = policy?.name || "unknown";
  const policyParams = policy?.params || {};
  const actions = Array.isArray(policyParams.actions)
    ? policyParams.actions.join(", ")
    : (policyParams.action ? String(policyParams.action) : "n/a");
  const phases = Array.isArray(program.phases)
    ? program.phases.map((p) => p.protocol).join(", ")
    : "";
  const consequenceMode = Array.isArray(program.phases) && program.phases.length > 0
    ? (program.phases[0]?.params?.consequence_mode || "n/a")
    : "n/a";
  const consequenceClass = operantConsequenceClass(consequenceMode);
  const isOperantConditioning = Array.isArray(program.phases) && program.phases.length > 0
    ? program.phases[0]?.protocol === "operant_conditioning"
    : false;

  return (
    <div className="summary">
      <div><strong>Run ID:</strong> {runId}</div>
      <div><strong>Preset:</strong> {report.preset || "unknown"}</div>
      <div><strong>Learner:</strong> {learning.rule || "unknown"}</div>
      <div><strong>Agent:</strong> {agent.name || "unknown"}</div>
      <div><strong>Representation:</strong> {representation || "unknown"}</div>
      <div><strong>Policy:</strong> {policyName}</div>
      <div><strong>Actions:</strong> {actions}</div>
      <div><strong>Phases:</strong> {phases || "none"}</div>
      {runtime?.update_mode && <div><strong>Update Mode:</strong> {runtime.update_mode}</div>}
      {runtime?.record_mode && <div><strong>Record Mode:</strong> {runtime.record_mode}</div>}
      {isOperantConditioning && (
        <>
          <div><strong>Consequence Mode:</strong> {consequenceMode}</div>
          <div><strong>Consequence Class:</strong> {consequenceClass}</div>
          <div><strong>Interpretation Note:</strong> v1.4 tracks consequence sign/class only.</div>
        </>
      )}
    </div>
  );
}

function FigureGallery({ runId, files }) {
  if (!files.length) {
    return <p>No figures found for this run.</p>;
  }

  return (
    <div className="figures">
      {files.map((file) => {
        const tags = inferFigureTags(file);
        return (
          <div key={file} className="summary" style={{ marginBottom: "1rem" }}>
            <div style={{ marginBottom: "0.45rem" }}>
              <strong>Figure:</strong> <code>{file}</code>
            </div>
            {tags.length > 0 && (
              <div className="links" style={{ marginBottom: "0.45rem" }}>
                {tags.map((tag) => (
                  <code key={`${file}-${tag}`} style={{ marginRight: "0.4rem" }}>{tag}</code>
                ))}
              </div>
            )}
            <img src={`/reports/${runId}/${file}`} alt={file} />
          </div>
        );
      })}
    </div>
  );
}

function MetricsList({ runId, files }) {
  if (!files.length) {
    return <p>No metric JSON files found for this run.</p>;
  }

  return (
    <div className="links">
      {files.map((file) => {
        const tags = inferMetricTags(file);
        return (
          <div key={file} style={{ marginBottom: "0.45rem" }}>
            <a href={`/reports/${runId}/metrics/${file}`} target="_blank" rel="noreferrer">
              {file}
            </a>
            {tags.length > 0 && (
              <span style={{ marginLeft: "0.45rem" }}>
                {tags.map((tag) => (
                  <code key={`${file}-${tag}`} style={{ marginRight: "0.35rem" }}>{tag}</code>
                ))}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}

function RecordsTable({ records, showAll }) {
  if (!records.length) {
    return <p>No records available.</p>;
  }

  const cols = Object.keys(records[0]);
  const view = showAll ? records : records.slice(0, 50);

  return (
    <table>
      <thead>
        <tr>
          {cols.map((c) => <th key={`head-${c}`}>{c}</th>)}
        </tr>
      </thead>
      <tbody>
        {view.map((r, idx) => (
          <tr key={`row-${idx}`}>
            {cols.map((c) => <td key={`cell-${idx}-${c}`}>{valueToString(r[c])}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ExplainabilityOverlay({ payload, records }) {
  const [selectedIndex, setSelectedIndex] = React.useState(0);

  React.useEffect(() => {
    if (!records.length) {
      setSelectedIndex(0);
      return;
    }
    setSelectedIndex((idx) => {
      if (idx < 0) return 0;
      if (idx >= records.length) return records.length - 1;
      return idx;
    });
  }, [records]);

  if (!records.length) {
    return <p>No records available for explainability overlay.</p>;
  }

  const selectedRecord = records[selectedIndex] || {};
  const explanation = behaviorToOperatorExplanation(payload, selectedRecord, selectedIndex);

  return (
    <div className="summary behavior-operator-overlay">
      <div style={{ marginBottom: "0.4rem" }}>
        <strong>Trial:</strong> {selectedIndex + 1} / {records.length}
      </div>
      <input
        type="range"
        min={0}
        max={records.length - 1}
        value={selectedIndex}
        onChange={(e) => setSelectedIndex(Number(e.target.value))}
      />
      <div className="trial-explanation-hook" style={{ marginTop: "0.6rem" }}>
        <div><strong>Prediction:</strong> {explanation.prediction === null ? "n/a" : explanation.prediction.toFixed(6)}</div>
        <div><strong>Outcome:</strong> {explanation.reward === null ? "n/a" : explanation.reward.toFixed(6)}</div>
        <div><strong>Prediction Error:</strong> {explanation.error === null ? "n/a" : explanation.error.toFixed(6)}</div>
        <div><strong>Operator Pipeline:</strong> {explanation.operatorStages.join(" -> ")}</div>
      </div>
      <pre className="operator-explainability" style={{ whiteSpace: "pre-wrap", marginTop: "0.6rem" }}>
        {explanation.summary}
      </pre>
    </div>
  );
}

function ResultsApp() {
  const [runId] = React.useState(getRunId);
  const [payload, setPayload] = React.useState(null);
  const [records, setRecords] = React.useState([]);
  const [figureFiles, setFigureFiles] = React.useState([]);
  const [metricFiles, setMetricFiles] = React.useState([]);
  const [showAll, setShowAll] = React.useState(false);
  const [error, setError] = React.useState("");
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!runId) {
        setError("Missing run_id in URL.");
        setLoading(false);
        return;
      }

      try {
        const payloadUrl = `/reports/${runId}/payload.json`;
        const recordsUrl = `/reports/${runId}/records.json`;

        const [nextPayload, nextRecords] = await Promise.all([
          fetchJson(payloadUrl),
          fetchJson(recordsUrl),
        ]);

        const existingFigures = [];
        for (const f of KNOWN_FIGURES) {
          try {
            const res = await fetch(`/reports/${runId}/${f}`, { method: "HEAD" });
            if (res.ok) {
              existingFigures.push(f);
            }
          } catch (_err) {
            // ignore individual figure lookup failures
          }
        }

        if (cancelled) {
          return;
        }

        const existingMetrics = [];
        for (const f of KNOWN_METRICS) {
          try {
            const res = await fetch(`/reports/${runId}/metrics/${f}`, { method: "HEAD" });
            if (res.ok) {
              existingMetrics.push(f);
            }
          } catch (_err) {
            // ignore metric lookup failures
          }
        }

        setPayload(nextPayload);
        setRecords(Array.isArray(nextRecords) ? nextRecords : []);
        setFigureFiles(existingFigures);
        setMetricFiles(existingMetrics);
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Failed to load results.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [runId]);

  if (loading) {
    return (
      <>
        <h1>Experiment Results</h1>
        <div className="summary">Loading summary...</div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <h1>Experiment Results</h1>
        <div className="summary">{error}</div>
      </>
    );
  }

  const pdfUrl = `/reports/${runId}/report.pdf`;
  const recordsUrl = `/reports/${runId}/records.json`;

  return (
    <>
      <h1>Experiment Results</h1>
      <Summary payload={payload} runId={runId} />

      <div className="summary">
        <button className="btn" onClick={() => window.history.back()}>Go back</button>
        <div className="links">
          <a href={pdfUrl} target="_blank" rel="noreferrer">Open PDF Report</a>
          <a href={pdfUrl} download>Download PDF</a>
        </div>
      </div>

      <h2>Figures</h2>
      <FigureGallery runId={runId} files={figureFiles} />

      <h2>Metrics</h2>
      <MetricsList runId={runId} files={metricFiles} />

      <h2>Explainability Overlay</h2>
      <ExplainabilityOverlay payload={payload} records={records} />

      <h2>Trial Records</h2>
      <button className="btn" onClick={() => setShowAll((v) => !v)}>
        {showAll ? "Show last 50" : "Show all"}
      </button>
      <button className="btn" onClick={() => {
        const link = document.createElement("a");
        link.href = recordsUrl;
        link.download = "records.json";
        link.click();
      }}>
        Download records.json
      </button>
      <div>
        <RecordsTable records={records} showAll={showAll} />
      </div>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<ResultsApp />);

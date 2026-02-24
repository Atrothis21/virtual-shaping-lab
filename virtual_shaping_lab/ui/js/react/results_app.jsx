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

function Summary({ payload, runId }) {
  const exp = payload?.experiment || {};
  const report = payload?.report || {};
  const representation = typeof exp.representation === "string"
    ? exp.representation
    : exp.representation?.name;
  const phases = Array.isArray(exp.phases)
    ? exp.phases.map((p) => p.protocol).join(", ")
    : "";

  return (
    <div className="summary">
      <div><strong>Run ID:</strong> {runId}</div>
      <div><strong>Preset:</strong> {report.preset || "unknown"}</div>
      <div><strong>Learner:</strong> {exp.learner || "unknown"}</div>
      <div><strong>Agent:</strong> {exp.agent || "unknown"}</div>
      <div><strong>Representation:</strong> {representation || "unknown"}</div>
      <div><strong>Phases:</strong> {phases || "none"}</div>
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

      <button className="btn" onClick={() => window.history.back()}>Go back</button>

      <div className="links">
        <a href={pdfUrl} target="_blank" rel="noreferrer">Open PDF Report</a>
        <a href={pdfUrl} download>Download PDF</a>
      </div>

      <h2>Figures</h2>
      <div className="figures">
        {figureFiles.map((file) => (
          <img key={file} src={`/reports/${runId}/${file}`} alt={file} />
        ))}
      </div>

      <h2>Metrics</h2>
      {metricFiles.length ? (
        <div className="links">
          {metricFiles.map((file) => (
            <a key={file} href={`/reports/${runId}/metrics/${file}`} target="_blank" rel="noreferrer">
              {file}
            </a>
          ))}
        </div>
      ) : (
        <p>No metric JSON files found for this run.</p>
      )}

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

window.VSLReact = window.VSLReact || {};

const STIMULI = ["lever", "tone", "noise", "light", "click"];
const ACTIONS = ["action_0", "action_1"];

function buildPolicy(params) {
  if (params.policy_type === "epsilon_greedy") {
    return {
      name: "epsilon_greedy",
      params: { actions: ACTIONS, epsilon: params.epsilon },
    };
  }
  if (params.policy_type === "softmax") {
    return {
      name: "softmax",
      params: { actions: ACTIONS, temperature: params.temperature },
    };
  }
  return {
    name: "fixed",
    params: { action: params.fixed_action },
  };
}

function buildPayload(params) {
  return {
    experiment: {
      learner: params.learner,
      agent: "operant_agent",
      policy: buildPolicy(params),
      representation: {
        name: params.representation,
        params: { stimuli: STIMULI, max_compound_size: 2 },
      },
      context_inference: { enabled: false, max_contexts: 3 },
      protocol: "matching_law",
      stimuli: {
        cs_plus: [params.cs_plus],
      },
      params: {
        n_trials: params.n_trials,
        schedule_left: {
          type: params.left_schedule_type,
          value: params.left_schedule_value,
        },
        schedule_right: {
          type: params.right_schedule_type,
          value: params.right_schedule_value,
        },
      },
    },
    report: { preset: "matching_law" },
  };
}

function validate(params) {
  if (params.n_trials < 1) throw new Error("n_trials must be at least 1");
}

function MatchingLawApp() {
  const [params, setParams] = React.useState({
    n_trials: 300,
    left_schedule_type: "variable_interval",
    left_schedule_value: 30,
    right_schedule_type: "variable_interval",
    right_schedule_value: 60,
    policy_type: "epsilon_greedy",
    epsilon: 0.1,
    temperature: 1.0,
    fixed_action: "action_0",
    cs_plus: "lever",
    learner: "q_learner",
    representation: "vector_elemental",
  });
  const [runOutput, setRunOutput] = React.useState("Not run yet.");
  const [runError, setRunError] = React.useState(false);

  const payload = React.useMemo(() => buildPayload(params), [params]);

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
      <h1>Matching Law Preset</h1>
      <p>Concurrent schedules with operant choice behavior.</p>

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
          max="1000"
          value={params.n_trials}
          onChange={(e) => setParams((prev) => ({ ...prev, n_trials: +e.target.value }))}
        />
      </div>

      <div className="panel">
        <h3>Left Schedule</h3>
        <label>Type</label>
        <select
          value={params.left_schedule_type}
          onChange={(e) => setParams((prev) => ({ ...prev, left_schedule_type: e.target.value }))}
        >
          <option value="variable_interval">variable_interval</option>
          <option value="variable_ratio">variable_ratio</option>
          <option value="fixed_interval">fixed_interval</option>
          <option value="fixed_ratio">fixed_ratio</option>
        </select>

        <label>Value: <span>{params.left_schedule_value}</span></label>
        <input
          type="range"
          min="1"
          max="100"
          value={params.left_schedule_value}
          onChange={(e) => setParams((prev) => ({ ...prev, left_schedule_value: +e.target.value }))}
        />
      </div>

      <div className="panel">
        <h3>Right Schedule</h3>
        <label>Type</label>
        <select
          value={params.right_schedule_type}
          onChange={(e) => setParams((prev) => ({ ...prev, right_schedule_type: e.target.value }))}
        >
          <option value="variable_interval">variable_interval</option>
          <option value="variable_ratio">variable_ratio</option>
          <option value="fixed_interval">fixed_interval</option>
          <option value="fixed_ratio">fixed_ratio</option>
        </select>

        <label>Value: <span>{params.right_schedule_value}</span></label>
        <input
          type="range"
          min="1"
          max="100"
          value={params.right_schedule_value}
          onChange={(e) => setParams((prev) => ({ ...prev, right_schedule_value: +e.target.value }))}
        />
      </div>

      <div className="panel">
        <h3>Policy</h3>
        <label>Policy Type</label>
        <select
          value={params.policy_type}
          onChange={(e) => setParams((prev) => ({ ...prev, policy_type: e.target.value }))}
        >
          <option value="epsilon_greedy">epsilon_greedy</option>
          <option value="softmax">softmax</option>
          <option value="fixed">fixed</option>
        </select>

        {params.policy_type === "epsilon_greedy" && (
          <div>
            <label>Epsilon: <span>{params.epsilon}</span></label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={params.epsilon}
              onChange={(e) => setParams((prev) => ({ ...prev, epsilon: +e.target.value }))}
            />
          </div>
        )}

        {params.policy_type === "softmax" && (
          <div>
            <label>Temperature: <span>{params.temperature}</span></label>
            <input
              type="range"
              min="0.1"
              max="5"
              step="0.1"
              value={params.temperature}
              onChange={(e) => setParams((prev) => ({ ...prev, temperature: +e.target.value }))}
            />
          </div>
        )}

        {params.policy_type === "fixed" && (
          <div>
            <label>Fixed Action</label>
            <select
              value={params.fixed_action}
              onChange={(e) => setParams((prev) => ({ ...prev, fixed_action: e.target.value }))}
            >
              <option value="action_0">action_0</option>
              <option value="action_1">action_1</option>
            </select>
          </div>
        )}
      </div>

      <div className="panel">
        <h3>Stimuli</h3>
        <label>CS+</label>
        <select
          value={params.cs_plus}
          onChange={(e) => setParams((prev) => ({ ...prev, cs_plus: e.target.value }))}
        >
          {STIMULI.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      <div className="panel">
        <h3>Learner / Representation</h3>
        <label>Learner</label>
        <select
          value={params.learner}
          onChange={(e) => setParams((prev) => ({ ...prev, learner: e.target.value }))}
        >
          <option value="q_learner">q_learner</option>
          <option value="td_value">td_value</option>
        </select>

        <label>Representation</label>
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
root.render(<MatchingLawApp />);

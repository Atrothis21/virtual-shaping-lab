window.VSLReact = window.VSLReact || {};

const STIMULI = ["lever", "tone", "noise", "light", "click"];
const OPERANT_ACTIONS = window.VSLReact.OPERANT_ACTIONS || ["nosepoke_L", "nosepoke_R", "leverpress", "keypeck"];
const CONSEQUENCE_MODE_OPTIONS = [
  { value: "positive_reinforcement", label: "Positive Reinforcement", rewardSign: +1 },
  { value: "negative_reinforcement", label: "Negative Reinforcement", rewardSign: +1 },
  { value: "positive_punishment", label: "Positive Punishment", rewardSign: -1 },
  { value: "negative_punishment", label: "Negative Punishment", rewardSign: -1 },
];

function consequenceLabel(mode) {
  const match = CONSEQUENCE_MODE_OPTIONS.find((opt) => opt.value === mode);
  return match ? match.label : mode;
}

function consequenceReward(mode, magnitude) {
  const match = CONSEQUENCE_MODE_OPTIONS.find((opt) => opt.value === mode);
  const sign = match ? match.rewardSign : 1;
  return sign * Math.max(0.1, Number(magnitude || 1));
}

function buildPolicy(params) {
  if (params.policy_type === "epsilon_greedy") {
    return {
      name: "epsilon_greedy",
      params: { actions: [params.action], epsilon: params.epsilon },
    };
  }
  if (params.policy_type === "softmax") {
    return {
      name: "softmax",
      params: { actions: [params.action], temperature: params.temperature },
    };
  }
  return {
    name: "fixed",
    params: { action: params.action },
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
      protocol: "operant_conditioning",
      stimuli: {
        cs_plus: [params.cs_plus],
      },
      params: {
        n_trials: params.n_trials,
        consequence_mode: params.consequence_mode,
        reward_schedule: {
          type: params.schedule_type,
          value: params.schedule_value,
          reward: consequenceReward(params.consequence_mode, params.consequence_magnitude),
        },
      },
    },
    report: { preset: "operant_conditioning" },
  };
}

function validate(params) {
  if (params.n_trials < 1) throw new Error("n_trials must be at least 1");
}

function OperantConditioningApp() {
  const [params, setParams] = React.useState({
    n_trials: 150,
    consequence_mode: "positive_reinforcement",
    consequence_magnitude: 1.0,
    schedule_type: "fixed_ratio",
    schedule_value: 5,
    policy_type: "epsilon_greedy",
    epsilon: 0.1,
    temperature: 1.0,
    action: "leverpress",
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
      <h1>Operant Conditioning Preset</h1>
      <p>Single-action operant learning with explicit consequence-mode semantics.</p>
      <p><em>Current v1.4 behavior:</em> consequence modes are sign-tracked (`+` appetitive vs `-` aversive) and do not yet model distinct process-level PR/NR or PP/NP mechanisms.</p>

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
        <h3>Consequence</h3>
        <label>Consequence Mode</label>
        <select
          value={params.consequence_mode}
          onChange={(e) => setParams((prev) => ({ ...prev, consequence_mode: e.target.value }))}
        >
          {CONSEQUENCE_MODE_OPTIONS.map((opt) => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
        </select>

        <label>Consequence Magnitude: <span>{params.consequence_magnitude.toFixed(1)}</span></label>
        <input
          type="range"
          min="0.1"
          max="3"
          step="0.1"
          value={params.consequence_magnitude}
          onChange={(e) => setParams((prev) => ({ ...prev, consequence_magnitude: +e.target.value }))}
        />

        <p><strong>Resolved consequence:</strong> {consequenceLabel(params.consequence_mode)} ({consequenceReward(params.consequence_mode, params.consequence_magnitude).toFixed(1)})</p>
      </div>

      <div className="panel">
        <h3>Schedule</h3>
        <label>Type</label>
        <select
          value={params.schedule_type}
          onChange={(e) => setParams((prev) => ({ ...prev, schedule_type: e.target.value }))}
        >
          <option value="fixed_ratio">fixed_ratio</option>
          <option value="variable_ratio">variable_ratio</option>
          <option value="fixed_interval">fixed_interval</option>
          <option value="variable_interval">variable_interval</option>
        </select>

        <label>Value: <span>{params.schedule_value}</span></label>
        <input
          type="range"
          min="1"
          max="50"
          value={params.schedule_value}
          onChange={(e) => setParams((prev) => ({ ...prev, schedule_value: +e.target.value }))}
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

        <label>Action</label>
        <select
          value={params.action}
          onChange={(e) => setParams((prev) => ({ ...prev, action: e.target.value }))}
        >
          {OPERANT_ACTIONS.map((a) => <option key={`op-a-${a}`} value={a}>{a}</option>)}
        </select>

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
root.render(<OperantConditioningApp />);

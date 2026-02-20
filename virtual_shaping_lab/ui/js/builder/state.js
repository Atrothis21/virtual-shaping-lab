let payload = null;
let activePhaseIndex = 0;

const phase = () => payload.experiment.phases[activePhaseIndex];

function debugLog(message, data = null) {
  const el = document.getElementById("debug-log");
  const stamp = new Date().toISOString().slice(11, 19);
  const entry = data ? `[${stamp}] ${message}\n${JSON.stringify(data, null, 2)}\n` : `[${stamp}] ${message}\n`;
  el.textContent = entry + el.textContent;
  console.log(message, data);
}

function initPayload() {
  const basePhase = buildPhase("acquisition", 0);
  payload = {
    experiment: {
      learner: "rescorla_wagner",
      agent: "classical_agent",
      representation: {
        name: "vector_elemental",
        params: { stimuli: STIMULI, max_compound_size: 2 }
      },
      context_inference: { enabled: false, max_contexts: 3 },
      salience: {},
      phases: [basePhase]
    },
    report: { preset: "acquisition" }
  };

  debugLog("Initialized default payload", payload);
}


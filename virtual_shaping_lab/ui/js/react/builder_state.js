window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click", "lever"];
const KNOWN_PRESETS = new Set([
  "aab_renewal",
  "aba_renewal",
  "abc_renewal",
  "acquisition",
  "basic_learning_curve",
  "blocking",
  "compound_acquisition",
  "conditioned_inhibition",
  "custom_protocol",
  "differential_acquisition",
  "extinction",
  "matching_law",
  "occasion_setting",
  "operant_conditioning",
  "rapid_reacquisition",
]);

function buildDefaultPhase(index) {
  return {
    name: `Phase ${index + 1}`,
    protocol: "acquisition",
    stimuli: { cs_plus: ["tone"] },
    params: { n_trials: 100, alpha: 0.2, gamma: 0.0 },
  };
}

function createInitialPayload() {
  return {
    experiment: {
      learner: "rescorla_wagner",
      agent: "classical_agent",
      representation: {
        name: "vector_elemental",
        params: { stimuli: STIMULI, max_compound_size: 2 },
      },
      context_inference: { enabled: false, max_contexts: 3 },
      salience: {},
      attention: {},
      phases: [buildDefaultPhase(0)],
    },
    report: { preset: "acquisition" },
  };
}

function normalizePayload(inputPayload) {
  const payload = JSON.parse(JSON.stringify(inputPayload));
  if (!payload.report) payload.report = { preset: "custom_protocol" };

  if (payload?.experiment?.attention) {
    Object.entries(payload.experiment.attention).forEach(([key, value]) => {
      if (value == null) return;
      if (typeof value === "number") {
        payload.experiment.attention[key] = { attention: value };
        return;
      }
      if (typeof value === "object" && typeof value.attention === "number") return;
      if (typeof value === "object" && value.attention == null && value.value != null) {
        payload.experiment.attention[key] = { attention: +value.value };
      }
    });
  }

  const phases = payload?.experiment?.phases || [];
  if (phases.length === 1) {
    const proto = phases[0].protocol;
    payload.report.preset = KNOWN_PRESETS.has(proto) ? proto : "custom_protocol";
  } else {
    payload.report.preset = "custom_protocol";
  }

  phases.forEach((phase) => {
    if (phase.protocol === "context_shift" && phase.stimuli) {
      delete phase.stimuli;
    }
  });

  return payload;
}

window.VSLReact.builderState = {
  buildDefaultPhase,
  createInitialPayload,
  normalizePayload,
};

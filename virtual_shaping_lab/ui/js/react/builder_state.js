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

const PHASE_DEFS = {
  acquisition: { n_trials: 100, stimulus_type: "cs" },
  nonreinforcement: { n_trials: 60, stimulus_type: "cs" },
  differential_acquisition: { n_trials: 120, stimulus_type: "cs_dual" },
  compound_acquisition: { n_trials: 100, stimulus_type: "compound" },
};

function safeClone(value) {
  return JSON.parse(JSON.stringify(value));
}

function getAvailableStimuli(payload) {
  const fromRep = payload?.experiment?.representation?.params?.stimuli;
  if (Array.isArray(fromRep) && fromRep.length) return fromRep;
  return [...STIMULI];
}

function pickStimulus(list, index, fallback) {
  if (Array.isArray(list) && list[index]) return list[index];
  return fallback;
}

function buildStimuliForProtocol(protocol, availableStimuli, prevStimuli) {
  const stimuli = Array.isArray(availableStimuli) && availableStimuli.length
    ? availableStimuli
    : [...STIMULI];
  const s1 = pickStimulus(stimuli, 0, "tone");
  const s2 = pickStimulus(stimuli, 1, s1 === "tone" ? "noise" : "tone");

  if (protocol === "compound_acquisition") {
    const prevCompound = Array.isArray(prevStimuli?.compound) ? prevStimuli.compound : [];
    const c1 = prevCompound[0] || s1;
    let c2 = prevCompound[1] || s2;
    if (c1 === c2) c2 = c1 === s1 ? s2 : s1;
    return { compound: [c1, c2] };
  }

  if (protocol === "differential_acquisition") {
    const plus = Array.isArray(prevStimuli?.cs_plus) ? [...prevStimuli.cs_plus] : [s1];
    let minus = Array.isArray(prevStimuli?.cs_minus) ? [...prevStimuli.cs_minus] : [s2];
    if (!plus.length) plus.push(s1);
    if (!minus.length) minus.push(s2);
    if (plus[0] === minus[0]) {
      minus[0] = plus[0] === s1 ? s2 : s1;
    }
    return { cs_plus: plus, cs_minus: minus };
  }

  const prevPlus = Array.isArray(prevStimuli?.cs_plus) ? [...prevStimuli.cs_plus] : [s1];
  return { cs_plus: prevPlus.length ? prevPlus : [s1] };
}

function buildParamsForProtocol(protocol, prevParams) {
  const def = PHASE_DEFS[protocol] || PHASE_DEFS.acquisition;
  const prior = prevParams || {};
  const n_trials = Number.isFinite(+prior.n_trials) ? +prior.n_trials : def.n_trials;

  if (protocol === "compound_acquisition") {
    return {
      n_trials,
      alpha_cs1: Number.isFinite(+prior.alpha_cs1) ? +prior.alpha_cs1 : 0.2,
      alpha_cs2: Number.isFinite(+prior.alpha_cs2) ? +prior.alpha_cs2 : 0.2,
      gamma: Number.isFinite(+prior.gamma) ? +prior.gamma : 0.0,
    };
  }

  return {
    n_trials,
    alpha: Number.isFinite(+prior.alpha) ? +prior.alpha : 0.2,
    gamma: Number.isFinite(+prior.gamma) ? +prior.gamma : 0.0,
  };
}

function coercePhaseShape(phase, availableStimuli) {
  const protocol = PHASE_DEFS[phase?.protocol] ? phase.protocol : "acquisition";
  return {
    name: phase?.name || "Phase 1",
    protocol,
    stimuli: buildStimuliForProtocol(protocol, availableStimuli, phase?.stimuli),
    params: buildParamsForProtocol(protocol, phase?.params),
  };
}

function buildDefaultPhase(index, availableStimuli) {
  return coercePhaseShape(
    {
      name: `Phase ${index + 1}`,
      protocol: "acquisition",
      stimuli: { cs_plus: ["tone"] },
      params: { n_trials: 100, alpha: 0.2, gamma: 0.0 },
    },
    availableStimuli || STIMULI
  );
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
      phases: [buildDefaultPhase(0, STIMULI)],
    },
    report: { preset: "acquisition" },
  };
}

function normalizePayload(inputPayload) {
  const payload = safeClone(inputPayload);
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

  const availableStimuli = getAvailableStimuli(payload);
  const rawPhases = payload?.experiment?.phases || [];
  payload.experiment.phases = rawPhases.map((phase) => coercePhaseShape(phase, availableStimuli));

  const phases = payload.experiment.phases;
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
  STIMULI,
  buildDefaultPhase,
  createInitialPayload,
  normalizePayload,
  getAvailableStimuli,
  coercePhaseShape,
};

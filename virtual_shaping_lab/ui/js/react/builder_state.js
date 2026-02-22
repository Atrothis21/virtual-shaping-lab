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

function dedupe(values) {
  const seen = new Set();
  const out = [];
  values.forEach((v) => {
    if (!seen.has(v)) {
      seen.add(v);
      out.push(v);
    }
  });
  return out;
}

function collectPriorStimuli(prevStimuli, availableStimuli) {
  const available = new Set(Array.isArray(availableStimuli) ? availableStimuli : STIMULI);
  const raw = [];

  if (Array.isArray(prevStimuli?.cs_plus)) raw.push(...prevStimuli.cs_plus);
  if (Array.isArray(prevStimuli?.cs_minus)) raw.push(...prevStimuli.cs_minus);
  if (Array.isArray(prevStimuli?.compound)) raw.push(...prevStimuli.compound);

  return dedupe(raw.filter((s) => available.has(s)));
}

function pickStimulus(pool, fallbackPool, index, notValue) {
  const merged = [...pool, ...fallbackPool];
  for (let i = 0; i < merged.length; i += 1) {
    const value = merged[(i + index) % merged.length];
    if (value != null && value !== notValue) return value;
  }
  return fallbackPool[0] || "tone";
}

function buildStimuliForProtocol(protocol, availableStimuli, prevStimuli) {
  const available = Array.isArray(availableStimuli) && availableStimuli.length
    ? availableStimuli
    : [...STIMULI];

  const prior = collectPriorStimuli(prevStimuli, available);
  const first = pickStimulus(prior, available, 0);
  const second = pickStimulus(prior, available, 1, first);

  if (protocol === "compound_acquisition") {
    return { compound: [first, second] };
  }

  if (protocol === "differential_acquisition") {
    const plus = Array.isArray(prevStimuli?.cs_plus) && prevStimuli.cs_plus.length
      ? prevStimuli.cs_plus[0]
      : first;
    const minusCandidate = Array.isArray(prevStimuli?.cs_minus) && prevStimuli.cs_minus.length
      ? prevStimuli.cs_minus[0]
      : second;
    const minus = minusCandidate === plus ? pickStimulus(prior, available, 1, plus) : minusCandidate;
    return { cs_plus: [plus], cs_minus: [minus] };
  }

  const csPlus = Array.isArray(prevStimuli?.cs_plus) && prevStimuli.cs_plus.length
    ? prevStimuli.cs_plus[0]
    : first;
  return { cs_plus: [csPlus] };
}

function finiteNumber(value, fallback) {
  return Number.isFinite(+value) ? +value : fallback;
}

function buildParamsForProtocol(protocol, prevParams) {
  const def = PHASE_DEFS[protocol] || PHASE_DEFS.acquisition;
  const prior = prevParams || {};
  const n_trials = finiteNumber(prior.n_trials, def.n_trials);
  const gamma = finiteNumber(prior.gamma, 0.0);

  if (protocol === "compound_acquisition") {
    const carryAlpha = finiteNumber(prior.alpha, 0.2);
    return {
      n_trials,
      alpha_cs1: finiteNumber(prior.alpha_cs1, carryAlpha),
      alpha_cs2: finiteNumber(prior.alpha_cs2, carryAlpha),
      gamma,
    };
  }

  const carryAlpha = Number.isFinite(+prior.alpha)
    ? +prior.alpha
    : finiteNumber(prior.alpha_cs1, finiteNumber(prior.alpha_cs2, 0.2));

  return {
    n_trials,
    alpha: carryAlpha,
    gamma,
  };
}

function buildDefaultPhase(index, availableStimuli) {
  return {
    name: `Phase ${index + 1}`,
    protocol: "acquisition",
    stimuli: buildStimuliForProtocol("acquisition", availableStimuli || STIMULI, null),
    params: buildParamsForProtocol("acquisition", null),
  };
}

function migratePhaseProtocol(phase, nextProtocol, availableStimuli) {
  const protocol = PHASE_DEFS[nextProtocol] ? nextProtocol : "acquisition";
  return {
    name: phase?.name || "Phase 1",
    protocol,
    stimuli: buildStimuliForProtocol(protocol, availableStimuli || STIMULI, phase?.stimuli),
    params: buildParamsForProtocol(protocol, phase?.params),
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
  STIMULI,
  buildDefaultPhase,
  migratePhaseProtocol,
  createInitialPayload,
  normalizePayload,
  getAvailableStimuli,
};

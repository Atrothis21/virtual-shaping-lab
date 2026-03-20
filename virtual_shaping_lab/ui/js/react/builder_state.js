window.VSLReact = window.VSLReact || {};

const STIMULI = ["tone", "noise", "light", "click", "lever"];
const BUILDER_SEED_KEY = "vsl_builder_seed_payload";
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
  "shaping",
  "resurgence",
  "superextinction",
  "spontaneous_recovery",
]);

const PHASE_DEFS = {
  acquisition: { n_trials: 100, stimulus_type: "cs" },
  nonreinforcement: { n_trials: 60, stimulus_type: "cs" },
  differential_acquisition: { n_trials: 120, stimulus_type: "cs_dual" },
  compound_acquisition: { n_trials: 100, stimulus_type: "compound" },
  compound_nonreinforcement: { n_trials: 60, stimulus_type: "compound" },
  probe: { n_trials: 20, stimulus_type: "cs" },
  context_shift: { n_trials: 0, stimulus_type: "none" },
  criterion_shift: { n_trials: 100, stimulus_type: "cs" },
};

const RAW_OPERATOR_WIRING_PATHS = [
  ["experiment", "runtime", "operator_pipeline"],
  ["experiment", "runtime", "operator_wiring"],
  ["experiment", "runtime", "operator_pipeline_overrides"],
  ["experiment", "runtime", "operator_graph"],
  ["experiment", "runtime", "operator_bindings"],
];

function safeClone(value) {
  return JSON.parse(JSON.stringify(value));
}

function getProgram(payload) {
  if (!payload.experiment || typeof payload.experiment !== "object") payload.experiment = {};
  if (!payload.experiment.program || typeof payload.experiment.program !== "object") {
    payload.experiment.program = {};
  }
  return payload.experiment.program;
}

function getAgent(payload) {
  if (!payload.experiment || typeof payload.experiment !== "object") payload.experiment = {};
  if (!payload.experiment.agent || typeof payload.experiment.agent !== "object") {
    payload.experiment.agent = {};
  }
  return payload.experiment.agent;
}

function getRuntime(payload) {
  if (!payload.experiment || typeof payload.experiment !== "object") payload.experiment = {};
  if (!payload.experiment.runtime || typeof payload.experiment.runtime !== "object") {
    payload.experiment.runtime = {};
  }
  return payload.experiment.runtime;
}

function getAvailableStimuli(payload) {
  const fromRep = payload?.experiment?.agent?.representation?.params?.stimuli;
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

  if (protocol === "compound_nonreinforcement") {
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

  if (protocol === "context_shift") {
    return {};
  }

  const csPlus = Array.isArray(prevStimuli?.cs_plus) && prevStimuli.cs_plus.length
    ? prevStimuli.cs_plus[0]
    : first;
  return { cs_plus: [csPlus] };
}

function finiteNumber(value, fallback) {
  return Number.isFinite(+value) ? +value : fallback;
}

function hasOwnPath(obj, path) {
  let cursor = obj;
  for (let i = 0; i < path.length; i += 1) {
    const key = path[i];
    if (!cursor || typeof cursor !== "object" || !Object.prototype.hasOwnProperty.call(cursor, key)) {
      return false;
    }
    cursor = cursor[key];
  }
  return true;
}

function findRawOperatorWiringPaths(payload) {
  return RAW_OPERATOR_WIRING_PATHS.filter((path) => hasOwnPath(payload, path));
}

function enforceControlSurfaceGuard(payload, options = {}) {
  const mode = String(options.mode || "builder").toLowerCase();
  const isExpert = mode === "expert";
  if (isExpert) return;
  const violations = findRawOperatorWiringPaths(payload);
  if (!violations.length) return;
  const formatted = violations.map((path) => path.join(".")).join(", ");
  throw new Error(
    `Raw operator wiring controls are only available in Expert mode. Remove: ${formatted}`,
  );
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

  if (protocol === "compound_nonreinforcement") {
    return {
      n_trials,
      alpha: finiteNumber(prior.alpha, 0.2),
      gamma,
    };
  }

  if (protocol === "probe") {
    return {
      n_trials,
      deliver_reward: Boolean(prior.deliver_reward),
      reward_value: finiteNumber(prior.reward_value, 0.0),
      context: ["A", "B", "C"].includes(prior.context) ? prior.context : "A",
    };
  }

  if (protocol === "context_shift") {
    return {
      context: ["A", "B", "C"].includes(prior.context) ? prior.context : "A",
    };
  }

  if (protocol === "criterion_shift") {
    const criterion = prior.criterion || {};
    return {
      n_trials,
      alpha: finiteNumber(prior.alpha, 0.2),
      gamma,
      context: ["A", "B", "C"].includes(prior.context) ? prior.context : "A",
      criterion: {
        type: "prediction_threshold",
        threshold: finiteNumber(criterion.threshold, 0.8),
        window: Math.max(1, Math.round(finiteNumber(criterion.window, 10))),
      },
      safety_cap: prior.safety_cap == null ? null : Math.max(1, Math.round(finiteNumber(prior.safety_cap, 200))),
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
  const seeded = loadSeedPayload();
  if (seeded) return seeded;

  const initialStimuli = [...STIMULI];
  return {
    experiment: {
      program: {
        phases: [buildDefaultPhase(0, initialStimuli)],
      },
      agent: {
        name: "classical_agent",
        representation: {
          name: "vector_elemental",
          params: { stimuli: initialStimuli, max_compound_size: 2 },
          salience: {},
        },
        learning: {
          rule: "rescorla_wagner",
          params: {},
          attention: {
            config: { name: "none", params: {} },
            initial: {},
          },
        },
        policy: null,
      },
      runtime: {
        update_mode: "trial",
        record_mode: "trial",
        context_inference: { enabled: false, max_contexts: 3 },
      },
    },
    report: { preset: "acquisition" },
  };
}

function loadSeedPayload() {
  try {
    const raw = window.localStorage.getItem(BUILDER_SEED_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    const normalized = normalizePayload(parsed);
    if (!normalized?.experiment) return null;
    window.localStorage.removeItem(BUILDER_SEED_KEY);
    return normalized;
  } catch (_err) {
    return null;
  }
}

function normalizePayload(inputPayload) {
  const payload = safeClone(inputPayload);
  if (!payload.report) payload.report = { preset: "custom_protocol" };

  if (!payload.experiment || typeof payload.experiment !== "object") {
    payload.experiment = {};
  }
  const exp = payload.experiment;

  // Seed-payload compatibility: lift old flat shape into canonical UI draft.
  if (!exp.program && Array.isArray(exp.phases)) {
    exp.program = { phases: safeClone(exp.phases) };
  }
  if (!exp.agent || typeof exp.agent !== "object" || Array.isArray(exp.agent)) {
    exp.agent = {};
  }
  if (!exp.runtime || typeof exp.runtime !== "object" || Array.isArray(exp.runtime)) {
    exp.runtime = {};
  }
  if (typeof exp.learner === "string") {
    if (!exp.agent.learning || typeof exp.agent.learning !== "object") exp.agent.learning = {};
    exp.agent.learning.rule = exp.learner;
    delete exp.learner;
  }
  if (typeof exp.agent === "string") {
    exp.agent = { name: exp.agent };
  }
  if (exp.representation) {
    exp.agent.representation = safeClone(exp.representation);
    delete exp.representation;
  }
  if (Object.prototype.hasOwnProperty.call(exp, "policy")) {
    exp.agent.policy = safeClone(exp.policy);
    delete exp.policy;
  }
  if (exp.context_inference) {
    exp.runtime.context_inference = safeClone(exp.context_inference);
    delete exp.context_inference;
  }
  if (exp.salience) {
    if (!exp.agent.representation || typeof exp.agent.representation !== "object") {
      exp.agent.representation = { name: "vector_elemental", params: {} };
    }
    exp.agent.representation.salience = safeClone(exp.salience);
    delete exp.salience;
  }
  if (exp.attention) {
    if (!exp.agent.learning || typeof exp.agent.learning !== "object") exp.agent.learning = {};
    if (!exp.agent.learning.attention || typeof exp.agent.learning.attention !== "object") {
      exp.agent.learning.attention = { config: { name: "none", params: {} }, initial: {} };
    }
    exp.agent.learning.attention.initial = safeClone(exp.attention);
    delete exp.attention;
  }

  const program = getProgram(payload);
  const phases = Array.isArray(program.phases) ? program.phases : [];
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
    if (!Number.isFinite(Number(phase.trials))) {
      const nTrials = phase?.params?.n_trials;
      phase.trials = Number.isFinite(Number(nTrials)) ? Number(nTrials) : 1;
    }
    if (!phase.params || typeof phase.params !== "object") {
      phase.params = {};
    }
    phase.params.n_trials = phase.trials;
  });
  program.phases = phases;

  return payload;
}

function hasPriorLearning(phases, index) {
  for (let i = 0; i < index; i += 1) {
    const proto = phases[i]?.protocol;
    if (
      proto === "acquisition"
      || proto === "nonreinforcement"
      || proto === "differential_acquisition"
      || proto === "compound_acquisition"
      || proto === "compound_nonreinforcement"
      || proto === "criterion_shift"
    ) {
      return true;
    }
  }
  return false;
}

function validateBeforeRun(inputPayload, options = {}) {
  const payload = normalizePayload(inputPayload);
  enforceControlSurfaceGuard(payload, options);
  const phases = payload?.experiment?.program?.phases || [];
  const repStimuli = payload?.experiment?.agent?.representation?.params?.stimuli || [];
  const repSet = new Set(Array.isArray(repStimuli) ? repStimuli : []);

  if (!Array.isArray(phases) || phases.length === 0) {
    throw new Error("At least one phase is required.");
  }

  phases.forEach((phase, idx) => {
    const phaseNum = idx + 1;
    const proto = phase?.protocol;
    const stimuli = phase?.stimuli || {};
    const params = phase?.params || {};

    if (!proto) {
      throw new Error(`Phase ${phaseNum} is missing a protocol.`);
    }

    if (
      (proto === "nonreinforcement"
        || proto === "compound_nonreinforcement"
        || proto === "probe"
        || proto === "criterion_shift")
      && !hasPriorLearning(phases, idx)
    ) {
      throw new Error(`Phase ${phaseNum} (${proto}) requires a prior learning phase.`);
    }

    if (proto === "acquisition" || proto === "nonreinforcement" || proto === "probe" || proto === "criterion_shift") {
      if (!Array.isArray(stimuli.cs_plus) || stimuli.cs_plus.length === 0) {
        throw new Error(`Phase ${phaseNum} (${proto}) requires at least one CS+ stimulus.`);
      }
    }

    if (proto === "differential_acquisition") {
      const plus = Array.isArray(stimuli.cs_plus) ? stimuli.cs_plus : [];
      const minus = Array.isArray(stimuli.cs_minus) ? stimuli.cs_minus : [];
      if (!plus.length || !minus.length) {
        throw new Error(`Phase ${phaseNum} (differential_acquisition) requires CS+ and CS- stimuli.`);
      }
      const overlap = plus.filter((s) => minus.includes(s));
      if (overlap.length) {
        throw new Error(`Phase ${phaseNum} (differential_acquisition) CS+ and CS- must not overlap.`);
      }
    }

    if (proto === "compound_acquisition" || proto === "compound_nonreinforcement") {
      const compound = Array.isArray(stimuli.compound) ? stimuli.compound : [];
      if (compound.length < 2) {
        throw new Error(`Phase ${phaseNum} (${proto}) requires a 2-stimulus compound.`);
      }
      if (compound[0] === compound[1]) {
        throw new Error(`Phase ${phaseNum} (${proto}) requires two distinct compound stimuli.`);
      }
    }

    if (proto === "context_shift") {
      const context = params.context;
      if (!["A", "B", "C"].includes(context)) {
        throw new Error(`Phase ${phaseNum} (context_shift) requires context A, B, or C.`);
      }
    }

    const referenced = [];
    if (Array.isArray(stimuli.cs_plus)) referenced.push(...stimuli.cs_plus);
    if (Array.isArray(stimuli.cs_minus)) referenced.push(...stimuli.cs_minus);
    if (Array.isArray(stimuli.compound)) referenced.push(...stimuli.compound);
    referenced.forEach((s) => {
      if (!repSet.has(s)) {
        throw new Error(`Phase ${phaseNum} references stimulus '${s}' not present in representation stimuli.`);
      }
    });
  });

  return payload;
}

window.VSLReact.builderState = {
  STIMULI,
  BUILDER_SEED_KEY,
  buildDefaultPhase,
  migratePhaseProtocol,
  createInitialPayload,
  loadSeedPayload,
  normalizePayload,
  enforceControlSurfaceGuard,
  validateBeforeRun,
  getAvailableStimuli,
  RAW_OPERATOR_WIRING_PATHS,
};

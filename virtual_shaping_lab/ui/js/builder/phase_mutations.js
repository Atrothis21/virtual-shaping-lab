function getPreviousStimuliCandidates() {
  if (activePhaseIndex <= 0) return [];
  const prev = payload.experiment.phases[activePhaseIndex - 1];
  if (!prev || !prev.stimuli) return [];

  if (Array.isArray(prev.stimuli.compound)) return prev.stimuli.compound;
  if (Array.isArray(prev.stimuli.cs_plus)) return prev.stimuli.cs_plus;
  return [];
}

function syncNonreinforcementTargets() {
  const p = phase();
  if (!p || p.protocol !== "nonreinforcement") return;

  // No payload-level target/reference; runtime will infer reference stimuli.
}

function onProtocolChanged(original, next) {
  const p = phase();

  const schema = ensurePhaseSchema(next);

  p.params = {};
  p.stimuli = {};

  if (schema) {
    p.stimuli = schemaStimuliDefaults(schema);
    p.params = schemaParamDefaults(schema);
  } else {
    // Minimal fallback until schema loads
    if (next === "compound_acquisition") {
      p.stimuli = { compound: [STIMULI[0], STIMULI[1]] };
      p.params = { n_trials: 100, alpha_cs1: 0.2, alpha_cs2: 0.12, gamma: 0.0 };
    } else if (next === "compound_nonreinforcement") {
      p.stimuli = { compound: [STIMULI[0], STIMULI[1]] };
      p.params = { n_trials: 60, alpha: 0.2, gamma: 0.0 };
    } else if (next === "differential_acquisition") {
      p.stimuli = { cs_plus: [STIMULI[0]], cs_minus: [STIMULI[1]] };
      p.params = { n_trials: 100, alpha: 0.2, gamma: 0.0 };
    } else if (next === "nonreinforcement") {
      p.stimuli = { cs_plus: [STIMULI[0]] };
      p.params = { n_trials: 60, alpha: 0.2, gamma: 0.0 };
    } else if (next === "probe") {
      p.stimuli = { cs_plus: [STIMULI[0]] };
      p.params = { n_trials: 20, deliver_reward: false, reward_value: 0.0 };
    } else if (next === "context_shift") {
      p.stimuli = {};
      p.params = { context: "A" };
    } else if (next === "criterion_shift") {
      p.stimuli = { cs_plus: [STIMULI[0]] };
      p.params = { context: "A" };
    } else {
      p.stimuli = { cs_plus: [STIMULI[0]] };
      p.params = { n_trials: 100, alpha: 0.2, gamma: 0.0, outcome: 1 };
    }
  }

  if (next === "nonreinforcement") {
    const prevCandidates = getPreviousStimuliCandidates();
    if (prevCandidates.length) {
      p.stimuli.cs_plus = [prevCandidates[0]];
    }
  }
}

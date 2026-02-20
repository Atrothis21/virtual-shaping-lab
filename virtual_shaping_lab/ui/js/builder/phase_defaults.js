function buildPhase(protocolName, index) {
  const schema = ensurePhaseSchema(protocolName);

  const phase = {
    name: `Phase ${index + 1}`,
    protocol: protocolName,
    stimuli: {},
    params: {},
  };

  if (schema) {
    phase.stimuli = schemaStimuliDefaults(schema);
    phase.params = schemaParamDefaults(schema);
  } else {
    // Fallback defaults while schema is loading
    if (protocolName === "compound_acquisition") {
      phase.stimuli = { compound: [STIMULI[0], STIMULI[1]] };
      phase.params = { n_trials: 100, alpha_cs1: 0.2, alpha_cs2: 0.12, gamma: 0.0 };
    } else if (protocolName === "compound_nonreinforcement") {
      phase.stimuli = { compound: [STIMULI[0], STIMULI[1]] };
      phase.params = { n_trials: 60, alpha: 0.2, gamma: 0.0 };
    } else if (protocolName === "differential_acquisition") {
      phase.stimuli = { cs_plus: [STIMULI[0]], cs_minus: [STIMULI[1]] };
      phase.params = { n_trials: 100, alpha: 0.2, gamma: 0.0 };
    } else if (protocolName === "nonreinforcement") {
      phase.stimuli = { cs_plus: [STIMULI[0]] };
      phase.params = { n_trials: 60, alpha: 0.2, gamma: 0.0 };
    } else if (protocolName === "probe") {
      phase.stimuli = { cs_plus: [STIMULI[0]] };
      phase.params = { n_trials: 20, deliver_reward: false, reward_value: 0.0 };
    } else if (protocolName === "context_shift") {
      phase.stimuli = {};
      phase.params = { context: "A" };
    } else if (protocolName === "criterion_shift") {
      phase.stimuli = { cs_plus: [STIMULI[0]] };
      phase.params = { context: "A" };
    } else {
      phase.stimuli = { cs_plus: [STIMULI[0]] };
      phase.params = { n_trials: 100, alpha: 0.2, gamma: 0.0, outcome: 1 };
    }
  }

  if (protocolName === "nonreinforcement") {
    const prevCandidates = getPreviousStimuliCandidates();
    if (prevCandidates.length) {
      phase.stimuli.cs_plus = [prevCandidates[0]];
    }
  }

  return phase;
}

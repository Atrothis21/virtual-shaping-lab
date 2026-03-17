function applyContextPropagation(phases) {
  let currentContext = "A";
  phases.forEach(p => {
    if (p.protocol === "context_shift") {
      currentContext = p.params.context || "A";
    } else {
      p.params.context = currentContext;
    }
  });
}

function validatePhaseOrder(phases) {
  let seenLearning = false;
  let seenAcquisition = false;

  phases.forEach((p, i) => {
    const proto = p.protocol;

    if (LEARNING_PHASES.has(proto)) {
      seenLearning = true;
      seenAcquisition = true;
    }

    if (PHASE_CONSTRAINTS.requires_prior_learning.has(proto) && !seenLearning) {
      throw new Error(`Phase ${i + 1} (${proto}) requires a prior learning phase`);
    }

    if (PHASE_CONSTRAINTS.requires_prior_acquisition.has(proto) && !seenAcquisition) {
      throw new Error(`Phase ${i + 1} (${proto}) requires a prior acquisition phase`);
    }
  });
}

function validateBeforeRun(payload) {
  if (!payload || !payload.experiment) {
    throw new Error("Invalid payload.");
  }

  const phases =
    payload.experiment &&
    payload.experiment.program &&
    Array.isArray(payload.experiment.program.phases)
      ? payload.experiment.program.phases
      : [];
  if (!Array.isArray(phases) || phases.length === 0) {
    throw new Error("At least one phase is required.");
  }

  phases.forEach((p, idx) => {
    if (!p.protocol) {
      throw new Error(`Phase ${idx + 1} is missing a protocol.`);
    }
    if (!p.params) {
      throw new Error(`Phase ${idx + 1} is missing params.`);
    }

    // Differential acquisition must include at least one CS-
    if (p.protocol === "differential_acquisition") {
      const csMinus = p.stimuli?.cs_minus || [];
      if (!Array.isArray(csMinus) || csMinus.length === 0) {
        throw new Error(`Phase ${idx + 1} (differential_acquisition) requires at least one CS- stimulus.`);
      }
    }
  });
}


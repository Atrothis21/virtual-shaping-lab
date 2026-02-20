const STIMULI = ["tone", "noise", "light", "click", "lever"];

const PHASE_DEFS = {
  acquisition: { trials: { key: "n_trials", default: 100, min: 1, max: 500 }, params: ["alpha", "gamma"], advancedParams: ["outcome"], stimuli: "cs" },
  nonreinforcement: { trials: { key: "n_trials", default: 60, min: 1, max: 500 }, params: ["alpha", "gamma"], stimuli: "cs" },
  differential_acquisition: { trials: { key: "n_trials", default: 120, min: 1, max: 500 }, params: ["alpha", "gamma"], stimuli: "cs" },
  compound_acquisition: { trials: { key: "n_trials", default: 100, min: 1, max: 500 }, params: ["alpha_cs1", "alpha_cs2", "gamma"], stimuli: "compound" },
  compound_nonreinforcement: { trials: { key: "n_trials", default: 80, min: 1, max: 500 }, params: ["alpha", "gamma"], stimuli: "compound" },
  probe: { trials: { key: "n_trials", default: 20, min: 1, max: 200 }, params: [], stimuli: "cs" },
  context_shift: { trials: null, params: ["context"], stimuli: "none" },
  criterion_shift: { trials: { key: "n_trials", default: 100, min: 1, max: 500 }, params: ["alpha", "gamma"], stimuli: "cs" }
};

const PHASE_CONSTRAINTS = {
  requires_prior_learning: new Set(["nonreinforcement", "compound_nonreinforcement", "probe", "criterion_shift"]),
  requires_prior_acquisition: new Set(["nonreinforcement", "compound_nonreinforcement", "probe", "criterion_shift"])
};

const LEARNING_PHASES = new Set([
  "acquisition",
  "nonreinforcement",
  "differential_acquisition",
  "compound_acquisition",
  "compound_nonreinforcement",
  "criterion_shift"
]);

function renderPayload() {
  const out = document.getElementById("payload-preview");
  if (!out) {
    return;
  }

  if (!payload.report) {
    payload.report = { preset: "custom_protocol" };
  }

  if (payload?.experiment?.attention) {
    Object.entries(payload.experiment.attention).forEach(([key, value]) => {
      if (value == null) return;
      if (typeof value === "number") {
        payload.experiment.attention[key] = { attention: value };
        return;
      }
      if (typeof value === "object" && typeof value.attention === "number") {
        return;
      }
      if (typeof value === "object" && value.attention == null && value.value != null) {
        payload.experiment.attention[key] = { attention: +value.value };
      }
    });
  }

  const phases = payload?.experiment?.phases || [];
  const knownPresets = new Set([
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

  if (phases.length === 1) {
    const proto = phases[0].protocol;
    payload.report.preset = knownPresets.has(proto) ? proto : "custom_protocol";
  } else {
    payload.report.preset = "custom_protocol";
  }

  phases.forEach(phase => {
    if (phase.protocol === "context_shift" && phase.stimuli) {
      delete phase.stimuli;
    }
  });

  out.textContent = JSON.stringify(payload, null, 2);
  debugLog("renderPayload", payload);
}

window.VSLReact = window.VSLReact || {};

function draft_to_payload(draft) {
  const normalized = draft && typeof draft === "object" ? draft : {};
  const presetKey = normalized.preset_key || normalized.protocol_key || "custom_protocol";
  const runMode = normalized.run_mode_hint === "tick" ? "tick" : "trial";
  return {
    settings: {
      update_mode: runMode,
      record_mode: "trial",
    },
    report: {
      preset: String(presetKey),
    },
  };
}

window.VSLReact.builderDraftTranslator = {
  draft_to_payload,
};

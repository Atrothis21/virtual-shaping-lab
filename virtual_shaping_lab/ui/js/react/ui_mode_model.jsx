window.VSLReact = window.VSLReact || {};

window.VSLReact.uiModes = window.VSLReact.uiModes || (() => {
  const MODES = Object.freeze({
    PRESET: "preset",
    TEACHING: "teaching",
    BUILDER: "builder",
    EXPERT: "expert",
  });

  const SURFACE_MODE_OPTIONS = Object.freeze({
    index: [MODES.PRESET],
    presets: [MODES.PRESET, MODES.TEACHING],
    preset_detail: [MODES.PRESET, MODES.TEACHING, MODES.BUILDER, MODES.EXPERT],
    builder: [MODES.BUILDER, MODES.EXPERT],
  });

  const STORAGE_KEY = "vsl_ui_mode";

  function validMode(mode) {
    return Object.values(MODES).includes(mode);
  }

  function sanitizeMode(mode, fallback) {
    return validMode(mode) ? mode : fallback;
  }

  function resolveMode(surfaceKey, requested) {
    const options = SURFACE_MODE_OPTIONS[surfaceKey] || [MODES.PRESET];
    const requestedMode = sanitizeMode(String(requested || "").toLowerCase(), "");
    if (requestedMode && options.includes(requestedMode)) {
      return requestedMode;
    }
    try {
      const persisted = sanitizeMode(localStorage.getItem(STORAGE_KEY), "");
      if (persisted && options.includes(persisted)) return persisted;
    } catch (_err) {
      // ignore storage access issues
    }
    return options[0];
  }

  function activate(surfaceKey, requested) {
    const mode = resolveMode(surfaceKey, requested);
    window.VSLReact.currentMode = mode;
    window.VSLReact.currentSurface = surfaceKey;
    window.VSLReact.availableModesForSurface = SURFACE_MODE_OPTIONS[surfaceKey] || [MODES.PRESET];
    try {
      localStorage.setItem(STORAGE_KEY, mode);
    } catch (_err) {
      // ignore storage access issues
    }
    return mode;
  }

  return {
    MODES,
    SURFACE_MODE_OPTIONS,
    resolveMode,
    activate,
  };
})();


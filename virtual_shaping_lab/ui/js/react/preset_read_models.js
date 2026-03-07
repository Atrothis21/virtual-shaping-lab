window.VSLReact = window.VSLReact || {};

function adaptPhenomenonSpecToPresetViewModel(key, spec) {
  const source = spec && typeof spec === "object" ? spec : {};
  const runModes = Array.isArray(source.default_run_modes) ? source.default_run_modes : [];
  const expectedSignals = Array.isArray(source.expected_signals) ? source.expected_signals : [];
  return {
    key,
    title: source.name || key,
    description: source.description || "No description provided.",
    protocolKey: source.protocol_key || "n/a",
    expectedSignals,
    defaultTemplate: source.recommended_template_key || source.default_template_key || "n/a",
    runModes,
  };
}

function selectPresetCatalogReadModel(catalogState) {
  const extensions = catalogState && catalogState.extensions ? catalogState.extensions : null;
  const phenomena = extensions && extensions.phenomena && typeof extensions.phenomena === "object"
    ? extensions.phenomena
    : {};

  const items = Object.entries(phenomena).map(([key, spec]) => {
    return adaptPhenomenonSpecToPresetViewModel(key, spec);
  });

  return {
    status: catalogState ? catalogState.requestStatus : "idle",
    items,
  };
}

function filterPresetViewModels(items, searchQuery, runModeFilter) {
  const source = Array.isArray(items) ? items : [];
  let next = [...source];
  const q = String(searchQuery || "").trim().toLowerCase();
  if (q) {
    next = next.filter((item) => {
      return (
        item.title.toLowerCase().includes(q) ||
        item.description.toLowerCase().includes(q) ||
        item.protocolKey.toLowerCase().includes(q)
      );
    });
  }
  if (runModeFilter && runModeFilter !== "all") {
    next = next.filter((item) => item.runModes.includes(runModeFilter));
  }
  return next;
}

function sortPresetViewModels(items, sortBy) {
  const source = Array.isArray(items) ? items : [];
  const next = [...source];
  if (sortBy === "protocol") {
    next.sort((a, b) => a.protocolKey.localeCompare(b.protocolKey));
  } else {
    next.sort((a, b) => a.title.localeCompare(b.title));
  }
  return next;
}

function selectPresetFromReadModels(allItems, filteredItems, selectedPresetKey) {
  const filtered = Array.isArray(filteredItems) ? filteredItems : [];
  const all = Array.isArray(allItems) ? allItems : [];
  if (!selectedPresetKey) return filtered[0] || null;
  const fromFiltered = filtered.find((item) => item.key === selectedPresetKey);
  if (fromFiltered) return fromFiltered;
  return all.find((item) => item.key === selectedPresetKey) || null;
}

window.VSLReact.presetReadModels = {
  adaptPhenomenonSpecToPresetViewModel,
  selectPresetCatalogReadModel,
  filterPresetViewModels,
  sortPresetViewModels,
  selectPresetFromReadModels,
};

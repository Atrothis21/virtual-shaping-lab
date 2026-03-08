(function initPresetsRoute(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});
  const routeContainers = (VSLReact.routeContainers = VSLReact.routeContainers || {});

  function getSignalSemanticTone(signal) {
    const normalized = String(signal || "").toLowerCase();
    if (normalized.includes("cs+") || normalized.includes("plus") || normalized.includes("acquisition")) return "cs-plus";
    if (normalized.includes("cs-") || normalized.includes("minus") || normalized.includes("nonreinforcement")) return "cs-minus";
    if (normalized.includes("probe") || normalized.includes("test")) return "probe";
    if (normalized.includes("compound")) return "compound";
    return "learning";
  }

  function getProtocolAccentTone(protocolKey) {
    const normalized = String(protocolKey || "").toLowerCase();
    if (normalized.includes("nonreinforcement") || normalized.includes("extinction")) return "cs-minus";
    if (normalized.includes("probe")) return "probe";
    if (normalized.includes("compound")) return "compound";
    if (normalized.includes("acquisition")) return "cs-plus";
    return "learning";
  }

  function PresetSignalChips({ signals, maxItems }) {
    const entries = Array.isArray(signals) ? signals : [];
    if (!entries.length) return <span className="preset-empty-cue">n/a</span>;
    const sliced = Number.isFinite(maxItems) ? entries.slice(0, maxItems) : entries;
    return (
      <div className="preset-signal-chip-row">
        {sliced.map((signal) => (
          <span key={`signal-${signal}`} className={`preset-signal-chip ${getSignalSemanticTone(signal)}`}>
            {signal}
          </span>
        ))}
      </div>
    );
  }

  function PresetBrowserGrid({ items, onUseInBuilder }) {
    if (!Array.isArray(items) || items.length === 0) {
      return (
        <div className="route-card">
          <p>No presets available from catalog metadata.</p>
        </div>
      );
    }
    return (
      <div className="preset-grid">
        {items.map((item) => (
          <div className={`route-card preset-card accent-${getProtocolAccentTone(item.protocolKey)}`} key={item.key}>
            <div className="route-card-header">
              <h2>{item.title}</h2>
              <span className={`vsl-status-badge semantic ${getProtocolAccentTone(item.protocolKey)}`}>{item.protocolKey}</span>
            </div>
            <p className="preset-meta-line">Preset Key: <code>{item.key}</code></p>
            <p>{item.description}</p>
            <p style={{ marginBottom: "0.35rem" }}><strong>Template:</strong> <code>{item.defaultTemplate}</code></p>
            <p style={{ marginBottom: "0.35rem" }}><strong>Run Modes:</strong> {item.runModes.length ? item.runModes.join(", ") : "n/a"}</p>
            <p style={{ marginBottom: "0.7rem" }}><strong>Expected Signals:</strong></p>
            <PresetSignalChips signals={item.expectedSignals} maxItems={3} />
            <div className="route-actions">
              <button type="button" className="route-action route-action-primary" onClick={() => typeof onUseInBuilder === "function" && onUseInBuilder(item)}>
                Use In Builder
              </button>
              <a className="route-action route-action-secondary" href="/ui/presets.html">Open Legacy Presets</a>
            </div>
          </div>
        ))}
      </div>
    );
  }

  function PresetDetailPanel({ item, onResolvePreset, onResolveRun, onResolveRunReport, actionState, RouteNotice }) {
    if (!item) {
      return (
        <div className="route-card preset-detail">
          <h2>Preset Detail</h2>
          <p>Select a preset to inspect details and lifecycle actions.</p>
        </div>
      );
    }
    return (
      <div className={`route-card preset-detail accent-${getProtocolAccentTone(item.protocolKey)}`}>
        <div className="route-card-header">
          <h2>{item.title}</h2>
          <span className={`vsl-status-badge semantic ${getProtocolAccentTone(item.protocolKey)}`}>{item.protocolKey}</span>
        </div>
        <p className="preset-meta-line">Preset Key: <code>{item.key}</code></p>
        <p>{item.description}</p>
        <p style={{ marginBottom: "0.35rem" }}><strong>Recommended Template:</strong> <code>{item.defaultTemplate}</code></p>
        <p style={{ marginBottom: "0.35rem" }}><strong>Run Modes:</strong> {item.runModes.length ? item.runModes.join(", ") : "n/a"}</p>
        <p style={{ marginBottom: "0.7rem" }}><strong>Expected Signals:</strong></p>
        <PresetSignalChips signals={item.expectedSignals} />
        <div className="route-actions">
          <button type="button" className="route-action route-action-primary" onClick={() => typeof onResolvePreset === "function" && onResolvePreset(item)}>Resolve Preset</button>
          <button type="button" className="route-action route-action-secondary" onClick={() => typeof onResolveRun === "function" && onResolveRun(item)}>Resolve + Run</button>
          <button type="button" className="route-action route-action-secondary" onClick={() => typeof onResolveRunReport === "function" && onResolveRunReport(item)}>Resolve + Run + Report</button>
        </div>
        <div className="preset-action-status">
          <strong>Action Status:</strong> <code>{actionState && actionState.status ? actionState.status : "idle"}</code>
          {actionState && actionState.step ? <span style={{ marginLeft: "0.45rem" }}><strong>Step:</strong> <code>{actionState.step}</code></span> : null}
          {actionState && actionState.message ? <RouteNotice level="info" className="preset-action-message" message={actionState.message} /> : null}
          {actionState && actionState.error && actionState.error.message ? (
            <RouteNotice level="error" className="preset-action-error" message={String(actionState.error.message)} />
          ) : null}
        </div>
      </div>
    );
  }

  function PhenomenonSupportPanel({ item }) {
    const accentTone = item ? getProtocolAccentTone(item.protocolKey) : "learning";
    const signalCount = item && Array.isArray(item.expectedSignals) ? item.expectedSignals.length : 0;
    return (
      <div className={`route-card phenomenon-support accent-${accentTone}`}>
        <div className="route-card-header">
          <h2>Phenomenon Support</h2>
          <span className="vsl-status-badge warning">metadata-only</span>
        </div>
        {!item ? (
          <p>Select a preset to view phenomenon guidance.</p>
        ) : (
          <>
            <p className="phenomenon-meta-line">Support Mode: <code>setup-guidance</code> | signal_count: <code>{signalCount}</code></p>
            <p><strong>{item.title}</strong> is currently selected. Use this panel to review expected signatures and reporting guidance before execution.</p>
            <p style={{ marginBottom: "0.35rem" }}><strong>Recommended Report Template:</strong> <code>{item.defaultTemplate}</code></p>
            <p style={{ marginBottom: "0.35rem" }}><strong>Expected Signals:</strong></p>
            <PresetSignalChips signals={item.expectedSignals} />
            <p style={{ marginTop: "0.55rem" }}>Scope note: this panel is a lightweight support surface. Full narrative teaching mode is out of scope for V2.17.1.</p>
          </>
        )}
      </div>
    );
  }

  function PresetsRouteContainer({
    catalogState,
    onSeedDraftFromPreset,
    onNavigate,
    onResolvePresetAction,
    onResolveRunAction,
    onResolveRunReportAction,
    actionState,
    RouteNotice,
    routeKeys,
  }) {
    const uiPrimitives = VSLReact.uiPrimitives || {};
    const RouteStatePanel = uiPrimitives.RouteStatePanel || (() => null);
    const keys = routeKeys || { builder: "builder", run: "run", report: "report" };
    const readModelApi = VSLReact.presetReadModels || {};
    const selectPresetCatalogReadModel = readModelApi.selectPresetCatalogReadModel;
    const filterPresetViewModels = readModelApi.filterPresetViewModels;
    const sortPresetViewModels = readModelApi.sortPresetViewModels;
    const selectPresetFromReadModels = readModelApi.selectPresetFromReadModels;

    const viewModel = React.useMemo(() => {
      if (typeof selectPresetCatalogReadModel === "function") return selectPresetCatalogReadModel(catalogState);
      return { status: "idle", items: [] };
    }, [catalogState, selectPresetCatalogReadModel]);

    const [searchQuery, setSearchQuery] = React.useState("");
    const [runModeFilter, setRunModeFilter] = React.useState("all");
    const [sortBy, setSortBy] = React.useState("title");
    const [selectedPresetKey, setSelectedPresetKey] = React.useState("");

    const filteredItems = React.useMemo(() => {
      const filtered = typeof filterPresetViewModels === "function"
        ? filterPresetViewModels(viewModel.items, searchQuery, runModeFilter)
        : [...viewModel.items];
      return typeof sortPresetViewModels === "function" ? sortPresetViewModels(filtered, sortBy) : filtered;
    }, [filterPresetViewModels, runModeFilter, searchQuery, sortBy, sortPresetViewModels, viewModel.items]);
    const browserStatePanel = React.useMemo(() => {
      if (viewModel.status === "loading") {
        return { state: "loading", title: "Catalog Loading", message: "Loading presets from catalog metadata..." };
      }
      if (viewModel.status === "error") {
        return { state: "error", title: "Catalog Unavailable", message: "Preset catalog request failed. Retry catalog refresh." };
      }
      if (viewModel.status === "success" && filteredItems.length === 0) {
        return { state: "empty", title: "No Presets Match Filters", message: "Adjust search/sort/run mode filters to broaden results." };
      }
      return { state: "success", title: "Presets Ready", message: `${filteredItems.length} preset(s) available for selection.` };
    }, [filteredItems.length, viewModel.status]);

    const selectedPreset = React.useMemo(() => {
      if (typeof selectPresetFromReadModels === "function") {
        return selectPresetFromReadModels(viewModel.items, filteredItems, selectedPresetKey);
      }
      if (!selectedPresetKey) return filteredItems[0] || null;
      return filteredItems.find((item) => item.key === selectedPresetKey) || viewModel.items.find((item) => item.key === selectedPresetKey) || null;
    }, [filteredItems, selectedPresetKey, selectPresetFromReadModels, viewModel.items]);

    const handleSeedToBuilder = React.useCallback((item) => {
      if (!item) return;
      if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
      if (typeof onNavigate === "function") onNavigate(keys.builder);
    }, [keys.builder, onNavigate, onSeedDraftFromPreset]);

    const handleResolvePreset = React.useCallback(async (item) => {
      if (!item) return;
      if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
      if (typeof onResolvePresetAction === "function") {
        const result = await onResolvePresetAction(item);
        if (result && result.ok && typeof onNavigate === "function") onNavigate(keys.run);
        return;
      }
      if (typeof onNavigate === "function") onNavigate(keys.run);
    }, [keys.run, onNavigate, onResolvePresetAction, onSeedDraftFromPreset]);

    const handleResolveRun = React.useCallback(async (item) => {
      if (!item) return;
      if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
      if (typeof onResolveRunAction === "function") {
        const result = await onResolveRunAction(item);
        if (result && result.ok && typeof onNavigate === "function") onNavigate(keys.run);
        return;
      }
      if (typeof onNavigate === "function") onNavigate(keys.run);
    }, [keys.run, onNavigate, onResolveRunAction, onSeedDraftFromPreset]);

    const handleResolveRunReport = React.useCallback(async (item) => {
      if (!item) return;
      if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
      if (typeof onResolveRunReportAction === "function") {
        const result = await onResolveRunReportAction(item);
        if (result && result.ok && typeof onNavigate === "function") onNavigate(result.routeKey || keys.report);
        return;
      }
      if (typeof onNavigate === "function") onNavigate(keys.report);
    }, [keys.report, onNavigate, onResolveRunReportAction, onSeedDraftFromPreset]);

    return (
      <section className="vsl-page-region">
        <div className="route-card">
          <div className="route-card-header">
            <h2>Presets Browser</h2>
            <span className="vsl-status-badge">{viewModel.status}</span>
          </div>
          <p>Browse catalog-backed phenomenon presets and choose a starting point.</p>
          <div className="preset-controls">
            <label>Search<input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search preset, protocol, signal..." /></label>
            <label>Run Mode<select value={runModeFilter} onChange={(e) => setRunModeFilter(e.target.value)}><option value="all">All</option><option value="trial">Trial</option><option value="tick">Tick</option></select></label>
            <label>Sort<select value={sortBy} onChange={(e) => setSortBy(e.target.value)}><option value="title">Name</option><option value="protocol">Protocol</option></select></label>
          </div>
          <RouteStatePanel state={browserStatePanel.state} title={browserStatePanel.title} message={browserStatePanel.message} />
        </div>

        <PresetDetailPanel item={selectedPreset} onResolvePreset={handleResolvePreset} onResolveRun={handleResolveRun} onResolveRunReport={handleResolveRunReport} actionState={actionState} RouteNotice={RouteNotice} />
        <PhenomenonSupportPanel item={selectedPreset} />
        <PresetBrowserGrid items={filteredItems} onUseInBuilder={handleSeedToBuilder} />

        <div className="route-card" style={{ marginTop: "0.75rem" }}>
          <strong>Quick Select</strong>
          <p style={{ marginTop: "0.35rem", marginBottom: "0.5rem" }}>Choose which preset appears in detail view.</p>
          <div className="preset-detail-selectors">
            {filteredItems.slice(0, 10).map((item) => (
              <button type="button" key={`select-${item.key}`} className={`route-action route-action-secondary ${selectedPreset?.key === item.key ? "active" : ""}`} onClick={() => setSelectedPresetKey(item.key)}>
                {item.title}
              </button>
            ))}
          </div>
        </div>
      </section>
    );
  }

  routeContainers.PresetsRouteContainer = PresetsRouteContainer;
})(typeof window !== "undefined" ? window : globalThis);

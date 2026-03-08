(function initLauncherRoute(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});
  const routeContainers = (VSLReact.routeContainers = VSLReact.routeContainers || {});

  function selectFeaturedPresetItems(catalogState, maxItems) {
    const readModels = VSLReact.presetReadModels || {};
    const selectPresetCatalogReadModel = readModels.selectPresetCatalogReadModel;
    const viewModel =
      typeof selectPresetCatalogReadModel === "function"
        ? selectPresetCatalogReadModel(catalogState)
        : { items: [] };
    const items = Array.isArray(viewModel.items) ? [...viewModel.items] : [];
    const ranked = items.sort((a, b) => {
      const ax = `${a.key} ${a.title} ${a.protocolKey}`.toLowerCase();
      const bx = `${b.key} ${b.title} ${b.protocolKey}`.toLowerCase();
      const score = (text) => {
        if (text.includes("acquisition")) return 0;
        if (text.includes("extinction")) return 1;
        if (text.includes("blocking")) return 2;
        return 3;
      };
      const s = score(ax) - score(bx);
      if (s !== 0) return s;
      return String(a.title || "").localeCompare(String(b.title || ""));
    });
    const cap = Number.isFinite(maxItems) ? maxItems : 4;
    return ranked.slice(0, cap);
  }

  function buildRecentActivityItems(runState, reportState, maxItems) {
    const rows = [];
    if (runState && runState.activeRunId) {
      rows.push({
        key: `run-${runState.activeRunId}`,
        label: "Recent run",
        value: `${runState.activeRunId} (${runState.lifecycleState || "unknown"})`,
      });
    }
    if (reportState && reportState.runId) {
      rows.push({
        key: `report-${reportState.runId}`,
        label: "Recent report",
        value: String(reportState.runId),
      });
    }
    const cap = Number.isFinite(maxItems) ? maxItems : 3;
    return rows.slice(0, cap);
  }

  function LauncherRouteContainer({
    onNavigate,
    routeKeys,
    catalogState,
    runState,
    reportState,
    onSeedDraftFromPreset,
    onResolveRunAction,
    onResolveRunReportAction,
    actionState,
  }) {
    const launcherFeature = VSLReact.launcherFeature || {};
    const LauncherView = launcherFeature.LauncherView || (() => null);
    const toPresets = routeKeys && routeKeys.presets ? routeKeys.presets : "presets";
    const toBuilder = routeKeys && routeKeys.builder ? routeKeys.builder : "builder";
    const toRun = routeKeys && routeKeys.run ? routeKeys.run : "run";
    const toReport = routeKeys && routeKeys.report ? routeKeys.report : "report";
    const featured = React.useMemo(() => selectFeaturedPresetItems(catalogState, 4), [catalogState]);
    const recentItems = React.useMemo(() => buildRecentActivityItems(runState, reportState, 3), [reportState, runState]);

    const handleQuickRun = React.useCallback(async (item) => {
      if (!item) return;
      if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
      if (typeof onResolveRunAction === "function") {
        const result = await onResolveRunAction(item);
        if (result && result.ok && typeof onNavigate === "function") onNavigate(toRun);
        return;
      }
      if (typeof onNavigate === "function") onNavigate(toPresets);
    }, [onNavigate, onResolveRunAction, onSeedDraftFromPreset, toPresets, toRun]);

    const handleQuickRunReport = React.useCallback(async (item) => {
      if (!item) return;
      if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
      if (typeof onResolveRunReportAction === "function") {
        const result = await onResolveRunReportAction(item);
        if (result && result.ok && typeof onNavigate === "function") onNavigate(result.routeKey || toReport);
        return;
      }
      if (typeof onNavigate === "function") onNavigate(toPresets);
    }, [onNavigate, onResolveRunReportAction, onSeedDraftFromPreset, toPresets, toReport]);

    return (
      <div className="route-card launcher-route-card">
        <div className="route-card-header">
          <h2>Home</h2>
          <span className="vsl-status-badge">First-open launcher</span>
        </div>
        <LauncherView
          onRunPreset={() => typeof onNavigate === "function" && onNavigate(toPresets)}
          onBuildExperiment={() => typeof onNavigate === "function" && onNavigate(toBuilder)}
        />
        <div className="launcher-callout-row">
          <span className="vsl-status-badge semantic learning">
            Example preset: {featured[0] ? featured[0].title : "acquisition"}
          </span>
        </div>
        <section className="launcher-featured">
          <h3>Featured presets</h3>
          <div className="launcher-featured-grid">
            {featured.map((item) => (
              <article key={`featured-${item.key}`} className="launcher-featured-card">
                <div className="launcher-featured-title-row">
                  <strong>{item.title}</strong>
                  <code>{item.protocolKey}</code>
                </div>
                <p>{item.description}</p>
                <div className="route-actions">
                  <button type="button" className="route-action route-action-primary" onClick={() => handleQuickRun(item)}>Run preset</button>
                  <button type="button" className="route-action route-action-secondary" onClick={() => handleQuickRunReport(item)}>Run + report</button>
                  <button type="button" className="route-action route-action-secondary" onClick={() => typeof onNavigate === "function" && onNavigate(toPresets)}>More presets</button>
                </div>
              </article>
            ))}
          </div>
          {actionState && actionState.message ? <p className="launcher-action-message">{actionState.message}</p> : null}
        </section>
        <section className="launcher-recent-strip">
          <h3>Recent activity</h3>
          {recentItems.length ? (
            <ul>
              {recentItems.map((row) => (
                <li key={row.key}><strong>{row.label}:</strong> <code>{row.value}</code></li>
              ))}
            </ul>
          ) : (
            <p>No recent run/report yet.</p>
          )}
        </section>
      </div>
    );
  }

  routeContainers.LauncherRouteContainer = LauncherRouteContainer;
})(window);

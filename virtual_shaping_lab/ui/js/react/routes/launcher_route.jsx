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

  function toEpochMs(value) {
    if (Number.isFinite(Number(value))) return Number(value);
    if (typeof value === "string") {
      const parsed = Date.parse(value);
      return Number.isFinite(parsed) ? parsed : 0;
    }
    return 0;
  }

  function buildRecentActivityItems(runState, reportState, maxItems) {
    const rows = [];
    if (runState && runState.activeRunId) {
      rows.push({
        key: `run-${runState.activeRunId}`,
        label: "Recent run",
        value: `${runState.activeRunId} (${runState.lifecycleState || "unknown"})`,
        atMs: toEpochMs(runState.lastPollAtMs),
      });
    }
    if (reportState && reportState.runId) {
      const reportMeta = reportState.reportData && reportState.reportData.metadata && typeof reportState.reportData.metadata === "object"
        ? reportState.reportData.metadata
        : {};
      rows.push({
        key: `report-${reportState.runId}`,
        label: "Recent report",
        value: String(reportState.runId),
        atMs: Math.max(
          toEpochMs(reportState.lastUpdatedAtMs),
          toEpochMs(reportMeta.generated_at_ms || reportMeta.generated_at || 0)
        ),
      });
    }
    const ranked = rows.sort((a, b) => {
      const timeDelta = Number(b.atMs || 0) - Number(a.atMs || 0);
      if (timeDelta !== 0) return timeDelta;
      return String(a.key).localeCompare(String(b.key));
    });
    const cap = Number.isFinite(maxItems) ? maxItems : 3;
    return ranked.slice(0, cap);
  }

  function LauncherRouteContainer({
    onNavigate,
    routeKeys,
    catalogState,
    runState,
    reportState,
    onStartGuidedBuilder,
    onSeedDraftFromPreset,
    onResolveRunAction,
    onResolveRunReportAction,
    onRetryCatalog,
    actionState,
  }) {
    const launcherFeature = VSLReact.launcherFeature || {};
    const LauncherView = launcherFeature.LauncherView || (() => null);
    const uiPrimitives = VSLReact.uiPrimitives || {};
    const RouteNotice = uiPrimitives.RouteNotice || (() => null);
    const RecoveryActionRow = uiPrimitives.RecoveryActionRow || (() => null);
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
          onBuildExperiment={() => {
            if (typeof onStartGuidedBuilder === "function") onStartGuidedBuilder(featured[0] || null);
            if (typeof onNavigate === "function") onNavigate(toBuilder);
          }}
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
                <div className="launcher-featured-meta"><strong>Experiment type:</strong> <code>{item.protocolKey}</code></div>
                <p>{item.description}</p>
                <div className="route-actions">
                  <button type="button" className="route-action route-action-secondary" onClick={() => handleQuickRun(item)}>Run preset</button>
                  <button type="button" className="route-action route-action-secondary" onClick={() => handleQuickRunReport(item)}>Run + report</button>
                  <button type="button" className="route-action route-action-tertiary" onClick={() => typeof onNavigate === "function" && onNavigate(toPresets)}>More presets</button>
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
        {catalogState && catalogState.requestStatus === "error" ? (
          <>
            <RouteNotice level="error" message="Launcher metadata is unavailable. Retry catalog load or continue with presets/builder." />
            <RecoveryActionRow
              onRetry={onRetryCatalog}
              onGoPresets={() => typeof onNavigate === "function" && onNavigate(toPresets)}
              onGoBuilder={() => typeof onNavigate === "function" && onNavigate(toBuilder)}
            />
          </>
        ) : null}
        {actionState && actionState.error && actionState.error.message ? (
          <>
            <RouteNotice level="error" message={String(actionState.error.message)} />
            <RecoveryActionRow
              onRetry={() => featured[0] ? handleQuickRun(featured[0]) : null}
              onGoPresets={() => typeof onNavigate === "function" && onNavigate(toPresets)}
              onGoBuilder={() => typeof onNavigate === "function" && onNavigate(toBuilder)}
            />
          </>
        ) : null}
      </div>
    );
  }

  routeContainers.LauncherRouteContainer = LauncherRouteContainer;
})(window);

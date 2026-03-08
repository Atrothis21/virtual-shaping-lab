(function initFirstOpenStateSelector(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});
  const launcherFeature = (VSLReact.launcherFeature = VSLReact.launcherFeature || {});

  function selectFirstOpenState(input) {
    const data = input && typeof input === "object" ? input : {};
    const recentItems = Array.isArray(data.recentItems) ? data.recentItems : [];
    const hasVisitedLauncher = Boolean(data.hasVisitedLauncher);

    // V2.17.5 policy:
    // - first-time/no-history: show launcher
    // - has recent activity: still show launcher with recent strip visible
    // - future extension may honor user preference for last-worked context
    return {
      initialRouteKey: "home",
      showRecentStrip: recentItems.length > 0,
      reason: hasVisitedLauncher ? "visited_launcher_before" : "first_open_or_no_history",
    };
  }

  launcherFeature.selectFirstOpenState = selectFirstOpenState;
})(window);

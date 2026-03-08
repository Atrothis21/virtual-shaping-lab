(function initLauncherRoute(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});
  const routeContainers = (VSLReact.routeContainers = VSLReact.routeContainers || {});

  function LauncherRouteContainer({ onNavigate, routeKeys }) {
    const launcherFeature = VSLReact.launcherFeature || {};
    const LauncherView = launcherFeature.LauncherView || (() => null);
    const toPresets = routeKeys && routeKeys.presets ? routeKeys.presets : "presets";
    const toBuilder = routeKeys && routeKeys.builder ? routeKeys.builder : "builder";

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
      </div>
    );
  }

  routeContainers.LauncherRouteContainer = LauncherRouteContainer;
})(window);

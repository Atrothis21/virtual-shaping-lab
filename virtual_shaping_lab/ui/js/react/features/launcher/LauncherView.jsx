(function initLauncherView(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});
  const launcherFeature = (VSLReact.launcherFeature = VSLReact.launcherFeature || {});

  function LauncherView({ onRunPreset, onBuildExperiment }) {
    const LauncherCard = launcherFeature.LauncherCard || (() => null);
    return (
      <section className="launcher-view">
        <h2>Choose your starting path</h2>
        <p>Start quickly with a preset, or build an experiment step by step.</p>
        <div className="launcher-grid">
          <LauncherCard
            tone="dominant"
            title="Run a preset"
            description="Start with a curated experiment and get results quickly."
            actionLabel="Run preset"
            onAction={onRunPreset}
          />
          <LauncherCard
            tone="secondary"
            title="Build an experiment"
            description="Create a guided draft and prepare your own experiment."
            actionLabel="Build experiment"
            onAction={onBuildExperiment}
          />
        </div>
      </section>
    );
  }

  launcherFeature.LauncherView = LauncherView;
})(window);

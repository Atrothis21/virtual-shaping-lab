(function initLauncherCard(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});
  const launcherFeature = (VSLReact.launcherFeature = VSLReact.launcherFeature || {});

  function LauncherCard({ title, description, actionLabel, onAction, tone }) {
    const toneClass = tone ? ` launcher-card-${tone}` : "";
    return (
      <article className={`launcher-card${toneClass}`}>
        <h3>{title}</h3>
        <p>{description}</p>
        <button type="button" className="route-action route-action-primary" onClick={onAction}>
          {actionLabel}
        </button>
      </article>
    );
  }

  launcherFeature.LauncherCard = LauncherCard;
})(window);

(function initLauncherCard(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});
  const launcherFeature = (VSLReact.launcherFeature = VSLReact.launcherFeature || {});

  function LauncherCard({ title, description, actionLabel, onAction, tone }) {
    const toneClass = tone ? ` launcher-card-${tone}` : "";
    const actionClass = tone === "dominant" ? "route-action route-action-primary" : "route-action route-action-secondary";
    return (
      <article className={`launcher-card${toneClass}`} data-launcher-tone={tone || "default"}>
        <h3>{title}</h3>
        <p>{description}</p>
        <button type="button" className={actionClass} onClick={onAction}>
          {actionLabel}
        </button>
      </article>
    );
  }

  launcherFeature.LauncherCard = LauncherCard;
})(window);

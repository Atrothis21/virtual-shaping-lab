window.VSLReact = window.VSLReact || {};

function NotificationToast({ item }) {
  return (
    <div className={`toast ${item.level || "info"}`}>
      <strong>{item.title || "Notice"}</strong>
      <div>{item.message || ""}</div>
    </div>
  );
}

function NotificationStack({ items }) {
  if (!Array.isArray(items) || items.length === 0) return null;
  return (
    <div className="toast-stack" role="status" aria-live="polite">
      {items.map((item) => (
        <NotificationToast key={item.id || `${item.level}-${item.message}`} item={item} />
      ))}
    </div>
  );
}

function GlobalBanner({ level, title, message, actionLabel, onAction }) {
  if (!title && !message) return null;
  return (
    <div className={`global-banner ${level || "info"}`} role="status">
      <div className="banner-content">
        <strong>{title || "Status"}</strong>
        <span>{message || ""}</span>
      </div>
      {actionLabel ? (
        <button type="button" className="banner-action" onClick={onAction}>
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}

function BlockingPanel({ title, message, actionLabel, onAction }) {
  return (
    <section className="blocking-panel" role="alert">
      <h2>{title || "Action required"}</h2>
      <p>{message || "The requested content is currently unavailable."}</p>
      {actionLabel ? (
        <button type="button" className="route-action" onClick={onAction}>
          {actionLabel}
        </button>
      ) : null}
    </section>
  );
}

function RouteNotice({ level, title, message, className }) {
  if (!title && !message) return null;
  return (
    <div className={`route-notice ${level || "info"} ${className || ""}`.trim()} role="status">
      {title ? <strong>{title}</strong> : null}
      {message ? <span>{message}</span> : null}
    </div>
  );
}

function buildConstraintChips(constraint) {
  if (!constraint || typeof constraint !== "object") return [];
  const chips = [];
  if (constraint.hidden) chips.push({ key: "hidden", text: "Hidden", tone: "is-hidden" });
  if (constraint.disabled) chips.push({ key: "disabled", text: "Disabled", tone: "is-disabled" });
  if (constraint.warning) chips.push({ key: "warning", text: "Warn", tone: "is-warning" });
  if (constraint.autoCorrect) chips.push({ key: "auto-correct", text: "Auto-correct", tone: "is-autocorrect" });
  if (constraint.autoCorrectBlocked) chips.push({ key: "auto-correct-blocked", text: "Auto-correct blocked", tone: "is-blocked" });
  return chips;
}

function ConstraintStateChips({ constraint, classNamePrefix }) {
  const prefix = classNamePrefix || "builder-constraint";
  const chips = buildConstraintChips(constraint);
  if (!chips.length) return null;
  return (
    <div className={`${prefix}-states`} role="status" aria-live="polite">
      {chips.map((chip) => (
        <span key={chip.key} className={`${prefix}-chip ${chip.tone}`}>
          {chip.text}
        </span>
      ))}
    </div>
  );
}

function ConstraintMessage({ constraint, classNamePrefix }) {
  const prefix = classNamePrefix || "builder-constraint";
  if (!constraint || !constraint.message) return null;
  const toneClass = constraint.warning ? `${prefix}-warning` : `${prefix}-note`;
  return <p className={toneClass}>{constraint.message}</p>;
}

function buildCatalogMismatchBanner(versionMismatch) {
  if (!versionMismatch || versionMismatch.field !== "catalog_version") return null;
  return {
    level: "warning",
    title: "Catalog version mismatch detected",
    message: `Expected ${versionMismatch.expected || "unknown"} but received ${versionMismatch.received || "unknown"}. Refresh catalog data before continuing.`,
    actionLabel: "Refresh Catalog",
  };
}

window.VSLReact.uiPrimitives = {
  NotificationStack,
  GlobalBanner,
  BlockingPanel,
  RouteNotice,
  buildConstraintChips,
  ConstraintStateChips,
  ConstraintMessage,
  buildCatalogMismatchBanner,
};

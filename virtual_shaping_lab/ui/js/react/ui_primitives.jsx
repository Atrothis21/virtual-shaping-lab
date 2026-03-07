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
  buildCatalogMismatchBanner,
};

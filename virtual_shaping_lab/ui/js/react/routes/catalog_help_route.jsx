(function initCatalogHelpRoute(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});
  const routeContainers = (VSLReact.routeContainers = VSLReact.routeContainers || {});

  function PlaceholderRouteCard({ title, description, status, actions }) {
    const foundation = VSLReact.foundationPrimitives || {};
    const SurfacePanel = foundation.SurfacePanel || ((props) => <div {...props} />);
    const StatusBadge = foundation.StatusBadge || ((props) => <span {...props} />);
    const SecondaryButton = foundation.SecondaryButton || ((props) => <button type="button" {...props} />);
    return (
      <SurfacePanel className="route-card">
        <div className="route-card-header">
          <h2>{title}</h2>
          <StatusBadge tone="success" className="route-status">{status}</StatusBadge>
        </div>
        <p>{description}</p>
        <div className="route-actions">
          {actions.map((action) => (
            <SecondaryButton key={`${title}-${action.href}`} className="route-action" onClick={() => { window.location.href = action.href; }}>
              {action.label}
            </SecondaryButton>
          ))}
        </div>
      </SurfacePanel>
    );
  }

  function CatalogHelpRouteContainer() {
    return (
      <PlaceholderRouteCard
        title="Catalog/Help Route Container"
        description="Catalog metadata, constraints, and compatibility/help visibility surface."
        status="Owned by Catalog/Help Route"
        actions={[{ label: "Open Main Menu", href: "/ui/index.html" }]}
      />
    );
  }

  routeContainers.CatalogHelpRouteContainer = CatalogHelpRouteContainer;
})(typeof window !== "undefined" ? window : globalThis);

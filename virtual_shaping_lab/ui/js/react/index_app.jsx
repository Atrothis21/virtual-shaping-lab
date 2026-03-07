window.VSLReact = window.VSLReact || {};

const ROUTES = {
  presets: { key: "presets", label: "Presets (/presets)", hash: "#/presets" },
  builder: { key: "builder", label: "Builder (/builder)", hash: "#/builder" },
  run: { key: "run", label: "Run (/run/:runId?)", hash: "#/run" },
  report: { key: "report", label: "Report (/report/:runId)", hash: "#/report" },
  catalogHelp: { key: "catalogHelp", label: "Catalog/Help (/catalog-help)", hash: "#/catalog-help" },
};

function parseRouteFromHash(hashValue) {
  const normalized = (hashValue || "").toLowerCase();
  if (normalized.startsWith("#/builder")) return ROUTES.builder.key;
  if (normalized.startsWith("#/run")) return ROUTES.run.key;
  if (normalized.startsWith("#/report")) return ROUTES.report.key;
  if (normalized.startsWith("#/catalog-help")) return ROUTES.catalogHelp.key;
  return ROUTES.presets.key;
}

function ShellNavItem({ label, isActive, onClick }) {
  return (
    <button
      type="button"
      className={`shell-nav-item${isActive ? " active" : ""}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
}

function PlaceholderRouteCard({ title, description, status, actions }) {
  const foundation = window.VSLReact.foundationPrimitives || {};
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
          <SecondaryButton
            key={`${title}-${action.href}`}
            className="route-action"
            onClick={() => {
              window.location.href = action.href;
            }}
          >
            {action.label}
          </SecondaryButton>
        ))}
      </div>
    </SurfacePanel>
  );
}

function PresetsRouteContainer() {
  return (
    <PlaceholderRouteCard
      title="Presets Route Container"
      description="Primary entry flow for preset-backed experiments and phenomenon metadata support."
      status="Owned by Presets Route"
      actions={[{ label: "Open Legacy Presets", href: "/ui/presets.html" }]}
    />
  );
}

function BuilderRouteContainer() {
  return (
    <PlaceholderRouteCard
      title="Builder Route Container"
      description="Constrained draft editing surface for builder-driven experiment setup."
      status="Owned by Builder Route"
      actions={[{ label: "Open Legacy Builder", href: "/ui/builder.html" }]}
    />
  );
}

function RunRouteContainer() {
  return (
    <PlaceholderRouteCard
      title="Run Route Container"
      description="Lifecycle execution surface for run creation, status polling, and provenance."
      status="Owned by Run Route"
      actions={[{ label: "Open Legacy Console", href: "/ui/console.html" }]}
    />
  );
}

function ReportRouteContainer() {
  return (
    <PlaceholderRouteCard
      title="Report Route Container"
      description="Report generation and artifact access surface tied to completed runs."
      status="Owned by Report Route"
      actions={[{ label: "Open Legacy Results", href: "/ui/results.html" }]}
    />
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

function AppShell() {
  const foundation = window.VSLReact.foundationPrimitives || {};
  const PageRegion = foundation.PageRegion || ((props) => <section {...props} />);
  const SurfacePanel = foundation.SurfacePanel || ((props) => <div {...props} />);
  const apiClient = React.useMemo(() => {
    if (!window.VSLApi || typeof window.VSLApi.createApiClient !== "function") return null;
    return window.VSLApi.createApiClient({ baseUrl: "" });
  }, []);
  const stateApi = window.VSLReact.stateDomains;
  const uiPrimitives = window.VSLReact.uiPrimitives || {};
  const GlobalBanner = uiPrimitives.GlobalBanner || (() => null);
  const BlockingPanel = uiPrimitives.BlockingPanel || (() => null);
  const NotificationStack = uiPrimitives.NotificationStack || (() => null);
  const buildCatalogMismatchBanner = uiPrimitives.buildCatalogMismatchBanner || (() => null);
  const initialState = React.useMemo(() => {
    return stateApi && typeof stateApi.createInitialUIState === "function"
      ? stateApi.createInitialUIState()
      : null;
  }, [stateApi]);
  const [uiState, setUiState] = React.useState(initialState);
  const [activeRoute, setActiveRoute] = React.useState(() => parseRouteFromHash(window.location.hash));
  const [notifications, setNotifications] = React.useState([]);

  const catalogState = stateApi && uiState ? stateApi.selectCatalogCacheState(uiState) : null;

  const dispatchEvent = React.useCallback(
    (event) => {
      if (!stateApi || typeof stateApi.applyUIEvent !== "function") return;
      setUiState((prev) => stateApi.applyUIEvent(prev || stateApi.createInitialUIState(), event));
    },
    [stateApi]
  );

  React.useEffect(() => {
    function onHashChange() {
      setActiveRoute(parseRouteFromHash(window.location.hash));
    }

    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  React.useEffect(() => {
    if (!apiClient || !stateApi || !catalogState) return;
    if (catalogState.requestStatus !== "idle") return;

    let cancelled = false;

    async function bootstrapCatalog() {
      dispatchEvent({ type: stateApi.UI_EVENTS.CATALOG_REFRESH_REQUESTED });
      try {
        const payload = await apiClient.getJson("catalog/extensions");
        if (cancelled) return;
        dispatchEvent({
          type: stateApi.UI_EVENTS.CATALOG_REFRESH_SUCCEEDED,
          payload: {
            extensions: payload && payload.extensions ? payload.extensions : null,
            versions: payload && payload.versions ? payload.versions : null,
            atMs: Date.now(),
          },
        });
      } catch (error) {
        if (cancelled) return;
        dispatchEvent({
          type: stateApi.UI_EVENTS.CATALOG_REFRESH_FAILED,
          payload: { error: error || null },
        });
      }
    }

    bootstrapCatalog();
    return () => {
      cancelled = true;
    };
  }, [apiClient, catalogState, dispatchEvent, stateApi]);

  React.useEffect(() => {
    if (!catalogState) return;
    if (catalogState.requestStatus !== "error") return;
    const err = catalogState.lastError;
    setNotifications((prev) => {
      const next = prev.filter((n) => n.id !== "catalog-bootstrap-error");
      return [
        ...next,
        {
          id: "catalog-bootstrap-error",
          level: "error",
          title: "Catalog bootstrap failed",
          message: err && err.message ? String(err.message) : "Could not load catalog metadata.",
        },
      ];
    });
  }, [catalogState]);

  const mismatchBanner = buildCatalogMismatchBanner(catalogState && catalogState.versionMismatch);
  const showBlockingCatalogPanel = Boolean(
    catalogState &&
    catalogState.requestStatus === "error" &&
    !catalogState.extensions
  );

  function refreshCatalog() {
    dispatchEvent({ type: stateApi.UI_EVENTS.CATALOG_REFRESH_REQUESTED });
    if (!apiClient) {
      dispatchEvent({
        type: stateApi.UI_EVENTS.CATALOG_REFRESH_FAILED,
        payload: { error: { message: "API client unavailable." } },
      });
      return;
    }
    apiClient
      .getJson("catalog/extensions")
      .then((payload) => {
        dispatchEvent({
          type: stateApi.UI_EVENTS.CATALOG_REFRESH_SUCCEEDED,
          payload: {
            extensions: payload && payload.extensions ? payload.extensions : null,
            versions: payload && payload.versions ? payload.versions : null,
            atMs: Date.now(),
          },
        });
      })
      .catch((error) => {
        dispatchEvent({
          type: stateApi.UI_EVENTS.CATALOG_REFRESH_FAILED,
          payload: { error: error || null },
        });
      });
  }

  function navigateTo(routeKey) {
    const route = Object.values(ROUTES).find((item) => item.key === routeKey);
    if (!route) return;
    if (window.location.hash !== route.hash) {
      window.location.hash = route.hash;
    } else {
      setActiveRoute(routeKey);
    }
  }

  function renderActiveRoute() {
    if (activeRoute === ROUTES.builder.key) return <BuilderRouteContainer />;
    if (activeRoute === ROUTES.run.key) return <RunRouteContainer />;
    if (activeRoute === ROUTES.report.key) return <ReportRouteContainer />;
    if (activeRoute === ROUTES.catalogHelp.key) return <CatalogHelpRouteContainer />;
    return <PresetsRouteContainer />;
  }

  return (
    <div className="shell-layout">
      <header className="shell-header">
        <div>
          <h1>Virtual Shaping Lab</h1>
          <p className="shell-subtitle">
            V2.17 app shell scaffold with first-pass route containers.
          </p>
          <p className="shell-subtitle" style={{ marginTop: "0.2rem" }}>
            State domains initialized: {initialState ? Object.keys(initialState).length : 0}
          </p>
          <p className="shell-subtitle" style={{ marginTop: "0.2rem" }}>
            Catalog bootstrap status: {catalogState ? catalogState.requestStatus : "n/a"}
          </p>
        </div>
      </header>

      <div className="shell-body">
        <SurfacePanel className="shell-nav">
          <h3>Navigation Scaffold</h3>
          <div style={{ marginBottom: "0.75rem", fontSize: "0.82rem", color: "#475569" }}>
            <div><strong>catalog_version:</strong> {catalogState?.versions?.catalog_version || "n/a"}</div>
            <div><strong>record_schema:</strong> {catalogState?.versions?.record_schema_version || "n/a"}</div>
            <div><strong>template_version:</strong> {catalogState?.versions?.template_version_used ?? "n/a"}</div>
          </div>
          {Object.values(ROUTES).map((route) => (
            <ShellNavItem
              key={route.key}
              label={route.label}
              isActive={activeRoute === route.key}
              onClick={() => navigateTo(route.key)}
            />
          ))}
        </SurfacePanel>

        <PageRegion className="shell-main">
          {mismatchBanner ? (
            <GlobalBanner
              level={mismatchBanner.level}
              title={mismatchBanner.title}
              message={mismatchBanner.message}
              actionLabel={mismatchBanner.actionLabel}
              onAction={refreshCatalog}
            />
          ) : null}
          {showBlockingCatalogPanel ? (
            <BlockingPanel
              title="Catalog unavailable"
              message="The app cannot bootstrap required catalog metadata right now. Retry catalog loading before continuing."
              actionLabel="Retry Catalog Load"
              onAction={refreshCatalog}
            />
          ) : null}
          {renderActiveRoute()}
        </PageRegion>
      </div>
      <NotificationStack items={notifications} />
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<AppShell />);

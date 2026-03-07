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
  return (
    <section className="route-card">
      <div className="route-card-header">
        <h2>{title}</h2>
        <span className="route-status">{status}</span>
      </div>
      <p>{description}</p>
      <div className="route-actions">
        {actions.map((action) => (
          <a key={`${title}-${action.href}`} className="route-action" href={action.href}>
            {action.label}
          </a>
        ))}
      </div>
    </section>
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
  const [activeRoute, setActiveRoute] = React.useState(() => parseRouteFromHash(window.location.hash));

  React.useEffect(() => {
    function onHashChange() {
      setActiveRoute(parseRouteFromHash(window.location.hash));
    }

    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

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
        </div>
      </header>

      <div className="shell-body">
        <nav className="shell-nav">
          <h3>Navigation Scaffold</h3>
          {Object.values(ROUTES).map((route) => (
            <ShellNavItem
              key={route.key}
              label={route.label}
              isActive={activeRoute === route.key}
              onClick={() => navigateTo(route.key)}
            />
          ))}
        </nav>

        <main className="shell-main">
          {renderActiveRoute()}
        </main>
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<AppShell />);

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

function navigateToRoute(routeKey, routes, setActiveRoute) {
  const table = routes || ROUTES;
  const route = Object.values(table).find((item) => item.key === routeKey);
  if (!route) return;
  if (window.location.hash !== route.hash) {
    window.location.hash = route.hash;
  } else if (typeof setActiveRoute === "function") {
    setActiveRoute(routeKey);
  }
}

window.VSLReact.routerState = {
  ROUTES,
  parseRouteFromHash,
  navigateToRoute,
};

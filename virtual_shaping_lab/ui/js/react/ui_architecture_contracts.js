window.VSLReact = window.VSLReact || {};

const STANDARD_PATTERNS = Object.freeze({
  container: Object.freeze({
    responsibilities: [
      "orchestrate domain hooks/services",
      "bind route params to state selectors",
      "dispatch domain events",
      "render presentational children with props",
    ],
    forbidden: [
      "direct fetch calls",
      "hardcoded payload assembly",
      "cross-feature internal imports",
    ],
  }),
  domainHook: Object.freeze({
    responsibilities: [
      "encapsulate one state domain or workflow concern",
      "derive memoized view-model data",
      "expose deterministic callbacks",
    ],
    forbidden: [
      "route navigation concerns",
      "UI layout rendering",
    ],
  }),
  apiService: Object.freeze({
    responsibilities: [
      "perform network calls via shared client",
      "normalize response and error envelopes",
      "return stable shapes for hooks/selectors",
    ],
    forbidden: [
      "component state mutation",
      "UI messaging/rendering decisions",
    ],
  }),
});

function _asList(value) {
  return Array.isArray(value) ? [...value] : [];
}

function createRouteContainerContract(spec) {
  const data = spec || {};
  return Object.freeze({
    type: "route_container",
    name: String(data.name || ""),
    requiredServices: Object.freeze(_asList(data.requiredServices)),
    consumedStateDomains: Object.freeze(_asList(data.consumedStateDomains)),
    outputs: Object.freeze(_asList(data.outputs)),
    notes: String(data.notes || ""),
  });
}

function createDomainHookContract(spec) {
  const data = spec || {};
  return Object.freeze({
    type: "domain_hook",
    name: String(data.name || ""),
    ownedDomain: String(data.ownedDomain || ""),
    inputs: Object.freeze(_asList(data.inputs)),
    outputs: Object.freeze(_asList(data.outputs)),
    sideEffects: Object.freeze(_asList(data.sideEffects)),
    notes: String(data.notes || ""),
  });
}

function createApiServiceContract(spec) {
  const data = spec || {};
  return Object.freeze({
    type: "api_service",
    name: String(data.name || ""),
    endpoints: Object.freeze(_asList(data.endpoints)),
    requestShapes: Object.freeze(_asList(data.requestShapes)),
    responseShapes: Object.freeze(_asList(data.responseShapes)),
    errorShapes: Object.freeze(_asList(data.errorShapes)),
    notes: String(data.notes || ""),
  });
}

function createDefaultContractRegistry() {
  return Object.freeze({
    routeContainers: Object.freeze([
      createRouteContainerContract({
        name: "AppShellRouteContainer",
        requiredServices: ["CatalogBootstrapService"],
        consumedStateDomains: ["catalogCacheState", "planState", "runState", "reportState"],
        outputs: ["GlobalBanner", "BlockingPanel", "RouteContainerSelection"],
        notes: "Top-level orchestrator for first-pass shell routes.",
      }),
    ]),
    domainHooks: Object.freeze([
      createDomainHookContract({
        name: "useCatalogBootstrapState",
        ownedDomain: "catalogCacheState",
        inputs: ["CATALOG_REFRESH_REQUESTED", "CATALOG_REFRESH_SUCCEEDED", "CATALOG_REFRESH_FAILED"],
        outputs: ["catalog status", "version mismatch data", "refresh action"],
        sideEffects: ["GET /catalog/extensions"],
      }),
    ]),
    apiServices: Object.freeze([
      createApiServiceContract({
        name: "CatalogBootstrapService",
        endpoints: ["GET /catalog/extensions"],
        requestShapes: ["none"],
        responseShapes: ["{status, extensions, versions}"],
        errorShapes: ["{status, code, message, details}"],
      }),
    ]),
  });
}

window.VSLReact.architectureContracts = {
  STANDARD_PATTERNS,
  createRouteContainerContract,
  createDomainHookContract,
  createApiServiceContract,
  createDefaultContractRegistry,
};

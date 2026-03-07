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

function buildConstrainedDraftSeedFromPreset(item) {
  if (!item) return null;
  return {
    seed_source: "preset-catalog",
    preset_key: item.key,
    phenomenon_key: item.key,
    protocol_key: item.protocolKey !== "n/a" ? item.protocolKey : null,
    template_key: item.defaultTemplate !== "n/a" ? item.defaultTemplate : null,
    run_mode_hint: item.runModes.length ? item.runModes[0] : null,
    expected_signals: Array.isArray(item.expectedSignals) ? item.expectedSignals : [],
  };
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

function selectPresetCatalogViewModel(catalogState) {
  const extensions = catalogState && catalogState.extensions ? catalogState.extensions : null;
  const phenomena = extensions && extensions.phenomena && typeof extensions.phenomena === "object"
    ? extensions.phenomena
    : {};
  const items = Object.entries(phenomena).map(([key, spec]) => {
    const runModes = Array.isArray(spec.default_run_modes) ? spec.default_run_modes : [];
    return {
      key,
      title: spec.name || key,
      description: spec.description || "No description provided.",
      protocolKey: spec.protocol_key || "n/a",
      expectedSignals: Array.isArray(spec.expected_signals) ? spec.expected_signals : [],
      defaultTemplate: spec.recommended_template_key || spec.default_template_key || "n/a",
      runModes,
    };
  });
  return {
    status: catalogState ? catalogState.requestStatus : "idle",
    items,
  };
}

function PresetBrowserGrid({ items, onUseInBuilder }) {
  if (!Array.isArray(items) || items.length === 0) {
    return (
      <div className="route-card">
        <p>No presets available from catalog metadata.</p>
      </div>
    );
  }

  return (
    <div className="preset-grid">
      {items.map((item) => (
        <div className="route-card preset-card" key={item.key}>
          <div className="route-card-header">
            <h2>{item.title}</h2>
            <span className="vsl-status-badge">{item.protocolKey}</span>
          </div>
          <p>{item.description}</p>
          <p style={{ marginBottom: "0.35rem" }}>
            <strong>Template:</strong> <code>{item.defaultTemplate}</code>
          </p>
          <p style={{ marginBottom: "0.35rem" }}>
            <strong>Run Modes:</strong> {item.runModes.length ? item.runModes.join(", ") : "n/a"}
          </p>
          <p style={{ marginBottom: "0.7rem" }}>
            <strong>Expected Signals:</strong>{" "}
            {item.expectedSignals.length ? item.expectedSignals.slice(0, 3).join(", ") : "n/a"}
          </p>
          <div className="route-actions">
            <button
              type="button"
              className="route-action"
              onClick={() => {
                if (typeof onUseInBuilder === "function") onUseInBuilder(item);
              }}
            >
              Use In Builder
            </button>
            <a className="route-action" href="/ui/presets.html">
              Open Legacy Presets
            </a>
          </div>
        </div>
      ))}
    </div>
  );
}

function PresetDetailPanel({ item, onResolvePreset, onResolveRun, onResolveRunReport }) {
  if (!item) {
    return (
      <div className="route-card preset-detail">
        <h2>Preset Detail</h2>
        <p>Select a preset to inspect details and lifecycle actions.</p>
      </div>
    );
  }

  return (
    <div className="route-card preset-detail">
      <div className="route-card-header">
        <h2>{item.title}</h2>
        <span className="vsl-status-badge">{item.protocolKey}</span>
      </div>
      <p>{item.description}</p>
      <p style={{ marginBottom: "0.35rem" }}>
        <strong>Recommended Template:</strong> <code>{item.defaultTemplate}</code>
      </p>
      <p style={{ marginBottom: "0.35rem" }}>
        <strong>Run Modes:</strong> {item.runModes.length ? item.runModes.join(", ") : "n/a"}
      </p>
      <p style={{ marginBottom: "0.7rem" }}>
        <strong>Expected Signals:</strong>{" "}
        {item.expectedSignals.length ? item.expectedSignals.join(", ") : "n/a"}
      </p>
      <div className="route-actions">
        <button type="button" className="route-action" onClick={() => { if (typeof onResolvePreset === "function") onResolvePreset(item); }}>
          Resolve Preset
        </button>
        <button type="button" className="route-action" onClick={() => { if (typeof onResolveRun === "function") onResolveRun(item); }}>
          Resolve + Run
        </button>
        <button type="button" className="route-action" onClick={() => { if (typeof onResolveRunReport === "function") onResolveRunReport(item); }}>
          Resolve + Run + Report
        </button>
      </div>
    </div>
  );
}

function PhenomenonSupportPanel({ item }) {
  return (
    <div className="route-card phenomenon-support">
      <div className="route-card-header">
        <h2>Phenomenon Support</h2>
        <span className="vsl-status-badge warning">metadata-only</span>
      </div>
      {!item ? (
        <p>Select a preset to view phenomenon guidance.</p>
      ) : (
        <>
          <p>
            <strong>{item.title}</strong> is currently selected. Use this panel to review expected signatures
            and reporting guidance before execution.
          </p>
          <p style={{ marginBottom: "0.35rem" }}>
            <strong>Recommended Report Template:</strong> <code>{item.defaultTemplate}</code>
          </p>
          <p style={{ marginBottom: "0.35rem" }}>
            <strong>Expected Signals:</strong>
          </p>
          {item.expectedSignals.length ? (
            <ul className="phenomenon-signal-list">
              {item.expectedSignals.map((signal) => (
                <li key={`${item.key}-${signal}`}>
                  <code>{signal}</code>
                </li>
              ))}
            </ul>
          ) : (
            <p>n/a</p>
          )}
          <p style={{ marginTop: "0.55rem" }}>
            Scope note: this panel is a lightweight support surface. Full narrative teaching mode is out of scope
            for V2.17.1.
          </p>
        </>
      )}
    </div>
  );
}

function PresetsRouteContainer({ catalogState, onSeedDraftFromPreset, onNavigate }) {
  const viewModel = React.useMemo(
    () => selectPresetCatalogViewModel(catalogState),
    [catalogState]
  );
  const [searchQuery, setSearchQuery] = React.useState("");
  const [runModeFilter, setRunModeFilter] = React.useState("all");
  const [sortBy, setSortBy] = React.useState("title");
  const [selectedPresetKey, setSelectedPresetKey] = React.useState("");

  const filteredItems = React.useMemo(() => {
    let next = [...viewModel.items];
    const q = searchQuery.trim().toLowerCase();
    if (q) {
      next = next.filter((item) => {
        return (
          item.title.toLowerCase().includes(q) ||
          item.description.toLowerCase().includes(q) ||
          item.protocolKey.toLowerCase().includes(q)
        );
      });
    }
    if (runModeFilter !== "all") {
      next = next.filter((item) => item.runModes.includes(runModeFilter));
    }
    if (sortBy === "protocol") {
      next.sort((a, b) => a.protocolKey.localeCompare(b.protocolKey));
    } else {
      next.sort((a, b) => a.title.localeCompare(b.title));
    }
    return next;
  }, [viewModel.items, searchQuery, runModeFilter, sortBy]);

  const selectedPreset = React.useMemo(() => {
    if (!selectedPresetKey) return filteredItems[0] || null;
    const fromFiltered = filteredItems.find((item) => item.key === selectedPresetKey);
    if (fromFiltered) return fromFiltered;
    return viewModel.items.find((item) => item.key === selectedPresetKey) || null;
  }, [filteredItems, selectedPresetKey, viewModel.items]);

  const handleSeedToBuilder = React.useCallback((item) => {
    if (!item) return;
    if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
    if (typeof onNavigate === "function") onNavigate(ROUTES.builder.key);
  }, [onNavigate, onSeedDraftFromPreset]);

  const handleResolvePreset = React.useCallback((item) => {
    if (!item) return;
    if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
    if (typeof onNavigate === "function") onNavigate(ROUTES.run.key);
  }, [onNavigate, onSeedDraftFromPreset]);

  const handleResolveRunReport = React.useCallback((item) => {
    if (!item) return;
    if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
    if (typeof onNavigate === "function") onNavigate(ROUTES.report.key);
  }, [onNavigate, onSeedDraftFromPreset]);

  return (
    <section className="vsl-page-region">
      <div className="route-card">
        <div className="route-card-header">
          <h2>Presets Browser</h2>
          <span className="vsl-status-badge">{viewModel.status}</span>
        </div>
        <p>Browse catalog-backed phenomenon presets and choose a starting point.</p>
        <div className="preset-controls">
          <label>
            Search
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search preset, protocol, signal..."
            />
          </label>
          <label>
            Run Mode
            <select value={runModeFilter} onChange={(e) => setRunModeFilter(e.target.value)}>
              <option value="all">All</option>
              <option value="trial">Trial</option>
              <option value="tick">Tick</option>
            </select>
          </label>
          <label>
            Sort
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="title">Name</option>
              <option value="protocol">Protocol</option>
            </select>
          </label>
        </div>
      </div>

      <PresetDetailPanel
        item={selectedPreset}
        onResolvePreset={handleResolvePreset}
        onResolveRun={handleResolvePreset}
        onResolveRunReport={handleResolveRunReport}
      />
      <PhenomenonSupportPanel item={selectedPreset} />

      <PresetBrowserGrid items={filteredItems} onUseInBuilder={handleSeedToBuilder} />

      <div className="route-card" style={{ marginTop: "0.75rem" }}>
        <strong>Quick Select</strong>
        <p style={{ marginTop: "0.35rem", marginBottom: "0.5rem" }}>
          Choose which preset appears in detail view.
        </p>
        <div className="preset-detail-selectors">
          {filteredItems.slice(0, 10).map((item) => (
            <button
              type="button"
              key={`select-${item.key}`}
              className={`route-action ${selectedPreset?.key === item.key ? "active" : ""}`}
              onClick={() => setSelectedPresetKey(item.key)}
            >
              {item.title}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

function BuilderRouteContainer({ builderDraftState }) {
  const seed = builderDraftState && builderDraftState.draft ? builderDraftState.draft : null;
  return (
    <PlaceholderRouteCard
      title="Builder Route Container"
      description="Constrained draft editing surface for builder-driven experiment setup."
      status={seed && seed.seed_source ? `Seeded: ${seed.seed_source}` : "Owned by Builder Route"}
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
  const contractApi = window.VSLReact.architectureContracts;
  const contractRegistry = React.useMemo(() => {
    if (!contractApi || typeof contractApi.createDefaultContractRegistry !== "function") return null;
    return contractApi.createDefaultContractRegistry();
  }, [contractApi]);
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
  const builderDraftState = stateApi && uiState ? stateApi.selectBuilderDraftState(uiState) : null;

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

  const seedDraftFromPreset = React.useCallback((presetItem) => {
    if (!stateApi || !presetItem) return;
    const draftSeed = buildConstrainedDraftSeedFromPreset(presetItem);
    dispatchEvent({
      type: stateApi.UI_EVENTS.DRAFT_EDITED,
      payload: { draft: draftSeed },
    });
  }, [dispatchEvent, stateApi]);

  function renderActiveRoute() {
    if (activeRoute === ROUTES.builder.key) return <BuilderRouteContainer builderDraftState={builderDraftState} />;
    if (activeRoute === ROUTES.run.key) return <RunRouteContainer />;
    if (activeRoute === ROUTES.report.key) return <ReportRouteContainer />;
    if (activeRoute === ROUTES.catalogHelp.key) return <CatalogHelpRouteContainer />;
    return (
      <PresetsRouteContainer
        catalogState={catalogState}
        onSeedDraftFromPreset={seedDraftFromPreset}
        onNavigate={navigateTo}
      />
    );
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
          <p className="shell-subtitle" style={{ marginTop: "0.2rem" }}>
            Architecture contracts loaded: {contractRegistry ? "yes" : "no"}
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

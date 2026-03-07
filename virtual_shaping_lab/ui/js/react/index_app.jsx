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

function summarizeResolvedPlan(resolvedPlan) {
  if (!resolvedPlan || typeof resolvedPlan !== "object") {
    return {
      unitCount: 0,
      flow: "n/a",
      totalTrials: 0,
    };
  }
  const units = Array.isArray(resolvedPlan.units) ? resolvedPlan.units : [];
  const flow = units.map((unit) => unit && (unit.protocol || unit.unit_key || unit.name || "unit")).join(" -> ");
  const totalTrials = units.reduce((acc, unit) => {
    const params = unit && unit.params && typeof unit.params === "object" ? unit.params : {};
    const nTrials = Number.isFinite(Number(params.n_trials)) ? Number(params.n_trials) : 0;
    return acc + nTrials;
  }, 0);
  return {
    unitCount: units.length,
    flow: flow || "n/a",
    totalTrials,
  };
}

function buildPresetItemFromDraftSeed(draftSeed) {
  if (!draftSeed || typeof draftSeed !== "object") return null;
  const presetKey = draftSeed.preset_key || draftSeed.phenomenon_key || null;
  if (!presetKey) return null;
  return {
    key: presetKey,
    title: presetKey,
    description: "Seed-derived preset context",
    protocolKey: draftSeed.protocol_key || "n/a",
    defaultTemplate: draftSeed.template_key || "n/a",
    runModes: draftSeed.run_mode_hint ? [draftSeed.run_mode_hint] : [],
    expectedSignals: Array.isArray(draftSeed.expected_signals) ? draftSeed.expected_signals : [],
  };
}

function extractFieldHintsFromReason(reason) {
  const text = String(reason || "");
  const matches = text.match(/([a-zA-Z_][a-zA-Z0-9_.\[\]]*)/g) || [];
  const candidates = matches.filter((token) => {
    const lower = token.toLowerCase();
    return (
      lower.includes("experiment") ||
      lower.includes("phase") ||
      lower.includes("protocol") ||
      lower.includes("stimuli") ||
      lower.includes("params") ||
      lower.includes("runtime") ||
      lower.includes("report")
    );
  });
  return Array.from(new Set(candidates)).slice(0, 6);
}

function buildPlanResolveErrorView(planState) {
  const err = planState && planState.lastError ? planState.lastError : null;
  if (!err) return null;
  const envelope = err.envelope && typeof err.envelope === "object" ? err.envelope : null;
  const code = envelope && envelope.code ? String(envelope.code) : "request_error";
  const message = envelope && envelope.message ? String(envelope.message) : String(err.message || "Plan resolve failed.");
  const details = envelope && envelope.details && typeof envelope.details === "object" ? envelope.details : {};
  const reason = details.reason ? String(details.reason) : "";
  const invalidFields = extractFieldHintsFromReason(reason);
  const hint = details.hint ? String(details.hint) : "Edit draft fields, revalidate, and retry plan resolution.";
  return {
    code,
    message,
    reason,
    invalidFields,
    hint,
  };
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

function getSignalSemanticTone(signal) {
  const normalized = String(signal || "").toLowerCase();
  if (normalized.includes("cs+") || normalized.includes("plus") || normalized.includes("acquisition")) {
    return "cs-plus";
  }
  if (normalized.includes("cs-") || normalized.includes("minus") || normalized.includes("nonreinforcement")) {
    return "cs-minus";
  }
  if (normalized.includes("probe") || normalized.includes("test")) {
    return "probe";
  }
  if (normalized.includes("compound")) {
    return "compound";
  }
  return "learning";
}

function getProtocolAccentTone(protocolKey) {
  const normalized = String(protocolKey || "").toLowerCase();
  if (normalized.includes("nonreinforcement") || normalized.includes("extinction")) return "cs-minus";
  if (normalized.includes("probe")) return "probe";
  if (normalized.includes("compound")) return "compound";
  if (normalized.includes("acquisition")) return "cs-plus";
  return "learning";
}

function PresetSignalChips({ signals, maxItems }) {
  const entries = Array.isArray(signals) ? signals : [];
  if (!entries.length) return <span className="preset-empty-cue">n/a</span>;
  const sliced = Number.isFinite(maxItems) ? entries.slice(0, maxItems) : entries;
  return (
    <div className="preset-signal-chip-row">
      {sliced.map((signal) => {
        const tone = getSignalSemanticTone(signal);
        return (
          <span key={`signal-${signal}`} className={`preset-signal-chip ${tone}`}>
            {signal}
          </span>
        );
      })}
    </div>
  );
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
        <div className={`route-card preset-card accent-${getProtocolAccentTone(item.protocolKey)}`} key={item.key}>
          <div className="route-card-header">
            <h2>{item.title}</h2>
            <span className={`vsl-status-badge semantic ${getProtocolAccentTone(item.protocolKey)}`}>{item.protocolKey}</span>
          </div>
          <p className="preset-meta-line">Preset Key: <code>{item.key}</code></p>
          <p>{item.description}</p>
          <p style={{ marginBottom: "0.35rem" }}>
            <strong>Template:</strong> <code>{item.defaultTemplate}</code>
          </p>
          <p style={{ marginBottom: "0.35rem" }}>
            <strong>Run Modes:</strong> {item.runModes.length ? item.runModes.join(", ") : "n/a"}
          </p>
          <p style={{ marginBottom: "0.7rem" }}>
            <strong>Expected Signals:</strong>
          </p>
          <PresetSignalChips signals={item.expectedSignals} maxItems={3} />
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

function PresetDetailPanel({
  item,
  onResolvePreset,
  onResolveRun,
  onResolveRunReport,
  actionState,
}) {
  if (!item) {
    return (
      <div className="route-card preset-detail">
        <h2>Preset Detail</h2>
        <p>Select a preset to inspect details and lifecycle actions.</p>
      </div>
    );
  }

  return (
    <div className={`route-card preset-detail accent-${getProtocolAccentTone(item.protocolKey)}`}>
      <div className="route-card-header">
        <h2>{item.title}</h2>
        <span className={`vsl-status-badge semantic ${getProtocolAccentTone(item.protocolKey)}`}>{item.protocolKey}</span>
      </div>
      <p className="preset-meta-line">
        Preset Key: <code>{item.key}</code>
      </p>
      <p>{item.description}</p>
      <p style={{ marginBottom: "0.35rem" }}>
        <strong>Recommended Template:</strong> <code>{item.defaultTemplate}</code>
      </p>
      <p style={{ marginBottom: "0.35rem" }}>
        <strong>Run Modes:</strong> {item.runModes.length ? item.runModes.join(", ") : "n/a"}
      </p>
      <p style={{ marginBottom: "0.7rem" }}>
        <strong>Expected Signals:</strong>
      </p>
      <PresetSignalChips signals={item.expectedSignals} />
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
      <div className="preset-action-status">
        <strong>Action Status:</strong>{" "}
        <code>{actionState && actionState.status ? actionState.status : "idle"}</code>
        {actionState && actionState.step ? (
          <span style={{ marginLeft: "0.45rem" }}>
            <strong>Step:</strong> <code>{actionState.step}</code>
          </span>
        ) : null}
        {actionState && actionState.message ? (
          <p className="preset-action-message">{actionState.message}</p>
        ) : null}
        {actionState && actionState.error && actionState.error.message ? (
          <p className="preset-action-error">
            {String(actionState.error.message)}
          </p>
        ) : null}
      </div>
    </div>
  );
}

function PhenomenonSupportPanel({ item }) {
  const accentTone = item ? getProtocolAccentTone(item.protocolKey) : "learning";
  const signalCount = item && Array.isArray(item.expectedSignals) ? item.expectedSignals.length : 0;
  return (
    <div className={`route-card phenomenon-support accent-${accentTone}`}>
      <div className="route-card-header">
        <h2>Phenomenon Support</h2>
        <span className="vsl-status-badge warning">metadata-only</span>
      </div>
      {!item ? (
        <p>Select a preset to view phenomenon guidance.</p>
      ) : (
        <>
          <p className="phenomenon-meta-line">
            Support Mode: <code>setup-guidance</code> | signal_count: <code>{signalCount}</code>
          </p>
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
          <PresetSignalChips signals={item.expectedSignals} />
          <p style={{ marginTop: "0.55rem" }}>
            Scope note: this panel is a lightweight support surface. Full narrative teaching mode is out of scope
            for V2.17.1.
          </p>
        </>
      )}
    </div>
  );
}

function PresetsRouteContainer({
  catalogState,
  onSeedDraftFromPreset,
  onNavigate,
  onResolvePresetAction,
  onResolveRunAction,
  onResolveRunReportAction,
  actionState,
}) {
  const readModelApi = window.VSLReact.presetReadModels || {};
  const selectPresetCatalogReadModel = readModelApi.selectPresetCatalogReadModel;
  const filterPresetViewModels = readModelApi.filterPresetViewModels;
  const sortPresetViewModels = readModelApi.sortPresetViewModels;
  const selectPresetFromReadModels = readModelApi.selectPresetFromReadModels;

  const viewModel = React.useMemo(
    () => {
      if (typeof selectPresetCatalogReadModel === "function") {
        return selectPresetCatalogReadModel(catalogState);
      }
      return { status: "idle", items: [] };
    },
    [catalogState, selectPresetCatalogReadModel]
  );
  const [searchQuery, setSearchQuery] = React.useState("");
  const [runModeFilter, setRunModeFilter] = React.useState("all");
  const [sortBy, setSortBy] = React.useState("title");
  const [selectedPresetKey, setSelectedPresetKey] = React.useState("");

  const filteredItems = React.useMemo(() => {
    const filtered = typeof filterPresetViewModels === "function"
      ? filterPresetViewModels(viewModel.items, searchQuery, runModeFilter)
      : [...viewModel.items];
    return typeof sortPresetViewModels === "function"
      ? sortPresetViewModels(filtered, sortBy)
      : filtered;
  }, [filterPresetViewModels, runModeFilter, searchQuery, sortBy, sortPresetViewModels, viewModel.items]);

  const selectedPreset = React.useMemo(() => {
    if (typeof selectPresetFromReadModels === "function") {
      return selectPresetFromReadModels(viewModel.items, filteredItems, selectedPresetKey);
    }
    if (!selectedPresetKey) return filteredItems[0] || null;
    const fromFiltered = filteredItems.find((item) => item.key === selectedPresetKey);
    if (fromFiltered) return fromFiltered;
    return viewModel.items.find((item) => item.key === selectedPresetKey) || null;
  }, [filteredItems, selectedPresetKey, selectPresetFromReadModels, viewModel.items]);

  const handleSeedToBuilder = React.useCallback((item) => {
    if (!item) return;
    if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
    if (typeof onNavigate === "function") onNavigate(ROUTES.builder.key);
  }, [onNavigate, onSeedDraftFromPreset]);

  const handleResolvePreset = React.useCallback(async (item) => {
    if (!item) return;
    if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
    if (typeof onResolvePresetAction === "function") {
      const result = await onResolvePresetAction(item);
      if (result && result.ok && typeof onNavigate === "function") onNavigate(ROUTES.run.key);
      return;
    }
    if (typeof onNavigate === "function") onNavigate(ROUTES.run.key);
  }, [onNavigate, onResolvePresetAction, onSeedDraftFromPreset]);

  const handleResolveRun = React.useCallback(async (item) => {
    if (!item) return;
    if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
    if (typeof onResolveRunAction === "function") {
      const result = await onResolveRunAction(item);
      if (result && result.ok && typeof onNavigate === "function") onNavigate(ROUTES.run.key);
      return;
    }
    if (typeof onNavigate === "function") onNavigate(ROUTES.run.key);
  }, [onNavigate, onResolveRunAction, onSeedDraftFromPreset]);

  const handleResolveRunReport = React.useCallback(async (item) => {
    if (!item) return;
    if (typeof onSeedDraftFromPreset === "function") onSeedDraftFromPreset(item);
    if (typeof onResolveRunReportAction === "function") {
      const result = await onResolveRunReportAction(item);
      if (result && result.ok && typeof onNavigate === "function") {
        onNavigate(result.routeKey || ROUTES.report.key);
      }
      return;
    }
    if (typeof onNavigate === "function") onNavigate(ROUTES.report.key);
  }, [onNavigate, onResolveRunReportAction, onSeedDraftFromPreset]);

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
        onResolveRun={handleResolveRun}
        onResolveRunReport={handleResolveRunReport}
        actionState={actionState}
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

function BuilderRouteContainer({ builderDraftState, planState, onResolvePlan, resolveErrorView }) {
  const seed = builderDraftState && builderDraftState.draft ? builderDraftState.draft : null;
  const resolvedPlan = planState && planState.resolvedPlan ? planState.resolvedPlan : null;
  const stableHash = planState && planState.stableHash ? planState.stableHash : "";
  const summary = summarizeResolvedPlan(resolvedPlan);
  return (
    <div className="route-card">
      <div className="route-card-header">
        <h2>Builder Route Container</h2>
        <span className="vsl-status-badge">
          {seed && seed.seed_source ? `Seeded: ${seed.seed_source}` : "Owned by Builder Route"}
        </span>
      </div>
      <p>Constrained draft editing surface for builder-driven experiment setup.</p>
      <div className="route-actions">
        <button
          type="button"
          className="route-action"
          onClick={() => {
            if (typeof onResolvePlan === "function") onResolvePlan();
          }}
        >
          Resolve Plan
        </button>
        <a className="route-action" href="/ui/builder.html">Open Legacy Builder</a>
      </div>
      <div className="plan-resolve-summary">
        <div><strong>Plan Status:</strong> <code>{planState && planState.requestStatus ? planState.requestStatus : "idle"}</code></div>
        <div><strong>Stable Hash:</strong> <code>{stableHash || "n/a"}</code></div>
        <div><strong>Unit Count:</strong> <code>{summary.unitCount}</code></div>
        <div><strong>Total Trials:</strong> <code>{summary.totalTrials}</code></div>
        <div><strong>Flow:</strong> <code>{summary.flow}</code></div>
      </div>
      {resolveErrorView ? (
        <div className="plan-resolve-inline-error">
          <div><strong>Resolve Error Code:</strong> <code>{resolveErrorView.code}</code></div>
          <div><strong>Message:</strong> {resolveErrorView.message}</div>
          {resolveErrorView.reason ? (
            <div><strong>Reason:</strong> <code>{resolveErrorView.reason}</code></div>
          ) : null}
          {resolveErrorView.invalidFields.length ? (
            <div>
              <strong>Likely Fields:</strong>
              <ul>
                {resolveErrorView.invalidFields.map((field) => (
                  <li key={`resolve-field-${field}`}><code>{field}</code></li>
                ))}
              </ul>
            </div>
          ) : null}
          <div><strong>Recovery:</strong> {resolveErrorView.hint}</div>
        </div>
      ) : null}
    </div>
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
  const [presetActionState, setPresetActionState] = React.useState(() => ({
    status: "idle",
    step: "",
    message: "",
    error: null,
  }));

  const catalogState = stateApi && uiState ? stateApi.selectCatalogCacheState(uiState) : null;
  const builderDraftState = stateApi && uiState ? stateApi.selectBuilderDraftState(uiState) : null;
  const planState = stateApi && uiState ? stateApi.selectPlanState(uiState) : null;

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
  const planResolveErrorView = React.useMemo(() => buildPlanResolveErrorView(planState), [planState]);
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

  const presetActionServiceApi = window.VSLReact.presetActionService || {};
  const presetActionHandlers = React.useMemo(() => {
    if (!apiClient || !stateApi) return null;
    if (typeof presetActionServiceApi.createPresetActionService !== "function") return null;
    return presetActionServiceApi.createPresetActionService({
      apiClient,
      stateApi,
      dispatchEvent,
      setActionState: setPresetActionState,
      routeKeys: {
        run: ROUTES.run.key,
        report: ROUTES.report.key,
      },
    });
  }, [apiClient, dispatchEvent, presetActionServiceApi, stateApi]);

  const seedDraftFromPreset = React.useCallback((presetItem) => {
    if (!stateApi || !presetItem) return;
    const draftSeed =
      presetActionServiceApi &&
      typeof presetActionServiceApi.buildConstrainedDraftSeedFromPreset === "function"
        ? presetActionServiceApi.buildConstrainedDraftSeedFromPreset(presetItem)
        : buildConstrainedDraftSeedFromPreset(presetItem);
    dispatchEvent({
      type: stateApi.UI_EVENTS.DRAFT_EDITED,
      payload: { draft: draftSeed },
    });
  }, [dispatchEvent, presetActionServiceApi, stateApi]);

  const resolvePresetFromSelection = React.useCallback(async (presetItem) => {
    if (!presetActionHandlers || typeof presetActionHandlers.resolvePresetFromSelection !== "function") {
      return { ok: false, error: { message: "Preset action service unavailable." } };
    }
    return presetActionHandlers.resolvePresetFromSelection(presetItem);
  }, [presetActionHandlers]);

  const resolveAndRunPresetFromSelection = React.useCallback(async (presetItem) => {
    if (!presetActionHandlers || typeof presetActionHandlers.resolveAndRunPresetFromSelection !== "function") {
      return { ok: false, error: { message: "Preset action service unavailable." } };
    }
    return presetActionHandlers.resolveAndRunPresetFromSelection(presetItem);
  }, [presetActionHandlers]);

  const resolveRunReportPresetFromSelection = React.useCallback(async (presetItem) => {
    if (!presetActionHandlers || typeof presetActionHandlers.resolveRunReportPresetFromSelection !== "function") {
      return { ok: false, error: { message: "Preset action service unavailable." } };
    }
    return presetActionHandlers.resolveRunReportPresetFromSelection(presetItem);
  }, [presetActionHandlers]);

  const resolvePlanFromBuilderContext = React.useCallback(async () => {
    const draftSeed = builderDraftState && builderDraftState.draft ? builderDraftState.draft : null;
    const presetItem = buildPresetItemFromDraftSeed(draftSeed);
    if (!presetItem) {
      setPresetActionState({
        status: "error",
        step: "plan",
        message: "No preset seed is available in builder context.",
        error: { message: "Seed a preset first, then resolve plan." },
      });
      return;
    }
    await resolvePresetFromSelection(presetItem);
  }, [builderDraftState, resolvePresetFromSelection]);

  function renderActiveRoute() {
    if (activeRoute === ROUTES.builder.key) {
      return (
        <BuilderRouteContainer
          builderDraftState={builderDraftState}
          planState={planState}
          onResolvePlan={resolvePlanFromBuilderContext}
          resolveErrorView={planResolveErrorView}
        />
      );
    }
    if (activeRoute === ROUTES.run.key) return <RunRouteContainer />;
    if (activeRoute === ROUTES.report.key) return <ReportRouteContainer />;
    if (activeRoute === ROUTES.catalogHelp.key) return <CatalogHelpRouteContainer />;
    return (
      <PresetsRouteContainer
        catalogState={catalogState}
        onSeedDraftFromPreset={seedDraftFromPreset}
        onNavigate={navigateTo}
        onResolvePresetAction={resolvePresetFromSelection}
        onResolveRunAction={resolveAndRunPresetFromSelection}
        onResolveRunReportAction={resolveRunReportPresetFromSelection}
        actionState={presetActionState}
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
          {activeRoute === ROUTES.builder.key && planResolveErrorView ? (
            <GlobalBanner
              level="error"
              title="Plan validation failed"
              message={
                planResolveErrorView.invalidFields.length
                  ? `Invalid fields: ${planResolveErrorView.invalidFields.join(", ")}`
                  : planResolveErrorView.message
              }
              actionLabel="Retry Resolve"
              onAction={resolvePlanFromBuilderContext}
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

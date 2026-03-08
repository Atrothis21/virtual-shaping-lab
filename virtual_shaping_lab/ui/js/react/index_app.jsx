window.VSLReact = window.VSLReact || {};

(function initIndexApp(global) {
const ROUTES = {
  home: { key: "home", label: "Home", hash: "#/home" },
  presets: { key: "presets", label: "Presets", hash: "#/presets" },
  builder: { key: "builder", label: "Builder", hash: "#/builder" },
  run: { key: "run", label: "Runs", hash: "#/run" },
  report: { key: "report", label: "Reports", hash: "#/report" },
  catalogHelp: { key: "catalogHelp", label: "Catalog Help", hash: "#/catalog-help" },
};

const PRIMARY_NAV_KEYS = ["home", "presets", "builder", "run", "report"];

function parseRouteFromHash(hashValue) {
  const normalized = (hashValue || "").toLowerCase();
  if (normalized.startsWith("#/home")) return ROUTES.home.key;
  if (normalized.startsWith("#/builder")) return ROUTES.builder.key;
  if (normalized.startsWith("#/run")) return ROUTES.run.key;
  if (normalized.startsWith("#/report")) return ROUTES.report.key;
  if (normalized.startsWith("#/catalog-help")) return ROUTES.catalogHelp.key;
  return ROUTES.home.key;
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

function hasBuilderDependenciesLoaded() {
  const vsl = window.VSLReact || {};
  return Boolean(
    vsl.builderDraftTranslator &&
    typeof vsl.builderDraftTranslator.draft_to_payload === "function" &&
    vsl.builderConstraintControls &&
    typeof vsl.builderConstraintControls.deriveBuilderConstraintState === "function" &&
    vsl.builderFormSchema &&
    typeof vsl.builderFormSchema.getBuilderSectionSchema === "function" &&
    vsl.builderSubmissionGuards &&
    typeof vsl.builderSubmissionGuards.assertBuilderDraftForTranslation === "function"
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
  const routerStateApi = window.VSLReact.routerState || {};
  const catalogBootstrapApi = window.VSLReact.catalogBootstrapService || {};
  const planWorkflowApi = window.VSLReact.planWorkflowService || {};
  const routeContainersApi = window.VSLReact.routeContainers || {};
  const lazyRouteLoaderApi = window.VSLReact.lazyRouteLoader || {};
  const GlobalBanner = uiPrimitives.GlobalBanner || (() => null);
  const BlockingPanel = uiPrimitives.BlockingPanel || (() => null);
  const NotificationStack = uiPrimitives.NotificationStack || (() => null);
  const RouteNotice = uiPrimitives.RouteNotice || (() => null);
  const buildCatalogMismatchBanner = uiPrimitives.buildCatalogMismatchBanner || (() => null);
  const initialState = React.useMemo(() => {
    return stateApi && typeof stateApi.createInitialUIState === "function"
      ? stateApi.createInitialUIState()
      : null;
  }, [stateApi]);
  const [uiState, setUiState] = React.useState(initialState);
  const routes = routerStateApi.ROUTES || ROUTES;
  const launcherFeature = window.VSLReact.launcherFeature || {};
  const selectFirstOpenState =
    typeof launcherFeature.selectFirstOpenState === "function"
      ? launcherFeature.selectFirstOpenState
      : () => ({ initialRouteKey: routes.home.key, showRecentStrip: false, reason: "default_policy" });
  const [activeRoute, setActiveRoute] = React.useState(() => {
    const currentHash = window.location.hash;
    if (currentHash) return parseRouteFromHash(currentHash);
    const nextState = selectFirstOpenState({ recentItems: [], hasVisitedLauncher: false });
    return nextState.initialRouteKey || routes.home.key;
  });
  const [notifications, setNotifications] = React.useState([]);
  const [builderModulesState, setBuilderModulesState] = React.useState(() => ({
    loading: false,
    ready: hasBuilderDependenciesLoaded(),
    error: null,
  }));
  const [presetActionState, setPresetActionState] = React.useState(() => ({
    status: "idle",
    step: "",
    message: "",
    error: null,
  }));
  const [runActionStatus, setRunActionStatus] = React.useState(() => ({
    message: "",
    error: null,
  }));
  const [reportActionStatus, setReportActionStatus] = React.useState(() => ({
    message: "",
    error: null,
  }));

  const catalogState = stateApi && uiState ? stateApi.selectCatalogCacheState(uiState) : null;
  const builderDraftState = stateApi && uiState ? stateApi.selectBuilderDraftState(uiState) : null;
  const planState = stateApi && uiState ? stateApi.selectPlanState(uiState) : null;
  const runState = stateApi && uiState ? stateApi.selectRunState(uiState) : null;
  const reportState = stateApi && uiState ? stateApi.selectReportState(uiState) : null;
  const debugAdvancedState = stateApi && uiState ? stateApi.selectDebugAdvancedState(uiState) : null;

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

    const bootstrapCatalog =
      typeof catalogBootstrapApi.bootstrapCatalog === "function"
        ? () => catalogBootstrapApi.bootstrapCatalog({ apiClient, stateApi, dispatchEvent })
        : async () => {};

    bootstrapCatalog();
    return () => {
      cancelled = true;
    };
  }, [apiClient, catalogBootstrapApi, catalogState, dispatchEvent, stateApi]);

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

  React.useEffect(() => {
    if (activeRoute !== routes.builder.key) return;
    if (builderModulesState.ready || builderModulesState.loading) return;
    const ensureBuilderModulesLoaded =
      lazyRouteLoaderApi && typeof lazyRouteLoaderApi.ensureBuilderModulesLoaded === "function"
        ? lazyRouteLoaderApi.ensureBuilderModulesLoaded
        : null;
    if (!ensureBuilderModulesLoaded) {
      setBuilderModulesState((prev) => ({ ...prev, ready: hasBuilderDependenciesLoaded() }));
      return;
    }
    let cancelled = false;
    setBuilderModulesState((prev) => ({ ...prev, loading: true, error: null }));
    ensureBuilderModulesLoaded()
      .then(() => {
        if (cancelled) return;
        setBuilderModulesState({ loading: false, ready: true, error: null });
      })
      .catch((error) => {
        if (cancelled) return;
        setBuilderModulesState({
          loading: false,
          ready: false,
          error: error && error.message ? String(error.message) : "Builder modules failed to load.",
        });
      });
    return () => {
      cancelled = true;
    };
  }, [activeRoute, builderModulesState.loading, builderModulesState.ready, lazyRouteLoaderApi, routes.builder.key]);

  React.useEffect(() => {
    if (activeRoute === routes.builder.key) return;
    setBuilderModulesState((prev) => {
      if (!prev.loading) return prev;
      return { ...prev, loading: false };
    });
  }, [activeRoute, routes.builder.key]);

  const lifecycleViewModelsApi = window.VSLReact.lifecycleViewModels || {};
  const isRunTerminalLifecycleFn =
    typeof lifecycleViewModelsApi.isRunTerminalLifecycle === "function"
      ? lifecycleViewModelsApi.isRunTerminalLifecycle
      : () => false;
  const selectRunProvenanceViewModelFn =
    lifecycleViewModelsApi.selectRunProvenanceViewModel || (() => ({}));
  const detectRunVersionMismatchesFn =
    lifecycleViewModelsApi.detectRunVersionMismatches || (() => []);
  const selectReportProvenanceViewModelFn =
    lifecycleViewModelsApi.selectReportProvenanceViewModel || (() => ({}));
  const detectReportVersionMismatchesFn =
    lifecycleViewModelsApi.detectReportVersionMismatches || (() => []);
  const selectReportArtifactViewModelFn =
    lifecycleViewModelsApi.selectReportArtifactViewModel || (() => ({ hasArtifacts: false, pdfPath: "", figureList: [] }));
  const extractFieldHintsFromReason =
    planWorkflowApi.extractFieldHintsFromReason || (() => []);
  const buildPlanResolveErrorView =
    planWorkflowApi.buildPlanResolveErrorView || (() => null);

  const mismatchBanner = buildCatalogMismatchBanner(catalogState && catalogState.versionMismatch);
  const planResolveErrorView = React.useMemo(() => buildPlanResolveErrorView(planState), [planState]);
  const runProvenanceView = React.useMemo(
    () => selectRunProvenanceViewModelFn(runState),
    [runState, selectRunProvenanceViewModelFn]
  );
  const runVersionMismatches = React.useMemo(
    () => detectRunVersionMismatchesFn(runProvenanceView, catalogState, planState),
    [catalogState, detectRunVersionMismatchesFn, planState, runProvenanceView]
  );
  const runBlockingMismatch = React.useMemo(
    () => runVersionMismatches.find((m) => m.severity === "blocking") || null,
    [runVersionMismatches]
  );
  const runWarningMismatch = React.useMemo(
    () => runVersionMismatches.find((m) => m.severity === "warning") || null,
    [runVersionMismatches]
  );
  const reportProvenanceView = React.useMemo(
    () => selectReportProvenanceViewModelFn(reportState),
    [reportState, selectReportProvenanceViewModelFn]
  );
  const reportVersionMismatches = React.useMemo(
    () => detectReportVersionMismatchesFn(reportProvenanceView, catalogState),
    [catalogState, detectReportVersionMismatchesFn, reportProvenanceView]
  );
  const reportBlockingMismatch = React.useMemo(
    () => reportVersionMismatches.find((m) => m.severity === "blocking") || null,
    [reportVersionMismatches]
  );
  const reportWarningMismatch = React.useMemo(
    () => reportVersionMismatches.find((m) => m.severity === "warning") || null,
    [reportVersionMismatches]
  );
  const reportArtifactView = React.useMemo(
    () => selectReportArtifactViewModelFn(reportState),
    [reportState, selectReportArtifactViewModelFn]
  );
  const isPlanFreshForCurrentDraft = Boolean(
    stateApi &&
    typeof stateApi.isPlanFreshForCurrentDraft === "function" &&
    stateApi.isPlanFreshForCurrentDraft(uiState)
  );
  const showBlockingCatalogPanel = Boolean(
    catalogState &&
    catalogState.requestStatus === "error" &&
    !catalogState.extensions
  );

  function refreshCatalog() {
    if (typeof catalogBootstrapApi.refreshCatalog === "function") {
      catalogBootstrapApi.refreshCatalog({ apiClient, stateApi, dispatchEvent });
      return;
    }
  }

  function navigateTo(routeKey) {
    if (typeof routerStateApi.navigateToRoute === "function") {
      routerStateApi.navigateToRoute(routeKey, routes, setActiveRoute);
      return;
    }
    const route = Object.values(routes).find((item) => item.key === routeKey);
    if (!route) return;
    if (window.location.hash !== route.hash) {
      window.location.hash = route.hash;
    } else {
      setActiveRoute(routeKey);
    }
  }

  const presetActionServiceApi = window.VSLReact.presetActionService || {};
  const builderDraftTranslatorApi = window.VSLReact.builderDraftTranslator || {};
  const builderSubmissionGuardsApi = window.VSLReact.builderSubmissionGuards || {};
  const runReportWorkflowApi = window.VSLReact.runReportWorkflowService || {};
  const presetActionHandlers = React.useMemo(() => {
    if (!apiClient || !stateApi) return null;
    if (typeof presetActionServiceApi.createPresetActionService !== "function") return null;
    return presetActionServiceApi.createPresetActionService({
      apiClient,
      stateApi,
      dispatchEvent,
      setActionState: setPresetActionState,
      routeKeys: {
        run: routes.run.key,
        report: routes.report.key,
      },
    });
  }, [apiClient, dispatchEvent, presetActionServiceApi, routes.report.key, routes.run.key, stateApi]);
  const runReportWorkflowHandlers = React.useMemo(() => {
    if (!apiClient || !stateApi) return null;
    if (typeof runReportWorkflowApi.createRunReportWorkflowService !== "function") return null;
    return runReportWorkflowApi.createRunReportWorkflowService({
      apiClient,
      stateApi,
      dispatchEvent,
      setRunActionStatus,
      setReportActionStatus,
      buildPresetItemFromDraftSeed,
      buildPresetApiPayload:
        presetActionServiceApi && typeof presetActionServiceApi.buildPresetApiPayload === "function"
          ? presetActionServiceApi.buildPresetApiPayload
          : null,
      draftToPayload:
        builderDraftTranslatorApi && typeof builderDraftTranslatorApi.draft_to_payload === "function"
          ? builderDraftTranslatorApi.draft_to_payload
          : null,
    });
  }, [apiClient, builderDraftTranslatorApi, dispatchEvent, presetActionServiceApi, runReportWorkflowApi, stateApi]);

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

  const startGuidedBuilderFromLauncher = React.useCallback((featuredPreset) => {
    if (!stateApi) return;
    const fallbackProtocol = featuredPreset && featuredPreset.protocolKey && featuredPreset.protocolKey !== "n/a"
      ? featuredPreset.protocolKey
      : "acquisition";
    const fallbackTemplate = featuredPreset && featuredPreset.defaultTemplate && featuredPreset.defaultTemplate !== "n/a"
      ? featuredPreset.defaultTemplate
      : "default";
    const draft = {
      seed_source: "launcher-guided-starter",
      guided_start_step: "start",
      preset_key: featuredPreset && featuredPreset.key ? featuredPreset.key : "",
      protocol_key: fallbackProtocol,
      template_key: fallbackTemplate,
      run_mode_hint: "trial",
      expected_signals: [],
      recommended_seed_hints: featuredPreset && Array.isArray(featuredPreset.expectedSignals)
        ? featuredPreset.expectedSignals.slice(0, 3)
        : [],
    };
    dispatchEvent({
      type: stateApi.UI_EVENTS.DRAFT_EDITED,
      payload: { draft },
    });
  }, [dispatchEvent, stateApi]);

  const editBuilderDraft = React.useCallback((nextDraft) => {
    if (!stateApi || !nextDraft || typeof nextDraft !== "object") return;
    dispatchEvent({
      type: stateApi.UI_EVENTS.DRAFT_EDITED,
      payload: { draft: nextDraft },
    });
  }, [dispatchEvent, stateApi]);

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
    if (typeof planWorkflowApi.resolvePlanFromBuilderContext !== "function") return;
    await planWorkflowApi.resolvePlanFromBuilderContext({
      apiClient,
      stateApi,
      builderDraftState,
      builderDraftTranslatorApi,
      builderSubmissionGuardsApi,
      dispatchEvent,
      setPresetActionState,
    });
  }, [apiClient, builderDraftState, builderDraftTranslatorApi, builderSubmissionGuardsApi, dispatchEvent, planWorkflowApi, stateApi]);

  const startRunFromResolvedPlan = React.useCallback(async () => {
    if (!runReportWorkflowHandlers || typeof runReportWorkflowHandlers.startRunFromResolvedPlan !== "function") return;
    await runReportWorkflowHandlers.startRunFromResolvedPlan({
      builderDraftState,
      planState,
    });
  }, [builderDraftState, planState, runReportWorkflowHandlers]);

  const refreshActiveRunStatus = React.useCallback(async () => {
    if (!runReportWorkflowHandlers || typeof runReportWorkflowHandlers.refreshActiveRunStatus !== "function") return;
    await runReportWorkflowHandlers.refreshActiveRunStatus({ runState });
  }, [runReportWorkflowHandlers, runState]);

  const createReportFromActiveRun = React.useCallback(async () => {
    if (!runReportWorkflowHandlers || typeof runReportWorkflowHandlers.createReportFromActiveRun !== "function") return;
    await runReportWorkflowHandlers.createReportFromActiveRun({
      runState,
      reportState,
      builderDraftState,
      planState,
    });
  }, [builderDraftState, planState, reportState, runReportWorkflowHandlers, runState]);

  React.useEffect(() => {
    if (!runReportWorkflowHandlers || typeof runReportWorkflowHandlers.pollActiveRunStatus !== "function") return;
    if (!runState || !runState.activeRunId) return;
    if (isRunTerminalLifecycleFn(runState.lifecycleState)) return;

    let cancelled = false;
    const intervalId = window.setInterval(async () => {
      await runReportWorkflowHandlers.pollActiveRunStatus({ runState });
      if (cancelled) return;
    }, 1500);
    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, [isRunTerminalLifecycleFn, runReportWorkflowHandlers, runState]);

  function renderActiveRoute() {
    const MissingRoute = () => (
      <div className="route-card">
        <h2>Route unavailable</h2>
        <p>Route component registry is missing a required route container.</p>
      </div>
    );
    const BuilderRoute = routeContainersApi.BuilderRouteContainer || MissingRoute;
    const RunRoute = routeContainersApi.RunRouteContainer || MissingRoute;
    const ReportRoute = routeContainersApi.ReportRouteContainer || MissingRoute;
    const PresetsRoute = routeContainersApi.PresetsRouteContainer || MissingRoute;
    const CatalogHelpRoute = routeContainersApi.CatalogHelpRouteContainer || MissingRoute;
    const LauncherRoute = routeContainersApi.LauncherRouteContainer || MissingRoute;
    if (activeRoute === routes.home.key) {
      return (
        <LauncherRoute
          catalogState={catalogState}
          runState={runState}
          reportState={reportState}
          onStartGuidedBuilder={startGuidedBuilderFromLauncher}
          onSeedDraftFromPreset={seedDraftFromPreset}
          onResolveRunAction={resolveAndRunPresetFromSelection}
          onResolveRunReportAction={resolveRunReportPresetFromSelection}
          onRetryCatalog={refreshCatalog}
          actionState={presetActionState}
          onNavigate={navigateTo}
          routeKeys={{
            presets: routes.presets.key,
            builder: routes.builder.key,
            run: routes.run.key,
            report: routes.report.key,
          }}
        />
      );
    }
    if (activeRoute === routes.builder.key) {
      if (!builderModulesState.ready) {
        const hasLoadError = Boolean(builderModulesState.error);
        return (
          <div className="route-card">
            <div className="route-card-header">
              <h2>Builder</h2>
              <span className="vsl-status-badge">{builderModulesState.loading ? "loading modules" : "modules unavailable"}</span>
            </div>
            <RouteNotice
              level={hasLoadError ? "error" : "info"}
              message={
                hasLoadError
                  ? `Builder modules failed to load. ${builderModulesState.error}`
                  : "Loading builder modules..."
              }
            />
            <div className="route-actions">
              <button
                type="button"
                className="route-action route-action-secondary"
                onClick={() => setBuilderModulesState({ loading: false, ready: false, error: null })}
                disabled={builderModulesState.loading && !hasLoadError}
              >
                Retry
              </button>
              <button type="button" className="route-action route-action-secondary" onClick={() => navigateTo(routes.presets.key)}>
                Go to presets
              </button>
            </div>
          </div>
        );
      }
      return (
          <BuilderRoute
            builderDraftState={builderDraftState}
            planState={planState}
            catalogState={catalogState}
            debugAdvancedState={debugAdvancedState}
            onResolvePlan={resolvePlanFromBuilderContext}
            onNavigate={navigateTo}
            routeKeys={{
              presets: routes.presets.key,
              builder: routes.builder.key,
            }}
            onDraftEdited={editBuilderDraft}
            resolveErrorView={planResolveErrorView}
          />
      );
    }
    if (activeRoute === routes.run.key) {
      return (
        <RunRoute
          runState={runState}
          planState={planState}
          builderDraftState={builderDraftState}
          onStartRun={startRunFromResolvedPlan}
          onRefreshRun={refreshActiveRunStatus}
          onNavigate={navigateTo}
          routeKeys={{ presets: routes.presets.key, builder: routes.builder.key }}
          runActionStatus={runActionStatus}
          provenanceView={runProvenanceView}
          mismatchView={runVersionMismatches}
          RouteNotice={RouteNotice}
        />
      );
    }
    if (activeRoute === routes.report.key) {
      return (
        <ReportRoute
          reportState={reportState}
          runState={runState}
          isPlanFresh={isPlanFreshForCurrentDraft}
          onCreateReport={createReportFromActiveRun}
          onRefreshRun={refreshActiveRunStatus}
          onNavigate={navigateTo}
          routeKeys={{ run: routes.run.key, presets: routes.presets.key, builder: routes.builder.key }}
          reportActionStatus={reportActionStatus}
          provenanceView={reportProvenanceView}
          mismatchView={reportVersionMismatches}
          artifactView={reportArtifactView}
          RouteNotice={RouteNotice}
        />
      );
    }
    if (activeRoute === routes.catalogHelp.key) return <CatalogHelpRoute />;
    return (
      <PresetsRoute
        catalogState={catalogState}
        onSeedDraftFromPreset={seedDraftFromPreset}
        onNavigate={navigateTo}
        onResolvePresetAction={resolvePresetFromSelection}
        onResolveRunAction={resolveAndRunPresetFromSelection}
        onResolveRunReportAction={resolveRunReportPresetFromSelection}
        actionState={presetActionState}
        RouteNotice={RouteNotice}
        routeKeys={{
          builder: routes.builder.key,
          run: routes.run.key,
          report: routes.report.key,
        }}
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
          <p className="shell-subtitle shell-subtitle-compact">
            State domains initialized: {initialState ? Object.keys(initialState).length : 0}
          </p>
          <p className="shell-subtitle shell-subtitle-compact">
            Catalog bootstrap status: {catalogState ? catalogState.requestStatus : "n/a"}
          </p>
          <p className="shell-subtitle shell-subtitle-compact">
            Architecture contracts loaded: {contractRegistry ? "yes" : "no"}
          </p>
        </div>
      </header>

      <div className="shell-body">
        <SurfacePanel className="shell-nav">
          <h3>Navigation Scaffold</h3>
          <div className="shell-nav-version-readout">
            <div><strong>catalog_version:</strong> {catalogState?.versions?.catalog_version || "n/a"}</div>
            <div><strong>record_schema:</strong> {catalogState?.versions?.record_schema_version || "n/a"}</div>
            <div><strong>template_version:</strong> {catalogState?.versions?.template_version_used ?? "n/a"}</div>
          </div>
          {PRIMARY_NAV_KEYS.map((key) => routes[key]).filter(Boolean).map((route) => (
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
          {activeRoute === routes.builder.key && planResolveErrorView ? (
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
          {activeRoute === routes.run.key && runWarningMismatch ? (
            <GlobalBanner
              level="warning"
              title="Version mismatch detected"
              message={`Field: ${runWarningMismatch.field} | Expected: ${runWarningMismatch.expected} | Received: ${runWarningMismatch.received} | Action: ${runWarningMismatch.action}`}
              actionLabel="Refresh Run Status"
              onAction={refreshActiveRunStatus}
            />
          ) : null}
          {activeRoute === routes.run.key && runBlockingMismatch ? (
            <BlockingPanel
              title="Incompatible data version"
              message={`This view cannot be rendered with ${runBlockingMismatch.field}. Expected ${runBlockingMismatch.expected}, received ${runBlockingMismatch.received}. Use manual refresh or open static artifacts.`}
              actionLabel="Refresh Run Status"
              onAction={refreshActiveRunStatus}
            />
          ) : null}
          {activeRoute === routes.report.key && reportWarningMismatch ? (
            <GlobalBanner
              level="warning"
              title="Version mismatch detected"
              message={`Field: ${reportWarningMismatch.field} | Expected: ${reportWarningMismatch.expected} | Received: ${reportWarningMismatch.received} | Action: ${reportWarningMismatch.action}`}
              actionLabel="Refresh Run Status"
              onAction={refreshActiveRunStatus}
            />
          ) : null}
          {activeRoute === routes.report.key && reportBlockingMismatch ? (
            <BlockingPanel
              title="Incompatible data version"
              message={`Report detail rendering is blocked for ${reportBlockingMismatch.field}. Expected ${reportBlockingMismatch.expected}, received ${reportBlockingMismatch.received}. Open static artifacts where available, then refresh context.`}
              actionLabel="Refresh Run Status"
              onAction={refreshActiveRunStatus}
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
})(window);


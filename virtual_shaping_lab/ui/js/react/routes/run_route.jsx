(function initRunRoute(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});
  const routeContainers = (VSLReact.routeContainers = VSLReact.routeContainers || {});

  function isRunTerminalLifecycle(lifecycleState) {
    const normalized = String(lifecycleState || "").toLowerCase();
    return normalized === "completed" || normalized === "complete" || normalized === "failed" || normalized === "error" || normalized === "cancelled" || normalized === "canceled";
  }

  function fallbackSelectRunLifecycleViewModel(runState, planState, builderDraftState) {
    const state = runState && runState.lifecycleState ? String(runState.lifecycleState) : "idle";
    const activeRunId = runState && runState.activeRunId ? String(runState.activeRunId) : "";
    const requestStatus = runState && runState.requestStatus ? String(runState.requestStatus) : "idle";
    const pollAt = runState && runState.lastPollAtMs ? new Date(runState.lastPollAtMs).toISOString() : "n/a";
    const canStartRun = Boolean(
      planState &&
      builderDraftState &&
      planState.requestStatus === "success" &&
      planState.stableHash &&
      planState.isFreshForDraftVersion != null &&
      planState.isFreshForDraftVersion === builderDraftState.draftVersion
    );
    return {
      state,
      requestStatus,
      activeRunId,
      pollAt,
      canStartRun,
      stableHash: planState && planState.stableHash ? String(planState.stableHash) : "",
      isTerminal: isRunTerminalLifecycle(state),
    };
  }

  function fallbackBuildLifecycleInstrumentView(lifecycleState, requestStatus) {
    const status = String(lifecycleState || "").toLowerCase();
    const request = String(requestStatus || "").toLowerCase();
    let tone = "learning";
    let progressPct = 8;
    let phaseLabel = "idle";
    if (status.includes("progress") || status.includes("running") || request === "loading") {
      tone = "probe";
      progressPct = 52;
      phaseLabel = "in_progress";
    } else if (status.includes("complete") || status.includes("reportcomplete") || status.includes("runcomplete")) {
      tone = "cs-plus";
      progressPct = 100;
      phaseLabel = "complete";
    } else if (status.includes("fail") || status.includes("error") || request === "error") {
      tone = "cs-minus";
      progressPct = 100;
      phaseLabel = "failure";
    }
    return { tone, progressPct, phaseLabel };
  }

  function RunRouteContainer({
    runState,
    planState,
    builderDraftState,
    onStartRun,
    onRefreshRun,
    runActionStatus,
    provenanceView,
    mismatchView,
    RouteNotice,
  }) {
    const lifecycleViewModelsApi = VSLReact.lifecycleViewModels || {};
    const selectRunLifecycleViewModelFn = lifecycleViewModelsApi.selectRunLifecycleViewModel || fallbackSelectRunLifecycleViewModel;
    const buildLifecycleInstrumentViewFn = lifecycleViewModelsApi.buildLifecycleInstrumentView || fallbackBuildLifecycleInstrumentView;
    const vm = selectRunLifecycleViewModelFn(runState, planState, builderDraftState);
    const lifecycleInstrument = buildLifecycleInstrumentViewFn(vm.state, vm.requestStatus);
    const blockingMismatch = Array.isArray(mismatchView) ? mismatchView.find((m) => m.severity === "blocking") : null;

    return (
      <div className="route-card run-lifecycle-card">
        <div className="route-card-header">
          <h2>Run Lifecycle</h2>
          <span className={`vsl-status-badge semantic lifecycle-badge ${lifecycleInstrument.tone}`}>{vm.state}</span>
        </div>
        <div className="lifecycle-instrument">
          <div className={`lifecycle-meter ${lifecycleInstrument.tone}`}><span style={{ width: `${lifecycleInstrument.progressPct}%` }} /></div>
          <div className="lifecycle-caption"><strong>phase:</strong> <code>{lifecycleInstrument.phaseLabel}</code></div>
        </div>
        <p>Create runs from resolved plans and monitor lifecycle progression.</p>
        <div className="route-actions">
          <button type="button" className="route-action" onClick={() => typeof onStartRun === "function" && onStartRun()} disabled={!vm.canStartRun || vm.requestStatus === "loading"}>
            {vm.requestStatus === "loading" ? "Starting Run..." : "Start Run"}
          </button>
          <button type="button" className="route-action" onClick={() => typeof onRefreshRun === "function" && onRefreshRun()} disabled={!vm.activeRunId}>
            Refresh Status
          </button>
          <a className="route-action" href="/ui/console.html">Open Legacy Console</a>
        </div>
        <div className="run-lifecycle-summary">
          <div><strong>Request Status:</strong> <code>{vm.requestStatus}</code></div>
          <div><strong>Active Run ID:</strong> <code>{vm.activeRunId || "n/a"}</code></div>
          <div><strong>Plan Hash:</strong> <code>{vm.stableHash || "n/a"}</code></div>
          <div><strong>Polling Updated:</strong> <code>{vm.pollAt}</code></div>
        </div>
        <div className="run-provenance-summary">
          <div><strong>Run Provenance</strong></div>
          <div><strong>run_id:</strong> <code>{provenanceView.runId || "n/a"}</code></div>
          <div><strong>plan_hash:</strong> <code>{provenanceView.planHash || "n/a"}</code></div>
          <div><strong>record_schema_version:</strong> <code>{provenanceView.recordSchemaVersion || "n/a"}</code></div>
          <div><strong>template_version_used:</strong> <code>{provenanceView.templateVersionUsed || "n/a"}</code></div>
          <div><strong>lifecycle:</strong> <code>{provenanceView.lifecycleState || "n/a"}</code></div>
          <div><strong>next_actions:</strong> <code>{provenanceView.nextActions.length ? provenanceView.nextActions.join(", ") : "n/a"}</code></div>
        </div>
        {blockingMismatch ? (
          <RouteNotice level="warning" className="run-blocking-note" title="Incompatible data version:" message={`This run detail is in blocking mode for ${blockingMismatch.field}.`} />
        ) : null}
        {runActionStatus && runActionStatus.message ? <RouteNotice level="info" className="run-action-message" message={runActionStatus.message} /> : null}
        {runActionStatus && runActionStatus.error && runActionStatus.error.message ? (
          <RouteNotice level="error" className="run-action-error" message={String(runActionStatus.error.message)} />
        ) : null}
        {!vm.canStartRun ? (
          <RouteNotice
            level="info"
            className="run-action-message"
            message={!vm.stableHash ? "Resolve a plan first to enable run creation from a stable execution hash." : "Plan is stale for current draft. Re-resolve plan to enable run creation."}
          />
        ) : null}
      </div>
    );
  }

  routeContainers.RunRouteContainer = RunRouteContainer;
})(typeof window !== "undefined" ? window : globalThis);

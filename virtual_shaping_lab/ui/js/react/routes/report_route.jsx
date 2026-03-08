(function initReportRoute(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});
  const routeContainers = (VSLReact.routeContainers = VSLReact.routeContainers || {});

  function fallbackSelectReportLifecycleViewModel(reportState, runState, context) {
    const requestStatus = reportState && reportState.requestStatus ? String(reportState.requestStatus) : "idle";
    const reportRunId = reportState && reportState.runId ? String(reportState.runId) : "";
    const activeRunId = runState && runState.activeRunId ? String(runState.activeRunId) : "";
    const effectiveRunId = reportRunId || activeRunId;
    const reportData = reportState && reportState.reportData && typeof reportState.reportData === "object" ? reportState.reportData : {};
    const lifecycle = reportData && reportData.lifecycle && typeof reportData.lifecycle === "object" ? reportData.lifecycle : {};
    const nextActions = Array.isArray(lifecycle.next_actions) ? lifecycle.next_actions : [];
    const isPlanFresh = Boolean(context && context.isPlanFresh);
    const runLifecycleState = runState && runState.lifecycleState ? String(runState.lifecycleState) : "";
    const terminalRun = ["completed", "complete", "failed", "error", "cancelled", "canceled"].includes(runLifecycleState.toLowerCase());
    return {
      requestStatus,
      effectiveRunId,
      lifecycleState: lifecycle.state ? String(lifecycle.state) : runLifecycleState,
      nextActions,
      reportData,
      isPlanFresh,
      canCreateReport: Boolean(effectiveRunId && isPlanFresh && terminalRun),
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

  function ReportRouteContainer({
    reportState,
    runState,
    isPlanFresh,
    onCreateReport,
    onRefreshRun,
    reportActionStatus,
    provenanceView,
    mismatchView,
    artifactView,
    RouteNotice,
  }) {
    const uiPrimitives = VSLReact.uiPrimitives || {};
    const ConstraintStateChips = uiPrimitives.ConstraintStateChips || (() => null);
    const RouteStatePanel = uiPrimitives.RouteStatePanel || (() => null);
    const lifecycleViewModelsApi = VSLReact.lifecycleViewModels || {};
    const selectReportLifecycleViewModelFn = lifecycleViewModelsApi.selectReportLifecycleViewModel || fallbackSelectReportLifecycleViewModel;
    const buildLifecycleInstrumentViewFn = lifecycleViewModelsApi.buildLifecycleInstrumentView || fallbackBuildLifecycleInstrumentView;
    const vm = selectReportLifecycleViewModelFn(reportState, runState, { isPlanFresh });
    const lifecycleInstrument = buildLifecycleInstrumentViewFn(vm.lifecycleState, vm.requestStatus);
    const warningMismatch = Array.isArray(mismatchView) ? mismatchView.find((m) => m.severity === "warning") : null;
    const reportConstraintState = vm.canCreateReport
      ? null
      : {
          disabled: true,
          warning: true,
          message: vm.isPlanFresh
            ? "Start and complete a run first to enable report generation."
            : "Plan is stale for current draft. Re-resolve plan before generating report.",
        };
    const reportStatePanel = React.useMemo(() => {
      if (vm.requestStatus === "loading") {
        return { state: "loading", title: "Generating Report", message: "Building artifacts from selected run..." };
      }
      if (artifactView && (artifactView.pdfPath || (artifactView.figureList && artifactView.figureList.length))) {
        return { state: "completed", title: "Artifacts Ready", message: "Report artifacts are available for inspection." };
      }
      if (!vm.effectiveRunId) {
        return { state: "empty", title: "No Run Selected", message: "Select or complete a run before requesting report generation." };
      }
      return { state: "success", title: "Report Route Ready", message: "Run context loaded. Generate report when eligible." };
    }, [artifactView, vm.effectiveRunId, vm.requestStatus]);

    return (
      <div className="route-card report-lifecycle-card">
        <div className="route-card-header">
          <h2>Report Lifecycle</h2>
          <span className={`vsl-status-badge semantic lifecycle-badge ${lifecycleInstrument.tone}`}>{vm.requestStatus}</span>
        </div>
        <div className="lifecycle-instrument">
          <div className={`lifecycle-meter ${lifecycleInstrument.tone}`}><span style={{ width: `${lifecycleInstrument.progressPct}%` }} /></div>
          <div className="lifecycle-caption"><strong>phase:</strong> <code>{lifecycleInstrument.phaseLabel}</code></div>
        </div>
        <p>Create report artifacts from completed runs and monitor report lifecycle state.</p>
        <RouteStatePanel state={reportStatePanel.state} title={reportStatePanel.title} message={reportStatePanel.message} />
        <div className="route-actions">
          <button type="button" className="route-action route-action-primary" onClick={() => typeof onCreateReport === "function" && onCreateReport()} disabled={!vm.canCreateReport || vm.requestStatus === "loading"}>
            {vm.requestStatus === "loading" ? "Generating Report..." : "Generate Report"}
          </button>
          <button type="button" className="route-action route-action-secondary" onClick={() => typeof onRefreshRun === "function" && onRefreshRun()} disabled={!vm.effectiveRunId}>
            Refresh Run Status
          </button>
          <a className="route-action route-action-secondary" href="/ui/results.html">Open Legacy Results</a>
        </div>
        <ConstraintStateChips constraint={reportConstraintState} classNamePrefix="route-constraint" />
        <div className="report-lifecycle-summary">
          <div><strong>Run ID:</strong> <code>{vm.effectiveRunId || "n/a"}</code></div>
          <div><strong>Lifecycle:</strong> <code>{vm.lifecycleState || "n/a"}</code></div>
          <div><strong>Next Actions:</strong> <code>{vm.nextActions.length ? vm.nextActions.join(", ") : "n/a"}</code></div>
        </div>
        <div className="report-provenance-summary">
          <div><strong>source_run_id:</strong> <code>{provenanceView.sourceRunId || "n/a"}</code></div>
          <div><strong>plan_hash:</strong> <code>{provenanceView.planHash || "n/a"}</code></div>
          <div><strong>record_schema_version:</strong> <code>{provenanceView.recordSchemaVersion || "n/a"}</code></div>
          <div><strong>template_version_used:</strong> <code>{provenanceView.templateVersionUsed || "n/a"}</code></div>
          <div><strong>regenerated:</strong> <code>{provenanceView.regenerated || "n/a"}</code></div>
          <div><strong>regeneration_mode:</strong> <code>{provenanceView.regenerationMode || "n/a"}</code></div>
          <div><strong>missing_source_metadata:</strong> <code>{provenanceView.missingSourceMetadata.length ? provenanceView.missingSourceMetadata.join(", ") : "n/a"}</code></div>
        </div>
        {warningMismatch ? (
          <RouteNotice level="warning" className="report-degraded-note" message={`Degraded mode active for ${warningMismatch.field}. Static artifacts remain available.`} />
        ) : null}
        <div className="report-artifact-grid">
          <div className="report-artifact-card">
            <strong>PDF Report</strong>
            <div>{artifactView.pdfPath ? <a href={artifactView.pdfPath} target="_blank" rel="noreferrer">Open report.pdf</a> : <span className="report-artifact-missing">Not available yet</span>}</div>
          </div>
          <div className="report-artifact-card">
            <strong>Figure Artifacts</strong>
            <div className="report-plot-legend">
              <span className="vsl-status-badge semantic cs-plus">CS+</span>
              <span className="vsl-status-badge semantic cs-minus">CS-</span>
              <span className="vsl-status-badge semantic probe">Probe</span>
              <span className="vsl-status-badge semantic compound">Compound</span>
              <span className="vsl-status-badge semantic learning">Learning</span>
            </div>
            {artifactView.figureList.length ? (
              <div className="report-figure-grid">
                {artifactView.figureList.map((figure) => (
                  <a key={figure.href} className={`report-figure-card accent-${figure.tone}`} href={figure.href} target="_blank" rel="noreferrer">
                    <span className="report-figure-title">{figure.label}</span>
                    <span className="report-figure-tone">{figure.tone}</span>
                  </a>
                ))}
              </div>
            ) : <span className="report-artifact-missing">No figures available yet</span>}
          </div>
        </div>
        {reportActionStatus && reportActionStatus.message ? <RouteNotice level="info" className="report-action-message" message={reportActionStatus.message} /> : null}
        {reportActionStatus && reportActionStatus.error && reportActionStatus.error.message ? (
          <RouteNotice level="error" className="report-action-error" message={String(reportActionStatus.error.message)} />
        ) : null}
        {!vm.canCreateReport ? (
          <RouteNotice
            level="info"
            className="report-action-message"
            message={vm.isPlanFresh ? "Start and complete a run first to enable report generation." : "Plan is stale for current draft. Re-resolve plan before generating report."}
          />
        ) : null}
      </div>
    );
  }

  routeContainers.ReportRouteContainer = ReportRouteContainer;
})(typeof window !== "undefined" ? window : globalThis);

window.VSLReact = window.VSLReact || {};

function isRunTerminalLifecycle(lifecycleState) {
  const normalized = String(lifecycleState || "").toLowerCase();
  return (
    normalized === "completed" ||
    normalized === "complete" ||
    normalized === "failed" ||
    normalized === "error" ||
    normalized === "cancelled" ||
    normalized === "canceled"
  );
}

function selectRunLifecycleViewModel(runState, planState, builderDraftState) {
  const state = runState && runState.lifecycleState ? String(runState.lifecycleState) : "idle";
  const activeRunId = runState && runState.activeRunId ? String(runState.activeRunId) : "";
  const requestStatus = runState && runState.requestStatus ? String(runState.requestStatus) : "idle";
  const pollAt = runState && runState.lastPollAtMs ? new Date(runState.lastPollAtMs).toISOString() : "n/a";
  const isPlanFresh = Boolean(
    planState &&
    builderDraftState &&
    planState.isFreshForDraftVersion != null &&
    planState.isFreshForDraftVersion === builderDraftState.draftVersion
  );
  const canStartRun = Boolean(
    planState &&
    planState.requestStatus === "success" &&
    typeof planState.stableHash === "string" &&
    planState.stableHash &&
    isPlanFresh
  );
  return {
    state,
    requestStatus,
    activeRunId,
    pollAt,
    canStartRun,
    isPlanFresh,
    stableHash: planState && planState.stableHash ? String(planState.stableHash) : "",
    isTerminal: isRunTerminalLifecycle(state),
  };
}

function selectRunProvenanceViewModel(runState) {
  const runData = runState && runState.runData && typeof runState.runData === "object"
    ? runState.runData
    : {};
  const metadata = runData && runData.metadata && typeof runData.metadata === "object"
    ? runData.metadata
    : {};
  const lifecycle = runData && runData.lifecycle && typeof runData.lifecycle === "object"
    ? runData.lifecycle
    : {};
  const nextActions = Array.isArray(lifecycle.next_actions) ? lifecycle.next_actions : [];
  return {
    runId: runData.run_id ? String(runData.run_id) : "",
    planHash: metadata.plan_hash ? String(metadata.plan_hash) : "",
    recordSchemaVersion: metadata.record_schema_version ? String(metadata.record_schema_version) : "",
    templateVersionUsed:
      metadata.template_version_used === undefined || metadata.template_version_used === null
        ? ""
        : String(metadata.template_version_used),
    lifecycleState: lifecycle.state ? String(lifecycle.state) : "",
    nextActions,
  };
}

function selectReportLifecycleViewModel(reportState, runState, options) {
  const opts = options && typeof options === "object" ? options : {};
  const isPlanFresh = Boolean(opts.isPlanFresh !== false);
  const requestStatus = reportState && reportState.requestStatus ? String(reportState.requestStatus) : "idle";
  const reportRunId = reportState && reportState.runId ? String(reportState.runId) : "";
  const activeRunId = runState && runState.activeRunId ? String(runState.activeRunId) : "";
  const effectiveRunId = reportRunId || activeRunId;
  const reportData = reportState && reportState.reportData && typeof reportState.reportData === "object"
    ? reportState.reportData
    : {};
  const lifecycle = reportData && reportData.lifecycle && typeof reportData.lifecycle === "object"
    ? reportData.lifecycle
    : {};
  const nextActions = Array.isArray(lifecycle.next_actions) ? lifecycle.next_actions : [];
  return {
    requestStatus,
    effectiveRunId,
    lifecycleState: lifecycle.state ? String(lifecycle.state) : "",
    nextActions,
    reportData,
    isPlanFresh,
    canCreateReport: Boolean(effectiveRunId && isPlanFresh),
  };
}

function normalizeArtifactHref(value) {
  if (!value) return "";
  const raw = String(value).trim();
  if (!raw) return "";
  if (/^https?:\/\//i.test(raw)) return raw;
  const slashed = raw.replace(/\\/g, "/");
  return slashed.startsWith("/") ? slashed : `/${slashed}`;
}

function inferFigureSemanticTone(pathValue) {
  const value = String(pathValue || "").toLowerCase();
  if (value.includes("cs_minus") || value.includes("cs-") || value.includes("minus")) return "cs-minus";
  if (value.includes("cs_plus") || value.includes("cs+") || value.includes("plus")) return "cs-plus";
  if (value.includes("probe")) return "probe";
  if (value.includes("compound")) return "compound";
  return "learning";
}

function selectReportArtifactViewModel(reportState) {
  const reportData = reportState && reportState.reportData && typeof reportState.reportData === "object"
    ? reportState.reportData
    : {};
  const artifacts = reportData && reportData.artifacts && typeof reportData.artifacts === "object"
    ? reportData.artifacts
    : {};
  const figureList = Array.isArray(artifacts.figures)
    ? artifacts.figures
        .map((item) => normalizeArtifactHref(item))
        .filter(Boolean)
        .map((href) => ({
          href,
          label: href.split("/").pop() || href,
          tone: inferFigureSemanticTone(href),
        }))
    : [];
  const pdfPath = normalizeArtifactHref(artifacts.pdf);
  return {
    hasArtifacts: Boolean(pdfPath || figureList.length),
    pdfPath,
    figureList,
  };
}

function selectReportProvenanceViewModel(reportState) {
  const reportData = reportState && reportState.reportData && typeof reportState.reportData === "object"
    ? reportState.reportData
    : {};
  const metadata = reportData && reportData.metadata && typeof reportData.metadata === "object"
    ? reportData.metadata
    : {};
  return {
    sourceRunId: metadata.source_run_id ? String(metadata.source_run_id) : "",
    planHash: metadata.plan_hash ? String(metadata.plan_hash) : "",
    recordSchemaVersion: metadata.record_schema_version ? String(metadata.record_schema_version) : "",
    templateVersionUsed:
      metadata.template_version_used === undefined || metadata.template_version_used === null
        ? ""
        : String(metadata.template_version_used),
    regenerated:
      metadata.regenerated === undefined || metadata.regenerated === null
        ? ""
        : String(Boolean(metadata.regenerated)),
    regenerationMode: metadata.regeneration_mode ? String(metadata.regeneration_mode) : "",
    missingSourceMetadata: Array.isArray(metadata.missing_source_metadata)
      ? metadata.missing_source_metadata.map((item) => String(item))
      : [],
  };
}

function detectRunVersionMismatches(provenance, catalogState, planState) {
  const versions = catalogState && catalogState.versions && typeof catalogState.versions === "object"
    ? catalogState.versions
    : {};
  const expectedRecord = versions.record_schema_version ? String(versions.record_schema_version) : "";
  const expectedTemplate =
    versions.template_version_used === undefined || versions.template_version_used === null
      ? ""
      : String(versions.template_version_used);
  const expectedPlan = planState && planState.stableHash ? String(planState.stableHash) : "";

  const mismatches = [];
  if (provenance.recordSchemaVersion && expectedRecord && provenance.recordSchemaVersion !== expectedRecord) {
    mismatches.push({
      field: "record_schema_version",
      expected: expectedRecord,
      received: provenance.recordSchemaVersion,
      severity: "blocking",
      action: "Refresh run status or open static artifacts while schema-dependent views are disabled.",
    });
  }
  if (provenance.templateVersionUsed && expectedTemplate && provenance.templateVersionUsed !== expectedTemplate) {
    mismatches.push({
      field: "template_version_used",
      expected: expectedTemplate,
      received: provenance.templateVersionUsed,
      severity: "warning",
      action: "Proceed in degraded mode and refresh if interactive controls remain unavailable.",
    });
  }
  if (provenance.planHash && expectedPlan && provenance.planHash !== expectedPlan) {
    mismatches.push({
      field: "plan_hash",
      expected: expectedPlan,
      received: provenance.planHash,
      severity: "warning",
      action: "Re-resolve plan and start a new run if you need strict hash parity.",
    });
  }
  return mismatches;
}

function detectReportVersionMismatches(provenance, catalogState) {
  const versions = catalogState && catalogState.versions && typeof catalogState.versions === "object"
    ? catalogState.versions
    : {};
  const expectedRecord = versions.record_schema_version ? String(versions.record_schema_version) : "";
  const expectedTemplate =
    versions.template_version_used === undefined || versions.template_version_used === null
      ? ""
      : String(versions.template_version_used);

  const mismatches = [];
  if (provenance.recordSchemaVersion && expectedRecord && provenance.recordSchemaVersion !== expectedRecord) {
    mismatches.push({
      field: "record_schema_version",
      expected: expectedRecord,
      received: provenance.recordSchemaVersion,
      severity: "blocking",
      action: "Open static artifacts where available, then refresh run/report context.",
    });
  }
  if (provenance.templateVersionUsed && expectedTemplate && provenance.templateVersionUsed !== expectedTemplate) {
    mismatches.push({
      field: "template_version_used",
      expected: expectedTemplate,
      received: provenance.templateVersionUsed,
      severity: "warning",
      action: "Proceed in degraded mode using static artifacts and refresh if needed.",
    });
  }
  return mismatches;
}

function resolveLifecycleTone(lifecycleState, requestStatus) {
  const status = String(lifecycleState || "").toLowerCase();
  const request = String(requestStatus || "").toLowerCase();
  if (status.includes("fail") || status.includes("error") || request === "error") return "cs-minus";
  if (status.includes("complete") || status.includes("reportcomplete") || status.includes("runcomplete")) return "cs-plus";
  if (status.includes("progress") || status.includes("running") || request === "loading") return "probe";
  return "learning";
}

function buildLifecycleInstrumentView(lifecycleState, requestStatus) {
  const status = String(lifecycleState || "").toLowerCase();
  const request = String(requestStatus || "").toLowerCase();
  let progressPct = 8;
  let phaseLabel = "idle";
  if (status.includes("progress") || status.includes("running") || request === "loading") {
    progressPct = 52;
    phaseLabel = "in_progress";
  } else if (status.includes("complete") || status.includes("reportcomplete") || status.includes("runcomplete")) {
    progressPct = 100;
    phaseLabel = "complete";
  } else if (status.includes("fail") || status.includes("error") || request === "error") {
    progressPct = 100;
    phaseLabel = "failure";
  } else if (request === "success") {
    progressPct = 72;
    phaseLabel = "ready";
  }
  return {
    tone: resolveLifecycleTone(lifecycleState, requestStatus),
    progressPct,
    phaseLabel,
  };
}

window.VSLReact.lifecycleViewModels = {
  isRunTerminalLifecycle,
  selectRunLifecycleViewModel,
  selectRunProvenanceViewModel,
  selectReportLifecycleViewModel,
  selectReportArtifactViewModel,
  selectReportProvenanceViewModel,
  detectRunVersionMismatches,
  detectReportVersionMismatches,
  buildLifecycleInstrumentView,
  resolveLifecycleTone,
  normalizeArtifactHref,
  inferFigureSemanticTone,
};

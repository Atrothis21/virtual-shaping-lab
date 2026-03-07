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

function selectRunLifecycleViewModel(runState, planState) {
  const state = runState && runState.lifecycleState ? String(runState.lifecycleState) : "idle";
  const activeRunId = runState && runState.activeRunId ? String(runState.activeRunId) : "";
  const requestStatus = runState && runState.requestStatus ? String(runState.requestStatus) : "idle";
  const pollAt = runState && runState.lastPollAtMs ? new Date(runState.lastPollAtMs).toISOString() : "n/a";
  const canStartRun = Boolean(
    planState &&
    planState.requestStatus === "success" &&
    typeof planState.stableHash === "string" &&
    planState.stableHash
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

function selectReportLifecycleViewModel(reportState, runState) {
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
    canCreateReport: Boolean(effectiveRunId),
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

function BuilderRouteContainer({ builderDraftState, planState, onResolvePlan, onDraftEdited, resolveErrorView }) {
  const seed = builderDraftState && builderDraftState.draft ? builderDraftState.draft : null;
  const resolvedPlan = planState && planState.resolvedPlan ? planState.resolvedPlan : null;
  const stableHash = planState && planState.stableHash ? planState.stableHash : "";
  const summary = summarizeResolvedPlan(resolvedPlan);
  const expectedSignals = seed && Array.isArray(seed.expected_signals) ? seed.expected_signals : [];
  const flowPreview = expectedSignals.length ? expectedSignals.join(", ") : "n/a";
  function updateDraftPatch(patch) {
    if (typeof onDraftEdited !== "function") return;
    const nextDraft = {
      ...(seed && typeof seed === "object" ? seed : {}),
      ...patch,
    };
    onDraftEdited(nextDraft);
  }

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
      <div className="builder-sections-grid">
        <section className="builder-section-panel">
          <h3 className="builder-section-heading">Overview</h3>
          <div className="builder-kv"><strong>Draft Ownership:</strong> <code>{builderDraftState?.ownership || "n/a"}</code></div>
          <div className="builder-kv"><strong>Draft Version:</strong> <code>{builderDraftState?.draftVersion ?? "n/a"}</code></div>
          <div className="builder-kv"><strong>Validation Errors:</strong> <code>{Array.isArray(builderDraftState?.validationErrors) ? builderDraftState.validationErrors.length : 0}</code></div>
        </section>
        <section className="builder-section-panel">
          <h3 className="builder-section-heading">Protocol/Seed Selection</h3>
          <div className="builder-kv"><strong>seed_source:</strong> <code>{seed?.seed_source || "n/a"}</code></div>
          <label className="builder-control">
            <span>preset_key</span>
            <input
              type="text"
              value={seed?.preset_key || ""}
              onChange={(e) => updateDraftPatch({ preset_key: e.target.value })}
            />
          </label>
          <label className="builder-control">
            <span>protocol_key</span>
            <input
              type="text"
              value={seed?.protocol_key || ""}
              onChange={(e) => updateDraftPatch({ protocol_key: e.target.value })}
            />
          </label>
        </section>
        <section className="builder-section-panel">
          <h3 className="builder-section-heading">Phases</h3>
          <div className="builder-kv"><strong>flow_preview:</strong> <code>{flowPreview}</code></div>
          <div className="builder-kv"><strong>phase_count_hint:</strong> <code>{expectedSignals.length || 0}</code></div>
          <label className="builder-control">
            <span>expected_signals (comma separated)</span>
            <input
              type="text"
              value={expectedSignals.join(", ")}
              onChange={(e) => {
                const nextSignals = String(e.target.value || "")
                  .split(",")
                  .map((item) => item.trim())
                  .filter(Boolean);
                updateDraftPatch({ expected_signals: nextSignals });
              }}
            />
          </label>
        </section>
        <section className="builder-section-panel">
          <h3 className="builder-section-heading">Runtime</h3>
          <label className="builder-control">
            <span>run_mode_hint</span>
            <select
              value={seed?.run_mode_hint || "trial"}
              onChange={(e) => updateDraftPatch({ run_mode_hint: e.target.value })}
            >
              <option value="trial">trial</option>
              <option value="tick">tick</option>
            </select>
          </label>
          <div className="builder-kv"><strong>plan_request_status:</strong> <code>{planState?.requestStatus || "idle"}</code></div>
        </section>
        <section className="builder-section-panel">
          <h3 className="builder-section-heading">Report</h3>
          <label className="builder-control">
            <span>template_key</span>
            <input
              type="text"
              value={seed?.template_key || ""}
              onChange={(e) => updateDraftPatch({ template_key: e.target.value })}
            />
          </label>
          <div className="builder-kv"><strong>stable_hash:</strong> <code>{stableHash || "n/a"}</code></div>
        </section>
        <section className="builder-section-panel builder-section-panel-muted">
          <h3 className="builder-section-heading">Advanced/Debug</h3>
          <div className="builder-kv"><strong>dirty:</strong> <code>{String(Boolean(builderDraftState?.dirty))}</code></div>
          <div className="builder-kv"><strong>is_ready:</strong> <code>{String(Boolean(builderDraftState?.isReady))}</code></div>
          <div className="builder-kv"><strong>validation_state:</strong> <code>{builderDraftState?.isReady ? "ready" : "needs_attention"}</code></div>
        </section>
      </div>
      <div className="builder-validation-panel">
        <div><strong>Draft Readiness:</strong> <code>{builderDraftState?.isReady ? "ready" : "not_ready"}</code></div>
        <div><strong>Validation Errors:</strong> <code>{Array.isArray(builderDraftState?.validationErrors) ? builderDraftState.validationErrors.length : 0}</code></div>
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

function RunRouteContainer({
  runState,
  planState,
  builderDraftState,
  onStartRun,
  onRefreshRun,
  runActionStatus,
  provenanceView,
  mismatchView,
}) {
  const lifecycleViewModelsApi = window.VSLReact.lifecycleViewModels || {};
  const selectRunLifecycleViewModelFn = lifecycleViewModelsApi.selectRunLifecycleViewModel || selectRunLifecycleViewModel;
  const buildLifecycleInstrumentViewFn = lifecycleViewModelsApi.buildLifecycleInstrumentView || buildLifecycleInstrumentView;
  const vm = selectRunLifecycleViewModelFn(runState, planState, builderDraftState);
  const lifecycleInstrument = buildLifecycleInstrumentViewFn(vm.state, vm.requestStatus);
  const blockingMismatch = Array.isArray(mismatchView)
    ? mismatchView.find((m) => m.severity === "blocking")
    : null;
  return (
    <div className="route-card run-lifecycle-card">
      <div className="route-card-header">
        <h2>Run Lifecycle</h2>
        <span className={`vsl-status-badge semantic lifecycle-badge ${lifecycleInstrument.tone}`}>
          {vm.state}
        </span>
      </div>
      <div className="lifecycle-instrument">
        <div className={`lifecycle-meter ${lifecycleInstrument.tone}`}>
          <span style={{ width: `${lifecycleInstrument.progressPct}%` }} />
        </div>
        <div className="lifecycle-caption">
          <strong>phase:</strong> <code>{lifecycleInstrument.phaseLabel}</code>
        </div>
      </div>
      <p>Create runs from resolved plans and monitor lifecycle progression.</p>
      <div className="route-actions">
        <button
          type="button"
          className="route-action"
          onClick={() => {
            if (typeof onStartRun === "function") onStartRun();
          }}
          disabled={!vm.canStartRun || vm.requestStatus === "loading"}
        >
          {vm.requestStatus === "loading" ? "Starting Run..." : "Start Run"}
        </button>
        <button
          type="button"
          className="route-action"
          onClick={() => {
            if (typeof onRefreshRun === "function") onRefreshRun();
          }}
          disabled={!vm.activeRunId}
        >
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
        <div>
          <strong>next_actions:</strong>{" "}
          <code>{provenanceView.nextActions.length ? provenanceView.nextActions.join(", ") : "n/a"}</code>
        </div>
      </div>
      {blockingMismatch ? (
        <div className="run-blocking-note">
          <strong>Incompatible data version:</strong>{" "}
          This run detail is in blocking mode for <code>{blockingMismatch.field}</code>.
        </div>
      ) : null}
      {runActionStatus && runActionStatus.message ? (
        <p className="run-action-message">{runActionStatus.message}</p>
      ) : null}
      {runActionStatus && runActionStatus.error && runActionStatus.error.message ? (
        <p className="run-action-error">{String(runActionStatus.error.message)}</p>
      ) : null}
      {!vm.canStartRun ? (
        <p className="run-action-message">
          {!vm.stableHash
            ? "Resolve a plan first to enable run creation from a stable execution hash."
            : "Plan is stale for current draft. Re-resolve plan to enable run creation."}
        </p>
      ) : null}
    </div>
  );
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
}) {
  const lifecycleViewModelsApi = window.VSLReact.lifecycleViewModels || {};
  const selectReportLifecycleViewModelFn = lifecycleViewModelsApi.selectReportLifecycleViewModel || selectReportLifecycleViewModel;
  const buildLifecycleInstrumentViewFn = lifecycleViewModelsApi.buildLifecycleInstrumentView || buildLifecycleInstrumentView;
  const vm = selectReportLifecycleViewModelFn(reportState, runState, { isPlanFresh });
  const lifecycleInstrument = buildLifecycleInstrumentViewFn(vm.lifecycleState, vm.requestStatus);
  const warningMismatch = Array.isArray(mismatchView)
    ? mismatchView.find((m) => m.severity === "warning")
    : null;
  return (
    <div className="route-card report-lifecycle-card">
      <div className="route-card-header">
        <h2>Report Lifecycle</h2>
        <span className={`vsl-status-badge semantic lifecycle-badge ${lifecycleInstrument.tone}`}>
          {vm.requestStatus}
        </span>
      </div>
      <div className="lifecycle-instrument">
        <div className={`lifecycle-meter ${lifecycleInstrument.tone}`}>
          <span style={{ width: `${lifecycleInstrument.progressPct}%` }} />
        </div>
        <div className="lifecycle-caption">
          <strong>phase:</strong> <code>{lifecycleInstrument.phaseLabel}</code>
        </div>
      </div>
      <p>Create report artifacts from completed runs and monitor report lifecycle state.</p>
      <div className="route-actions">
        <button
          type="button"
          className="route-action"
          onClick={() => {
            if (typeof onCreateReport === "function") onCreateReport();
          }}
          disabled={!vm.canCreateReport || vm.requestStatus === "loading"}
        >
          {vm.requestStatus === "loading" ? "Generating Report..." : "Create Report"}
        </button>
        <button
          type="button"
          className="route-action"
          onClick={() => {
            if (typeof onRefreshRun === "function") onRefreshRun();
          }}
          disabled={!vm.effectiveRunId}
        >
          Refresh Run Status
        </button>
        <a className="route-action" href="/ui/results.html">Open Legacy Results</a>
      </div>
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
        <div>
          <strong>missing_source_metadata:</strong>{" "}
          <code>{provenanceView.missingSourceMetadata.length ? provenanceView.missingSourceMetadata.join(", ") : "n/a"}</code>
        </div>
      </div>
      {warningMismatch ? (
        <p className="report-degraded-note">
          Degraded mode active for <code>{warningMismatch.field}</code>. Static artifacts remain available.
        </p>
      ) : null}
      <div className="report-artifact-grid">
        <div className="report-artifact-card">
          <strong>PDF Report</strong>
          <div>
            {artifactView.pdfPath ? (
              <a href={artifactView.pdfPath} target="_blank" rel="noreferrer">Open report.pdf</a>
            ) : (
              <span className="report-artifact-missing">Not available yet</span>
            )}
          </div>
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
                <a
                  key={figure.href}
                  className={`report-figure-card accent-${figure.tone}`}
                  href={figure.href}
                  target="_blank"
                  rel="noreferrer"
                >
                  <span className="report-figure-title">{figure.label}</span>
                  <span className="report-figure-tone">{figure.tone}</span>
                </a>
              ))}
            </div>
          ) : (
            <span className="report-artifact-missing">No figures available yet</span>
          )}
        </div>
      </div>
      {reportActionStatus && reportActionStatus.message ? (
        <p className="report-action-message">{reportActionStatus.message}</p>
      ) : null}
      {reportActionStatus && reportActionStatus.error && reportActionStatus.error.message ? (
        <p className="report-action-error">{String(reportActionStatus.error.message)}</p>
      ) : null}
      {!vm.canCreateReport ? (
        <p className="report-action-message">
          {vm.isPlanFresh
            ? "Start and complete a run first to enable report generation."
            : "Plan is stale for current draft. Re-resolve plan before generating report."}
        </p>
      ) : null}
    </div>
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

  const lifecycleViewModelsApi = window.VSLReact.lifecycleViewModels || {};
  const selectRunProvenanceViewModelFn =
    lifecycleViewModelsApi.selectRunProvenanceViewModel || selectRunProvenanceViewModel;
  const detectRunVersionMismatchesFn =
    lifecycleViewModelsApi.detectRunVersionMismatches || detectRunVersionMismatches;
  const selectReportProvenanceViewModelFn =
    lifecycleViewModelsApi.selectReportProvenanceViewModel || selectReportProvenanceViewModel;
  const detectReportVersionMismatchesFn =
    lifecycleViewModelsApi.detectReportVersionMismatches || detectReportVersionMismatches;
  const selectReportArtifactViewModelFn =
    lifecycleViewModelsApi.selectReportArtifactViewModel || selectReportArtifactViewModel;

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
  const builderDraftTranslatorApi = window.VSLReact.builderDraftTranslator || {};
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
        run: ROUTES.run.key,
        report: ROUTES.report.key,
      },
    });
  }, [apiClient, dispatchEvent, presetActionServiceApi, stateApi]);
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
    if (!apiClient || !stateApi) return;
    const draftSeed = builderDraftState && builderDraftState.draft ? builderDraftState.draft : null;
    if (!draftSeed) {
      setPresetActionState({
        status: "error",
        step: "plan",
        message: "No preset seed is available in builder context.",
        error: { message: "Seed a preset first, then resolve plan." },
      });
      return;
    }
    const draft_to_payload = builderDraftTranslatorApi && typeof builderDraftTranslatorApi.draft_to_payload === "function"
      ? builderDraftTranslatorApi.draft_to_payload
      : null;
    if (!draft_to_payload) {
      setPresetActionState({
        status: "error",
        step: "plan",
        message: "Builder translator unavailable.",
        error: { message: "draft_to_payload translator is required for builder submission." },
      });
      return;
    }

    const translatedPayload = draft_to_payload(draftSeed);
    setPresetActionState({
      status: "loading",
      step: "plan",
      message: "Resolving builder plan...",
      error: null,
    });
    dispatchEvent({ type: stateApi.UI_EVENTS.PLAN_RESOLVE_REQUESTED });
    try {
      const data = await apiClient.postJson("plan", translatedPayload);
      dispatchEvent({
        type: stateApi.UI_EVENTS.PLAN_RESOLVE_SUCCEEDED,
        payload: {
          resolvedPlan: data && data.plan ? data.plan : null,
          stableHash: data && data.stable_hash ? data.stable_hash : "",
        },
      });
      setPresetActionState({
        status: "success",
        step: "plan",
        message: "Builder plan resolved.",
        error: null,
      });
    } catch (error) {
      const normalized = error && typeof error === "object" ? error : { message: "Builder plan resolve failed." };
      dispatchEvent({
        type: stateApi.UI_EVENTS.PLAN_RESOLVE_FAILED,
        payload: { error: normalized },
      });
      setPresetActionState({
        status: "error",
        step: "plan",
        message: "Builder plan resolve failed.",
        error: normalized,
      });
    }
  }, [apiClient, builderDraftState, builderDraftTranslatorApi, dispatchEvent, stateApi]);

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
    if (isRunTerminalLifecycle(runState.lifecycleState)) return;

    let cancelled = false;
    const intervalId = window.setInterval(async () => {
      await runReportWorkflowHandlers.pollActiveRunStatus({ runState });
      if (cancelled) return;
    }, 1500);
    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, [runReportWorkflowHandlers, runState]);

  function renderActiveRoute() {
    if (activeRoute === ROUTES.builder.key) {
      return (
        <BuilderRouteContainer
          builderDraftState={builderDraftState}
          planState={planState}
          onResolvePlan={resolvePlanFromBuilderContext}
          onDraftEdited={editBuilderDraft}
          resolveErrorView={planResolveErrorView}
        />
      );
    }
    if (activeRoute === ROUTES.run.key) {
      return (
        <RunRouteContainer
          runState={runState}
          planState={planState}
          builderDraftState={builderDraftState}
          onStartRun={startRunFromResolvedPlan}
          onRefreshRun={refreshActiveRunStatus}
          runActionStatus={runActionStatus}
          provenanceView={runProvenanceView}
          mismatchView={runVersionMismatches}
        />
      );
    }
    if (activeRoute === ROUTES.report.key) {
      return (
        <ReportRouteContainer
          reportState={reportState}
          runState={runState}
          isPlanFresh={isPlanFreshForCurrentDraft}
          onCreateReport={createReportFromActiveRun}
          onRefreshRun={refreshActiveRunStatus}
          reportActionStatus={reportActionStatus}
          provenanceView={reportProvenanceView}
          mismatchView={reportVersionMismatches}
          artifactView={reportArtifactView}
        />
      );
    }
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
          {activeRoute === ROUTES.run.key && runWarningMismatch ? (
            <GlobalBanner
              level="warning"
              title="Version mismatch detected"
              message={`Field: ${runWarningMismatch.field} | Expected: ${runWarningMismatch.expected} | Received: ${runWarningMismatch.received} | Action: ${runWarningMismatch.action}`}
              actionLabel="Refresh Run Status"
              onAction={refreshActiveRunStatus}
            />
          ) : null}
          {activeRoute === ROUTES.run.key && runBlockingMismatch ? (
            <BlockingPanel
              title="Incompatible data version"
              message={`This view cannot be rendered with ${runBlockingMismatch.field}. Expected ${runBlockingMismatch.expected}, received ${runBlockingMismatch.received}. Use manual refresh or open static artifacts.`}
              actionLabel="Refresh Run Status"
              onAction={refreshActiveRunStatus}
            />
          ) : null}
          {activeRoute === ROUTES.report.key && reportWarningMismatch ? (
            <GlobalBanner
              level="warning"
              title="Version mismatch detected"
              message={`Field: ${reportWarningMismatch.field} | Expected: ${reportWarningMismatch.expected} | Received: ${reportWarningMismatch.received} | Action: ${reportWarningMismatch.action}`}
              actionLabel="Refresh Run Status"
              onAction={refreshActiveRunStatus}
            />
          ) : null}
          {activeRoute === ROUTES.report.key && reportBlockingMismatch ? (
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

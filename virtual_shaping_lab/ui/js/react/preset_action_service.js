window.VSLReact = window.VSLReact || {};

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

function buildPresetApiPayload(item, draftSeed) {
  if (!item) return { report: { preset: "custom_protocol" } };
  const seed = draftSeed || buildConstrainedDraftSeedFromPreset(item);
  const runModeHint = seed && seed.run_mode_hint ? seed.run_mode_hint : "trial";
  return {
    settings: {
      update_mode: runModeHint === "tick" ? "tick" : "trial",
      record_mode: "trial",
    },
    report: {
      preset: item.key || "custom_protocol",
    },
  };
}

function toUserError(error, fallbackMessage) {
  if (error && typeof error === "object" && error.message) return error;
  return {
    message: fallbackMessage || "Request failed.",
    status: error && typeof error === "object" && error.status ? error.status : 0,
    envelope: error && typeof error === "object" && error.envelope ? error.envelope : null,
  };
}

function extractErrorMessage(error) {
  if (!error || typeof error !== "object") return "";
  if (error.message) return String(error.message);
  if (error.envelope && error.envelope.message) return String(error.envelope.message);
  return "";
}

function isPlanHashMismatchError(error) {
  return extractErrorMessage(error).toLowerCase().includes("plan hash mismatch");
}

function isRunTerminalFromPayload(runData) {
  const lifecycleState = runData && runData.lifecycle && runData.lifecycle.state
    ? String(runData.lifecycle.state).toLowerCase()
    : (runData && runData.state ? String(runData.state).toLowerCase() : "");
  if (!lifecycleState) return false;
  return (
    lifecycleState === "completed" ||
    lifecycleState === "complete" ||
    lifecycleState === "failed" ||
    lifecycleState === "error" ||
    lifecycleState === "cancelled" ||
    lifecycleState === "canceled"
  );
}

function waitMs(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function createPresetActionService(deps) {
  const {
    apiClient,
    stateApi,
    dispatchEvent,
    setActionState,
    routeKeys,
  } = deps || {};

  async function resolvePresetFromSelection(presetItem) {
    if (!apiClient || !stateApi || !presetItem) return { ok: false, error: { message: "Missing API or preset." } };
    const draftSeed = buildConstrainedDraftSeedFromPreset(presetItem);
    const payload = buildPresetApiPayload(presetItem, draftSeed);
    setActionState({
      status: "loading",
      step: "plan",
      message: "Resolving preset plan...",
      error: null,
    });
    dispatchEvent({ type: stateApi.UI_EVENTS.PLAN_RESOLVE_REQUESTED });
    try {
      const data = await apiClient.postJson("plan", payload);
      dispatchEvent({
        type: stateApi.UI_EVENTS.PLAN_RESOLVE_SUCCEEDED,
        payload: {
          resolvedPlan: data && data.plan ? data.plan : null,
          stableHash: data && data.stable_hash ? data.stable_hash : "",
        },
      });
      setActionState({
        status: "success",
        step: "plan",
        message: "Preset plan resolved.",
        error: null,
      });
      return { ok: true, data, payload };
    } catch (error) {
      const normalized = toUserError(error, "Preset plan resolve failed.");
      dispatchEvent({
        type: stateApi.UI_EVENTS.PLAN_RESOLVE_FAILED,
        payload: { error: normalized },
      });
      setActionState({
        status: "error",
        step: "plan",
        message: "Preset plan resolve failed.",
        error: normalized,
      });
      return { ok: false, error: normalized };
    }
  }

  async function resolveAndRunPresetFromSelection(presetItem) {
    if (!apiClient || !stateApi || !presetItem) return { ok: false, error: { message: "Missing API or preset." } };
    const resolved = await resolvePresetFromSelection(presetItem);
    if (!resolved.ok) return resolved;

    const payload = resolved.payload || buildPresetApiPayload(presetItem, buildConstrainedDraftSeedFromPreset(presetItem));
    const expectedPlanHash = resolved.data && resolved.data.stable_hash ? resolved.data.stable_hash : "";
    const runPayload = expectedPlanHash ? { ...payload, expected_plan_hash: expectedPlanHash } : payload;

    setActionState({
      status: "loading",
      step: "run",
      message: "Starting preset run...",
      error: null,
    });
    dispatchEvent({ type: stateApi.UI_EVENTS.RUN_START_REQUESTED });
    try {
      const runData = await apiClient.postJson("run", runPayload);
      dispatchEvent({
        type: stateApi.UI_EVENTS.RUN_START_SUCCEEDED,
        payload: {
          runId: runData && runData.run_id ? String(runData.run_id) : "",
          lifecycleState: runData && runData.lifecycle && runData.lifecycle.state
            ? String(runData.lifecycle.state).toLowerCase()
            : "running",
          runData: runData || null,
          atMs: Date.now(),
        },
      });
      setActionState({
        status: "success",
        step: "run",
        message: "Preset run started.",
        error: null,
      });
      return { ok: true, data: runData };
    } catch (error) {
      const normalized = toUserError(error, "Preset run failed.");
      const mismatch = isPlanHashMismatchError(normalized);
      dispatchEvent({
        type: stateApi.UI_EVENTS.RUN_START_FAILED,
        payload: { error: normalized },
      });
      setActionState({
        status: "error",
        step: "run",
        message: mismatch
          ? "Plan hash mismatch detected. Re-resolve preset and retry run."
          : "Preset run failed.",
        error: normalized,
      });
      return { ok: false, error: normalized };
    }
  }

  async function waitForRunReportReadiness(runId) {
    let lastData = null;
    for (let i = 0; i < 12; i += 1) {
      const polled = await apiClient.getJson(`runs/${encodeURIComponent(runId)}`);
      lastData = polled || null;
      dispatchEvent({
        type: stateApi.UI_EVENTS.RUN_STATUS_UPDATED,
        payload: {
          runData: polled || null,
          lifecycleState: polled && polled.lifecycle && polled.lifecycle.state
            ? String(polled.lifecycle.state).toLowerCase()
            : undefined,
          atMs: Date.now(),
        },
      });
      if (isRunTerminalFromPayload(polled)) return { ok: true, runData: polled };
      await waitMs(1000);
    }
    return { ok: false, runData: lastData };
  }

  async function resolveRunReportPresetFromSelection(presetItem) {
    const runResult = await resolveAndRunPresetFromSelection(presetItem);
    if (!runResult.ok) return runResult;

    const runData = runResult.data || null;
    const runId = runData && runData.run_id ? String(runData.run_id) : "";
    if (!runId) {
      const err = { message: "Run started but no run_id was returned." };
      setActionState({
        status: "error",
        step: "report",
        message: "Unable to continue to report step.",
        error: err,
      });
      return { ok: false, error: err };
    }

    setActionState({
      status: "loading",
      step: "report_ready",
      message: "Waiting for run readiness before report...",
      error: null,
    });

    const ready = isRunTerminalFromPayload(runData)
      ? { ok: true, runData }
      : await waitForRunReportReadiness(runId);

    if (!ready.ok) {
      setActionState({
        status: "success",
        step: "report_ready",
        message: "Run not report-ready yet. Continue from Run route when complete.",
        error: null,
      });
      return { ok: true, deferred: true, routeKey: routeKeys && routeKeys.run ? routeKeys.run : "run" };
    }

    dispatchEvent({
      type: stateApi.UI_EVENTS.REPORT_REQUESTED,
      payload: { runId },
    });
    setActionState({
      status: "loading",
      step: "report",
      message: "Generating report...",
      error: null,
    });
    try {
      const reportData = await apiClient.postJson(`runs/${encodeURIComponent(runId)}/report`, {});
      dispatchEvent({
        type: stateApi.UI_EVENTS.REPORT_SUCCEEDED,
        payload: {
          runId,
          reportData: reportData || null,
        },
      });
      setActionState({
        status: "success",
        step: "report",
        message: "Preset report generated.",
        error: null,
      });
      return { ok: true, data: reportData, routeKey: routeKeys && routeKeys.report ? routeKeys.report : "report" };
    } catch (error) {
      const normalized = toUserError(error, "Preset report generation failed.");
      dispatchEvent({
        type: stateApi.UI_EVENTS.REPORT_FAILED,
        payload: { error: normalized },
      });
      setActionState({
        status: "error",
        step: "report",
        message: "Preset report generation failed.",
        error: normalized,
      });
      return { ok: false, error: normalized };
    }
  }

  return {
    resolvePresetFromSelection,
    resolveAndRunPresetFromSelection,
    resolveRunReportPresetFromSelection,
  };
}

window.VSLReact.presetActionService = {
  buildConstrainedDraftSeedFromPreset,
  buildPresetApiPayload,
  toUserError,
  isPlanHashMismatchError,
  isRunTerminalFromPayload,
  waitMs,
  createPresetActionService,
};

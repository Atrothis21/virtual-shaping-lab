window.VSLReact = window.VSLReact || {};

function toUserError(error, fallbackMessage) {
  if (error && typeof error === "object" && error.message) return error;
  return {
    message: fallbackMessage || "Request failed.",
    status: error && typeof error === "object" && error.status ? error.status : 0,
    envelope: error && typeof error === "object" && error.envelope ? error.envelope : null,
  };
}

function createRunReportWorkflowService(deps) {
  const {
    apiClient,
    stateApi,
    dispatchEvent,
    setRunActionStatus,
    setReportActionStatus,
    buildPresetItemFromDraftSeed,
    buildPresetApiPayload,
  } = deps || {};

  async function startRunFromResolvedPlan(context) {
    if (!apiClient || !stateApi) return;
    const builderDraftState = context && context.builderDraftState ? context.builderDraftState : null;
    const planState = context && context.planState ? context.planState : null;
    const draftSeed = builderDraftState && builderDraftState.draft ? builderDraftState.draft : null;
    const presetItem = typeof buildPresetItemFromDraftSeed === "function"
      ? buildPresetItemFromDraftSeed(draftSeed)
      : null;
    if (!presetItem) {
      setRunActionStatus({
        message: "Run start blocked.",
        error: { message: "Seed a preset first to provide run payload context." },
      });
      return;
    }
    if (!planState || planState.requestStatus !== "success" || !planState.stableHash) {
      setRunActionStatus({
        message: "Run start blocked.",
        error: { message: "Resolve plan first to produce stable_hash for run start." },
      });
      return;
    }

    const payload = typeof buildPresetApiPayload === "function"
      ? buildPresetApiPayload(presetItem, draftSeed)
      : { report: { preset: presetItem.key || "custom_protocol" } };
    const runPayload = { ...payload, expected_plan_hash: planState.stableHash };

    setRunActionStatus({ message: "Starting run from resolved plan...", error: null });
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
      setRunActionStatus({ message: "Run started.", error: null });
    } catch (error) {
      const normalized = toUserError(error, "Run creation failed.");
      dispatchEvent({
        type: stateApi.UI_EVENTS.RUN_START_FAILED,
        payload: { error: normalized },
      });
      setRunActionStatus({
        message: "Run creation failed.",
        error: normalized,
      });
    }
  }

  async function refreshActiveRunStatus(context) {
    if (!apiClient || !stateApi) return;
    const runState = context && context.runState ? context.runState : null;
    if (!runState || !runState.activeRunId) return;
    const runId = String(runState.activeRunId);
    try {
      const runData = await apiClient.getJson(`runs/${encodeURIComponent(runId)}`);
      dispatchEvent({
        type: stateApi.UI_EVENTS.RUN_STATUS_UPDATED,
        payload: {
          runData: runData || null,
          lifecycleState: runData && runData.lifecycle && runData.lifecycle.state
            ? String(runData.lifecycle.state).toLowerCase()
            : undefined,
          atMs: Date.now(),
        },
      });
      setRunActionStatus({ message: "Run status refreshed.", error: null });
      return runData || null;
    } catch (error) {
      setRunActionStatus({
        message: "Run status refresh failed.",
        error: toUserError(error, "Run status refresh failed."),
      });
      return null;
    }
  }

  async function pollActiveRunStatus(context) {
    const runData = await refreshActiveRunStatus(context);
    if (!runData) {
      setRunActionStatus((prev) => ({
        ...prev,
        message: "Polling interrupted. You can refresh status manually.",
        error: prev.error,
      }));
    }
  }

  async function createReportFromActiveRun(context) {
    if (!apiClient || !stateApi) return;
    const runState = context && context.runState ? context.runState : null;
    const reportState = context && context.reportState ? context.reportState : null;
    const runId = (reportState && reportState.runId) || (runState && runState.activeRunId) || "";
    if (!runId) {
      setReportActionStatus({
        message: "Report generation unavailable until a run is selected.",
        error: { message: "No run_id available for report creation." },
      });
      return;
    }

    setReportActionStatus({ message: "Generating report artifacts...", error: null });
    dispatchEvent({
      type: stateApi.UI_EVENTS.REPORT_REQUESTED,
      payload: { runId: String(runId) },
    });
    try {
      const reportData = await apiClient.postJson(`runs/${encodeURIComponent(runId)}/report`, {});
      dispatchEvent({
        type: stateApi.UI_EVENTS.REPORT_SUCCEEDED,
        payload: {
          runId: String(runId),
          reportData: reportData || null,
        },
      });
      setReportActionStatus({ message: "Report artifacts generated.", error: null });
    } catch (error) {
      const normalized = toUserError(error, "Report generation failed.");
      dispatchEvent({
        type: stateApi.UI_EVENTS.REPORT_FAILED,
        payload: { error: normalized },
      });
      setReportActionStatus({
        message: "Report generation failed. Retry when run lifecycle is report-ready.",
        error: normalized,
      });
    }
  }

  return {
    startRunFromResolvedPlan,
    refreshActiveRunStatus,
    pollActiveRunStatus,
    createReportFromActiveRun,
  };
}

window.VSLReact.runReportWorkflowService = {
  createRunReportWorkflowService,
  toUserError,
};

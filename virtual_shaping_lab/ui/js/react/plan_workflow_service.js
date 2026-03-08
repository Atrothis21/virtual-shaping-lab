window.VSLReact = window.VSLReact || {};

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

async function resolvePlanFromBuilderContext(deps) {
  const {
    apiClient,
    stateApi,
    builderDraftState,
    builderDraftTranslatorApi,
    builderSubmissionGuardsApi,
    dispatchEvent,
    setPresetActionState,
  } = deps || {};
  if (!apiClient || !stateApi || typeof dispatchEvent !== "function" || typeof setPresetActionState !== "function") return;

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
  const assertBuilderDraftForTranslation =
    builderSubmissionGuardsApi && typeof builderSubmissionGuardsApi.assertBuilderDraftForTranslation === "function"
      ? builderSubmissionGuardsApi.assertBuilderDraftForTranslation
      : (value) => value;
  const assertTranslatedBuilderPayload =
    builderSubmissionGuardsApi && typeof builderSubmissionGuardsApi.assertTranslatedBuilderPayload === "function"
      ? builderSubmissionGuardsApi.assertTranslatedBuilderPayload
      : (value) => value;
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

  let translatedPayload;
  try {
    const guardedDraft = assertBuilderDraftForTranslation(draftSeed);
    translatedPayload = assertTranslatedBuilderPayload(draft_to_payload(guardedDraft));
  } catch (error) {
    const normalized = error && typeof error === "object" ? error : { message: "Builder submission guard failed." };
    setPresetActionState({
      status: "error",
      step: "plan",
      message: "Builder submission guard blocked payload.",
      error: normalized,
    });
    dispatchEvent({
      type: stateApi.UI_EVENTS.PLAN_RESOLVE_FAILED,
      payload: { error: normalized },
    });
    return;
  }
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
}

window.VSLReact.planWorkflowService = {
  extractFieldHintsFromReason,
  buildPlanResolveErrorView,
  resolvePlanFromBuilderContext,
};

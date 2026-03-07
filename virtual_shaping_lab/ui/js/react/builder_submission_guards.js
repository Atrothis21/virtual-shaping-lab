(function initBuilderSubmissionGuards(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});

  function isObjectLike(value) {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
  }

  function assertBuilderDraftForTranslation(draft) {
    if (!isObjectLike(draft)) {
      throw new Error("Builder draft is required before translation.");
    }
    // Guard against slipping execution payload through builder route.
    if (Object.prototype.hasOwnProperty.call(draft, "settings") || Object.prototype.hasOwnProperty.call(draft, "report")) {
      throw new Error("Builder route rejected direct payload-shaped draft input.");
    }
    return draft;
  }

  function assertTranslatedBuilderPayload(payload) {
    if (!isObjectLike(payload)) {
      throw new Error("Translator output must be an object payload.");
    }
    if (!isObjectLike(payload.settings) || !isObjectLike(payload.report)) {
      throw new Error("Translator output missing required settings/report payload sections.");
    }
    if (
      Object.prototype.hasOwnProperty.call(payload, "preset_key") ||
      Object.prototype.hasOwnProperty.call(payload, "protocol_key")
    ) {
      throw new Error("Translator boundary violation: draft-only fields leaked into submission payload.");
    }
    return payload;
  }

  VSLReact.builderSubmissionGuards = {
    assertBuilderDraftForTranslation,
    assertTranslatedBuilderPayload,
  };
})(typeof window !== "undefined" ? window : globalThis);

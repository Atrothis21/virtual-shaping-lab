window.VSLReact = window.VSLReact || {};

async function bootstrapCatalog(deps) {
  const { apiClient, stateApi, dispatchEvent } = deps || {};
  if (!apiClient || !stateApi || typeof dispatchEvent !== "function") return;
  dispatchEvent({ type: stateApi.UI_EVENTS.CATALOG_REFRESH_REQUESTED });
  try {
    const payload = await apiClient.getJson("catalog/extensions");
    dispatchEvent({
      type: stateApi.UI_EVENTS.CATALOG_REFRESH_SUCCEEDED,
      payload: {
        extensions: payload && payload.extensions ? payload.extensions : null,
        versions: payload && payload.versions ? payload.versions : null,
        atMs: Date.now(),
      },
    });
  } catch (error) {
    dispatchEvent({
      type: stateApi.UI_EVENTS.CATALOG_REFRESH_FAILED,
      payload: { error: error || null },
    });
  }
}

function refreshCatalog(deps) {
  const { apiClient, stateApi, dispatchEvent } = deps || {};
  if (!stateApi || typeof dispatchEvent !== "function") return;
  if (!apiClient) {
    dispatchEvent({
      type: stateApi.UI_EVENTS.CATALOG_REFRESH_FAILED,
      payload: { error: { message: "API client unavailable." } },
    });
    return;
  }
  bootstrapCatalog({ apiClient, stateApi, dispatchEvent });
}

window.VSLReact.catalogBootstrapService = {
  bootstrapCatalog,
  refreshCatalog,
};

debugLog("boot", {
  time: new Date().toISOString(),
  payloadLoaded: typeof payload !== "undefined",
  phaseCount: payload?.experiment?.phases?.length ?? 0
});

if (typeof initPayload !== "function") {
  console.warn("initPayload missing");
} else {
  initPayload();
}

if (typeof renderPhaseList !== "function") {
  console.warn("renderPhaseList missing");
} else {
  renderPhaseList();
}

if (typeof renderPhaseEditor !== "function") {
  console.warn("renderPhaseEditor missing");
} else {
  renderPhaseEditor();
}

{
  const adv = document.getElementById("advanced-toggle");
  if (adv) {
    adv.onchange = () => {
      renderPhaseEditor();
    };
  }
}

if (typeof initPhaseControls === "function") initPhaseControls();
if (typeof initParamControls === "function") initParamControls();
if (typeof initStimuliControls === "function") initStimuliControls();
if (typeof initRunControls === "function") initRunControls();

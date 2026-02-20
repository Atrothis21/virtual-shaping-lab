function initPhaseControls() {
  if (typeof protocol !== "undefined" && protocol) {
    protocol.onchange = () => {
      const original = phase().protocol;
      const next = protocol.value;

      phase().protocol = next;

      try {
        validatePhaseOrder(payload.experiment.phases);
      } catch (err) {
        phase().protocol = original;
        protocol.value = original;
        debugLog("Phase order invalid", { error: err.message });
        alert(err.message);
        return;
      }

      onProtocolChanged(original, next);

      debugLog("protocol changed", { protocol: protocol.value });
      renderPhaseEditor();
    };
  }

  const addBtn = document.getElementById("add-phase-btn");
  if (addBtn) {
    addBtn.onclick = () => {
      const nextProtocol = "acquisition";
      const newPhase = buildPhase(nextProtocol, payload.experiment.phases.length);

      payload.experiment.phases.push(newPhase);

      try {
        validatePhaseOrder(payload.experiment.phases);
      } catch (err) {
        payload.experiment.phases.pop();
        debugLog("Phase order invalid", { error: err.message });
        alert(err.message);
        return;
      }

      activePhaseIndex = payload.experiment.phases.length - 1;
      renderPhaseList();
      renderPhaseEditor();
    };
  }
}

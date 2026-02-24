window.VSLReact = window.VSLReact || {};

(function mountPresetHandoff() {
  const slugMatch = window.location.pathname.match(/\/ui\/presets\/([a-z0-9_]+)\.html$/i);
  if (!slugMatch) return;

  const actions = document.querySelector(".actions");
  const runButton = Array.from(document.querySelectorAll("button"))
    .find((b) => (b.textContent || "").trim().toLowerCase() === "run experiment");
  if (!actions || !runButton) return;
  if (document.getElementById("handoff-builder-btn")) return;

  const btn = document.createElement("button");
  btn.id = "handoff-builder-btn";
  btn.className = "btn secondary";
  btn.type = "button";
  btn.textContent = "Open In Builder With This Payload";

  const status = document.createElement("div");
  status.style.fontSize = "0.84rem";
  status.style.color = "#4b5563";
  status.style.marginTop = "0.4rem";

  function findPayload() {
    const preBlocks = Array.from(document.querySelectorAll("pre"));
    for (const pre of preBlocks) {
      const txt = (pre.textContent || "").trim();
      if (!txt || txt === "Not run yet.") continue;
      try {
        const parsed = JSON.parse(txt);
        if (parsed && parsed.experiment) return parsed;
      } catch (_err) {
        // ignore non-json pre blocks
      }
    }
    return null;
  }

  btn.addEventListener("click", () => {
    const payload = findPayload();
    if (!payload) {
      status.textContent = "Could not read generated payload yet. Adjust any control once and try again.";
      return;
    }

    try {
      const key = window.VSLReact?.builderState?.BUILDER_SEED_KEY || "vsl_builder_seed_payload";
      window.localStorage.setItem(key, JSON.stringify(payload));
      status.textContent = "Payload transferred. Opening builder...";
      window.location.href = "/ui/builder.html?from=preset";
    } catch (err) {
      status.textContent = `Transfer failed: ${err.message}`;
    }
  });

  actions.appendChild(btn);
  actions.appendChild(status);
})();

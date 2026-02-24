window.VSLReact = window.VSLReact || {};

const PRESET_FOCUS = {
  acquisition: [],
  extinction: [],
  compound_acquisition: ["salience"],
  differential_acquisition: ["similarity"],
  blocking: ["salience"],
  overshadowing: ["salience", "attention"],
  overexpectation: ["salience"],
  conditioned_inhibition: ["salience"],
  occasion_setting: ["context"],
  rapid_reacquisition: ["context"],
  aba_renewal: ["context"],
  abc_renewal: ["context"],
  aab_renewal: ["context"],
  operant_conditioning: [],
  matching_law: [],
};

const MECH_HELP = {
  salience: "representation strength",
  attention: "learning-rate scaling",
  similarity: "generalization structure",
  context: "latent context assignment",
};

function getPresetSlug() {
  const match = window.location.pathname.match(/\/ui\/presets\/([a-z0-9_]+)\.html$/i);
  return match ? match[1] : null;
}

function norm(txt) {
  return String(txt || "").toLowerCase();
}

function findControlFromLabel(labelEl) {
  if (!labelEl) return null;
  let node = labelEl.nextElementSibling;
  while (node) {
    const tag = node.tagName;
    if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA") return node;
    node = node.nextElementSibling;
  }
  return null;
}

function neutralizeAndDisable(control, mechanism, lock) {
  if (!control) return;

  if (!lock) {
    control.disabled = false;
    return;
  }

  if (mechanism === "salience") {
    if (control.tagName === "INPUT" && control.type === "range") {
      control.value = "1";
      control.dispatchEvent(new Event("input", { bubbles: true }));
      control.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }

  if (mechanism === "attention") {
    if (control.tagName === "INPUT" && control.type === "range") {
      control.value = "1";
      control.dispatchEvent(new Event("input", { bubbles: true }));
      control.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }

  if (mechanism === "context") {
    if (control.tagName === "INPUT" && control.type === "checkbox") {
      control.checked = false;
      control.dispatchEvent(new Event("input", { bubbles: true }));
      control.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }

  if (mechanism === "similarity") {
    if (control.tagName === "INPUT" && control.type === "checkbox") {
      control.checked = false;
      control.dispatchEvent(new Event("input", { bubbles: true }));
      control.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }

  control.disabled = true;
}

function applyFocusMode(focusList, unlockAll) {
  const focus = new Set(focusList || []);
  const lock = !unlockAll;

  const labels = Array.from(document.querySelectorAll("label"));
  labels.forEach((labelEl) => {
    const txt = norm(labelEl.textContent);
    const control = findControlFromLabel(labelEl);
    if (!control) return;

    if (txt.includes("salience")) {
      neutralizeAndDisable(control, "salience", lock && !focus.has("salience"));
      return;
    }
    if (txt.includes("attention")) {
      neutralizeAndDisable(control, "attention", lock && !focus.has("attention"));
      return;
    }
    if (txt.includes("similarity")) {
      neutralizeAndDisable(control, "similarity", lock && !focus.has("similarity"));
      return;
    }
    if (txt.includes("context inference") || txt.includes("max contexts")) {
      neutralizeAndDisable(control, "context", lock && !focus.has("context"));
    }
  });
}

function buildBanner(focusList, unlockAll, onToggle) {
  const banner = document.createElement("section");
  banner.id = "preset-focus-mode";
  banner.className = "panel";
  banner.style.borderLeft = "3px solid #93c5fd";
  banner.style.background = "#f0f9ff";
  banner.style.padding = "0.75rem 1rem";
  banner.style.marginTop = "1rem";
  banner.style.borderRadius = "6px";
  banner.style.position = "sticky";
  banner.style.top = "0.4rem";
  banner.style.zIndex = "8";

  const focusText = (focusList || []).length
    ? focusList.map((m) => MECH_HELP[m] || m).join(", ")
    : "baseline prediction-error behavior";

  banner.innerHTML = `
    <h3 style="margin:0 0 0.35rem 0;">Mechanism Focus Mode</h3>
    <div style="font-size:0.9rem;color:#1f2937;">
      This preset teaches <strong>${focusText}</strong>. Other mechanisms are held neutral by default.
    </div>
    <label style="display:block;margin-top:0.5rem;font-weight:600;">
      <input id="focus-unlock-toggle" type="checkbox" ${unlockAll ? "checked" : ""} />
      Unlock all mechanisms (advanced)
    </label>
    <div style="font-size:0.82rem;color:#4b5563;margin-top:0.25rem;">
      Unlocking may move behavior away from the canonical teaching configuration.
    </div>
  `;

  const toggle = banner.querySelector("#focus-unlock-toggle");
  toggle.addEventListener("change", (e) => onToggle(Boolean(e.target.checked)));

  return banner;
}

(function mountPresetFocusMode() {
  const slug = getPresetSlug();
  if (!slug) return;
  if (document.getElementById("preset-focus-mode")) return;

  const focusList = PRESET_FOCUS[slug];
  if (!focusList) return;

  let unlockAll = false;
  const LS_KEY = `vsl_preset_unlock_${slug}`;
  try {
    unlockAll = localStorage.getItem(LS_KEY) === "1";
  } catch (_err) {
    unlockAll = false;
  }

  const root = document.getElementById("root");
  if (!root || !root.parentNode) return;

  const banner = buildBanner(focusList, unlockAll, (nextUnlock) => {
    unlockAll = nextUnlock;
    try {
      localStorage.setItem(LS_KEY, nextUnlock ? "1" : "0");
    } catch (_err) {
      // no-op
    }
    applyFocusMode(focusList, unlockAll);
  });

  root.parentNode.insertBefore(banner, root);

  const observer = new MutationObserver(() => {
    applyFocusMode(focusList, unlockAll);
  });
  observer.observe(root, { childList: true, subtree: true });

  setTimeout(() => applyFocusMode(focusList, unlockAll), 0);
  setTimeout(() => applyFocusMode(focusList, unlockAll), 50);
})();

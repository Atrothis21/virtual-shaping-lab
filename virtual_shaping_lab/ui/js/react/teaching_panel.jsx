window.VSLReact = window.VSLReact || {};

window.VSLReact.uiModes = window.VSLReact.uiModes || (() => {
  const MODES = Object.freeze({
    PRESET: "preset",
    TEACHING: "teaching",
    BUILDER: "builder",
    EXPERT: "expert",
  });

  const SURFACE_MODE_OPTIONS = Object.freeze({
    index: [MODES.PRESET],
    presets: [MODES.PRESET, MODES.TEACHING],
    preset_detail: [MODES.PRESET, MODES.TEACHING, MODES.BUILDER, MODES.EXPERT],
    builder: [MODES.BUILDER, MODES.EXPERT],
  });

  const STORAGE_KEY = "vsl_ui_mode";

  function validMode(mode) {
    return Object.values(MODES).includes(mode);
  }

  function resolveMode(surfaceKey, requested) {
    const options = SURFACE_MODE_OPTIONS[surfaceKey] || [MODES.PRESET];
    const requestedMode = String(requested || "").toLowerCase();
    if (validMode(requestedMode) && options.includes(requestedMode)) return requestedMode;
    try {
      const persisted = String(localStorage.getItem(STORAGE_KEY) || "").toLowerCase();
      if (validMode(persisted) && options.includes(persisted)) return persisted;
    } catch (_err) {
      // ignore storage access issues
    }
    return options[0];
  }

  function activate(surfaceKey, requested) {
    const mode = resolveMode(surfaceKey, requested);
    window.VSLReact.currentMode = mode;
    window.VSLReact.currentSurface = surfaceKey;
    window.VSLReact.availableModesForSurface = SURFACE_MODE_OPTIONS[surfaceKey] || [MODES.PRESET];
    try {
      localStorage.setItem(STORAGE_KEY, mode);
    } catch (_err) {
      // ignore storage access issues
    }
    return mode;
  }

  return {
    MODES,
    SURFACE_MODE_OPTIONS,
    resolveMode,
    activate,
  };
})();

window.VSLReact.toCanonicalPayload = window.VSLReact.toCanonicalPayload || function toCanonicalPayload(payload) {
  if (!payload || typeof payload !== "object") return payload;
  const source = JSON.parse(JSON.stringify(payload));
  const experiment = source.experiment || {};
  const report = source.report || {};

  if (experiment.program && experiment.agent && experiment.runtime) return source;

  const hasLegacyShape =
    Object.prototype.hasOwnProperty.call(experiment, "learner") ||
    Object.prototype.hasOwnProperty.call(experiment, "phases") ||
    Object.prototype.hasOwnProperty.call(experiment, "protocol");

  if (!hasLegacyShape) {
    throw new Error("Teaching panel requires canonical payloads.");
  }

  const legacyPhases = Array.isArray(experiment.phases)
    ? experiment.phases
    : [{
        name: "Phase 0",
        protocol: experiment.protocol,
        stimuli: experiment.stimuli || {},
        params: experiment.params || {},
      }];

  const canonicalPhases = legacyPhases.map((phase, idx) => {
    const params = { ...((phase && phase.params) || {}) };
    const trialsRaw = phase && phase.trials != null ? phase.trials : (params.n_trials != null ? params.n_trials : 1);
    const trials = Math.max(1, Number.parseInt(trialsRaw, 10) || 1);
    params.n_trials = trials;
    return {
      name: (phase && phase.name) || `Phase ${idx}`,
      protocol: phase && phase.protocol,
      stimuli: (phase && phase.stimuli) || {},
      params,
      trials,
    };
  });

  const representationInput = experiment.representation;
  const representation =
    typeof representationInput === "string"
      ? { name: representationInput, params: {} }
      : { ...(representationInput || {}) };
  representation.params = { ...(representation.params || {}) };
  if (experiment.salience && typeof experiment.salience === "object") {
    representation.salience = { ...experiment.salience };
  }

  const learning = {
    rule: experiment.learner,
    params: {},
  };
  const hasAttentionInitial = experiment.attention && typeof experiment.attention === "object";
  const hasAttentionConfig = experiment.attention_config && typeof experiment.attention_config === "object";
  if (hasAttentionInitial || hasAttentionConfig) {
    learning.attention = {
      initial: hasAttentionInitial ? { ...experiment.attention } : {},
      config: hasAttentionConfig ? { ...experiment.attention_config } : {},
    };
  }

  const runtime = { ...((experiment.runtime && typeof experiment.runtime === "object") ? experiment.runtime : {}) };
  if (experiment.context_inference && typeof experiment.context_inference === "object") {
    runtime.context_inference = { ...experiment.context_inference };
  }

  return {
    experiment: {
      program: { phases: canonicalPhases },
      agent: {
        name: experiment.agent,
        representation,
        learning,
        policy: experiment.policy || null,
      },
      runtime,
    },
    report,
  };
};

const MECHANISM_HELP = {
  Baseline: "Baseline behavior arises with neutral mechanism settings and prediction-error learning.",
  Salience: "Salience scales representation strength, changing how strongly cues are encoded.",
  Similarity: "Similarity spreads activation across cues, driving generalization and overlap effects.",
  Attention: "Attention scales effective learning rate by cue identity during updates.",
  Context: "Context partitions learning/retrieval across environments or inferred latent states.",
  "Prediction Error": "Prediction error is the mismatch between expected and observed outcome.",
  "Operant Value Learning": "Operant learners update action values from reinforcement history.",
};

const PRESET_ORDER = [
  "acquisition",
  "extinction",
  "differential_acquisition",
  "compound_acquisition",
  "blocking",
  "overshadowing",
  "overexpectation",
  "conditioned_inhibition",
  "aba_renewal",
  "abc_renewal",
  "aab_renewal",
  "rapid_reacquisition",
  "occasion_setting",
  "operant_conditioning",
  "matching_law",
  "shaping",
  "resurgence",
  "superextinction",
  "spontaneous_recovery",
];

const REVEAL_LAYERS = Object.freeze({
  INTUITION: "intuition",
  MECHANISM: "mechanism",
  OPERATOR: "operator",
  ALGEBRA: "algebra",
});

const REVEAL_LAYER_LABELS = Object.freeze({
  [REVEAL_LAYERS.INTUITION]: "Intuition",
  [REVEAL_LAYERS.MECHANISM]: "Mechanism",
  [REVEAL_LAYERS.OPERATOR]: "Operator",
  [REVEAL_LAYERS.ALGEBRA]: "Full Algebra",
});

const TRIAL_STATE_IO = Object.freeze({
  Phi: { reads: ["s"], writes: ["x"] },
  C: { reads: ["x", "m.persistent.context"], writes: ["z"] },
  P: { reads: ["z", "w"], writes: ["y.prediction"] },
  Policy: { reads: ["y.prediction", "a"], writes: ["a"] },
  Env: { reads: ["a", "u"], writes: ["u"] },
  Err: { reads: ["u", "y.prediction"], writes: ["y.error", "m.derived.error"] },
  Update: { reads: ["y.error", "x", "z", "w"], writes: ["w", "m.persistent.weights"] },
  Measure: { reads: ["w", "y", "u"], writes: ["m.derived.metrics"] },
});

function ioForStage(stage) {
  return TRIAL_STATE_IO[stage] || { reads: ["state"], writes: ["state"] };
}

function pipelineNodeMarkup(stage) {
  const io = ioForStage(stage);
  return `
    <div class="tp-pipeline-node" data-stage="${stage}" style="border:1px solid #dbeafe;border-radius:6px;padding:0.35rem 0.45rem;background:#ffffff;min-width:12rem;">
      <div style="font-weight:700;color:#1e3a8a;margin-bottom:0.2rem;">${stage}</div>
      <div class="tp-trialstate-io" data-stage="${stage}">
        <div style="font-size:0.8rem;color:#334155;"><strong>Reads:</strong> ${io.reads.join(", ")}</div>
        <div style="font-size:0.8rem;color:#334155;"><strong>Writes:</strong> ${io.writes.join(", ")}</div>
      </div>
    </div>
  `;
}

function pipelineVisualizationMarkup(spec) {
  const seq = operatorSequenceFor(spec);
  const nodes = seq.map((stage) => pipelineNodeMarkup(stage)).join("");
  return `
    <div class="tp-operator-pipeline" style="display:flex;flex-wrap:wrap;gap:0.45rem;align-items:stretch;">
      ${nodes}
    </div>
  `;
}

function operatorSequenceFor(spec) {
  const mechanisms = Array.isArray(spec?.mechanisms) ? spec.mechanisms : [];
  const hasContext = mechanisms.includes("Context");
  const hasOperant = mechanisms.includes("Operant Value Learning");
  const seq = ["Phi"];
  if (hasContext) seq.push("C");
  seq.push("P");
  if (hasOperant) seq.push("Policy");
  seq.push("Env", "Err", "Update", "Measure");
  return seq;
}

function revealContentFor(spec, layer) {
  if (layer === REVEAL_LAYERS.INTUITION) {
    return `<p style="margin:0;color:#374151;">${spec.summary}</p>`;
  }
  if (layer === REVEAL_LAYERS.MECHANISM) {
    const mechanisms = Array.isArray(spec.mechanisms) ? spec.mechanisms : [];
    const mechanismList = mechanisms.length ? mechanisms.join(", ") : "Baseline";
    return `
      <p style="margin:0 0 0.25rem 0;color:#374151;"><strong>Mechanisms:</strong> ${mechanismList}</p>
      <p style="margin:0;color:#4b5563;">${spec.expected}</p>
    `;
  }
  if (layer === REVEAL_LAYERS.OPERATOR) {
    const seq = operatorSequenceFor(spec).join(" -> ");
    const pipeline = pipelineVisualizationMarkup(spec);
    return `
      <p style="margin:0 0 0.25rem 0;color:#374151;"><strong>Pipeline:</strong> ${seq}</p>
      <p style="margin:0;color:#4b5563;">Operator labels map to the mechanism view above and stay read-only in this teaching surface.</p>
      <div style="margin-top:0.45rem;">${pipeline}</div>
    `;
  }
  const pipeline = pipelineVisualizationMarkup(spec);
  return `
    <p style="margin:0 0 0.25rem 0;color:#374151;"><strong>TrialState Coordinates:</strong> s, x, z, w, a, u, y, m</p>
    <p style="margin:0;color:#4b5563;">Advanced inspection mode exposes full state-flow interpretation without changing payload semantics.</p>
    <div style="margin-top:0.45rem;">${pipeline}</div>
  `;
}

window.VSLReact.teachingPanels = {
  acquisition: {
    phaseFlow: ["Acquisition"],
    mechanisms: ["Baseline"],
    summary: "Associative strength increases under repeated reinforced CS presentations.",
    expected: "Prediction rises over trials and approaches asymptote.",
  },
  extinction: {
    phaseFlow: ["Acquisition", "Nonreinforcement"],
    mechanisms: ["Baseline"],
    summary: "Previously reinforced cue is presented without reinforcement to reduce responding.",
    expected: "Prediction declines during extinction relative to acquisition tail.",
  },
  differential_acquisition: {
    phaseFlow: ["Differential Acquisition"],
    mechanisms: ["Similarity"],
    summary: "CS+ and CS- are trained with different outcomes to build discrimination.",
    expected: "CS+ prediction exceeds CS-; separation changes with similarity.",
  },
  compound_acquisition: {
    phaseFlow: ["Compound Acquisition"],
    mechanisms: ["Salience"],
    summary: "Two cues are trained together; cue weighting influences joint learning.",
    expected: "Both cues learn, with stronger-weighted cue contributing more.",
  },
  blocking: {
    phaseFlow: ["Acquisition", "Compound Acquisition"],
    mechanisms: ["Salience", "Prediction Error"],
    summary: "Prior learning on one cue can reduce acquisition to a newly added cue.",
    expected: "Primary cue retains stronger control after compound phase.",
  },
  overshadowing: {
    phaseFlow: ["Acquisition", "Compound Acquisition"],
    mechanisms: ["Attention", "Salience"],
    summary: "A more strongly weighted cue dominates compound learning.",
    expected: "Dominant cue prediction exceeds companion cue in compound phase.",
  },
  overexpectation: {
    phaseFlow: ["Acquisition", "Compound Acquisition"],
    mechanisms: ["Salience", "Prediction Error"],
    summary: "Combining already predictive cues creates expectation mismatch dynamics.",
    expected: "Compound behavior departs from simple additive intuition.",
  },
  conditioned_inhibition: {
    phaseFlow: ["Acquisition", "Compound Nonreinforcement", "Probe"],
    mechanisms: ["Salience", "Prediction Error"],
    summary: "Compound nonreinforcement establishes inhibitory control by cue structure.",
    expected: "Probe and inhibition phases show suppressed responding vs excitatory baseline.",
  },
  aba_renewal: {
    phaseFlow: ["Acquisition (A)", "Context Shift (B)", "Nonreinforcement", "Context Shift (A)", "Probe"],
    mechanisms: ["Context"],
    summary: "Returning to training context after extinction can recover responding.",
    expected: "Probe in original context exceeds extinction-context responding.",
  },
  abc_renewal: {
    phaseFlow: ["Acquisition (A)", "Context Shift (B)", "Nonreinforcement", "Context Shift (C)", "Probe"],
    mechanisms: ["Context"],
    summary: "Probe in a novel context tests retrieval outside extinction context.",
    expected: "Probe can recover above extinction tail with context change.",
  },
  aab_renewal: {
    phaseFlow: ["Acquisition (A)", "Nonreinforcement (A)", "Context Shift (B)", "Probe"],
    mechanisms: ["Context"],
    summary: "Extinction in acquisition context with probe elsewhere yields different recovery pattern.",
    expected: "Probe recovery pattern differs from ABA/ABC structure.",
  },
  rapid_reacquisition: {
    phaseFlow: ["Acquisition (A)", "Context Shift (B)", "Nonreinforcement", "Context Shift (A)", "Acquisition"],
    mechanisms: ["Context"],
    summary: "Relearning in prior acquisition context can accelerate compared with initial learning.",
    expected: "Reacquisition tail rises above extinction tail and recovers quickly.",
  },
  occasion_setting: {
    phaseFlow: ["Acquisition", "Nonreinforcement", "Probe"],
    mechanisms: ["Context"],
    summary: "One cue modulates interpretation of another across phase structure.",
    expected: "Probe behavior sits between pure excitatory and nonreinforced baselines.",
  },
  operant_conditioning: {
    phaseFlow: ["Operant Acquisition"],
    mechanisms: ["Operant Value Learning"],
    summary: "Action values increase under reinforcement schedule contingencies.",
    expected: "Prediction/value trends increase with delivered reinforcement.",
  },
  matching_law: {
    phaseFlow: ["Matching Law Protocol"],
    mechanisms: ["Operant Value Learning"],
    summary: "Action allocation reflects relative reinforcement across concurrent options.",
    expected: "Choice distribution shifts toward richer schedule.",
  },
  shaping: {
    phaseFlow: ["Shaping Stage 1", "Shaping Stage 2"],
    mechanisms: ["Operant Value Learning"],
    summary: "Behavior is established under dense reinforcement then tested under leaner contingency.",
    expected: "Reward density is lower in the harder second stage while behavior remains organized.",
  },
  resurgence: {
    phaseFlow: ["Reinforcement", "Suppression", "Recovery"],
    mechanisms: ["Operant Value Learning"],
    summary: "A suppressed response can re-emerge when reinforcement conditions shift again.",
    expected: "Recovery block reward/prediction exceeds suppression block.",
  },
  superextinction: {
    phaseFlow: ["Reinforcement", "Punishment"],
    mechanisms: ["Operant Value Learning"],
    summary: "Negative outcomes suppress responding more aggressively than omission alone.",
    expected: "Punishment-phase outcomes trend below acquisition outcomes.",
  },
  spontaneous_recovery: {
    phaseFlow: ["Acquisition (A)", "Extinction (B)", "Probe (A)"],
    mechanisms: ["Operant Value Learning", "Context"],
    summary: "Returning to the acquisition context can recover responding after extinction.",
    expected: "Probe in context A rises above extinction tail from context B.",
  },
};

(function mountTeachingPanel() {
  const slugMatch = window.location.pathname.match(/\/ui\/presets\/([a-z0-9_]+)\.html$/i);
  const slug = slugMatch ? slugMatch[1] : null;
  if (!slug) return;

  const spec = window.VSLReact.teachingPanels[slug];
  if (!spec) return;
  if (document.getElementById("teaching-panel")) return;
  const modeModel = window.VSLReact.uiModes;
  const queryMode = new URLSearchParams(window.location.search || "").get("mode");
  let activeMode = modeModel ? modeModel.activate("preset_detail", queryMode || "teaching") : "teaching";

  const panel = document.createElement("section");
  panel.id = "teaching-panel";
  panel.className = "panel";
  panel.style.borderLeft = "3px solid #c7d2fe";
  panel.style.background = "#f8faff";
  panel.style.padding = "0.75rem 1rem";
  panel.style.marginTop = "1rem";
  panel.style.borderRadius = "6px";

  const phaseFlow = Array.isArray(spec.phaseFlow) ? spec.phaseFlow.join(" -> ") : "";
  const mechanisms = Array.isArray(spec.mechanisms) ? spec.mechanisms : [];
  const mechanismPills = mechanisms
    .map((name) => `<button type="button" class="tp-pill" data-mech="${name}" style="border:1px solid #c7d2fe;background:#eef2ff;color:#1e3a8a;border-radius:999px;padding:0.12rem 0.5rem;font-size:0.78rem;cursor:pointer;">${name}</button>`)
    .join("");

  let activeLayer = REVEAL_LAYERS.INTUITION;
  panel.innerHTML = `
    <div style="display:flex;justify-content:space-between;gap:0.5rem;align-items:center;margin-bottom:0.5rem;flex-wrap:wrap;">
      <div style="font-size:0.86rem;color:#374151;">
        <strong>Navigation:</strong> <a href="/ui/index.html">Menu</a> / <a href="/ui/presets.html">Presets</a> / ${slug.replaceAll("_", " ")}
      </div>
      <div id="tp-nav-links" style="display:flex;gap:0.35rem;flex-wrap:wrap;"></div>
    </div>
    <h3 style="margin:0 0 0.25rem 0;">Teaching Panel</h3>
    <div style="font-size:0.85rem;color:#374151;margin-bottom:0.45rem;">
      <strong>UI Mode:</strong> <span id="tp-ui-mode">${activeMode}</span>
    </div>
    <div id="tp-mode-actions" style="display:flex;gap:0.35rem;flex-wrap:wrap;margin-bottom:0.5rem;">
      <button type="button" class="tp-pill" data-mode="preset" style="border:1px solid #c7d2fe;background:#eef2ff;color:#1e3a8a;border-radius:999px;padding:0.12rem 0.5rem;font-size:0.78rem;cursor:pointer;">Preset</button>
      <button type="button" class="tp-pill" data-mode="teaching" style="border:1px solid #c7d2fe;background:#eef2ff;color:#1e3a8a;border-radius:999px;padding:0.12rem 0.5rem;font-size:0.78rem;cursor:pointer;">Teaching</button>
      <button type="button" class="tp-pill" data-mode="builder" style="border:1px solid #c7d2fe;background:#eef2ff;color:#1e3a8a;border-radius:999px;padding:0.12rem 0.5rem;font-size:0.78rem;cursor:pointer;">Builder</button>
      <button type="button" class="tp-pill" data-mode="expert" style="border:1px solid #c7d2fe;background:#eef2ff;color:#1e3a8a;border-radius:999px;padding:0.12rem 0.5rem;font-size:0.78rem;cursor:pointer;">Expert</button>
    </div>
    <div style="font-size:0.78rem;font-weight:700;color:#334155;letter-spacing:0.04em;text-transform:uppercase;margin-bottom:0.25rem;">
      Progressive Reveal
    </div>
    <div id="tp-reveal-actions" style="display:flex;gap:0.35rem;flex-wrap:wrap;margin-bottom:0.5rem;">
      <button type="button" class="tp-pill" data-layer="intuition" style="border:1px solid #c7d2fe;background:#eef2ff;color:#1e3a8a;border-radius:999px;padding:0.12rem 0.5rem;font-size:0.78rem;cursor:pointer;">Intuition</button>
      <button type="button" class="tp-pill" data-layer="mechanism" style="border:1px solid #c7d2fe;background:#eef2ff;color:#1e3a8a;border-radius:999px;padding:0.12rem 0.5rem;font-size:0.78rem;cursor:pointer;">Mechanism</button>
      <button type="button" class="tp-pill" data-layer="operator" style="border:1px solid #c7d2fe;background:#eef2ff;color:#1e3a8a;border-radius:999px;padding:0.12rem 0.5rem;font-size:0.78rem;cursor:pointer;">Operator</button>
      <button type="button" class="tp-pill" data-layer="algebra" style="border:1px solid #c7d2fe;background:#eef2ff;color:#1e3a8a;border-radius:999px;padding:0.12rem 0.5rem;font-size:0.78rem;cursor:pointer;">Full Algebra</button>
    </div>
    <div id="tp-reveal-content" style="font-size:0.88rem;color:#1f2937;background:#ffffff;border:1px solid #dbeafe;border-radius:6px;padding:0.45rem 0.55rem;margin-bottom:0.55rem;"></div>
    <div style="display:flex;gap:0.45rem;flex-wrap:wrap;margin-bottom:0.55rem;">
      ${mechanismPills}
    </div>
    <div id="tp-mech-help" style="display:none;font-size:0.88rem;color:#374151;background:#ffffff;border:1px solid #dbeafe;border-radius:6px;padding:0.45rem 0.55rem;margin-bottom:0.55rem;"></div>
    <details open style="margin-bottom:0.4rem;">
      <summary style="cursor:pointer;font-weight:600;color:#111827;">Phase Flow</summary>
      <div style="font-size:0.92rem;color:#374151;margin-top:0.35rem;">${phaseFlow}</div>
    </details>
    <details style="margin-bottom:0.4rem;">
      <summary style="cursor:pointer;font-weight:600;color:#111827;">What This Demonstrates</summary>
      <div style="font-size:0.92rem;color:#374151;margin-top:0.35rem;">${spec.summary}</div>
    </details>
    <details style="margin-bottom:0.2rem;">
      <summary style="cursor:pointer;font-weight:600;color:#111827;">Expected Signature</summary>
      <div style="font-size:0.92rem;color:#374151;margin-top:0.35rem;">${spec.expected}</div>
    </details>
  `;

  const navHost = panel.querySelector("#tp-nav-links");
  const idx = PRESET_ORDER.indexOf(slug);
  const prev = idx > 0 ? PRESET_ORDER[idx - 1] : null;
  const next = idx >= 0 && idx < PRESET_ORDER.length - 1 ? PRESET_ORDER[idx + 1] : null;
  if (prev) {
    const a = document.createElement("a");
    a.href = `/ui/presets/${prev}.html`;
    a.textContent = "Previous";
    a.className = "btn secondary";
    a.style.marginTop = "0";
    navHost.appendChild(a);
  }
  if (next) {
    const a = document.createElement("a");
    a.href = `/ui/presets/${next}.html`;
    a.textContent = "Next";
    a.className = "btn secondary";
    a.style.marginTop = "0";
    navHost.appendChild(a);
  }

  const help = panel.querySelector("#tp-mech-help");
  const pills = panel.querySelectorAll(".tp-pill");
  pills.forEach((pill) => {
    pill.addEventListener("click", () => {
      const name = pill.getAttribute("data-mech");
      const text = MECHANISM_HELP[name] || "Mechanism explanation coming soon.";
      help.style.display = "block";
      help.innerHTML = `<strong>${name}:</strong> ${text}`;
    });
  });

  const modeLabel = panel.querySelector("#tp-ui-mode");
  const modeButtons = panel.querySelectorAll("#tp-mode-actions .tp-pill");
  modeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const requested = button.getAttribute("data-mode");
      if (!modeModel) return;
      activeMode = modeModel.activate("preset_detail", requested);
      if (modeLabel) modeLabel.textContent = activeMode;
      renderReveal();
      if (activeMode === "builder") {
        const destination = `/ui/builder.html?mode=builder&from=preset`;
        window.location.href = destination;
      }
    });
  });

  const revealContent = panel.querySelector("#tp-reveal-content");
  const revealButtons = panel.querySelectorAll("#tp-reveal-actions .tp-pill");
  const renderReveal = () => {
    if (!revealContent) return;
    if (activeLayer === REVEAL_LAYERS.ALGEBRA && activeMode !== "expert") {
      activeLayer = REVEAL_LAYERS.OPERATOR;
    }
    revealContent.innerHTML = revealContentFor(spec, activeLayer);
    revealButtons.forEach((button) => {
      const layer = button.getAttribute("data-layer");
      const isActive = layer === activeLayer;
      const isAlgebra = layer === REVEAL_LAYERS.ALGEBRA;
      const disableForMode = isAlgebra && activeMode !== "expert";
      button.disabled = disableForMode;
      button.style.background = isActive ? "#1e3a8a" : "#eef2ff";
      button.style.color = isActive ? "#ffffff" : "#1e3a8a";
      button.setAttribute("aria-pressed", isActive ? "true" : "false");
      button.title = REVEAL_LAYER_LABELS[layer] || layer;
    });
  };
  revealButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const requested = button.getAttribute("data-layer");
      if (!requested || !Object.values(REVEAL_LAYERS).includes(requested)) return;
      activeLayer = requested;
      renderReveal();
    });
  });
  renderReveal();

  const root = document.getElementById("root");
  if (root && root.parentNode) {
    root.parentNode.insertBefore(panel, root);
  } else {
    document.body.prepend(panel);
  }

  // Collapse generated payload by default to reduce visual complexity.
  const h2s = Array.from(document.querySelectorAll("h2"));
  const payloadHeader = h2s.find((h) => (h.textContent || "").trim().toLowerCase() === "generated payload");
  if (payloadHeader && payloadHeader.nextElementSibling && payloadHeader.nextElementSibling.tagName === "PRE") {
    const payloadPre = payloadHeader.nextElementSibling;
    const details = document.createElement("details");
    details.style.marginTop = "0.6rem";
    const summary = document.createElement("summary");
    summary.textContent = "Show Generated Payload JSON";
    summary.style.cursor = "pointer";
    summary.style.fontWeight = "600";
    details.appendChild(summary);
    details.appendChild(payloadPre);
    payloadHeader.replaceWith(details);
  }

  // Lightweight run feedback: status line near run controls.
  const runButton = Array.from(document.querySelectorAll("button"))
    .find((b) => ((b.textContent || "").trim().toLowerCase() === "run experiment"));
  if (runButton) {
    const status = document.createElement("div");
    status.id = "preset-run-status";
    status.style.marginTop = "0.8rem";
    status.style.marginBottom = "0.35rem";
    status.style.fontSize = "0.9rem";
    status.innerHTML = "<strong>Run Status:</strong> Idle";

    const outputPre = runButton.nextElementSibling;
    runButton.parentNode.insertBefore(status, runButton);
    runButton.addEventListener("click", () => {
      status.innerHTML = "<strong>Run Status:</strong> Validating / Running";
    });

    if (outputPre && outputPre.tagName === "PRE") {
      const syncStatus = () => {
        const txt = (outputPre.textContent || "").trim().toLowerCase();
        if (!txt || txt === "not run yet.") {
          status.innerHTML = "<strong>Run Status:</strong> Idle";
        } else if (txt.includes("running")) {
          status.innerHTML = "<strong>Run Status:</strong> Running";
        } else if (outputPre.classList.contains("error") || txt.includes("error") || txt.includes("failed")) {
          status.innerHTML = "<strong>Run Status:</strong> Error";
        } else {
          status.innerHTML = "<strong>Run Status:</strong> Completed / Redirecting";
        }
      };
      const obs = new MutationObserver(syncStatus);
      obs.observe(outputPre, { childList: true, subtree: true, characterData: true });
      syncStatus();
    }
  }
})();

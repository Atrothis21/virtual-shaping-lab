window.VSLReact = window.VSLReact || {};

window.VSLReact.toCanonicalPayload = window.VSLReact.toCanonicalPayload || function toCanonicalPayload(payload) {
  if (!payload || typeof payload !== "object") return payload;
  const experiment = payload.experiment || {};
  if (experiment.program && experiment.agent) return payload;

  const legacyPhases = Array.isArray(experiment.phases) && experiment.phases.length
    ? experiment.phases
    : (experiment.protocol
      ? [{
          name: "Phase 0",
          protocol: experiment.protocol,
          stimuli: experiment.stimuli || null,
          params: (experiment.params && typeof experiment.params === "object") ? { ...experiment.params } : {},
        }]
      : []);

  const phases = legacyPhases.map((phase, idx) => {
    const params = (phase && typeof phase.params === "object") ? { ...phase.params } : {};
    const trials = Number.isInteger(phase?.trials)
      ? phase.trials
      : Number.isInteger(params.n_trials)
        ? params.n_trials
        : 1;
    params.n_trials = trials;
    return {
      name: phase?.name || `Phase ${idx}`,
      protocol: phase?.protocol,
      stimuli: phase?.stimuli || null,
      params,
      trials,
    };
  });

  const representation = (experiment.representation && typeof experiment.representation === "object")
    ? { ...experiment.representation, params: { ...(experiment.representation.params || {}) } }
    : { name: experiment.representation, params: {} };

  if (experiment.salience && typeof experiment.salience === "object") {
    representation.salience = { ...experiment.salience };
  }

  const runtime = (experiment.runtime && typeof experiment.runtime === "object")
    ? { ...experiment.runtime }
    : {};
  if (experiment.context_inference && typeof experiment.context_inference === "object") {
    runtime.context_inference = { ...experiment.context_inference };
  }

  return {
    experiment: {
      program: { phases },
      agent: {
        name: experiment.agent,
        representation,
        learning: {
          rule: experiment.learner,
          params: {},
          attention: {
            config: (experiment.attention_config && typeof experiment.attention_config === "object")
              ? { ...experiment.attention_config }
              : {},
            initial: (experiment.attention && typeof experiment.attention === "object")
              ? { ...experiment.attention }
              : {},
          },
        },
        policy: experiment.policy ?? null,
      },
      runtime,
    },
    report: payload.report || {},
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

  panel.innerHTML = `
    <div style="display:flex;justify-content:space-between;gap:0.5rem;align-items:center;margin-bottom:0.5rem;flex-wrap:wrap;">
      <div style="font-size:0.86rem;color:#374151;">
        <strong>Navigation:</strong> <a href="/ui/index.html">Menu</a> / <a href="/ui/presets.html">Presets</a> / ${slug.replaceAll("_", " ")}
      </div>
      <div id="tp-nav-links" style="display:flex;gap:0.35rem;flex-wrap:wrap;"></div>
    </div>
    <h3 style="margin:0 0 0.45rem 0;">Teaching Panel</h3>
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

window.VSLReact = window.VSLReact || {};

const MECHANISM_HELP = {
  Baseline: "Baseline behavior arises with neutral mechanism settings and prediction-error learning.",
  Salience: "Salience scales representation strength, changing how strongly cues are encoded.",
  Similarity: "Similarity spreads activation across cues, driving generalization and overlap effects.",
  Attention: "Attention scales effective learning rate by cue identity during updates.",
  Context: "Context partitions learning/retrieval across environments or inferred latent states.",
  "Prediction Error": "Prediction error is the mismatch between expected and observed outcome.",
  "Operant Value Learning": "Operant learners update action values from reinforcement history.",
};

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
})();

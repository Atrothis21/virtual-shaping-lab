window.VSLReact = window.VSLReact || {};

function preset(def) {
  return {
    mechanisms: [],
    phaseSummary: "",
    teaches: "",
    builderNext: "",
    builderHref: "/ui/builder.html",
    ...def,
  };
}

window.VSLReact.presetSections = [
  {
    title: "Classical Agent - Single-Phase Procedures",
    note: "Pavlovian phases for isolated behavior.",
    items: [
      preset({
        name: "Acquisition",
        description: "Phase: Acquisition.",
        phaseSummary: "Acquisition",
        teaches: "How associative strength grows under repeated reinforced CS trials.",
        builderNext: "Change alpha, outcome, or CS identity and compare learning curves.",
        href: "/ui/presets/acquisition.html",
      }),
      preset({
        name: "Compound Acquisition",
        description: "Phase: Compound Acquisition (CS1 and CS2).",
        phaseSummary: "Compound Acquisition",
        mechanisms: ["Salience"],
        teaches: "How two cues learn together and how cue strength balance affects compound learning.",
        builderNext: "Adjust salience per cue and compare asymmetry between CS1 and CS2.",
        href: "/ui/presets/compound_acquisition.html",
      }),
      preset({
        name: "Differential Acquisition",
        description: "Phase: Differential Acquisition (CS+ vs CS-).",
        phaseSummary: "Differential Acquisition",
        mechanisms: ["Similarity"],
        teaches: "How the system separates reinforced and nonreinforced cues.",
        builderNext: "Enable similarity and test how CS- responds as similarity to CS+ increases.",
        href: "/ui/presets/differential_acquisition.html",
      }),
    ]
  },
  {
    title: "Classical Agent - Multi-Phase Phenomena",
    note: "Canonical multi-phase behavioral effects.",
    items: [
      preset({
        name: "Extinction",
        description: "Phases: Acquisition -> Nonreinforcement.",
        phaseSummary: "Acquisition -> Nonreinforcement",
        teaches: "How learned responding decays when reinforcement is withheld.",
        builderNext: "Add a probe phase to inspect residual responding after extinction.",
        href: "/ui/presets/extinction.html",
      }),
      preset({
        name: "Overshadowing",
        description: "Phases: Acquisition (CS1) -> Compound Acquisition (CS1+CS2).",
        phaseSummary: "Acquisition -> Compound Acquisition",
        mechanisms: ["Attention", "Salience"],
        teaches: "How one cue can dominate learning in a compound due to stronger weighting.",
        builderNext: "Vary attention or salience asymmetry and compare cue-specific predictions.",
        href: "/ui/presets/overshadowing.html",
      }),
      preset({
        name: "Overexpectation",
        description: "Phases: Acquisition (A+, B+) -> Compound Acquisition (AB+).",
        phaseSummary: "Acquisition -> Compound Acquisition",
        mechanisms: ["Salience"],
        teaches: "How combining already predictive cues can induce expectation mismatch.",
        builderNext: "Adjust acquisition/compound trial counts to see overexpectation sensitivity.",
        href: "/ui/presets/overexpectation.html",
      }),
      preset({
        name: "Conditioned Inhibition",
        description: "Phases: Acquisition -> Compound Nonreinforcement -> Probe.",
        phaseSummary: "Acquisition -> Compound Nonreinforcement -> Probe",
        mechanisms: ["Salience"],
        teaches: "How inhibitory cue structure suppresses responding in compound presentations.",
        builderNext: "Modify inhibition/probe proportions and compare suppression strength.",
        href: "/ui/presets/conditioned_inhibition.html",
      }),
      preset({
        name: "ABA Renewal",
        description: "Phases: Acquisition (A) -> Context Shift (B) -> Nonreinforcement -> Context Shift (A) -> Probe.",
        phaseSummary: "Acquisition -> Context Shift -> Nonreinforcement -> Context Shift -> Probe",
        mechanisms: ["Context"],
        teaches: "How returning to the original context can recover responding after extinction.",
        builderNext: "Toggle context inference and compare inferred vs explicit context behavior.",
        href: "/ui/presets/aba_renewal.html",
      }),
      preset({
        name: "ABC Renewal",
        description: "Phases: Acquisition (A) -> Context Shift (B) -> Nonreinforcement -> Context Shift (C) -> Probe.",
        phaseSummary: "Acquisition -> Context Shift -> Nonreinforcement -> Context Shift -> Probe",
        mechanisms: ["Context"],
        teaches: "How a novel probe context can partially recover responding after extinction elsewhere.",
        builderNext: "Swap probe context and compare ABC against ABA/AAB response recovery.",
        href: "/ui/presets/abc_renewal.html",
      }),
      preset({
        name: "AAB Renewal",
        description: "Phases: Acquisition (A) -> Nonreinforcement (A) -> Context Shift (B) -> Probe.",
        phaseSummary: "Acquisition -> Nonreinforcement -> Context Shift -> Probe",
        mechanisms: ["Context"],
        teaches: "How shifting probe context without extinction-context mismatch changes recovery pattern.",
        builderNext: "Test AAB vs ABA with identical trial counts to isolate context effects.",
        href: "/ui/presets/aab_renewal.html",
      }),
      preset({
        name: "Rapid Reacquisition",
        description: "Phases: Acquisition (A) -> Context Shift (B) -> Nonreinforcement -> Context Shift (A) -> Acquisition.",
        phaseSummary: "Acquisition -> Context Shift -> Nonreinforcement -> Context Shift -> Acquisition",
        mechanisms: ["Context"],
        teaches: "How relearning can occur rapidly when returning to a prior learning context.",
        builderNext: "Modify extinction depth and test how it changes reacquisition speed.",
        href: "/ui/presets/rapid_reacquisition.html",
      }),
      preset({
        name: "Occasion Setting",
        description: "Phases: Acquisition (S+X) -> Nonreinforcement (X) -> Probe.",
        phaseSummary: "Acquisition -> Nonreinforcement -> Probe",
        mechanisms: ["Context"],
        teaches: "How one cue can modulate meaning of another cue across phase structure.",
        builderNext: "Adjust salience on setting vs target cue and inspect probe separation.",
        href: "/ui/presets/occasion_setting.html",
      }),
      preset({
        name: "Blocking",
        description: "Phases: Acquisition (A+) -> Compound Acquisition (AX+).",
        phaseSummary: "Acquisition -> Compound Acquisition",
        mechanisms: ["Salience"],
        teaches: "How prior learning on one cue can limit learning to a new added cue.",
        builderNext: "Change initial acquisition length to see blocking strength differences.",
        href: "/ui/presets/blocking.html",
      }),
    ]
  },
  {
    title: "Operant Agent - Procedures",
    note: "Action-based learning and choice.",
    items: [
      preset({
        name: "Operant Conditioning",
        description: "Phase: Operant Acquisition (operant schedule).",
        phaseSummary: "Operant Acquisition",
        teaches: "How action values rise under reinforcement schedules.",
        builderNext: "Modify schedule parameters and compare action value trajectories.",
        href: "/ui/presets/operant_conditioning.html",
      }),
      preset({
        name: "Matching Law",
        description: "Protocol: Concurrent schedules (left/right) with operant choice.",
        phaseSummary: "Matching Law",
        teaches: "How action selection matches relative reinforcement rates across options.",
        builderNext: "Change left/right schedule ratios and inspect choice allocation shifts.",
        href: "/ui/presets/matching_law.html",
      }),
    ]
  }
];

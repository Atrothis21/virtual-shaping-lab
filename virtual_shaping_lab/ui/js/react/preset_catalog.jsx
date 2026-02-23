window.VSLReact = window.VSLReact || {};

window.VSLReact.presetSections = [
  {
    title: "Classical Agent - Single-Phase Procedures",
    note: "Pavlovian phases for isolated behavior.",
    items: [
      { name: "Acquisition", description: "Phase: Acquisition.", phaseSummary: "Acquisition", mechanisms: [], href: "/ui/presets/acquisition.html" },
      { name: "Compound Acquisition", description: "Phase: Compound Acquisition (CS1 and CS2).", phaseSummary: "Compound Acquisition", mechanisms: ["Salience"], href: "/ui/presets/compound_acquisition.html" },
      { name: "Differential Acquisition", description: "Phase: Differential Acquisition (CS+ vs CS-).", phaseSummary: "Differential Acquisition", mechanisms: ["Similarity"], href: "/ui/presets/differential_acquisition.html" }
    ]
  },
  {
    title: "Classical Agent - Multi-Phase Phenomena",
    note: "Canonical multi-phase behavioral effects.",
    items: [
      { name: "Extinction", description: "Phases: Acquisition -> Nonreinforcement.", phaseSummary: "Acquisition -> Nonreinforcement", mechanisms: [], href: "/ui/presets/extinction.html" },
      { name: "Overshadowing", description: "Phases: Acquisition (CS1) -> Compound Acquisition (CS1+CS2).", phaseSummary: "Acquisition -> Compound Acquisition", mechanisms: ["Attention", "Salience"], href: "/ui/presets/overshadowing.html" },
      { name: "Overexpectation", description: "Phases: Acquisition (A+, B+) -> Compound Acquisition (AB+).", phaseSummary: "Acquisition -> Compound Acquisition", mechanisms: ["Salience"], href: "/ui/presets/overexpectation.html" },
      { name: "Conditioned Inhibition", description: "Phases: Acquisition -> Compound Nonreinforcement -> Probe.", phaseSummary: "Acquisition -> Compound Nonreinforcement -> Probe", mechanisms: ["Salience"], href: "/ui/presets/conditioned_inhibition.html" },
      { name: "ABA Renewal", description: "Phases: Acquisition (A) -> Context Shift (B) -> Nonreinforcement -> Context Shift (A) -> Probe.", phaseSummary: "Acquisition -> Context Shift -> Nonreinforcement -> Context Shift -> Probe", mechanisms: ["Context"], href: "/ui/presets/aba_renewal.html" },
      { name: "ABC Renewal", description: "Phases: Acquisition (A) -> Context Shift (B) -> Nonreinforcement -> Context Shift (C) -> Probe.", phaseSummary: "Acquisition -> Context Shift -> Nonreinforcement -> Context Shift -> Probe", mechanisms: ["Context"], href: "/ui/presets/abc_renewal.html" },
      { name: "AAB Renewal", description: "Phases: Acquisition (A) -> Nonreinforcement (A) -> Context Shift (B) -> Probe.", phaseSummary: "Acquisition -> Nonreinforcement -> Context Shift -> Probe", mechanisms: ["Context"], href: "/ui/presets/aab_renewal.html" },
      { name: "Rapid Reacquisition", description: "Phases: Acquisition (A) -> Context Shift (B) -> Nonreinforcement -> Context Shift (A) -> Acquisition.", phaseSummary: "Acquisition -> Context Shift -> Nonreinforcement -> Context Shift -> Acquisition", mechanisms: ["Context"], href: "/ui/presets/rapid_reacquisition.html" },
      { name: "Occasion Setting", description: "Phases: Acquisition (S+X) -> Nonreinforcement (X) -> Probe.", phaseSummary: "Acquisition -> Nonreinforcement -> Probe", mechanisms: ["Context"], href: "/ui/presets/occasion_setting.html" },
      { name: "Blocking", description: "Phases: Acquisition (A+) -> Compound Acquisition (AX+).", phaseSummary: "Acquisition -> Compound Acquisition", mechanisms: ["Salience"], href: "/ui/presets/blocking.html" }
    ]
  },
  {
    title: "Operant Agent - Procedures",
    note: "Action-based learning and choice.",
    items: [
      { name: "Operant Conditioning", description: "Phase: Operant Acquisition (operant schedule).", phaseSummary: "Operant Acquisition", mechanisms: [], href: "/ui/presets/operant_conditioning.html" },
      { name: "Matching Law", description: "Protocol: Concurrent schedules (left/right) with operant choice.", phaseSummary: "Matching Law", mechanisms: [], href: "/ui/presets/matching_law.html" }
    ]
  }
];

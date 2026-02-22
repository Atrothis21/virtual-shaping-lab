window.VSLReact = window.VSLReact || {};

window.VSLReact.presetSections = [
  {
    title: "Classical Agent - Single-Phase Procedures",
    note: "Pavlovian phases for isolated behavior.",
    items: [
      { name: "Acquisition", description: "Phase: Acquisition.", href: "/ui/presets/acquisition.html" },
      { name: "Compound Acquisition", description: "Phase: Compound Acquisition (CS1 and CS2).", href: "/ui/presets/compound_acquisition.html" },
      { name: "Differential Acquisition", description: "Phase: Differential Acquisition (CS+ vs CS-).", href: "/ui/presets/differential_acquisition.html" }
    ]
  },
  {
    title: "Classical Agent - Multi-Phase Phenomena",
    note: "Canonical multi-phase behavioral effects.",
    items: [
      { name: "Extinction", description: "Phases: Acquisition -> Nonreinforcement.", href: "/ui/presets/extinction.html" },
      { name: "Overshadowing", description: "Phases: Acquisition (CS1) -> Compound Acquisition (CS1+CS2).", href: "/ui/presets/overshadowing.html" },
      { name: "Overexpectation", description: "Phases: Acquisition (A+, B+) -> Compound Acquisition (AB+).", href: "/ui/presets/overexpectation.html" },
      { name: "Conditioned Inhibition", description: "Phases: Acquisition -> Compound Nonreinforcement -> Probe.", href: "/ui/presets/conditioned_inhibition.html" },
      { name: "ABA Renewal", description: "Phases: Acquisition (A) -> Context Shift (B) -> Nonreinforcement -> Context Shift (A) -> Probe.", href: "/ui/presets/aba_renewal.html" },
      { name: "ABC Renewal", description: "Phases: Acquisition (A) -> Context Shift (B) -> Nonreinforcement -> Context Shift (C) -> Probe.", href: "/ui/presets/abc_renewal.html" },
      { name: "AAB Renewal", description: "Phases: Acquisition (A) -> Nonreinforcement (A) -> Context Shift (B) -> Probe.", href: "/ui/presets/aab_renewal.html" },
      { name: "Rapid Reacquisition", description: "Phases: Acquisition (A) -> Context Shift (B) -> Nonreinforcement -> Context Shift (A) -> Acquisition.", href: "/ui/presets/rapid_reacquisition.html" },
      { name: "Occasion Setting", description: "Phases: Acquisition (S+X) -> Nonreinforcement (X) -> Probe.", href: "/ui/presets/occasion_setting.html" },
      { name: "Blocking", description: "Phases: Acquisition (A+) -> Compound Acquisition (AX+).", href: "/ui/presets/blocking.html" }
    ]
  },
  {
    title: "Operant Agent - Procedures",
    note: "Action-based learning and choice.",
    items: [
      { name: "Operant Conditioning", description: "Phase: Operant Acquisition (operant schedule).", href: "/ui/presets/operant_conditioning.html" },
      { name: "Matching Law", description: "Protocol: Concurrent schedules (left/right) with operant choice.", href: "/ui/presets/matching_law.html" }
    ]
  }
];

function initStimuliControls() {
  if (typeof cs_plus !== "undefined" && cs_plus) {
    cs_plus.onchange = () => {
      phase().stimuli.cs_plus = Array.from(cs_plus.selectedOptions).map(o => o.value);
      if (phase().protocol === "nonreinforcement") syncNonreinforcementTargets();
      renderPayload();
    };
  }

  if (typeof cs_minus !== "undefined" && cs_minus) {
    cs_minus.onchange = () => {
      if (!phase().stimuli.cs_minus) phase().stimuli.cs_minus = [];
      phase().stimuli.cs_minus = Array.from(cs_minus.selectedOptions).map(o => o.value);
      renderPayload();
    };
  }

  const c1 = document.getElementById("compound_1");
  const c2 = document.getElementById("compound_2");

  if (c1) {
    c1.onchange = e => {
      const s1 = e.target.value;
      const s2 = c2 ? c2.value : null;
      phase().stimuli.compound = [s1, s2].filter(Boolean);
      renderPayload();
    };
  }

  if (c2) {
    c2.onchange = e => {
      const s2 = e.target.value;
      const s1 = c1 ? c1.value : null;
      phase().stimuli.compound = [s1, s2].filter(Boolean);
      renderPayload();
    };
  }
}

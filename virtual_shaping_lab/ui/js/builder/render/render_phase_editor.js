function renderTrialControls(p, schema) {
  const trialsBlock = document.getElementById("trials-block");
  const trialsLabel = document.getElementById("trials-label");
  const trialsInput = document.getElementById("trials");
  const trialsValue = document.getElementById("trials-value");

  if (!trialsBlock || !trialsLabel || !trialsInput || !trialsValue) return;

  const key = schemaTrialKey(schema);
  if (!key) {
    trialsBlock.classList.add("hidden");
    return;
  }

  trialsBlock.classList.remove("hidden");
  trialsLabel.textContent = key;

  const bounds = schemaNumberBounds(schema, key, 1, 200);
  trialsInput.min = bounds.min;
  trialsInput.max = bounds.max;

  const current = p.params && p.params[key] != null ? p.params[key] : bounds.min;
  trialsInput.value = current;
  trialsValue.textContent = trialsInput.value;

  trialsInput.oninput = () => {
    p.params[key] = +trialsInput.value;
    trialsValue.textContent = trialsInput.value;
    renderPayload();
  };
}

function renderAdvancedParams(p, schema) {
  const advancedContainer = document.getElementById("advanced-params");
  advancedContainer.innerHTML = "";

  if (!schemaHasParam(schema, "outcome")) {
    return;
  }

  const row = document.createElement("div");
  row.className = "form-row";

  const label = document.createElement("label");
  label.textContent = "Outcome";
  row.appendChild(label);

  const input = document.createElement("input");
  input.type = "range";

  const bounds = schemaNumberBounds(schema, "outcome", 0, 2);
  input.min = bounds.min;
  input.max = bounds.max;
  input.step = 0.05;
  input.value = p.params.outcome ?? 1.0;

  const value = document.createElement("span");
  value.textContent = input.value;

  input.oninput = () => {
    p.params.outcome = +input.value;
    value.textContent = input.value;
    renderPayload();
  };

  row.appendChild(input);
  row.appendChild(value);
  advancedContainer.appendChild(row);
}

function renderSalienceControls(p) {
  const salienceContainer = document.getElementById("salience-controls");
  salienceContainer.innerHTML = "";

  const currentStimuli = [];
  if (p.stimuli?.cs_plus) currentStimuli.push(...p.stimuli.cs_plus);
  if (p.stimuli?.cs_minus) currentStimuli.push(...p.stimuli.cs_minus);
  if (p.stimuli?.compound) currentStimuli.push(...p.stimuli.compound);

  const uniqueStimuli = Array.from(new Set(currentStimuli));

  uniqueStimuli.forEach(stim => {
    const row = document.createElement("div");
    row.className = "form-row";

    const label = document.createElement("label");
    label.textContent = `${stim} salience`;
    row.appendChild(label);

    const input = document.createElement("input");
    input.type = "range";
    input.min = 0;
    input.max = 1;
    input.step = 0.05;

    const currentVal = payload.experiment.salience?.[stim]?.salience ?? 0.2;
    input.value = currentVal;

    const value = document.createElement("span");
    value.textContent = input.value;

    input.oninput = () => {
      if (!payload.experiment.salience) payload.experiment.salience = {};
      payload.experiment.salience[stim] = { salience: +input.value };
      value.textContent = input.value;
      renderPayload();
    };

    row.appendChild(input);
    row.appendChild(value);
    salienceContainer.appendChild(row);
  });
}

function renderAttentionControls(p) {
  const attentionContainer = document.getElementById("attention-controls");
  attentionContainer.innerHTML = "";

  const currentStimuli = [];
  if (p.stimuli?.cs_plus) currentStimuli.push(...p.stimuli.cs_plus);
  if (p.stimuli?.cs_minus) currentStimuli.push(...p.stimuli.cs_minus);
  if (p.stimuli?.compound) currentStimuli.push(...p.stimuli.compound);

  const uniqueStimuli = Array.from(new Set(currentStimuli));

  uniqueStimuli.forEach(stim => {
    const row = document.createElement("div");
    row.className = "form-row";

    const label = document.createElement("label");
    label.textContent = `${stim} attention`;
    row.appendChild(label);

    const input = document.createElement("input");
    input.type = "range";
    input.min = 0;
    input.max = 1;
    input.step = 0.05;

    const currentVal = payload.experiment.attention?.[stim]?.attention ?? 1.0;
    input.value = currentVal;

    const value = document.createElement("span");
    value.textContent = input.value;

    input.oninput = () => {
      if (!payload.experiment.attention) payload.experiment.attention = {};
      payload.experiment.attention[stim] = { attention: +input.value };
      value.textContent = input.value;
      renderPayload();
    };

    row.appendChild(input);
    row.appendChild(value);
    attentionContainer.appendChild(row);
  });
}

function renderPhaseEditor() {
  const title = document.getElementById("phase-title");
  if (!title) {
    return;
  }

  const p = phase();
  const schema = ensurePhaseSchema(p.protocol);
  if (!schema) {
    return;
  }

  title.textContent = p.name || `Phase ${activePhaseIndex + 1}`;

  if (typeof protocol !== "undefined" && protocol) {
    protocol.value = p.protocol;
  }

  renderTrialControls(p, schema);

  const alphaBlock = document.getElementById("alpha-block");
  const gammaBlock = document.getElementById("gamma-block");
  const alphaCs1Block = document.getElementById("alpha-cs1-block");
  const alphaCs2Block = document.getElementById("alpha-cs2-block");
  if (alphaBlock) {
    alphaBlock.classList.toggle("hidden", !schemaHasParam(schema, "alpha"));
  }
  if (gammaBlock) {
    gammaBlock.classList.toggle("hidden", !schemaHasParam(schema, "gamma"));
  }
  if (alphaCs1Block) {
    alphaCs1Block.classList.toggle("hidden", !schemaHasParam(schema, "alpha_cs1"));
  }
  if (alphaCs2Block) {
    alphaCs2Block.classList.toggle("hidden", !schemaHasParam(schema, "alpha_cs2"));
  }

  if (schemaHasParam(schema, "alpha")) {
    if (typeof alpha !== "undefined" && alpha) {
      alpha.value = p.params.alpha ?? 0.2;
    }
    if (typeof alpha_value !== "undefined" && alpha_value) {
      alpha_value.textContent = alpha.value;
    }
  }
  if (schemaHasParam(schema, "alpha_cs1")) {
    if (typeof alpha_cs1 !== "undefined" && alpha_cs1) {
      alpha_cs1.value = p.params.alpha_cs1 ?? 0.2;
    }
    if (typeof alpha_cs1_value !== "undefined" && alpha_cs1_value) {
      alpha_cs1_value.textContent = alpha_cs1.value;
    }
  }
  if (schemaHasParam(schema, "alpha_cs2")) {
    if (typeof alpha_cs2 !== "undefined" && alpha_cs2) {
      alpha_cs2.value = p.params.alpha_cs2 ?? 0.12;
    }
    if (typeof alpha_cs2_value !== "undefined" && alpha_cs2_value) {
      alpha_cs2_value.textContent = alpha_cs2.value;
    }
  }
  if (schemaHasParam(schema, "gamma")) {
    if (typeof gamma !== "undefined" && gamma) {
      gamma.value = p.params.gamma ?? 0.0;
    }
    if (typeof gamma_value !== "undefined" && gamma_value) {
      gamma_value.textContent = gamma.value;
    }
  }

  const stimuliPanel = document.getElementById("stimuli-panel");
  const csBlock = document.getElementById("cs-block");
  const compoundBlock = document.getElementById("compound-block");

  const stimType = schemaStimuliType(schema);
  if (stimType === "none") {
    if (stimuliPanel) stimuliPanel.classList.add("hidden");
  } else {
    if (stimuliPanel) stimuliPanel.classList.remove("hidden");
  }

  if (csBlock) {
    csBlock.classList.toggle("hidden", stimType !== "cs");
  }
  if (compoundBlock) {
    compoundBlock.classList.toggle("hidden", stimType !== "compound");
  }

  if (stimType === "cs") {
    if (typeof cs_plus !== "undefined" && cs_plus) {
      populateStimuli(cs_plus, p.stimuli.cs_plus || []);
    }
    const hasCsMinus = Object.prototype.hasOwnProperty.call(
      schemaStimuliProps(schema),
      "cs_minus"
    );
    if (hasCsMinus) {
      if (typeof cs_minus !== "undefined" && cs_minus) {
        populateStimuli(cs_minus, p.stimuli.cs_minus || []);
      }
    }
  }

  const hasCsMinus = Object.prototype.hasOwnProperty.call(
    schemaStimuliProps(schema),
    "cs_minus"
  );
  const csMinusRow = typeof cs_minus !== "undefined" && cs_minus
    ? cs_minus.closest(".form-row")
    : null;
  const csMinusLabel = document.getElementById("cs_minus_label");

  if (csMinusRow) {
    if (hasCsMinus && (p.protocol === "differential_acquisition" || (p.stimuli.cs_minus || []).length)) {
      csMinusRow.classList.remove("hidden");
    } else {
      csMinusRow.classList.add("hidden");
    }
  } else {
    if (csMinusLabel) {
      csMinusLabel.classList.toggle("hidden", !hasCsMinus);
    }
    if (typeof cs_minus !== "undefined" && cs_minus) {
      cs_minus.classList.toggle("hidden", !hasCsMinus);
    }
  }

  if (stimType === "compound") {
    const s1 = document.getElementById("compound_1");
    const s2 = document.getElementById("compound_2");
    if (!s1 || !s2) {
      return;
    }
    s1.innerHTML = "";
    s2.innerHTML = "";

    STIMULI.forEach(s => {
      const o1 = document.createElement("option");
      o1.value = s;
      o1.textContent = s;
      s1.appendChild(o1);

      const o2 = document.createElement("option");
      o2.value = s;
      o2.textContent = s;
      s2.appendChild(o2);
    });

    const compound = p.stimuli.compound || [STIMULI[0], STIMULI[1]];
    s1.value = compound[0];
    s2.value = compound[1];
  }

  const contextPanel = document.getElementById("context-panel");
  const showContext = p.protocol === "probe" || p.protocol === "context_shift";
  if (contextPanel) {
    contextPanel.classList.toggle("hidden", !showContext);
  }

  if (showContext) {
    if (typeof context !== "undefined" && context) {
      context.value = p.params.context || "A";
    }
  }

  const adv = document.getElementById("advanced-toggle");
  const advancedPanel = document.getElementById("advanced-panel");
  const saliencePanel = document.getElementById("salience-panel");
  const attentionPanel = document.getElementById("attention-panel");

  const showAdvanced = !!(adv && adv.checked);

  if (advancedPanel) {
    advancedPanel.classList.toggle("hidden", !showAdvanced);
  }
  if (saliencePanel) {
    saliencePanel.classList.toggle("hidden", !showAdvanced);
  }
  if (attentionPanel) {
    attentionPanel.classList.toggle("hidden", !showAdvanced);
  }

  if (showAdvanced) {
    renderAdvancedParams(p, schema);
    renderSalienceControls(p);
    renderAttentionControls(p);
  }

  renderPayload();
}

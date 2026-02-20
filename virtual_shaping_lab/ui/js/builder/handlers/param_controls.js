function initParamControls() {
  const contextInferenceToggle = document.getElementById("context_inference_toggle");
  const contextInferenceMax = document.getElementById("context_inference_max");
  const similarityToggle = document.getElementById("similarity_toggle");
  const similarityOffdiag = document.getElementById("similarity_offdiag");
  const similarityOffdiagValue = document.getElementById("similarity_offdiag_value");
  const similarityApply = document.getElementById("similarity_apply");
  const similarityReset = document.getElementById("similarity_reset");
  const similarityGrid = document.getElementById("similarity_grid");
  const similarityPreview = document.getElementById("similarity_preview");

  if (contextInferenceToggle) {
    if (!payload.experiment.context_inference) {
      payload.experiment.context_inference = { enabled: false, max_contexts: 3 };
    }
    contextInferenceToggle.checked = !!payload.experiment.context_inference.enabled;

    if (contextInferenceMax) {
      const currentMax = payload.experiment.context_inference.max_contexts ?? 3;
      contextInferenceMax.value = String(currentMax);
    }

    contextInferenceToggle.onchange = () => {
      payload.experiment.context_inference.enabled = contextInferenceToggle.checked;
      renderPayload();
    };

    if (contextInferenceMax) {
      contextInferenceMax.onchange = () => {
        payload.experiment.context_inference.max_contexts = +contextInferenceMax.value;
        renderPayload();
      };
    }
  }

  function buildDefaultSimilarity(stimuli, offdiag) {
    const values = stimuli.map((_, i) =>
      stimuli.map((__, j) => (i === j ? 1.0 : offdiag))
    );
    return {
      type: "matrix",
      stimuli: [...stimuli],
      values,
    };
  }

  function updateSimilarityPreview(similarity) {
    if (!similarityPreview) return;
    if (!similarity) {
      similarityPreview.textContent = "";
      return;
    }
    similarityPreview.textContent = JSON.stringify(similarity, null, 2);
  }

  function renderSimilarityGrid(similarity) {
    if (!similarityGrid) return;
    similarityGrid.innerHTML = "";
    if (!similarity) return;

    const stimuli = similarity.stimuli || [];
    const values = similarity.values || [];
    if (!stimuli.length || !values.length) return;

    const table = document.createElement("table");
    table.style.borderCollapse = "collapse";

    const headerRow = document.createElement("tr");
    headerRow.appendChild(document.createElement("th"));
    stimuli.forEach(label => {
      const th = document.createElement("th");
      th.textContent = label;
      th.style.padding = "4px 6px";
      headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    stimuli.forEach((rowLabel, i) => {
      const row = document.createElement("tr");
      const th = document.createElement("th");
      th.textContent = rowLabel;
      th.style.padding = "4px 6px";
      row.appendChild(th);

      stimuli.forEach((colLabel, j) => {
        const cell = document.createElement("td");
        cell.style.padding = "2px 4px";
        const input = document.createElement("input");
        input.type = "number";
        input.min = 0;
        input.max = 1;
        input.step = 0.05;
        input.value = values[i]?.[j] ?? (i === j ? 1.0 : 0.0);
        input.style.width = "60px";
        if (i === j) {
          input.disabled = true;
        }

        input.onchange = () => {
          const val = Math.max(0, Math.min(1, parseFloat(input.value) || 0));
          similarity.values[i][j] = val;
          similarity.values[j][i] = val;
          updateSimilarityPreview(similarity);
          renderPayload();
        };

        cell.appendChild(input);
        row.appendChild(cell);
      });

      table.appendChild(row);
    });

    similarityGrid.appendChild(table);
  }

  function applySimilarity(offdiag) {
    const stimuli = payload?.experiment?.representation?.params?.stimuli || [];
    if (!stimuli.length) {
      debugLog("similarity missing stimuli");
      return;
    }
    const similarity = buildDefaultSimilarity(stimuli, offdiag);
    if (!payload.experiment.representation.params) {
      payload.experiment.representation.params = {};
    }
    payload.experiment.representation.params.similarity = similarity;
    updateSimilarityPreview(similarity);
    renderSimilarityGrid(similarity);
    renderPayload();
  }

  if (similarityToggle) {
    const existing = payload?.experiment?.representation?.params?.similarity;
    similarityToggle.checked = !!existing;
    updateSimilarityPreview(existing || null);
    renderSimilarityGrid(existing || null);
  }

  if (similarityOffdiag && similarityOffdiagValue) {
    similarityOffdiagValue.textContent = similarityOffdiag.value;
    similarityOffdiag.oninput = () => {
      similarityOffdiagValue.textContent = similarityOffdiag.value;
      if (similarityToggle && similarityToggle.checked) {
        applySimilarity(+similarityOffdiag.value);
      }
    };
  }

  if (similarityApply) {
    similarityApply.onclick = () => {
      if (similarityToggle) {
        similarityToggle.checked = true;
      }
      applySimilarity(+similarityOffdiag.value);
    };
  }

  if (similarityReset) {
    similarityReset.onclick = () => {
      if (similarityToggle) {
        similarityToggle.checked = true;
      }
      applySimilarity(0.0);
    };
  }

  if (similarityToggle) {
    similarityToggle.onchange = () => {
      if (!similarityToggle.checked) {
        if (payload.experiment?.representation?.params) {
          delete payload.experiment.representation.params.similarity;
        }
        updateSimilarityPreview(null);
        renderSimilarityGrid(null);
        renderPayload();
        return;
      }
      applySimilarity(+similarityOffdiag.value);
    };
  }

  if (typeof alpha !== "undefined" && alpha) {
    alpha.oninput = () => {
      phase().params.alpha = +alpha.value;
      if (typeof alpha_value !== "undefined" && alpha_value) {
        alpha_value.textContent = alpha.value;
      }
      renderPayload();
    };
  }

  if (typeof gamma !== "undefined" && gamma) {
    gamma.oninput = () => {
      phase().params.gamma = +gamma.value;
      if (typeof gamma_value !== "undefined" && gamma_value) {
        gamma_value.textContent = gamma.value;
      }
      renderPayload();
    };
  }

  if (typeof alpha_cs1 !== "undefined" && alpha_cs1) {
    alpha_cs1.oninput = () => {
      phase().params.alpha_cs1 = +alpha_cs1.value;
      if (typeof alpha_cs1_value !== "undefined" && alpha_cs1_value) {
        alpha_cs1_value.textContent = alpha_cs1.value;
      }
      renderPayload();
    };
  }

  if (typeof alpha_cs2 !== "undefined" && alpha_cs2) {
    alpha_cs2.oninput = () => {
      phase().params.alpha_cs2 = +alpha_cs2.value;
      if (typeof alpha_cs2_value !== "undefined" && alpha_cs2_value) {
        alpha_cs2_value.textContent = alpha_cs2.value;
      }
      renderPayload();
    };
  }

  if (typeof context !== "undefined" && context) {
    context.oninput = () => {
      phase().params.context = context.value;
      renderPayload();
    };
  }
}

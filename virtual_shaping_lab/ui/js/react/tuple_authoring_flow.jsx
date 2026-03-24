window.VSLReact = window.VSLReact || {};

window.VSLReact.tupleAuthoring = window.VSLReact.tupleAuthoring || (() => {
  const STEP_ORDER = Object.freeze(["arrangement", "task", "agent"]);
  const EXPECTED_OUTCOME_STATUSES = Object.freeze([
    "success",
    "partial",
    "structurally_invalid",
    "behaviorally_unsupported",
    "novel",
  ]);
  const DETAIL_COMPATIBILITY_STATES = Object.freeze([
    "success",
    "partial",
    "behaviorally_unsupported",
    "novel",
  ]);
  const DETAIL_ENTRY_MODES = Object.freeze([
    "smart_preset_prefill",
    "manual_tuple_explore",
  ]);
  const VISIBILITY_POLICY = Object.freeze({
    hide_structurally_impossible_agents: true,
    show_disabled_behaviorally_invalid_agents: true,
  });

  // Contract marker: selectable universes are registry/API generated, not hand-authored in UI.
  const SELECTABLE_UNIVERSE_SOURCE = "registry_generated";

  function _normalizeId(value) {
    return String(value || "").trim().toLowerCase();
  }

  function _clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function _isObject(value) {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
  }

  async function fetchTupleCatalog({ arrangement = null, task = null } = {}) {
    const params = new URLSearchParams();
    if (arrangement) params.set("arrangement", arrangement);
    if (task) params.set("task", task);
    const suffix = params.toString() ? `?${params.toString()}` : "";
    const response = await fetch(`/catalog/tuple-authoring${suffix}`);
    if (!response.ok) {
      throw new Error(`Tuple catalog request failed: ${response.status}`);
    }
    return response.json();
  }

  async function fetchTupleCompatibility({ arrangement, task, agent, edits = {} } = {}) {
    const response = await fetch("/catalog/tuple-authoring/compatibility", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        arrangement,
        task,
        agent,
        edits: edits && typeof edits === "object" ? edits : {},
      }),
    });
    if (!response.ok) {
      throw new Error(`Tuple compatibility request failed: ${response.status}`);
    }
    return response.json();
  }

  async function fetchSmartPresetCatalog() {
    const response = await fetch("/catalog/smart-presets");
    if (!response.ok) {
      throw new Error(`Smart preset catalog request failed: ${response.status}`);
    }
    return response.json();
  }

  async function projectSmartPreset({ smartPresetId, edits = {} } = {}) {
    const response = await fetch(`/catalog/smart-presets/${encodeURIComponent(String(smartPresetId || ""))}/project`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        edits: edits && typeof edits === "object" ? edits : {},
      }),
    });
    if (!response.ok) {
      throw new Error(`Smart preset projection request failed: ${response.status}`);
    }
    return response.json();
  }

  function canRunForExpectedOutcome(compatibility) {
    const status = _normalizeId(compatibility && compatibility.status);
    return status !== "structurally_invalid";
  }

  function canRunForDetailFlow({ compatibility, compositionError } = {}) {
    if (_isObject(compositionError)) {
      return false;
    }
    const status = _normalizeId(compatibility && compatibility.status);
    return DETAIL_COMPATIBILITY_STATES.includes(status);
  }

  function _guidanceForStatus(status) {
    if (status === "structurally_invalid") {
      return "Run is disabled because the selected tuple is structurally invalid.";
    }
    if (status === "behaviorally_unsupported") {
      return "This tuple is unlikely to reproduce the standard effect, but may still yield interpretable behavior.";
    }
    if (status === "partial") {
      return "Partial support: run is allowed, but expected signatures may be incomplete.";
    }
    if (status === "novel") {
      return "Novel prediction: run is allowed with explicit rationale attribution.";
    }
    return "Supported behavior: run is allowed.";
  }

  function deriveExpectedOutcomePanelModel(compatibility) {
    const payload = compatibility && typeof compatibility === "object" ? compatibility : {};
    const status = _normalizeId(payload.status);
    const statusNormalized = EXPECTED_OUTCOME_STATUSES.includes(status)
      ? status
      : "behaviorally_unsupported";
    const source = _normalizeId(payload.source || "unknown");
    const sourceAllowed = source === "behavioral_registry"
      || source === "behavioral_registry_fallback"
      || source === "legality_engine";
    const keyFactors = Array.isArray(payload.key_operator_factors)
      ? payload.key_operator_factors.filter((item) => item && typeof item === "object")
      : [];
    return {
      status: statusNormalized,
      badge_label: statusNormalized,
      explanation: String(payload.explanation || ""),
      can_run: canRunForExpectedOutcome({ status: statusNormalized }),
      guidance: _guidanceForStatus(statusNormalized),
      unmet_behavioral_requirements: Array.isArray(payload.unmet_behavioral_requirements)
        ? payload.unmet_behavioral_requirements
        : [],
      key_operator_factors: keyFactors,
      explanation_source: sourceAllowed ? source : "unknown",
      source_integrity_ok: sourceAllowed,
    };
  }

  function deriveCompositionErrorPanelModel(error) {
    const payload = _isObject(error) ? error : {};
    const code = _normalizeId(payload.code || "composition_error");
    const message = String(payload.message || "Selected tuple cannot be composed.").trim();
    return {
      type: "composition_error",
      code,
      message,
      can_run: false,
    };
  }

  function deriveReadableProvenanceFactors(panelModel) {
    const factors = Array.isArray(panelModel?.key_operator_factors)
      ? panelModel.key_operator_factors
      : [];
    return factors.map((factor) => {
      const kind = _normalizeId(factor?.kind);
      if (kind === "required_operators") {
        const value = Array.isArray(factor?.value) ? factor.value.join(", ") : "";
        return `Required operator slots shape this behavior: ${value}`;
      }
      if (kind === "task_implementation_id") {
        return `Task implementation drives protocol behavior: ${String(factor?.value || "")}`;
      }
      if (kind === "forbidden_slots") {
        const value = Array.isArray(factor?.value) ? factor.value.join(", ") : "";
        return `Arrangement constraints forbid slots: ${value}`;
      }
      return `Operator factor: ${JSON.stringify(factor || {})}`;
    });
  }

  function deriveTupleSelectionState(input = {}) {
    return {
      arrangement: _normalizeId(input.arrangement) || null,
      task: _normalizeId(input.task) || null,
      agent: _normalizeId(input.agent) || null,
      edits: _isObject(input.edits) ? _clone(input.edits) : {},
    };
  }

  function deriveDetailFlowStateFromSmartPresetProjection(projection = {}) {
    return {
      entry_mode: "smart_preset_prefill",
      tuple_selection_state: deriveTupleSelectionState(projection),
    };
  }

  function deriveDetailFlowStateFromManualTupleSelection(selection = {}) {
    return {
      entry_mode: "manual_tuple_explore",
      tuple_selection_state: deriveTupleSelectionState(selection),
    };
  }

  function deriveUnifiedDetailFlowModel({
    entryMode,
    selection,
    compatibility,
    compositionError,
  } = {}) {
    const mode = DETAIL_ENTRY_MODES.includes(_normalizeId(entryMode))
      ? _normalizeId(entryMode)
      : "manual_tuple_explore";
    const tupleSelection = deriveTupleSelectionState(selection || {});
    const expectedOutcomePanel = _isObject(compositionError)
      ? null
      : deriveExpectedOutcomePanelModel(compatibility || {});
    const compositionErrorPanel = _isObject(compositionError)
      ? deriveCompositionErrorPanelModel(compositionError)
      : null;
    const readableFactors = expectedOutcomePanel
      ? deriveReadableProvenanceFactors(expectedOutcomePanel)
      : [];
    return {
      entry_mode: mode,
      tuple_selection_state: tupleSelection,
      expected_outcome_panel: expectedOutcomePanel,
      composition_error_panel: compositionErrorPanel,
      readable_provenance_factors: readableFactors,
      can_run: canRunForDetailFlow({
        compatibility: compatibility || {},
        compositionError,
      }),
    };
  }

  function deriveTupleSelectionModel(catalog, selection = {}) {
    const payload = catalog && typeof catalog === "object" ? catalog : {};
    const selectedArrangement = _normalizeId(selection.arrangement);
    const selectedTask = _normalizeId(selection.task);

    const tasks = Array.isArray(payload.tasks) ? payload.tasks : [];
    const agents = Array.isArray(payload.agents) ? payload.agents : [];

    const taskOptions = tasks.map((task) => ({
      id: _normalizeId(task.id),
      enabled: Boolean(task.enabled),
      hidden: false,
      task_implementation_id: task.task_implementation_id || null,
      protocol_family: task.protocol_family || null,
    }));

    const agentOptions = [];
    for (const agent of agents) {
      const enabled = Boolean(agent.enabled);
      const structurallyCompatible = Array.isArray(agent.arrangement_compatibility)
        ? agent.arrangement_compatibility.map(_normalizeId).includes(selectedArrangement)
        : true;

      if (!enabled && !structurallyCompatible && VISIBILITY_POLICY.hide_structurally_impossible_agents) {
        continue;
      }
      agentOptions.push({
        id: _normalizeId(agent.id),
        enabled,
        hidden: false,
        disabled_reason: enabled ? null : String(agent.reason || "Unavailable for selected tuple."),
      });
    }

    const availableEdits = payload.available_edits && typeof payload.available_edits === "object"
      ? _clone(payload.available_edits)
      : {};

    return {
      contract_version: payload.contract_version || null,
      authoring_mode: payload.authoring_mode || null,
      selectable_universe_source: payload.registry_generated ? SELECTABLE_UNIVERSE_SOURCE : "unknown",
      step_order: STEP_ORDER,
      visibility_policy: VISIBILITY_POLICY,
      selection: {
        arrangement: selectedArrangement || null,
        task: selectedTask || null,
        agent: _normalizeId(selection.agent) || null,
      },
      options: {
        tasks: taskOptions,
        agents: agentOptions,
      },
      available_edits: availableEdits,
    };
  }

  return {
    STEP_ORDER,
    EXPECTED_OUTCOME_STATUSES,
    DETAIL_COMPATIBILITY_STATES,
    DETAIL_ENTRY_MODES,
    VISIBILITY_POLICY,
    SELECTABLE_UNIVERSE_SOURCE,
    fetchTupleCatalog,
    fetchTupleCompatibility,
    fetchSmartPresetCatalog,
    projectSmartPreset,
    canRunForExpectedOutcome,
    canRunForDetailFlow,
    deriveExpectedOutcomePanelModel,
    deriveCompositionErrorPanelModel,
    deriveReadableProvenanceFactors,
    deriveTupleSelectionState,
    deriveDetailFlowStateFromSmartPresetProjection,
    deriveDetailFlowStateFromManualTupleSelection,
    deriveUnifiedDetailFlowModel,
    deriveTupleSelectionModel,
  };
})();


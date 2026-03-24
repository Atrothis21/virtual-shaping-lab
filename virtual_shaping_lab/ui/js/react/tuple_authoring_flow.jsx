window.VSLReact = window.VSLReact || {};

window.VSLReact.tupleAuthoring = window.VSLReact.tupleAuthoring || (() => {
  const STEP_ORDER = Object.freeze(["arrangement", "task", "agent"]);
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
    VISIBILITY_POLICY,
    SELECTABLE_UNIVERSE_SOURCE,
    fetchTupleCatalog,
    deriveTupleSelectionModel,
  };
})();


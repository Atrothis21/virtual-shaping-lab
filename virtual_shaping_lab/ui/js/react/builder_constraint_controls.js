window.VSLReact = window.VSLReact || {};

const CONSTRAINT_ACTIONS = Object.freeze({
  HIDE: "hide",
  DISABLE: "disable",
  WARN: "warn",
  AUTO_CORRECT: "auto-correct",
  NONE: "none",
});

const NON_SEMANTIC_AUTOCORRECT_FIELDS = Object.freeze(["template_key"]);

function _normalizeProtocolKeys(protocolEntries) {
  if (!Array.isArray(protocolEntries)) return [];
  return protocolEntries
    .map((item) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object") return item.key || item.name || "";
      return "";
    })
    .map((value) => String(value || "").trim())
    .filter(Boolean);
}

function _normalizeTemplateByProtocol(reportTemplates) {
  if (!reportTemplates || typeof reportTemplates !== "object") return {};
  const out = {};
  Object.entries(reportTemplates).forEach(([protocolKey, value]) => {
    const key = String(protocolKey || "").trim();
    if (!key) return;
    if (typeof value === "string") {
      out[key] = value;
      return;
    }
    if (value && typeof value === "object") {
      if (typeof value.default_template === "string") {
        out[key] = value.default_template;
      } else if (typeof value.report_name === "string") {
        out[key] = value.report_name;
      }
    }
  });
  return out;
}

function deriveBuilderConstraintState(args) {
  const context = args && typeof args === "object" ? args : {};
  const catalogState = context.catalogState && typeof context.catalogState === "object" ? context.catalogState : {};
  const draft = context.draft && typeof context.draft === "object" ? context.draft : {};
  const extensions = catalogState.extensions && typeof catalogState.extensions === "object"
    ? catalogState.extensions
    : {};
  const availableProtocols = _normalizeProtocolKeys(extensions.protocols);
  const templateByProtocol = _normalizeTemplateByProtocol(extensions.report_templates);

  const protocolKey = String(draft.protocol_key || "").trim();
  const templateKey = String(draft.template_key || "").trim();
  const runModeHint = String(draft.run_mode_hint || "trial").trim().toLowerCase();

  const state = {
    protocol_key: { action: CONSTRAINT_ACTIONS.NONE, message: "" },
    template_key: { action: CONSTRAINT_ACTIONS.NONE, message: "" },
    run_mode_hint: { action: CONSTRAINT_ACTIONS.NONE, message: "" },
    advanced_debug: { action: CONSTRAINT_ACTIONS.NONE, message: "" },
  };

  if (availableProtocols.length && protocolKey && !availableProtocols.includes(protocolKey)) {
    state.protocol_key = {
      action: CONSTRAINT_ACTIONS.WARN,
      message: "Selected protocol is not present in current catalog metadata.",
    };
  }

  if (!protocolKey) {
    state.template_key = {
      action: CONSTRAINT_ACTIONS.DISABLE,
      message: "Select protocol_key before editing template_key.",
    };
  } else {
    const defaultTemplate = templateByProtocol[protocolKey];
    if (!templateKey && defaultTemplate) {
      state.template_key = {
        action: CONSTRAINT_ACTIONS.AUTO_CORRECT,
        correctedValue: defaultTemplate,
        message: "Applied catalog default template for selected protocol.",
      };
    } else if (templateKey && defaultTemplate && templateKey !== defaultTemplate) {
      state.template_key = {
        action: CONSTRAINT_ACTIONS.WARN,
        message: "template_key differs from catalog default template for this protocol.",
      };
    }
  }

  if (runModeHint === "tick") {
    state.run_mode_hint = {
      action: CONSTRAINT_ACTIONS.WARN,
      message: "tick mode may increase telemetry volume and render cost.",
    };
    state.advanced_debug = {
      action: CONSTRAINT_ACTIONS.HIDE,
      message: "Advanced/debug controls are hidden in tick mode by default.",
    };
  }

  return state;
}

function evaluateConstraintBehavior(rule, fieldKey) {
  const current = rule && typeof rule === "object" ? rule : { action: CONSTRAINT_ACTIONS.NONE };
  const key = String(fieldKey || "").trim();
  const canAutoCorrect = NON_SEMANTIC_AUTOCORRECT_FIELDS.includes(key);
  const autoCorrectBlocked = current.action === CONSTRAINT_ACTIONS.AUTO_CORRECT && !canAutoCorrect;
  return {
    hidden: current.action === CONSTRAINT_ACTIONS.HIDE,
    disabled: current.action === CONSTRAINT_ACTIONS.DISABLE,
    warning: current.action === CONSTRAINT_ACTIONS.WARN ? (current.message || "") : "",
    autoCorrect:
      current.action === CONSTRAINT_ACTIONS.AUTO_CORRECT && canAutoCorrect
        ? (current.correctedValue || "")
        : "",
    autoCorrectBlocked,
    message:
      autoCorrectBlocked
        ? "Semantic auto-correct blocked; explicit user update required."
        : (current.message || ""),
  };
}

window.VSLReact.builderConstraintControls = {
  CONSTRAINT_ACTIONS,
  NON_SEMANTIC_AUTOCORRECT_FIELDS,
  deriveBuilderConstraintState,
  evaluateConstraintBehavior,
};

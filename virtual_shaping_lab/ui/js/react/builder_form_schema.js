(function initBuilderFormSchema(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});

  const BUILDER_SECTION_SCHEMA = Object.freeze([
    {
      key: "protocol_seed",
      title: "Protocol/Seed Selection",
      index: "S2",
      className: "builder-section-protocol",
      subheading: "Protocol identity and seed context.",
      readouts: [{ label: "seed_source", key: "seed_source" }],
      fields: [
        { key: "preset_key", label: "preset_key", control: "text" },
        { key: "protocol_key", label: "protocol_key", control: "text", constraintKey: "protocol_key" },
      ],
      constraintFieldKey: "protocol_key",
    },
    {
      key: "phases",
      title: "Phases",
      index: "S3",
      className: "builder-section-phases",
      subheading: "Flow and signal-shaping controls.",
      readouts: [
        { label: "flow_preview", key: "flow_preview" },
        { label: "phase_count_hint", key: "phase_count_hint" },
      ],
      fields: [
        {
          key: "expected_signals",
          label: "expected_signals (comma separated)",
          control: "text",
          valueKey: "expected_signals_csv",
        },
      ],
    },
    {
      key: "runtime",
      title: "Runtime",
      index: "S4",
      className: "builder-section-runtime",
      subheading: "Execution mode and plan request state.",
      readouts: [{ label: "plan_request_status", key: "plan_request_status" }],
      fields: [
        {
          key: "run_mode_hint",
          label: "run_mode_hint",
          control: "select",
          options: [
            { value: "trial", label: "trial" },
            { value: "tick", label: "tick" },
          ],
          constraintKey: "run_mode_hint",
        },
      ],
      constraintFieldKey: "run_mode_hint",
    },
    {
      key: "report",
      title: "Report",
      index: "S5",
      className: "builder-section-report",
      subheading: "Template selection and resolve hash snapshot.",
      readouts: [{ label: "stable_hash", key: "stable_hash" }],
      fields: [
        { key: "template_key", label: "template_key", control: "text", constraintKey: "template_key" },
      ],
      constraintFieldKey: "template_key",
    },
  ]);

  const DEFAULT_BEHAVIOR = Object.freeze({
    hidden: false,
    disabled: false,
    warning: "",
    autoCorrect: "",
    autoCorrectBlocked: false,
    message: "",
  });

  function parseSignalCsv(rawValue) {
    return String(rawValue || "")
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  function getBuilderSectionSchema() {
    return BUILDER_SECTION_SCHEMA;
  }

  function buildBuilderSectionViewModels(context) {
    const seed = context && context.seed ? context.seed : {};
    const expectedSignals = context && Array.isArray(context.expectedSignals) ? context.expectedSignals : [];
    const flowPreview = context && context.flowPreview ? context.flowPreview : "n/a";
    const planRequestStatus = context && context.planRequestStatus ? context.planRequestStatus : "idle";
    const stableHash = context && context.stableHash ? context.stableHash : "n/a";
    const constraintBehaviorByField = context && context.constraintBehaviorByField ? context.constraintBehaviorByField : {};
    const readoutValues = {
      seed_source: seed.seed_source || "n/a",
      flow_preview: flowPreview,
      phase_count_hint: expectedSignals.length || 0,
      plan_request_status: planRequestStatus,
      stable_hash: stableHash,
    };

    return BUILDER_SECTION_SCHEMA.map((section) => {
      const fields = section.fields.map((field) => {
        const behavior =
          (field.constraintKey && constraintBehaviorByField[field.constraintKey]) ||
          constraintBehaviorByField[field.key] ||
          DEFAULT_BEHAVIOR;
        const valueKey = field.valueKey || field.key;
        const value =
          valueKey === "expected_signals_csv"
            ? expectedSignals.join(", ")
            : seed[field.key] == null
              ? ""
              : String(seed[field.key]);
        return {
          ...field,
          value,
          behavior,
        };
      });
      const constraint =
        (section.constraintFieldKey && constraintBehaviorByField[section.constraintFieldKey]) || DEFAULT_BEHAVIOR;
      return {
        ...section,
        fields,
        constraint,
        readouts: section.readouts.map((item) => ({ label: item.label, value: readoutValues[item.key] })),
      };
    });
  }

  function toDraftPatch(fieldKey, rawValue) {
    if (fieldKey === "expected_signals") {
      return { expected_signals: parseSignalCsv(rawValue) };
    }
    return { [fieldKey]: rawValue };
  }

  VSLReact.builderFormSchema = {
    getBuilderSectionSchema,
    buildBuilderSectionViewModels,
    toDraftPatch,
  };
})(typeof window !== "undefined" ? window : globalThis);

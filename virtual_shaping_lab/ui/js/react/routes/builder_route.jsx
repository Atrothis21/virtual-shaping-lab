(function initBuilderRoute(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});
  const routeContainers = (VSLReact.routeContainers = VSLReact.routeContainers || {});

  function summarizeResolvedPlan(resolvedPlan) {
    if (!resolvedPlan || typeof resolvedPlan !== "object") return { unitCount: 0, flow: "n/a", totalTrials: 0 };
    const units = Array.isArray(resolvedPlan.units) ? resolvedPlan.units : [];
    const flow = units.map((unit) => unit && (unit.protocol || unit.unit_key || unit.name || "unit")).join(" -> ");
    const totalTrials = units.reduce((acc, unit) => {
      const params = unit && unit.params && typeof unit.params === "object" ? unit.params : {};
      const nTrials = Number.isFinite(Number(params.n_trials)) ? Number(params.n_trials) : 0;
      return acc + nTrials;
    }, 0);
    return { unitCount: units.length, flow: flow || "n/a", totalTrials };
  }

  function BuilderRouteContainer({
    builderDraftState,
    planState,
    catalogState,
    debugAdvancedState,
    onResolvePlan,
    onDraftEdited,
    resolveErrorView,
  }) {
    const seed = builderDraftState && builderDraftState.draft ? builderDraftState.draft : null;
    const resolvedPlan = planState && planState.resolvedPlan ? planState.resolvedPlan : null;
    const stableHash = planState && planState.stableHash ? planState.stableHash : "";
    const summary = summarizeResolvedPlan(resolvedPlan);
    const expectedSignals = seed && Array.isArray(seed.expected_signals) ? seed.expected_signals : [];
    const flowPreview = expectedSignals.length ? expectedSignals.join(", ") : "n/a";
    const constraintApi = VSLReact.builderConstraintControls || {};
    const formSchemaApi = VSLReact.builderFormSchema || {};
    const deriveBuilderConstraintState = typeof constraintApi.deriveBuilderConstraintState === "function" ? constraintApi.deriveBuilderConstraintState : () => ({});
    const evaluateConstraintBehavior =
      typeof constraintApi.evaluateConstraintBehavior === "function"
        ? constraintApi.evaluateConstraintBehavior
        : () => ({ hidden: false, disabled: false, warning: "", autoCorrect: "", autoCorrectBlocked: false, message: "" });
    const constraints = React.useMemo(() => deriveBuilderConstraintState({ catalogState, draft: seed }), [catalogState, deriveBuilderConstraintState, seed]);
    const protocolConstraint = evaluateConstraintBehavior(constraints.protocol_key, "protocol_key");
    const templateConstraint = evaluateConstraintBehavior(constraints.template_key, "template_key");
    const runModeConstraint = evaluateConstraintBehavior(constraints.run_mode_hint, "run_mode_hint");
    const advancedConstraint = evaluateConstraintBehavior(constraints.advanced_debug, "advanced_debug");
    const [advancedVisible, setAdvancedVisible] = React.useState(false);
    const [debugDetailsVisible, setDebugDetailsVisible] = React.useState(false);
    const getBuilderSectionSchema = typeof formSchemaApi.getBuilderSectionSchema === "function" ? formSchemaApi.getBuilderSectionSchema : () => [];
    const buildBuilderSectionViewModels = typeof formSchemaApi.buildBuilderSectionViewModels === "function" ? formSchemaApi.buildBuilderSectionViewModels : () => [];
    const toDraftPatchBySchema = typeof formSchemaApi.toDraftPatch === "function" ? formSchemaApi.toDraftPatch : (fieldKey, rawValue) => ({ [fieldKey]: rawValue });
    const constraintBehaviorByField = React.useMemo(() => ({
      protocol_key: protocolConstraint,
      template_key: templateConstraint,
      run_mode_hint: runModeConstraint,
      advanced_debug: advancedConstraint,
    }), [advancedConstraint, protocolConstraint, runModeConstraint, templateConstraint]);
    const builderSectionSchema = React.useMemo(() => getBuilderSectionSchema(), [getBuilderSectionSchema]);
    const builderSectionViewModels = React.useMemo(
      () =>
        buildBuilderSectionViewModels({
          schema: builderSectionSchema,
          seed,
          expectedSignals,
          flowPreview,
          planRequestStatus: planState?.requestStatus || "idle",
          stableHash: stableHash || "n/a",
          constraintBehaviorByField,
        }),
      [buildBuilderSectionViewModels, builderSectionSchema, constraintBehaviorByField, expectedSignals, flowPreview, planState?.requestStatus, seed, stableHash]
    );
    const [autoCorrectNotice, setAutoCorrectNotice] = React.useState(null);
    const [templateAutoCorrectSuppressed, setTemplateAutoCorrectSuppressed] = React.useState(false);

    function updateDraftPatch(patch) {
      if (typeof onDraftEdited !== "function") return;
      const nextDraft = { ...(seed && typeof seed === "object" ? seed : {}), ...patch };
      onDraftEdited(nextDraft);
    }

    React.useEffect(() => {
      if (templateAutoCorrectSuppressed) return;
      if (!templateConstraint.autoCorrect) return;
      const current = seed && seed.template_key ? String(seed.template_key) : "";
      if (current === String(templateConstraint.autoCorrect)) return;
      setAutoCorrectNotice({
        field: "template_key",
        before: current || "(empty)",
        after: String(templateConstraint.autoCorrect),
        reason: templateConstraint.message || "Applied safe catalog-derived normalization.",
      });
      updateDraftPatch({ template_key: String(templateConstraint.autoCorrect) });
    }, [seed, templateAutoCorrectSuppressed, templateConstraint.autoCorrect, templateConstraint.message]);

    const renderConstraintStates = (constraint) => {
      if (!constraint) return null;
      const chips = [];
      if (constraint.hidden) chips.push({ key: "hidden", text: "Hidden", tone: "is-hidden" });
      if (constraint.disabled) chips.push({ key: "disabled", text: "Disabled", tone: "is-disabled" });
      if (constraint.warning) chips.push({ key: "warning", text: "Warn", tone: "is-warning" });
      if (constraint.autoCorrect) chips.push({ key: "auto-correct", text: "Auto-correct", tone: "is-autocorrect" });
      if (constraint.autoCorrectBlocked) chips.push({ key: "auto-correct-blocked", text: "Auto-correct blocked", tone: "is-blocked" });
      if (!chips.length) return null;
      return (
        <div className="builder-constraint-states" role="status" aria-live="polite">
          {chips.map((chip) => <span key={chip.key} className={`builder-constraint-chip ${chip.tone}`}>{chip.text}</span>)}
        </div>
      );
    };

    const renderBuilderFieldControl = (fieldVm) => {
      if (!fieldVm || (fieldVm.behavior && fieldVm.behavior.hidden)) return null;
      const isDisabled = Boolean(fieldVm.behavior && fieldVm.behavior.disabled);
      const onFieldChange = (nextValue) => {
        if (fieldVm.key === "protocol_key" || fieldVm.key === "template_key") setTemplateAutoCorrectSuppressed(false);
        updateDraftPatch(toDraftPatchBySchema(fieldVm.key, nextValue));
      };
      if (fieldVm.control === "select") {
        return (
          <label className="builder-control" key={fieldVm.key}>
            <span>{fieldVm.label}</span>
            <select value={fieldVm.value} onChange={(e) => onFieldChange(e.target.value)} disabled={isDisabled}>
              {(fieldVm.options || []).map((option) => <option key={`${fieldVm.key}-${option.value}`} value={option.value}>{option.label}</option>)}
            </select>
          </label>
        );
      }
      return (
        <label className="builder-control" key={fieldVm.key}>
          <span>{fieldVm.label}</span>
          <input type="text" value={fieldVm.value} onChange={(e) => onFieldChange(e.target.value)} disabled={isDisabled} />
        </label>
      );
    };

    return (
      <div className="route-card">
        <div className="route-card-header">
          <h2>Builder Route Container</h2>
          <span className="vsl-status-badge">{seed && seed.seed_source ? `Seeded: ${seed.seed_source}` : "Owned by Builder Route"}</span>
        </div>
        <p>Constrained draft editing surface for builder-driven experiment setup.</p>
        <div className="route-actions">
          <button type="button" className="route-action" onClick={() => typeof onResolvePlan === "function" && onResolvePlan()}>Resolve Plan</button>
          <a className="route-action" href="/ui/builder.html">Open Legacy Builder</a>
        </div>
        <div className="builder-sections-grid">
          <section className="builder-section-panel builder-section-overview">
            <div className="builder-section-header"><h3 className="builder-section-heading">Overview</h3><span className="builder-section-index">S1</span></div>
            <p className="builder-section-subheading">Draft ownership and readiness telemetry.</p>
            <div className="builder-kv"><strong>Draft Ownership:</strong> <code className="builder-readout">{builderDraftState?.ownership || "n/a"}</code></div>
            <div className="builder-kv"><strong>Draft Version:</strong> <code className="builder-readout">{builderDraftState?.draftVersion ?? "n/a"}</code></div>
            <div className="builder-kv"><strong>Validation Errors:</strong> <code className="builder-readout">{Array.isArray(builderDraftState?.validationErrors) ? builderDraftState.validationErrors.length : 0}</code></div>
          </section>
          {builderSectionViewModels.map((sectionVm) => (
            <section key={sectionVm.key} className={`builder-section-panel ${sectionVm.className || ""}`}>
              <div className="builder-section-header"><h3 className="builder-section-heading">{sectionVm.title}</h3><span className="builder-section-index">{sectionVm.index}</span></div>
              <p className="builder-section-subheading">{sectionVm.subheading}</p>
              {Array.isArray(sectionVm.readouts) ? sectionVm.readouts.map((item) => (
                <div key={`${sectionVm.key}-${item.label}`} className="builder-kv"><strong>{item.label}:</strong> <code className="builder-readout">{String(item.value)}</code></div>
              )) : null}
              <div className="builder-control-group">{Array.isArray(sectionVm.fields) ? sectionVm.fields.map((fieldVm) => renderBuilderFieldControl(fieldVm)) : null}</div>
              {renderConstraintStates(sectionVm.constraint)}
              {sectionVm.constraint && sectionVm.constraint.message ? <p className={sectionVm.constraint.warning ? "builder-constraint-warning" : "builder-constraint-note"}>{sectionVm.constraint.message}</p> : null}
            </section>
          ))}
          {!advancedConstraint.hidden ? (
            <section className="builder-section-panel builder-section-panel-muted builder-section-advanced">
              <div className="builder-section-header"><h3 className="builder-section-heading">Advanced/Debug</h3><span className="builder-section-index">S6</span></div>
              <p className="builder-section-subheading">Low-prominence diagnostics for route-state troubleshooting.</p>
              <div className="builder-advanced-wrapper">
                <button
                  type="button"
                  className="route-action builder-advanced-toggle"
                  aria-expanded={advancedVisible ? "true" : "false"}
                  onClick={() => setAdvancedVisible((value) => { const next = !value; if (!next) setDebugDetailsVisible(false); return next; })}
                >
                  {advancedVisible ? "Hide Advanced Diagnostics" : "Show Advanced Diagnostics"}
                </button>
                {advancedVisible ? (
                  <div className="builder-advanced-content">
                    {renderConstraintStates(advancedConstraint)}
                    <div className="builder-debug-summary" role="status" aria-live="polite">
                      <div><strong>debug_mode:</strong> <code className="builder-readout">{debugAdvancedState?.mode || "off"}</code></div>
                      <div><strong>render_cap_rows:</strong> <code className="builder-readout">{debugAdvancedState?.maxRows ?? 200}</code></div>
                      <div><strong>sampled:</strong> <code className="builder-readout">{String(Boolean(debugAdvancedState?.sampled))}</code></div>
                      <div><strong>sample_every_n_ticks:</strong> <code className="builder-readout">{debugAdvancedState?.sampleEveryNTicks ?? "none"}</code></div>
                    </div>
                    <button type="button" className="route-action builder-debug-details-toggle" aria-expanded={debugDetailsVisible ? "true" : "false"} onClick={() => setDebugDetailsVisible((value) => !value)}>
                      {debugDetailsVisible ? "Hide Debug Details" : "Show Debug Details"}
                    </button>
                    {debugDetailsVisible ? (
                      <pre className="builder-debug-details">{JSON.stringify({
                        mode: debugAdvancedState?.mode || "off",
                        max_rows: debugAdvancedState?.maxRows ?? 200,
                        sampled: Boolean(debugAdvancedState?.sampled),
                        sample_every_n_ticks: debugAdvancedState?.sampleEveryNTicks ?? null,
                        cap_policy: "backend-cap-aware",
                        decimation_policy: debugAdvancedState?.sampled ? "active" : "inactive",
                      }, null, 2)}</pre>
                    ) : null}
                    <div className="builder-kv"><strong>dirty:</strong> <code className="builder-readout">{String(Boolean(builderDraftState?.dirty))}</code></div>
                    <div className="builder-kv"><strong>is_ready:</strong> <code className="builder-readout">{String(Boolean(builderDraftState?.isReady))}</code></div>
                    <div className="builder-kv"><strong>validation_state:</strong> <code className="builder-readout">{builderDraftState?.isReady ? "ready" : "needs_attention"}</code></div>
                  </div>
                ) : null}
              </div>
            </section>
          ) : null}
        </div>
        {autoCorrectNotice ? (
          <div className="builder-autocorrect-notice">
            <div><strong>Auto-correct applied:</strong> <code>{autoCorrectNotice.field}</code></div>
            <div><strong>Before:</strong> <code>{autoCorrectNotice.before}</code></div>
            <div><strong>After:</strong> <code>{autoCorrectNotice.after}</code></div>
            <div><strong>Reason:</strong> {autoCorrectNotice.reason}</div>
            <button
              type="button"
              className="route-action"
              onClick={() => {
                const previous = autoCorrectNotice.before === "(empty)" ? "" : autoCorrectNotice.before;
                setTemplateAutoCorrectSuppressed(true);
                updateDraftPatch({ template_key: previous });
                setAutoCorrectNotice(null);
              }}
            >
              Undo Auto-correct
            </button>
          </div>
        ) : null}
        <div className="builder-validation-panel">
          <div><strong>Draft Readiness:</strong> <code>{builderDraftState?.isReady ? "ready" : "not_ready"}</code></div>
          <div><strong>Validation Errors:</strong> <code>{Array.isArray(builderDraftState?.validationErrors) ? builderDraftState.validationErrors.length : 0}</code></div>
        </div>
        <div className="plan-resolve-summary">
          <div><strong>Plan Status:</strong> <code>{planState && planState.requestStatus ? planState.requestStatus : "idle"}</code></div>
          <div><strong>Stable Hash:</strong> <code>{stableHash || "n/a"}</code></div>
          <div><strong>Unit Count:</strong> <code>{summary.unitCount}</code></div>
          <div><strong>Total Trials:</strong> <code>{summary.totalTrials}</code></div>
          <div><strong>Flow:</strong> <code>{summary.flow}</code></div>
        </div>
        {resolveErrorView ? (
          <div className="plan-resolve-inline-error">
            <div><strong>Resolve Error Code:</strong> <code>{resolveErrorView.code}</code></div>
            <div><strong>Message:</strong> {resolveErrorView.message}</div>
            {resolveErrorView.reason ? <div><strong>Reason:</strong> <code>{resolveErrorView.reason}</code></div> : null}
            {resolveErrorView.invalidFields.length ? (
              <div>
                <strong>Likely Fields:</strong>
                <ul>{resolveErrorView.invalidFields.map((field) => <li key={`resolve-field-${field}`}><code>{field}</code></li>)}</ul>
              </div>
            ) : null}
            <div><strong>Recovery:</strong> {resolveErrorView.hint}</div>
          </div>
        ) : null}
      </div>
    );
  }

  routeContainers.BuilderRouteContainer = BuilderRouteContainer;
})(typeof window !== "undefined" ? window : globalThis);

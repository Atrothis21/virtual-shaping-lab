# V2.17.5 Summary - First-Open Usability Simplification

## Overview
V2.17.5 simplifies first-open UX so users can immediately choose a clear path, while keeping V2.17 architecture boundaries (route orchestration, services for side effects, selector/view-model shaping, and guard enforcement).

Primary outcomes:
- launcher-first home with clear intent hierarchy
- preset-first quick-success path with capped density
- guided builder framing with progressive advanced/debug disclosure
- single-primary-action semantics across key route surfaces
- compact recent-activity continuity with deterministic ordering
- standardized recovery actions across launcher/builder/run/report
- lazy-loaded builder-heavy modules to reduce first-open blocking
- expanded guard + scaffold coverage for first-open simplicity contracts

---

## Delivered Changes

### 1) First-Open Launcher and Intent Routing
Updated:
- `virtual_shaping_lab/ui/js/react/features/launcher/LauncherView.jsx`
- `virtual_shaping_lab/ui/js/react/features/launcher/LauncherCard.jsx`
- `virtual_shaping_lab/ui/js/react/features/launcher/first_open_state_selector.js`
- `virtual_shaping_lab/ui/js/react/routes/launcher_route.jsx`
- `virtual_shaping_lab/ui/js/react/index_app.jsx`

Behavior:
- first-open defaults to `home` launcher route
- exactly two intent cards:
  - `Run a preset` (dominant)
  - `Build an experiment` (secondary)
- first-open selector policy is explicit and test-covered:
  - no-history and has-history both open launcher
  - recent strip visibility driven by recent-item presence

### 2) Preset-First Quick Success and Density Caps
Updated:
- `virtual_shaping_lab/ui/js/react/routes/launcher_route.jsx`
- `virtual_shaping_lab/ui/js/react/routes/presets_route.jsx`

Behavior:
- featured presets capped at 4 on launcher
- recent activity capped at 3 on launcher
- preset detail primary action shifted to `Run preset`
- supporting actions demoted to secondary/tertiary to reduce decision noise

### 3) Guided Builder and Progressive Disclosure
Updated:
- `virtual_shaping_lab/ui/js/react/routes/builder_route.jsx`
- `virtual_shaping_lab/ui/js/react/index_app.jsx`
- `virtual_shaping_lab/ui/css/index.css`

Behavior:
- builder presented as explicit guided sequence:
  - `Start`
  - `Configure phases`
  - `Runtime/report choices`
  - `Resolve plan`
- launcher -> builder handoff seeds guided starter draft
- advanced/debug remains collapsed by default
- reveal controls are local UI state only, with explicit `aria-controls` wiring

### 4) Action Semantics and Recovery Consistency
Updated:
- `virtual_shaping_lab/ui/js/react/ui_primitives.jsx`
- `virtual_shaping_lab/ui/js/react/routes/launcher_route.jsx`
- `virtual_shaping_lab/ui/js/react/routes/builder_route.jsx`
- `virtual_shaping_lab/ui/js/react/routes/run_route.jsx`
- `virtual_shaping_lab/ui/js/react/routes/report_route.jsx`
- `virtual_shaping_lab/ui/css/index.css`

Behavior:
- single-primary-action hierarchy enforced per key surface
- legacy escape hatches consistently demoted to tertiary actions
- shared recovery row introduced with standardized actions:
  - `Retry`
  - `Go to presets`
  - `Go to builder`

### 5) Continuity and First-Open Performance
Updated:
- `virtual_shaping_lab/ui/js/react/state_domains.js`
- `virtual_shaping_lab/ui/js/react/routes/launcher_route.jsx`
- `virtual_shaping_lab/ui/js/react/lazy_route_loader.js`
- `virtual_shaping_lab/ui/index.html`
- `virtual_shaping_lab/ui/js/react/index_app.jsx`

Behavior:
- recent activity ordering is deterministic and most-recent-first
- report state now tracks update timestamps for recent-item ranking
- builder-heavy modules are lazy-loaded on builder-route entry:
  - `builder_draft_translator.js`
  - `builder_constraint_controls.js`
  - `builder_form_schema.js`
  - `builder_submission_guards.js`
- launcher/preset-first path renders without waiting on builder bundle
- route transition fallback/retry behavior for lazy loading is explicit and test-covered

### 6) Guard and Scaffold Expansion
Added/updated tests:
- `tests/test_ui_single_primary_action_hierarchy_scaffold.py`
- `tests/test_ui_recent_activity_cap_scaffold.py`
- `tests/test_ui_recovery_consistency_scaffold.py`
- `tests/test_ui_lazy_loading_scaffold.py`
- `tests/test_ui_lazy_loading_route_transition_scaffold.py`
- `tests/v2_11_guards/test_ui_first_open_launcher_contract_guard.py`
- updated scaffold expectations in:
  - `tests/test_ui_launcher_intent_flow_scaffold.py`
  - `tests/test_ui_route_scaffold.py`
  - `tests/test_ui_builder_sections_scaffold.py`

---

## Usability Validation Outcomes (Phase 5.2)

Artifacts:
- `docs/ui_usability_validation_protocol.md`
- `V2.17.5_usability_findings.md`

Recorded outcomes:
- first-open intent discovery improved (launcher card hierarchy is clear)
- preset quick-success path improved (`Run preset` primary)
- builder onboarding reduced form-wall effect via guided stepper + starter hints
- residual observation logged: some dense surfaces still carry multiple secondary actions

---

## Terminology Mapping Outcome

First-open/entry wording now reflects intent-focused language:
- `Experiment type` is used in launcher/preset surfaces
- `Run preset`, `Prepare preset`, `Run preset + report` remain plain-language verbs
- technical vocabulary remains bounded to advanced/debug and diagnostic contexts

---

## Selector Policy Outcome

`selectFirstOpenState(...)` contract in `features/launcher/first_open_state_selector.js`:
- `initialRouteKey: "home"` (launcher-first)
- `showRecentStrip` depends on recent-item presence
- reason codes capture first-open/no-history vs prior launcher visit

---

## Validation

Representative V2.17.5 slice gates executed:
- Phase 1 gate:
  - `tests/test_ui_route_scaffold.py`
  - `tests/test_ui_route_component_files_scaffold.py`
  - `tests/test_ui_launcher_view_scaffold.py`
  - `tests/test_ui_first_open_state_selector.py`
- Phase 4 gate:
  - `tests/test_ui_builder_sections_scaffold.py`
  - `tests/test_ui_builder_constraint_behavior_scaffold.py`
  - `tests/test_ui_builder_submission_guards_scaffold.py`
- Phase 5 gate:
  - `tests/test_ui_action_semantics_scaffold.py`
  - `tests/test_ui_single_primary_action_hierarchy_scaffold.py`
  - `tests/test_ui_first_open_terminology_mapping_scaffold.py`
- Phase 6 gate:
  - `tests/test_ui_route_state_panels_scaffold.py`
  - `tests/test_ui_notice_consistency_scaffold.py`
  - `tests/test_ui_plan_resolve_error_handling_scaffold.py`
  - `tests/test_ui_recent_activity_cap_scaffold.py`
  - `tests/test_ui_recovery_consistency_scaffold.py`
- Phase 7 gate:
  - `tests/test_ui_lazy_loading_scaffold.py`
  - `tests/test_ui_lazy_loading_route_transition_scaffold.py`
  - `tests/test_ui_route_scaffold.py`
- Phase 8 guard gate:
  - `tests/v2_11_guards/test_ui_first_open_launcher_contract_guard.py`
  - `tests/v2_11_guards/test_ui_route_api_and_translator_boundaries_guard.py`
  - `tests/v2_11_guards/test_ui_v2_architecture_boundaries_guard.py`

Required CI-policy closeout gate:
- `tests/v2_11_guards`
- `tests/v2_11_contract`
- `tests/behavioral_signatures`
- `tests/test_run_api_contract.py`
- `tests/test_api_contract_snapshots.py`
- `tests/test_visualizations.py`

Execution result:
- `python -m pytest -q tests/v2_11_guards tests/v2_11_contract tests/behavioral_signatures tests/test_run_api_contract.py tests/test_api_contract_snapshots.py tests/test_visualizations.py`
- passed (`82 passed`), with one expected transitional deprecation warning from `phase_factory` compatibility shim.

---

## Residual Limitations / Deferred Items

Tracked via:
- `docs/ui_known_limitations.md`
- `V2.17.5_usability_findings.md`

Residuals:
- route scaffold tests are still primarily structure/contract oriented
- further consolidation of secondary actions may be needed on dense detail surfaces
- deeper route-specific extraction remains possible for long-term maintainability

---

## Net State After V2.17.5

- first-open is launcher-first, clearer, and lower-noise
- quick success is preset-forward with stronger action hierarchy
- builder is guided with bounded advanced complexity
- recovery and route-state messaging are more consistent
- recent continuity is compact and deterministic
- first-open rendering is less blocked by builder-heavy modules
- simplicity contract is guard-protected against drift

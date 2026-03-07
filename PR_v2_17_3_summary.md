# V2.17.3 Summary - Constrained Builder Refactor

## Overview
V2.17.3 completes the constrained builder refactor by moving builder editing to a draft-first, schema-driven surface with strict translator boundaries, explicit invalidation semantics, and scientific control-console UX.

Primary outcomes:
- builder editing remains draft-owned (`BuilderExperimentDraft` semantics) with no raw payload editor path
- plan submission is translator-only (`draft_to_payload`) and now guarded against payload-boundary violations
- draft edits continue to invalidate stale plan/report state and enforce re-resolve before run/report
- constraint behavior (`hide/disable/warn/auto-correct`) is centralized and transparent in the UI
- builder sections and controls are now schema/view-model driven instead of hardcoded wiring
- builder theme now reads as an instrument control console with clear hierarchy and low-prominence advanced diagnostics

---

## Delivered Changes

### 1) Builder Structure + Draft Binding (Phase 1)
Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`

Delivered:
- sectioned builder layout:
  - Overview
  - Protocol/Seed Selection
  - Phases
  - Runtime
  - Report
  - Advanced/Debug
- controls bound to draft state edit path (`DRAFT_EDITED`) only
- readiness and validation surfacing preserved in route container

Result:
- builder acts as a constrained draft editor, not a payload editor.

### 2) Translation + Invalidation Semantics (Phase 2)
Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`
- existing freshness/invalidation behavior in `virtual_shaping_lab/ui/js/react/state_domains.js` and run/report workflow retained

Delivered:
- builder plan resolve path uses translator boundary (`draft_to_payload`) as the only submission bridge
- stale plan gating behavior remains enforced for downstream run/report actions

Result:
- resolve/run/report flow is freshness-aware and contract-boundary safe.

### 3) Constraint-Driven UX Enforcement (Phase 3)
Added:
- `virtual_shaping_lab/ui/js/react/builder_constraint_controls.js`

Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`
- `virtual_shaping_lab/ui/index.html`

Delivered:
- shared constraint behavior evaluation for `hide/disable/warn/auto-correct`
- semantic auto-correct guardrail:
  - only allowed for declared non-semantic fields
  - semantic auto-corrects are explicitly blocked
- auto-correct transparency UX:
  - before/after/reason notice
  - undo action

Result:
- no silent semantic mutations; constraint behavior is explicit and consistent.

### 4) Builder Theme Application (Phase 4)
Updated:
- `virtual_shaping_lab/ui/index.html`
- `virtual_shaping_lab/ui/js/react/index_app.jsx`

Delivered:
- scientific panel styling and spacing hierarchy across builder sections
- section headers/subheadings/index markers and grouped controls for console-like structure
- monospaced technical readouts for key route telemetry
- consistent constraint-state affordances (chips/callouts)
- reduced visual prominence for advanced/debug section

Result:
- builder now reads as a scientific control surface rather than a generic form.

### 5) Architecture Hardening: Schema + Guards (Phase 5)
Added:
- `virtual_shaping_lab/ui/js/react/builder_form_schema.js`
  - `getBuilderSectionSchema(...)`
  - `buildBuilderSectionViewModels(...)`
  - `toDraftPatch(...)`
- `virtual_shaping_lab/ui/js/react/builder_submission_guards.js`
  - `assertBuilderDraftForTranslation(...)`
  - `assertTranslatedBuilderPayload(...)`

Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`
- `virtual_shaping_lab/ui/index.html`

Delivered:
- protocol/phases/runtime/report sections now render from schema/view-model adapters
- field edits flow through schema adapter patching (not ad hoc per-field wiring)
- strict resolve guardrails:
  - reject payload-shaped draft input at builder boundary
  - reject malformed translator output
  - block plan submission on boundary violations with explicit UI failure state

Result:
- builder structure is metadata-driven and protected against payload-editor regressions.

---

## Test Coverage

Added:
- `tests/test_ui_builder_autocorrect_transparency_scaffold.py`
- `tests/test_ui_builder_form_schema_scaffold.py`
- `tests/test_ui_builder_submission_guards_scaffold.py`

Updated:
- `tests/test_ui_builder_sections_scaffold.py`
- `tests/test_ui_builder_constraint_behavior_scaffold.py`
- `tests/test_ui_builder_draft_translator_scaffold.py`
- `tests/test_ui_state_domains_scaffold.py`
- `tests/test_ui_route_scaffold.py`

Representative gates executed during implementation:
- `python -m pytest -q tests/test_ui_builder_constraint_behavior_scaffold.py tests/test_ui_builder_autocorrect_transparency_scaffold.py tests/test_ui_route_scaffold.py`
- `python -m pytest -q tests/test_ui_builder_sections_scaffold.py tests/test_ui_builder_draft_binding_scaffold.py tests/test_ui_builder_constraint_behavior_scaffold.py tests/test_ui_builder_autocorrect_transparency_scaffold.py tests/test_ui_route_scaffold.py`
- `python -m pytest -q tests/test_ui_builder_form_schema_scaffold.py tests/test_ui_builder_sections_scaffold.py tests/test_ui_builder_draft_binding_scaffold.py tests/test_ui_builder_constraint_behavior_scaffold.py tests/test_ui_builder_autocorrect_transparency_scaffold.py tests/test_ui_route_scaffold.py`
- `python -m pytest -q tests/test_ui_builder_submission_guards_scaffold.py tests/test_ui_builder_draft_translator_scaffold.py tests/test_ui_state_domains_scaffold.py tests/test_ui_run_report_workflow_service_scaffold.py tests/test_ui_route_scaffold.py`

---

## Net State After V2.17.3

- builder editing is constrained, draft-driven, and translator-only
- payload-boundary guardrails now explicitly block direct payload regressions
- plan freshness invalidation remains enforced across run/report entrypoints
- constraint UX is centralized, transparent, and semantically safe
- builder section rendering is schema/view-model driven for extensibility
- builder visuals now align with instrument-console usability goals


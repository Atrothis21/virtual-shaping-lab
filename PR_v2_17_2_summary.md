# V2.17.2 Summary - Plan/Run/Report Lifecycle Surfaces

## Overview
V2.17.2 turns plan resolution, run lifecycle, and report generation into explicit, policy-driven route surfaces with scientific theming and stronger separation of concerns.

Primary outcomes:
- builder route now exposes explicit resolve-plan checkpoint + stable hash context
- run route now supports API-backed lifecycle start/refresh/poll with provenance + mismatch handling
- report route now supports API-backed report generation, provenance context, artifacts, and degraded-mode behavior
- run/report lifecycle UI now uses consistent scientific status theming and instrument-like progress affordances
- run/report side effects moved behind workflow service boundaries
- run/report rendering uses normalized lifecycle selector/view-model boundaries

---

## Delivered Changes

### 1) Plan Resolve Surface (Phase 1)
Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`

Behavior:
- explicit **Resolve Plan** action from builder context
- resolved plan summary block now shows:
  - plan status
  - stable hash
  - unit count
  - total trials
  - flow
- resolve failure handling aligned to `docs/ui_error_handling_matrix.md` via banner + inline actionable context

Result:
- users can clearly distinguish editable draft state from resolved execution plan state.

### 2) Run Lifecycle Surface (Phase 2)
Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`
- `virtual_shaping_lab/ui/index.html`

Behavior:
- run creation from resolved plan (`expected_plan_hash` path)
- lifecycle refresh + polling from `GET /runs/{id}`
- run provenance rendering:
  - `run_id`
  - `plan_hash`
  - `record_schema_version`
  - `template_version_used`
  - lifecycle + next actions
- mismatch policy handling:
  - record schema mismatch -> blocking treatment
  - template/plan mismatch -> warning treatment

Result:
- run lifecycle progression and compatibility state are explicit and recoverable.

### 3) Report Lifecycle + Artifacts Surface (Phase 3)
Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`
- `virtual_shaping_lab/ui/index.html`

Behavior:
- report generation action from report route: `POST /runs/{id}/report`
- report lifecycle context and retry-friendly status/error messaging
- report provenance rendering:
  - `source_run_id`
  - `plan_hash`
  - `record_schema_version`
  - `template_version_used`
  - `regenerated`
  - `regeneration_mode`
  - `missing_source_metadata`
- artifact rendering:
  - PDF link
  - figure artifact cards/links
- degraded-mode policy handling:
  - template mismatch -> warning/degraded mode, static artifacts remain available
  - record schema mismatch -> blocking treatment

Result:
- report creation and artifact access are first-class lifecycle behaviors under both normal and degraded conditions.

### 4) Theme Application for Run/Report (Phase 4)
Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`
- `virtual_shaping_lab/ui/index.html`

Behavior:
- unified lifecycle status semantics across run/report
- shared lifecycle instrument UI:
  - semantic status badge
  - meter/progress affordance
  - phase caption
- report figure presentation upgraded to scientific dashboard style:
  - dark analysis surfaces
  - subtle axis/grid-like overlays
  - semantic condition chips and figure card accent rails (`cs-plus`, `cs-minus`, `probe`, `compound`, `learning`)

Result:
- run/report routes now read as scientific instrument/workstation surfaces rather than generic cards.

### 5) SOC Hardening: Workflow Services + Lifecycle Selectors (Phase 5)
Added:
- `virtual_shaping_lab/ui/js/react/run_report_workflow_service.js`
- `virtual_shaping_lab/ui/js/react/lifecycle_view_models.js`

Updated:
- `virtual_shaping_lab/ui/js/react/index_app.jsx`
- `virtual_shaping_lab/ui/index.html`

Behavior:
- run/report side effects extracted from route container internals into workflow service boundary:
  - `startRunFromResolvedPlan`
  - `refreshActiveRunStatus`
  - `pollActiveRunStatus`
  - `createReportFromActiveRun`
- run/report view rendering now uses normalized selector module:
  - lifecycle view models
  - provenance view models
  - artifact view models
  - mismatch detection
  - lifecycle instrument mapping

Result:
- side-effect orchestration and UI rendering responsibilities are separated, reducing future rework risk.

---

## Test Coverage

Added/updated scaffolds:
- `tests/test_ui_plan_resolve_surface_scaffold.py`
- `tests/test_ui_plan_resolve_error_handling_scaffold.py`
- `tests/test_ui_run_lifecycle_surface_scaffold.py`
- `tests/test_ui_run_mismatch_handling_scaffold.py`
- `tests/test_ui_report_lifecycle_surface_scaffold.py`
- `tests/test_ui_report_degraded_mode_scaffold.py`
- `tests/test_ui_run_report_workflow_service_scaffold.py`
- `tests/test_ui_lifecycle_view_models_scaffold.py`
- `tests/test_ui_route_scaffold.py`

Representative gates passed during implementation:
- `python -m pytest -q tests/test_ui_report_lifecycle_surface_scaffold.py tests/test_ui_route_scaffold.py tests/test_ui_preset_action_flow_scaffold.py`
- `python -m pytest -q tests/test_ui_report_lifecycle_surface_scaffold.py tests/test_ui_report_degraded_mode_scaffold.py tests/test_ui_route_scaffold.py tests/test_ui_run_mismatch_handling_scaffold.py`
- `python -m pytest -q tests/test_ui_run_lifecycle_surface_scaffold.py tests/test_ui_report_lifecycle_surface_scaffold.py tests/test_ui_run_mismatch_handling_scaffold.py tests/test_ui_report_degraded_mode_scaffold.py`
- `python -m pytest -q tests/test_ui_run_report_workflow_service_scaffold.py tests/test_ui_run_lifecycle_surface_scaffold.py tests/test_ui_report_lifecycle_surface_scaffold.py tests/test_ui_route_scaffold.py tests/test_ui_preset_action_flow_scaffold.py`
- `python -m pytest -q tests/test_ui_lifecycle_view_models_scaffold.py tests/test_ui_run_report_workflow_service_scaffold.py tests/test_ui_run_lifecycle_surface_scaffold.py tests/test_ui_report_lifecycle_surface_scaffold.py tests/test_ui_route_scaffold.py`

---

## Net State After V2.17.2

- plan/run/report are explicit route-level lifecycle surfaces
- resolve/run/report mismatch and error behaviors are policy-driven and recoverable
- report artifacts and provenance are first-class UI outputs
- run/report visual language is scientifically themed and semantically encoded
- run/report orchestration now lives in workflow services, not route containers
- lifecycle rendering now depends on normalized selector/view-model boundaries

---

## Follow-On Readiness

V2.17.2 establishes the architecture needed for subsequent route-level expansion (V2.17.3+), with low-friction extension points for additional lifecycle policies, richer artifact experiences, and stricter contract tests.

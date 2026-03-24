# V3.17.0 Summary - Comprehensive Preset UX Cutover

## Overview
V3.17.0 completes the tuple-first preset UX cutover from catalog selection through detail/edit/run and into run/report artifact identity surfaces.

Primary outcomes:
- migrated preset catalog UX to contract-driven tuple/smart-preset hierarchy with deterministic status-prioritized ordering
- unified smart-preset and manual tuple entry into one shared detail/edit/run flow
- enforced compatibility-vs-composition boundary (`structurally_invalid` as composition/legality failure, not UX compatibility badge)
- propagated tuple/smart-preset UX provenance through run metadata, status metadata, regenerated reports, and artifact identity payloads
- hardened accessibility and copy semantics (non-color status labels, ARIA labeling, supportive `behaviorally_unsupported` guidance)
- published preset UX cutover docs and added a blocking CI bucket for end-to-end UX contract enforcement

This slice closes the preset UX cutover milestone and aligns execution/test/CI boundaries with tuple-first contracts.

---

## Slice 1 - Preset Catalog IA Cutover

### Objective
Replace legacy/static preset-card assumptions with contract-driven catalog IA and deterministic ordering.

### Implemented
Updated:
- `virtual_shaping_lab/ui/js/react/app.jsx`
- `tests/test_v3_ui_preset_catalog_ux_contract.py`

Changes:
- catalog now renders from `/catalog/preset-ux` contract shape
- hierarchy enforced by:
  - arrangement
  - phenomenon class
  - smart preset variants
- status-priority ordering enforced:
  - `success`
  - `partial`
  - `novel`
  - `behaviorally_unsupported`
- structural-invalid tuple combinations suppressed from catalog cards
- degraded fallback mode retained when catalog endpoint is unavailable
- density controls added with collapsed sections + top recommended-first behavior

---

## Slice 2 - Tuple-First Preset Detail/Editor UX

### Objective
Converge smart-preset and manual tuple entry into one detail/edit/run experience.

### Implemented
Updated:
- `virtual_shaping_lab/ui/js/react/tuple_authoring_flow.jsx`
- `virtual_shaping_lab/ui/js/react/app.jsx`
- `tests/test_v3_ui_preset_detail_tuple_flow.py`

Changes:
- smart preset projection path and manual tuple path now converge to a single detail flow model
- expected-outcome panel rendered pre-run
- run gating enforces:
  - blocked on composition/legality failures
  - allowed for `partial`, `novel`, `behaviorally_unsupported` with guidance
- provenance interpretation layer added for readable operator-factor statements
- explicit manual entry CTA surfaced:
  - `Explore Tuple Space`

---

## Slice 3 - Legacy Preset Routing and Migration Boundary

### Objective
Enforce explicit tuple-first route strategy while retaining bounded fallback for unmigrated routes.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/preset_route_migration.py`
- `tests/test_v3_ui_preset_route_migration.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`
- `virtual_shaping_lab/api/run.py`
- `virtual_shaping_lab/ui/js/react/teaching_panel.jsx`
- `tests/test_run_api_contract.py`

Changes:
- explicit route migration map contract exposed via:
  - `GET /catalog/preset-route-migration`
- migrated routes reject legacy bridge behavior
- deprecated tuple input diagnostics enriched with migration strategy context
- route map snapshot/shape coverage added

---

## Slice 4 - Run/Report UX Integration and Artifact Surfaces

### Objective
Carry preset UX context through run/report metadata and artifact identities with regeneration parity.

### Implemented
Updated:
- `virtual_shaping_lab/api/services.py`
- `virtual_shaping_lab/ui/contracts/tuple_authoring_api.py`
- `virtual_shaping_lab/analysis/report/report.py`
- `tests/test_run_api_contract.py`

Changes:
- run and report metadata now propagate:
  - `tuple_authoring_identity`
  - `preset_ux_identity`
  - `basis_compile_identity`
  - `measurement_provenance_identity`
- tuple materialization preserves preset UX context in canonical payload metadata
- `artifact_identity.json` now persists `preset_ux_identity`
- regeneration parity assertions added for run/report identity continuity

---

## Slice 5 - Accessibility, Copy, and Interaction Hardening

### Objective
Harden preset UX accessibility semantics and enforce copy distinction between compatibility guidance and composition failure.

### Implemented
Updated:
- `virtual_shaping_lab/ui/js/react/app.jsx`
- `virtual_shaping_lab/ui/js/react/tuple_authoring_flow.jsx`
- `tests/test_v3_ui_preset_accessibility_contract.py`

Added:
- `tests/test_v3_ui_manual_tuple_exploration_entry.py`
- `tests/test_v3_ui_provenance_explanation_readability.py`

Changes:
- status badges now include non-color semantic labels
- ARIA labels added for compatibility status/explanation/guidance and action links
- copy deck centralized for compatibility states
- composition-error copy separated from compatibility copy
- `behaviorally_unsupported` wording enforced as exploration-supportive
- focus/action order contract assertions added for primary vs exploratory actions

---

## Slice 6 - CI/Docs/Closeout Hardening

### Objective
Publish end-to-end cutover docs and block regressions via dedicated CI coverage.

### Implemented
Added:
- `docs/v3_17_0_preset_ux_cutover.md`
- `tests/test_v3_preset_ux_docs_contract.py`
- `tests/test_v3_ui_preset_catalog_ordering.py`
- `tests/test_v3_ui_preset_catalog_density_controls.py`

Updated:
- `.github/workflows/ci.yml`
- `V3_17_0_plan.md`

Changes:
- documented:
  - catalog IA and route strategy
  - expected-outcome interaction model
  - migration playbook for remaining legacy routes
  - post-cutover checklist for new presets
- added blocking CI step:
  - `Run V3 preset UX cutover`
- aligned test plan and CI selectors with implemented gates

---

## Closeout Impact

After V3.17.0:
- preset UX is contract-driven from catalog to detail flow and no longer relies on hardcoded legacy preset assumptions for migrated paths
- compatibility guidance and composition failure handling are explicitly separated in UX semantics
- tuple/smart-preset provenance identity is preserved across run, status, report regeneration, and artifact identity outputs
- accessibility/copy and docs boundaries are test-enforced
- CI blocks regressions on core preset UX cutover contracts

V3.17.0 therefore completes the comprehensive preset UX cutover and establishes a stable tuple-first UX baseline for future preset expansion.

---

## Validation

### Slice and UX Contract Gates
Validated via:
- `tests/test_v3_ui_preset_catalog_ux_contract.py`
- `tests/test_v3_ui_preset_catalog_ordering.py`
- `tests/test_v3_ui_preset_catalog_density_controls.py`
- `tests/test_v3_ui_preset_detail_tuple_flow.py`
- `tests/test_v3_ui_manual_tuple_exploration_entry.py`
- `tests/test_v3_ui_preset_route_migration.py`
- `tests/test_v3_ui_preset_accessibility_contract.py`
- `tests/test_v3_ui_provenance_explanation_readability.py`
- `tests/test_v3_preset_ux_docs_contract.py`
- `tests/test_run_api_contract.py -k "preset_ux_catalog_endpoint_shape or preset_route_migration_endpoint_shape or smart_preset or tuple_compatibility or tuple_identity or keeps_tuple_identity or preset_ux_identity"`

### CI-Facing Contract Checks
Validated by assertions that:
- catalog hierarchy/ordering/density controls are deterministic and contract-driven
- smart preset and manual tuple paths converge to one detail/run flow
- migrated route boundaries remain explicit with fallback only where allowed
- run/report/artifact identity surfaces preserve tuple + preset UX provenance parity
- accessibility/copy boundaries and docs-linked UX contracts remain synchronized

---

## Net State After V3.17.0

- tuple-first preset UX cutover is active across catalog, detail, run, and report paths
- compatibility/composition semantics are explicit and test-enforced
- dedicated CI coverage blocks preset UX contract regressions
- migration and onboarding docs are published with enforceable checklist coverage

V3.17.0 closes the comprehensive preset UX cutover phase.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_ui_preset_catalog_ux_contract.py`
- `python -m pytest -q tests/test_v3_ui_preset_catalog_ordering.py`
- `python -m pytest -q tests/test_v3_ui_preset_catalog_density_controls.py`
- `python -m pytest -q tests/test_v3_ui_preset_detail_tuple_flow.py`
- `python -m pytest -q tests/test_v3_ui_manual_tuple_exploration_entry.py`
- `python -m pytest -q tests/test_v3_ui_preset_route_migration.py`
- `python -m pytest -q tests/test_v3_ui_preset_accessibility_contract.py`
- `python -m pytest -q tests/test_v3_ui_provenance_explanation_readability.py`
- `python -m pytest -q tests/test_v3_preset_ux_docs_contract.py`
- `python -m pytest -q tests/test_run_api_contract.py -k "preset_ux_catalog_endpoint_shape or preset_route_migration_endpoint_shape or smart_preset or tuple_compatibility or tuple_identity or keeps_tuple_identity or preset_ux_identity"`

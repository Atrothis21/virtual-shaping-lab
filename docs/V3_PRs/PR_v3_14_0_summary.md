# V3.14.0 Summary - UI Basis-First Cutover and Payload Boundary Enforcement

## Overview
V3.14.0 completes the UI contract cutover for core presets onto basis-first authoring paths and tightens API boundaries against legacy/mixed payload forms.

Primary outcomes:
- migrated core preset editors to basis authoring payloads (`operator_subset` + `edits`) instead of legacy experiment blobs
- generalized basis authoring/materialization contracts from acquisition-only to core presets (`acquisition`, `extinction`, `differential_acquisition`)
- added generic preset API catalog/materialization endpoints alongside compatibility acquisition endpoints
- enforced migrated-route bridge rejection in browser canonicalization fallback for core basis-first pages
- expanded contract and editor-surface tests for extinction and differential acquisition parity
- updated blocking CI bucket selectors to include generic basis endpoint and core preset run-path assertions

This slice closes the core UI authoring gap between basis-first contract design and preset page execution paths.

---

## Slice 1 - UI Basis-First Payload Authoring

### Objective
Move preset UI authoring from legacy experiment payload construction to basis subset authoring contracts.

### Implemented
Updated:
- `virtual_shaping_lab/ui/js/react/acquisition_editor.jsx`
- `virtual_shaping_lab/ui/js/react/extinction_editor.jsx`
- `virtual_shaping_lab/ui/js/react/differential_acquisition_editor.jsx`
- `tests/test_v3_ui_basis_authoring_editor_surface.py`

Changes:
- editors now emit basis authoring payloads:
  - `preset_id`
  - `operator_subset`
  - `edits`
- canonical experiment payloads are generated via API materialization route, not browser-side legacy conversion
- operator choices and rule choices are registry-sourced from authoring contract payloads
- added no-legacy-emission assertions for extinction and differential pages

---

## Slice 2 - Core Preset Basis Authoring Generalization

### Objective
Generalize basis authoring contracts/materialization beyond acquisition to core presets.

### Implemented
Updated:
- `virtual_shaping_lab/ui/contracts/preset_basis_authoring.py`
- `virtual_shaping_lab/ui/contracts/__init__.py`
- `tests/test_v3_ui_basis_authoring_contract.py`

Changes:
- added generic contract/materialization entry points:
  - `build_preset_basis_authoring_contract(...)`
  - `materialize_preset_basis_payload(...)`
- added preset-specific wrappers for:
  - acquisition
  - extinction
  - differential acquisition
- added per-preset editable default handling (`n_trials` vs extinction phase counts vs `cs_minus`)
- preserved acquisition wrapper behavior for backward compatibility
- added contract/materialization tests for all core presets

---

## Slice 3 - Legacy Canonicalization Bridge Cutover

### Objective
Disable legacy canonicalization bridge usage on migrated basis-first routes while preserving fallback for unmigrated pages.

### Implemented
Updated:
- `virtual_shaping_lab/ui/js/react/teaching_panel.jsx`
- `tests/test_ui_teaching_contract.py`

Changes:
- expanded migrated route set:
  - `acquisition`
  - `extinction`
  - `differential_acquisition`
- legacy bridge now throws explicit migration error on those routes
- retained `toCanonicalPayload -> legacyToCanonicalPayload` fallback contract for unmigrated routes
- added/updated tests verifying both migrated-route rejection and unmigrated-route fallback retention

---

## Slice 4 - API Boundary Enforcement

### Objective
Expose generic basis-first preset endpoints and enforce payload boundary diagnostics through run flows.

### Implemented
Updated:
- `virtual_shaping_lab/api/run.py`
- `tests/test_run_api_contract.py`

Changes:
- added generic preset endpoints:
  - `GET /catalog/presets/{preset_id}/basis-authoring`
  - `POST /catalog/presets/{preset_id}/materialize-basis`
- preserved acquisition-specific endpoints for compatibility
- propagated preset-aware validation/internal error envelopes for generic routes
- added API tests for:
  - generic contract endpoint shape
  - generic materialization + run for extinction/differential
  - mixed legacy/canonical rejection + payload mode diagnostics

---

## Slice 5 - CI Bucket Hardening

### Objective
Finalize blocking CI coverage for basis-first UI/API boundary with core preset parity.

### Implemented
Updated:
- `.github/workflows/ci.yml`

Changes:
- hardened `Run V3 basis-first UI/API boundary` API selector to include:
  - generic preset basis contract endpoint tests
  - generic basis materialization tests
  - core preset materialization run tests
  - payload-mode and mixed/legacy rejection assertions

---

## Closeout Impact

After V3.14.0:
- acquisition, extinction, and differential acquisition preset pages author through basis-first contracts
- migrated routes no longer depend on legacy browser canonicalization bridge behavior
- API now serves generic basis authoring/materialization surfaces for core presets
- payload-boundary diagnostics remain explicit for mixed and legacy payload forms
- blocking CI enforces the basis-first boundary across UI surface, bridge behavior, and API contract paths

V3.14.0 therefore completes the core preset UI/API basis-first cutover milestone.

---

## Validation

### Slice and Boundary Gates
Validated via:
- `tests/test_v3_ui_basis_authoring_contract.py`
- `tests/test_v3_ui_basis_authoring_editor_surface.py`
- `tests/test_v3_ui_preset_basis_migration.py`
- `tests/test_ui_teaching_contract.py`
- `tests/test_run_api_contract.py`

### CI-Facing Contract Checks
Validated by assertions that:
- core preset editors emit basis authoring payloads and avoid legacy experiment blob construction
- migrated routes reject legacy canonicalization bridge usage
- generic preset basis endpoints materialize runnable canonical payloads
- mixed legacy/canonical payloads remain rejected with actionable diagnostics
- payload mode identity remains present in run metadata

---

## Net State After V3.14.0

- core preset UI authoring is aligned with first-class operator-basis contracts
- basis-first preset API surfaces are generalized beyond acquisition
- migrated-route legacy bridge dependency is removed
- CI bucket coverage matches the expanded core preset basis-first boundary

V3.14.0 establishes the stabilized basis-first authoring boundary for subsequent preset expansion in V3.15.x.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_ui_basis_authoring_contract.py tests/test_v3_ui_basis_authoring_editor_surface.py tests/test_v3_ui_preset_basis_migration.py`
- `python -m pytest -q tests/test_ui_teaching_contract.py -k "legacy_bridge_is_disabled_for_basis_first_migrated_routes or legacy_bridge_retained_for_unmigrated_routes_via_explicit_fallback"`
- `python -m pytest -q tests/test_run_api_contract.py -k "preset_basis_authoring_contract_endpoint_shape or basis_materialization_endpoint_emits_canonical_payload or basis_materialization_endpoint_payload_runs_for_core_presets or acquisition_basis_materialization_endpoint_payload_runs or mixed_legacy_and_canonical_payload_with_actionable_details or rejects_legacy_flat_payload_with_actionable_details or payload_mode_identity"`

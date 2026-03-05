# V2.12 Summary - Phase Catalog Unification

## Overview
V2.12 moves runtime phase construction ownership out of factory internals and into an explicit phase catalog seam, aligned with the protocol-catalog model.

Primary outcomes:
- introduced authoritative runtime phase catalog API (`catalog_runtime`)
- routed public phase construction seam to catalog runtime
- converted `phase_factory` to compatibility/deprecation shim
- tightened import guards to block direct `phase_factory` usage in runtime code
- added browser-critical API contract snapshot fixtures/tests
- added explicit `acquisition` default report-template mapping to remove fallback warning path

---

## Delivered Changes

### 1) Runtime Phase Catalog Surface
Added:
- `virtual_shaping_lab/experiment/phases/catalog_runtime.py`

Includes:
- `PHASE_BUILDERS`
- `available_phases()`
- `validate_phase_key()`
- `build_phase(...)`

Coverage:
- `tests/test_phase_catalog_runtime.py`

### 2) Public Phase Seam Repointing
Updated:
- `virtual_shaping_lab/experiment/phases/public.py`

Behavior:
- `build_phase(...)` now delegates to `experiment.phases.catalog_runtime`, not `experiment.factories.phase_factory`.

### 3) Phase Factory Quarantine (Compatibility Shim)
Updated:
- `virtual_shaping_lab/experiment/factories/phase_factory.py`

Behavior:
- file is now a thin compatibility wrapper around catalog runtime behavior
- emits one-time `DeprecationWarning` on direct usage
- keeps compatibility exports (`PHASE_REGISTRY`, `validate_phase`, `build_phase`)

### 4) Import-Graph Guard Tightening
Updated:
- `virtual_shaping_lab/experiment/assemble.py` now imports phase construction via `experiment.phases.public`
- `tests/v2_11_guards/test_factory_boundary_usage_guard.py`

Guard policy:
- direct imports of `experiment.factories.phase_factory` are now forbidden in runtime code
- phase construction must flow through public/catalog seams

### 5) API Contract Snapshot Fixtures
Added:
- `tests/fixtures/api_contract_snapshots.json`
- `tests/test_api_contract_snapshots.py`

Snapshot-covered endpoints:
- `POST /plan`
- `POST /run`
- `GET /runs/{id}`
- `POST /runs/{id}/report`
- `GET /catalog/extensions`

### 6) Report Mapping Parity (`acquisition`)
Updated:
- `virtual_shaping_lab/analysis/report/catalog.py`
- `tests/test_analysis_report_catalog.py`

Behavior:
- added explicit default report template mapping for protocol `acquisition`
- standard run/report flows no longer hit fallback-template warning path for `acquisition`

---

## Migration Table (Old Seam -> New Seam)

- phase-construction authority:
  - `experiment.factories.phase_factory` -> `experiment.phases.catalog_runtime`
- runtime/protocol phase import:
  - direct factory imports -> `experiment.phases.public.build_phase`
- compatibility path:
  - `experiment.factories.phase_factory` -> shim/deprecation wrapper over catalog runtime

---

## Compatibility Notes

- No runtime behavior break intended for existing payloads.
- Canonical/template phase key parity retained.
- Control-flow class exceptions remain intact:
  - `context_shift`
  - `criterion_shift`
- `phase_factory` remains available during migration window but is no longer authoritative.

---

## Validation

Representative gates run during V2.12:
- `python -m pytest -q tests/test_phase_catalog_runtime.py tests/test_factories.py`
- `python -m pytest -q tests/test_phase_catalog_runtime.py tests/test_phases.py tests/test_behavioral_phenomena_defaults.py`
- `python -m pytest -q tests/v2_11_guards/test_factory_boundary_usage_guard.py tests/test_import_boundaries.py`
- `python -m pytest -q tests/test_factories.py tests/test_assemble_coverage.py`
- `python -m pytest -q tests/test_run_api_contract.py tests/test_api_contract_snapshots.py`
- `python -m pytest -q tests/test_analysis_report_catalog.py tests/test_run_api_contract.py`

Closeout gate:
- `python -m pytest -q`

---

## Net State After V2.12

- phase construction ownership is explicit and catalog-backed
- runtime assembly/routes use public phase seam, not factory internals
- browser-critical API envelope shapes are snapshot-protected
- `acquisition` has explicit report-template mapping parity
- import boundaries are tighter and enforce intended phase-construction seams

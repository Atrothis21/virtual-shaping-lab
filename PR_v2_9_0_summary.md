## Overview
V2.9 completes template-first classical phase migration and introduces public facade entrypoints for experiment execution and analysis reporting.

Primary outcomes:
- canonical classical authoring is template-first by default
- legacy class-based canonical phases are isolated behind explicit `*_legacy` keys
- approved custom/class-based exceptions are clearly scoped
- experiment and analysis now expose stable public facades for orchestration
- API services and extension discovery were moved to facade-first imports
- import-boundary tests now enforce facade-first usage from `api/`

---

## What Was Delivered

### 1) Canonical Migration Inventory
Added:
- `docs/v2_9_phase_migration_inventory.md`

Contents:
- remaining legacy classical paths by protocol
- `migrate_now` vs `keep_custom` categorization
- required subphase naming invariants for test/report compatibility
- explicit phase-2 migration checklist

### 2) Remaining Canonical Classical Protocol Migration
Migrated protocol composition to template-backed phase construction:
- `virtual_shaping_lab/protocols/extinction.py`
- `virtual_shaping_lab/protocols/rapid_reacquisition.py`
- `virtual_shaping_lab/protocols/occasion_setting.py`

Compatibility behavior preserved:
- subphase names kept stable (`acquisition`, `nonreinforcement`, `probe` where applicable)
- `ContextShiftPhase` retained as class-based control-flow phase in rapid reacquisition

### 3) Legacy Canonical Deprecation/Isolation Pass
Updated:
- `virtual_shaping_lab/experiment/factories/phase_factory.py`
- `virtual_shaping_lab/experiment/phases/catalog.py`

Changes:
- canonical keys now template-first:
  - `acquisition`
  - `nonreinforcement`
  - `compound_acquisition`
  - `compound_nonreinforcement`
  - `probe`
- explicit legacy class aliases added:
  - `acquisition_legacy`
  - `nonreinforcement_legacy`
  - `compound_acquisition_legacy`
  - `compound_nonreinforcement_legacy`
  - `differential_acquisition_legacy`
  - `probe_legacy`
- temporary parity-safe exception retained class-based:
  - `differential_acquisition`

### 4) Experiment Public Facade
Added:
- `virtual_shaping_lab/experiment/public.py`

Stable entrypoints:
- `build_plan(payload)`
- `validate_plan(plan)`
- `assemble_from_plan(plan)`
- `run_from_plan(plan, ...)`

Additional support:
- `ExecutionResult` now includes both flattened `records` and per-unit `unit_records` for service-layer metadata shaping.

### 5) Analysis Public Facade
Added:
- `virtual_shaping_lab/analysis/public.py`

Stable entrypoints:
- `run_preset_report(...)`
- `run_default_protocol_report(...)`
- `get_protocol_default_template(...)`
- `list_protocol_default_templates(...)`

### 6) Facade Adoption and Import Cleanup
Updated:
- `virtual_shaping_lab/api/services.py`
- `virtual_shaping_lab/api/extensions.py`

Changes:
- plan build/assembly/execution now route through `experiment.public`
- report template/default lookup and template listing route through `analysis.public`
- compatibility symbols retained for patch-based contract tests:
  - `api.services.assemble_experiment`
  - `api.services.run_report`

### 7) Import Boundary Enforcement
Updated:
- `tests/test_import_boundaries.py`

New enforced rule:
- API layer must not import deep experiment/analysis internals (`experiment.assemble`, `experiment.config`, `experiment.runner`, `analysis.report.*`, `analysis.registry`); it must use public facades.

---

## Validation

Phase gates run and passing during implementation:
- Phase 1:
  - `python -m pytest -q tests/test_factories.py tests/test_protocols.py`
- Phase 2:
  - `python -m pytest -q tests/test_phases.py tests/test_protocols.py tests/behavioral_signatures/test_blocking.py tests/behavioral_signatures/test_conditioned_inhibition.py tests/behavioral_signatures/test_renewal.py`
- Phase 3:
  - `python -m pytest -q tests/test_factories.py tests/test_assemble_coverage.py tests/test_full_payloads.py`
- Phase 4:
  - `python -m pytest -q tests/test_run_api_contract.py tests/test_runner_protocol.py tests/test_assemble_coverage.py`
- Phase 5:
  - `python -m pytest -q tests/test_report.py tests/test_analysis_registry.py tests/test_verification_report.py tests/test_run_api_contract.py`
- Phase 6:
  - `python -m pytest -q tests/test_import_boundaries.py tests/test_analysis_registry.py tests/test_runner_protocol.py`

Closeout gate:
- `python -m pytest -q`

---

## Net Architectural State After V2.9

- Canonical classical phase authoring is template-first by default.
- Legacy class-based canonical phases are no longer defaulted and are explicitly isolated.
- Custom control-flow phase exceptions remain explicit and policy-scoped.
- Experiment and analysis expose stable public orchestration facades.
- API cross-layer integrations are facade-first and guarded by import-boundary tests.
- V2.9 closes template-first migration and public-surface hardening while preserving existing external behavior.

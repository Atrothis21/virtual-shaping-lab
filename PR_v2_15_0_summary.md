# V2.15 Summary - UI Sprint Enablement Layer

## Overview
V2.15 delivers the backend enablement layer needed for browser usability work without coupling UI code to runtime internals.

Primary outcomes:
- added typed UI metadata contracts and completeness validation across phase/protocol/report catalogs
- populated catalog metadata with explicit labels/descriptions/schema/defaults/constraints/examples
- introduced a typed phenomena catalog with protocol-backed validation
- exposed phenomena through extension/API catalog payloads
- implemented opt-in runtime debug telemetry contract and emission
- added anti-drift guards for catalog completeness and UI adapter import boundaries
- added UI integration documentation for catalog-driven and debug-enabled browser flows

---

## Delivered Changes

### 1) Shared UI Catalog Metadata Contracts
Added:
- `virtual_shaping_lab/domain/catalog_metadata.py`

Includes:
- `UICatalogMetadata`
- `make_default_ui_metadata(...)`
- `validate_ui_metadata_map(...)`

Applied in:
- `virtual_shaping_lab/experiment/phases/catalog_runtime.py`
- `virtual_shaping_lab/protocols/catalog.py`
- `virtual_shaping_lab/analysis/report/catalog.py`

### 2) Phase Catalog Metadata Completion
Updated:
- `virtual_shaping_lab/experiment/phases/catalog_runtime.py`

Behavior:
- replaced generic metadata placeholders with explicit per-phase metadata for:
  - canonical template-backed phases
  - control-flow phases
  - template aliases
- retained canonical phase keys and runtime construction behavior

### 3) Protocol + Report Metadata Completion
Updated:
- `virtual_shaping_lab/protocols/catalog.py`
- `virtual_shaping_lab/analysis/report/catalog.py`

Behavior:
- added explicit per-protocol metadata contracts
- added explicit report-template metadata contracts
- preserved protocol builder and default report resolution behavior

### 4) Phenomena Layer (Typed Registry)
Added:
- `virtual_shaping_lab/experiment/phenomena/catalog.py`
- `virtual_shaping_lab/experiment/phenomena/__init__.py`

Includes:
- `PhenomenonSpec`
- `PHENOMENA_REGISTRY`
- `available_phenomena()`, `get_phenomenon(...)`
- `validate_phenomena_registry(...)` with fail-fast protocol reference checks

### 5) API Exposure for Phenomena
Updated:
- `virtual_shaping_lab/api/extensions.py`
- `virtual_shaping_lab/experiment/public.py`

Behavior:
- `ExtensionCatalog.snapshot()` now includes `phenomena`
- added `experiment.public.list_phenomena()` facade helper
- updated API snapshot/contract tests for new payload shape

### 6) Runtime Debug Contract + Emission
Updated:
- `virtual_shaping_lab/experiment/config.py`
- `virtual_shaping_lab/experiment/plan_builder.py`
- `virtual_shaping_lab/experiment/parameters/types.py`
- `virtual_shaping_lab/experiment/parameters/pipeline.py`
- `virtual_shaping_lab/experiment/parameters/composer.py`
- `virtual_shaping_lab/experiment/runner.py`
- `virtual_shaping_lab/experiment/trial_executor.py`
- `virtual_shaping_lab/experiment/runtime_records.py`

Behavior:
- introduced `runtime.debug` (default `false`) as a validated config/runtime parameter
- added debug schema validator at record finalization boundary
- emits `record["debug"]` only when debug mode is enabled
- keeps non-debug runs schema-compatible and unchanged

Debug payload fields:
- `value`
- `prediction_error`
- `active_features`
- `attention_effective`
- `salience_effective`

### 7) Guardrails and Boundary Enforcement
Added/updated:
- `tests/v2_11_guards/test_catalog_metadata_completeness_guard.py`
- `tests/v2_11_guards/test_ui_adapter_import_guard.py`
- `tests/v2_11_guards/test_factory_boundary_usage_guard.py`
- `tests/v2_11_guards/test_no_legacy_shim_paths_guard.py`

Behavior:
- enforces metadata completeness in canonical catalogs
- enforces no runtime-internal imports in UI adapter path (`api/extensions.py`)
- closes indirect `phase_factory` import loophole
- hardens legacy-shim import guard using AST import analysis (avoids string false positives)

### 8) UI Integration Documentation
Added:
- `docs/ui_integration_catalogs_and_debug.md`

Covers:
- extension catalog contract
- phenomena payload shape
- catalog metadata usage model
- runtime debug toggle and emitted schema
- recommended UI data flow and boundary rules

---

## Test Coverage and Validation

Targeted gates run during implementation included:
- `python -m pytest -q tests/test_phase_catalog_runtime.py tests/test_protocol_catalog.py tests/test_analysis_report_catalog.py`
- `python -m pytest -q tests/test_phase_catalog_runtime.py tests/test_phases.py`
- `python -m pytest -q tests/test_protocol_catalog.py tests/test_analysis_report_catalog.py tests/test_analysis_registry.py`
- `python -m pytest -q tests/test_protocol_catalog.py tests/test_behavioral_phenomena_defaults.py tests/test_phenomena_catalog.py`
- `python -m pytest -q tests/test_extension_catalog.py tests/test_api_contract_snapshots.py tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_config.py tests/test_runtime_records.py tests/test_trial_executor.py`
- `python -m pytest -q tests/test_runner_protocol.py tests/test_runtime_records.py tests/test_sinks.py tests/test_full_payloads.py`
- `python -m pytest -q tests/v2_11_guards tests/test_import_boundaries.py tests/test_extension_catalog.py`
- `python -m pytest -q tests/v2_11_guards/test_factory_boundary_usage_guard.py tests/test_phase_catalog_runtime.py tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_api_contract_snapshots.py tests/test_run_api_contract.py`

Closeout gate:
- `python -m pytest -q`

---

## Net State After V2.15

- backend discovery surfaces are now UI-grade and catalog-driven
- phenomena are first-class API-visible objects, not UI-side mapping tables
- debug telemetry is explicitly contracted, opt-in, and schema-validated
- guardrails prevent drift back into runtime/shim internals for UI paths
- browser integration can proceed with contract-first metadata and telemetry inputs

# V2.16 Summary - UI Contract Hardening Before Dedicated UI Refactor

## Overview
V2.16 hardens the backend/UI contract surfaces so the upcoming UI refactor can rely on stable, explicit, test-protected interfaces instead of runtime internals.

Primary outcomes:
- introduced a canonical UI contract manifest
- added typed builder draft contracts and draft-to-payload translation
- formalized and enforced debug telemetry policy for browser-safe payloads
- converted catalog constraints to machine-checkable canonical symbols
- enriched phenomenon contracts with recommended output guidance
- added explicit version stamps to extension payloads and snapshot protection

---

## Delivered Changes

### 1) Canonical UI Contract Manifest
Added:
- `docs/ui_contract_manifest.md`

Includes:
- endpoint inventory and purpose
- request/response envelope expectations
- lifecycle states and transitions
- required UI rendering fields
- ownership boundaries (UI must not invent runtime-owned fields)
- versioning and snapshot bump policy

Updated cross-links:
- `docs/core_engine_architecture.md`
- `docs/ui_integration_catalogs_and_debug.md`

Result:
- one authoritative UI contract entrypoint for backend-aligned browser integration.

### 2) Builder Draft Contract + Translation Adapter
Added:
- `virtual_shaping_lab/ui/contracts/builder_draft.py`
- `virtual_shaping_lab/ui/contracts/translator.py`
- `virtual_shaping_lab/ui/contracts/__init__.py`

Key contracts:
- `BuilderExperimentDraft`
- `BuilderPhaseDraft`
- `BuilderRuntimeDraft`
- `BuilderDraftValidationError`
- `draft_to_payload(...)`

Test coverage:
- `tests/test_ui_builder_draft_contracts.py`
- `tests/test_ui_builder_draft_translation.py`

Result:
- UI can build runs through typed draft objects and translation, without hand-assembling raw execution payload internals.

### 3) Debug Telemetry Policy and Enforcement
Added:
- `virtual_shaping_lab/experiment/debug_policy.py`
- `docs/debug_telemetry_policy.md`

Updated:
- `virtual_shaping_lab/experiment/trial_executor.py`
- `virtual_shaping_lab/experiment/runner.py`

Policy behavior:
- supports `debug_mode` of `trial`, `tick`, or `both`
- supports bounded debug output via `debug_max_active_features`
- supports decimation via `debug_sample_every_n_ticks`
- preserves backward compatibility with `debug=True`

Result:
- debug payload emission is deterministic and bounded for browser use.

### 4) Machine-Checkable Constraint Semantics
Added:
- `virtual_shaping_lab/domain/catalog_metadata.py`

Updated to canonical constraints:
- `virtual_shaping_lab/experiment/phases/catalog_runtime.py`
- `virtual_shaping_lab/protocols/catalog.py`
- `virtual_shaping_lab/analysis/report/catalog.py`

Tests updated:
- `tests/test_phase_catalog_runtime.py`
- `tests/test_protocol_catalog.py`
- `tests/test_analysis_report_catalog.py`

Result:
- UI gating can rely on canonical constraint symbols instead of free-text parsing.

### 5) Phenomenon Output Guidance Enrichment
Updated:
- `virtual_shaping_lab/experiment/phenomena/catalog.py`
- `virtual_shaping_lab/api/extensions.py`
- `virtual_shaping_lab/experiment/public.py`

`PhenomenonSpec` enrichment:
- `expected_signals`
- `recommended_template_key`
- `recommended_figures`
- `default_run_modes`

Tests updated:
- `tests/test_phenomena_catalog.py`
- `tests/test_extension_catalog.py`

Result:
- teaching-mode/report recommendations are exposed contractually from backend catalogs.

### 6) Extension Payload Version Stamps + Snapshot Lock
Updated:
- `virtual_shaping_lab/api/extensions.py`
- `virtual_shaping_lab/api/run.py`

Added version metadata in extension payload:
- `catalog_version`
- `record_schema_version`
- `template_version_used`

Snapshot updates:
- `tests/fixtures/api_contract_snapshots.json`
- `tests/test_api_contract_snapshots.py`
- `tests/test_run_api_contract.py`

Result:
- UI can detect contract-version mismatches explicitly, and payload drift is CI-visible.

---

## Validation

Representative gates run during V2.16:
- `python -m pytest -q tests/test_api_contract_snapshots.py tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_ui_builder_draft_contracts.py tests/test_validate_payload.py tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_ui_builder_draft_translation.py tests/test_full_payloads.py tests/test_validate_payload.py tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_runtime_records.py tests/test_trial_executor.py`
- `python -m pytest -q tests/test_runner_protocol.py tests/test_runtime_records.py tests/test_full_payloads.py`
- `python -m pytest -q tests/test_phase_catalog_runtime.py tests/test_protocol_catalog.py tests/test_analysis_report_catalog.py`
- `python -m pytest -q tests/test_phenomena_catalog.py tests/test_extension_catalog.py tests/test_api_contract_snapshots.py`
- `python -m pytest -q tests/test_extension_catalog.py tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_api_contract_snapshots.py tests/test_run_api_contract.py`

Closeout full-suite run is planned in slice 6.2.

---

## Compatibility Notes

- Public run/report API shapes remain backward compatible, with additive metadata fields.
- Debug behavior preserves existing `debug=True` usage while enabling stricter policy controls.
- Builder draft contracts are additive and do not remove existing payload-based execution paths.

---

## Net State After V2.16

- backend/UI contract boundary is explicit, documented, and snapshot-protected
- UI-facing constraints and phenomenon guidance are machine-consumable
- debug telemetry is bounded and policy-driven
- extension/catalog payloads now expose explicit version stamps for safer browser integration

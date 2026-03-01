## Overview
V2.5.1 hardens the V2.5 browser/API contract by adding provenance guarantees, run-plan drift protection, lifecycle transition enforcement, and store abstraction seams.

Primary outcomes:
- run execution now binds to resolved `ExperimentPlan` semantics
- provenance metadata is explicit and auditable across run/status/report paths
- lifecycle labels/transitions are centralized and validated
- status storage now has an interface seam for future persistence backends
- regeneration metadata now reports source-provenance completeness

---

## Delivered Changes

### 1) Provenance Metadata on Run and Report Contracts
Updated:
- `virtual_shaping_lab/api/contracts.py`
- `virtual_shaping_lab/api/services.py`
- `virtual_shaping_lab/api/run.py`

Added/propagated metadata fields:
- `plan_hash`
- `record_schema_version`
- `template_version_used`

Applied to:
- `POST /run` response
- `GET /runs/{run_id}` response
- `POST /runs/{run_id}/report` response

---

### 2) Run Drift Guard and Resolved-Plan Execution
Updated:
- `virtual_shaping_lab/api/services.py` (`RunService`)

Behavior:
- run path now executes from resolved `ExperimentPlan` object (`assemble_experiment(plan)`), not a parallel config-only execution path.
- optional `expected_plan_hash` guard added to `RunService.execute(...)`:
  - mismatch raises explicit error.

Result:
- reduces risk of plan/run drift for browser/API workflows.

---

### 3) Lifecycle Contract Centralization and Transition Validation
Added:
- `virtual_shaping_lab/api/lifecycle.py`

Includes:
- lifecycle constants
- allowed transition graph
- transition validator

Updated:
- `virtual_shaping_lab/api/contracts.py` now uses lifecycle constants
- `virtual_shaping_lab/api/services.py` enforces lifecycle transitions on status writes

Note:
- idempotent same-state writes are allowed to handle repeated persistence safely.

---

### 4) Run Status Store Abstraction Seam
Added:
- `virtual_shaping_lab/api/stores.py`
  - `RunStatusStoreProtocol`
  - `InMemoryRunStatusStore`

Updated:
- `virtual_shaping_lab/api/services.py`
  - services now accept optional injected status store
  - retained backward-compatible `RunStatusStore` facade for existing callers/tests

Result:
- clean seam for future persistent/distributed status storage in V2.6+.

---

### 5) Regeneration Determinism and Source-Provenance Completeness
Updated:
- `virtual_shaping_lab/api/services.py` (`ReportService.create_default`)

Added regeneration metadata:
- `regeneration_mode = "from_artifacts"`
- `source_metadata_complete` (`bool`)
- `missing_source_metadata` (`list[str]`)

Result:
- regeneration paths are now explicit about provenance completeness and degraded-source conditions.

---

### 6) Documentation Closeout
Updated:
- `docs/browser_recovery_checklist.md`

Added verification points for provenance metadata and regeneration completeness fields.

---

## Test Coverage

Updated/added tests:
- `tests/test_run_api_contract.py`
- `tests/test_api_lifecycle.py`

Notable coverage:
- run/report metadata field presence and consistency
- expected plan hash mismatch rejection
- resolved-plan execution path assertion
- lifecycle transition validity/invalidity checks
- injected status-store support
- regeneration missing-source metadata diagnostics

---

## Validation

Executed and passing during 2.5.1 work:
- `python -m pytest -q tests/test_run_api_contract.py tests/test_config.py`
- `python -m pytest -q tests/test_run_api_contract.py tests/test_full_payloads.py tests/test_assemble_coverage.py`
- `python -m pytest -q tests/test_api_lifecycle.py tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_run_api_contract.py tests/test_report.py tests/test_analysis_report_catalog.py`

Final release gate:
- `python -m pytest -q`

---

## Net Result

V2.5.1 reinforces V2.5’s browser-facing API into a stronger contract:
- execution semantics are less drift-prone
- response payloads carry enough provenance for auditing/replay
- lifecycle is enforced as a contract, not just conventions
- status persistence is now swappable without API surgery


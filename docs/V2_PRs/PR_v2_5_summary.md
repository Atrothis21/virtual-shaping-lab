## Overview
V2.5 restores browser-facing simulator execution as a contract-first API surface built on top of the V2.4 runtime platform.

Primary outcomes:
- explicit API DTO contracts for plan/run/status/report flows
- service-layer orchestration (`PlanService`, `RunService`, `ReportService`)
- standardized error envelopes across 400/404/500 paths
- extension discovery endpoint for browser builder flows
- lifecycle transition metadata embedded in responses for UI state-machine alignment

This milestone closes the browser recovery loop:
`PlanDraft -> PlanResolved -> RunComplete -> ReportComplete`.

---

## Delivered Changes

### 1) API DTO Contracts
Added:
- `virtual_shaping_lab/api/contracts.py`

Contracts now include:
- `PlanResolveRequest/Response`
- `RunCreateRequest/Response`
- `RunStatusResponse`
- `ReportCreateRequest/Response`
- `ErrorEnvelope`

Response builders:
- `build_plan_resolve_response(...)`
- `build_run_create_response(...)`
- `build_run_status_response(...)`
- `build_report_create_response(...)`

---

### 2) PlanService and Plan Endpoint
Added:
- `PlanService` in `virtual_shaping_lab/api/services.py`

Added endpoint:
- `POST /plan` in `virtual_shaping_lab/api/run.py`

Behavior:
- validates payload
- resolves deterministic plan via `ExperimentConfig.plan_from_payload(...)`
- returns `plan` + `stable_hash`

---

### 3) RunService and Status Endpoint
Added:
- `RunService` and in-process `RunStatusStore` in `virtual_shaping_lab/api/services.py`

Updated endpoint:
- `POST /run` now delegates execution to `RunService`

Added endpoint:
- `GET /runs/{run_id}`

Behavior:
- run execution orchestration moved out of HTTP layer
- explicit run state surfaced in response contract

---

### 4) ReportService and Report Endpoint
Added:
- `ReportService` in `virtual_shaping_lab/api/services.py`

Added endpoint:
- `POST /runs/{run_id}/report`

Behavior:
- regenerates report from stored run artifacts (`records.json`, `payload.json`)
- returns report artifacts + structured metadata:
  - `source_run_id`
  - `preset`
  - `regenerated`

---

### 5) Unified Error Envelope Mapping
Added:
- `virtual_shaping_lab/api/errors.py`

Centralized helpers:
- `raise_validation_error(...)`
- `raise_not_found(...)`
- `raise_internal_error(...)`

Applied across API endpoints so all errors use:
- `detail.code`
- `detail.message`
- `detail.details`

---

### 6) Extension Discovery SDK Surface
Added:
- `virtual_shaping_lab/api/extensions.py` with `ExtensionCatalog`

Added endpoint:
- `GET /catalog/extensions`

Unified discovery payload includes normalized deterministic:
- protocols
- learners
- policies
- representations
- report templates

---

### 7) UI Lifecycle Contract Alignment
Added lifecycle metadata to success responses:
- `PlanResolveResponse.lifecycle`
- `RunCreateResponse.lifecycle`
- `RunStatusResponse.lifecycle`
- `ReportCreateResponse.lifecycle`

Lifecycle states now explicitly surfaced:
- `PlanResolved`
- `RunInProgress` / `RunComplete`
- `ReportComplete`

Next actions emitted for client transitions (e.g., `create_run`, `create_report`, `view_report`).

---

### 8) Browser Recovery Checklist
Added:
- `docs/browser_recovery_checklist.md`

Covers:
- API flow verification
- artifact path verification
- lifecycle state verification
- regression gate checklist

---

## Test Coverage and Validation

Updated/added tests:
- `tests/test_run_api_contract.py`
- `tests/test_extension_catalog.py`

Relevant suites run during implementation:
- `python -m pytest -q tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_run_api_contract.py tests/test_config.py tests/test_assemble_coverage.py`
- `python -m pytest -q tests/test_run_api_contract.py tests/test_runner_protocol.py tests/test_full_payloads.py`
- `python -m pytest -q tests/test_run_api_contract.py tests/test_report.py tests/test_analysis_registry.py tests/test_verification_report.py`
- `python -m pytest -q tests/test_extension_catalog.py tests/test_protocol_catalog.py tests/test_analysis_report_catalog.py tests/test_factories.py tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_run_api_contract.py tests/test_full_payloads.py`

Final release gate:
- `python -m pytest -q`

---

## Compatibility Notes

- Core runtime and experiment execution contracts remain unchanged.
- API surface is additive (`/plan`, `/runs/{id}`, `/runs/{id}/report`, `/catalog/extensions`).
- Existing `/run` flow remains supported with stronger contracts and lifecycle metadata.

---

## Net Result

V2.5 shifts browser integration from ad-hoc endpoint behavior to a clear contract/service architecture:
- deterministic plan resolution
- explicit run/report orchestration services
- normalized extension discovery
- consistent error semantics
- client-driven lifecycle transitions

The simulator is now positioned for reliable browser operation and downstream UI/API productization.


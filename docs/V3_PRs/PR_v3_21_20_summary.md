# V3.21 Summary - Protocol Contract-to-Runtime Closeout

## Overview
V3.21 closes the protocol line end-to-end: canonical protocol contract ownership, executable protocol core, runtime protocol seam cutover, trace/report promotion, and closeout CI hardening with replay determinism safeguards.

Primary outcomes:
- established canonical symbolic protocol ownership and legality boundaries
- delivered executable protocol operators/presets with canonical bundle execution order
- integrated runtime harness to a single protocol seam (`RuntimeProtocolAdapter.emit/resolve`)
- promoted protocol traces into rollout/report artifacts with stable normalized fields
- added single-path/namespace guardrails and closeout CI aggregation
- completed end-to-end matrix and replay/hash determinism hardening for protocol-trace-inclusive runs

This closeout summarizes V3.21.0, V3.21.5, V3.21.10, V3.21.15, and V3.21.20.

---

## V3.21.0 - Canonical Protocol Contract Ownership

### Objective
Define one canonical protocol grammar owner and legality-first boundary materialization.

### Implemented
Added:
- `virtual_shaping_lab/vsl/protocol/spec.py`
- `virtual_shaping_lab/vsl/protocol/validation.py`
- `virtual_shaping_lab/vsl/protocol/registry.py`
- `virtual_shaping_lab/vsl/protocol/presets.py`
- `virtual_shaping_lab/vsl/protocol/adapters.py`
- `virtual_shaping_lab/vsl/protocol/instantiate.py`

Changes:
- canonical protocol grammar (`ProtocolSpec`) with deterministic identity helpers
- legality validator + typed failure contract (`ProtocolSpecValidationError`)
- deterministic registry/preset payload/hash APIs
- grammar/runtime adapter split and runtime aliasing
- legality-first instantiation boundary and failure catalog

---

## V3.21.5 - Executable Protocol Core

### Objective
Implement executable protocol operators and one canonical protocol bundle execution path.

### Implemented
Added:
- `virtual_shaping_lab/vsl/protocol/operators/*`
- `virtual_shaping_lab/vsl/protocol/output.py`
- `virtual_shaping_lab/vsl/protocol/bundle.py`
- `virtual_shaping_lab/vsl/protocol/executable_presets.py`

Changes:
- typed stage outputs (`EmissionOutput`, `ConsequenceOutput`, `AdvanceOutput`, `StopOutput`)
- canonical execution order:
  - `emit -> consequence -> advance -> stop -> finalize`
- deterministic stage trace metadata in protocol outputs
- executable preset materialization and golden-proof coverage

---

## V3.21.10 - Runtime Protocol Seam Integration

### Objective
Route active runtime harness protocol flow through one canonical runtime seam.

### Implemented
Added:
- `virtual_shaping_lab/vsl/runtime/protocol_adapter.py`

Updated:
- `virtual_shaping_lab/vsl/rollout/harness.py`

Changes:
- runtime protocol seam APIs:
  - `RuntimeProtocolAdapter`
  - `build_runtime_protocol_adapter(...)`
- harness routing to:
  - `protocol_adapter.emit(...)`
  - `protocol_adapter.resolve(...)`
- preserved explicit protocol-agent causal split from `agent_protocol_interaction.md`
- boundary invariants and runtime parity/ordering tests added

---

## V3.21.15 - Trace Promotion and Path Guardrails

### Objective
Promote protocol traces into rollout/report surfaces and enforce single-path/namespace guardrails.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/records/adapters/rollout_records.py`
- `virtual_shaping_lab/analysis/report/report.py`
- `virtual_shaping_lab/vsl/rollout/harness.py`
- `.github/workflows/ci.yml`

Added:
- `tests/test_v3_single_path_protocol_execution.py`
- `tests/test_v3_protocol_namespace_import_audit.py`
- `tests/test_v3_protocol_namespace_hard_removal.py`

Changes:
- rollout protocol trace promotion:
  - `metadata.protocol_traces.*`
- report protocol normalization:
  - `protocol_emission`, `protocol_consequence`, `protocol_advance`, `protocol_stop`, `protocol_timing`, `protocol_provenance`
- bridge markers with owner/expiry for deferred compatibility
- blocking CI bucket for protocol trace + single-path enforcement

---

## V3.21.20 - Closeout CI, Matrix, and Evidence

### Objective
Finalize protocol closeout with integration matrix, determinism hardening, CI aggregation, and architecture evidence artifacts.

### Implemented
Added:
- `tests/test_v3_protocol_integration_matrix.py`
- `docs/v3_21_single_path_protocol_architecture.md`
- `docs/v3_21_pr_evidence_checklist.md`

Updated:
- `tests/test_v3_rollout_replay_harness.py`
- `virtual_shaping_lab/vsl/records/adapters/rollout_records.py`
- `.github/workflows/ci.yml`

Changes:
- end-to-end protocol integration matrix (classical + actioned families)
- replay/hash determinism hardening for protocol-trace-inclusive paths
- payload key-order stability assertions for protocol trace hashing
- final CI aggregation bucket:
  - `Run V3.21 protocol closeout gates`

---

## Closeout Impact

After V3.21:
- protocol ownership is canonical from symbolic grammar through executable runtime seam
- protocol runtime execution is single-path and CI-enforced
- protocol traces are stable across rollout and report artifacts
- protocol-agent causal boundary is explicit, typed, and guarded
- replay/hash determinism is covered for protocol-inclusive flows

V3.21 therefore completes protocol contract-to-runtime closeout and establishes the hardened baseline for downstream protocol evolution.

---

## Validation

### Core Gates
Validated via:
- `tests/test_v3_protocol_contract_ownership.py`
- `tests/test_v3_protocol_bundle_execution.py`
- `tests/test_v3_protocol_executable_instantiation.py`
- `tests/test_v3_protocol_golden.py`
- `tests/test_v3_runtime_protocol_adapter.py`
- `tests/test_v3_protocol_runtime_parity.py`
- `tests/test_v3_agent_protocol_loop_contract.py`
- `tests/test_v3_agent_protocol_boundary_invariants.py`
- `tests/test_v3_rollout_record_schema.py -k protocol`
- `tests/test_report.py -k protocol`
- `tests/test_v3_single_path_protocol_execution.py`
- `tests/test_v3_protocol_namespace_import_audit.py`
- `tests/test_v3_protocol_namespace_hard_removal.py`
- `tests/test_v3_protocol_integration_matrix.py`
- `tests/test_v3_rollout_replay_harness.py -k "protocol or replay or hash"`

### CI-Facing Contract Checks
Validated by assertions that:
- protocol ownership/adapter/bundle contracts do not drift
- runtime seam ordering remains causal and explicit
- protocol traces remain promoted and normalized
- single-path execution and namespace hard-removal guardrails stay enforced
- replay/hash determinism remains stable with protocol traces present

---

## Net State After V3.21

- canonical protocol symbolic + executable + runtime seams are fully hardened
- protocol traces and report-normalized protocol fields are stable and test-backed
- closeout CI aggregation is in place and blocking for protocol regressions
- architecture/evidence docs provide auditable change-control standards for future protocol edits

V3.21 is closed out as a protocol-complete, replay-stable, CI-guarded baseline.

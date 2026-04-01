# V3.21.15 Summary - Protocol Trace Promotion and Legacy Path Removal

## Overview
V3.21.15 promotes protocol traces into rollout/report artifacts, removes duplicate runtime protocol-path logic from active harness semantics, and adds blocking guardrails to prevent regression back to legacy protocol execution and import paths.

Primary outcomes:
- promoted protocol-stage traces into rollout record metadata with stable trace/provenance/timing keys
- normalized protocol trace fields into report artifacts for downstream consumers
- removed duplicated harness-local protocol action-semantics inference and aligned semantics to protocol emission outputs
- added explicit bridge markers (owner + expiry) for deferred runtime compatibility paths
- added single-path protocol execution and namespace hard-guard tests
- added blocking CI bucket for protocol trace promotion and single-path enforcement

This slice closes the V3.21.15 milestone for protocol trace promotion and runtime single-path hardening.

---

## Slice 1 - Rollout Record Protocol Trace Promotion

### Objective
Promote protocol stage traces to first-class rollout record metadata fields.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/records/adapters/rollout_records.py`
- `tests/test_v3_rollout_record_schema.py`
- `V3.21.15_plan.md`

Changes:
- added protocol trace promotion into rollout records:
  - `metadata.protocol_traces.emission`
  - `metadata.protocol_traces.consequence`
  - `metadata.protocol_traces.advance`
  - `metadata.protocol_traces.stop`
  - `metadata.protocol_traces.provenance.preset_name`
  - `metadata.protocol_traces.provenance.pipeline_order`
  - `metadata.protocol_traces.timing.t`
  - `metadata.protocol_traces.timing.phase_step`
  - `metadata.protocol_traces.timing.dt_s`
- added schema gate:
  - `test_v3_rollout_step_adapter_promotes_protocol_traces_into_record_metadata`

---

## Slice 2 - Report Normalization for Protocol Traces

### Objective
Normalize protocol trace fields into stable report-facing record surfaces.

### Implemented
Updated:
- `virtual_shaping_lab/analysis/report/report.py`
- `tests/test_report.py`
- `V3.21.15_plan.md`

Changes:
- added normalized report fields:
  - `protocol_emission`
  - `protocol_consequence`
  - `protocol_advance`
  - `protocol_stop`
  - `protocol_timing`
  - `protocol_provenance`
- added compatibility bridge behavior:
  - prefer `metadata.protocol_traces`
  - fallback to `metadata.protocol` when needed
- added report contract gate:
  - `test_normalize_record_for_artifact_promotes_protocol_traces`

---

## Slice 3 - Legacy Runtime Path Cleanup

### Objective
Remove duplicated runtime protocol-path logic and make deferred compatibility explicit.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/rollout/harness.py`
- `V3.21.15_plan.md`

Changes:
- removed duplicated harness-local operant/classical protocol-name inference for trial-state semantics
- aligned operant action semantics to canonical protocol emission ownership (`protocol_pre.available_actions`)
- added explicit deferred bridge markers with owner + expiry:
  - `metadata.protocol.bridge_markers.external_action_override`
  - `metadata.protocol.bridge_markers.compiled_plan_reward_override`

---

## Slice 4 - Namespace and Import Hard Guards

### Objective
Add hard guardrails that fail fast on single-path regressions and legacy protocol namespace drift.

### Implemented
Added:
- `tests/test_v3_single_path_protocol_execution.py`
- `tests/test_v3_protocol_namespace_import_audit.py`
- `tests/test_v3_protocol_namespace_hard_removal.py`

Updated:
- `V3.21.15_plan.md`

Changes:
- added single-path harness guard checks for protocol seam usage (`emit -> resolve`)
- added runtime import audit for banned legacy protocol surfaces
- added hard-removal checks for legacy protocol module paths

---

## Slice 5 - CI Bucket for Trace + Single-Path Enforcement

### Objective
Add blocking CI enforcement for protocol trace promotion and protocol single-path runtime contracts.

### Implemented
Updated:
- `.github/workflows/ci.yml`
- `V3.21.15_plan.md`

Changes:
- added blocking CI step:
  - `Run V3.21.15 protocol trace and single-path enforcement`
- CI bucket includes:
  - `tests/test_v3_rollout_record_schema.py -k protocol`
  - `tests/test_report.py -k protocol`
  - `tests/test_v3_single_path_protocol_execution.py`
  - `tests/test_v3_protocol_namespace_import_audit.py`
  - `tests/test_v3_protocol_namespace_hard_removal.py`

---

## Closeout Impact

After V3.21.15:
- protocol traces are first-class in rollout records and normalized report artifacts
- runtime protocol flow remains single-path through canonical runtime protocol seam surfaces
- legacy runtime protocol bypass risk is reduced and deferred bridges are explicit/auditable
- namespace/import guardrails and CI bucket block regressions to removed protocol paths

V3.21.15 therefore completes protocol trace promotion and protocol runtime-path guardrail hardening for the V3.21 line.

---

## Validation

### Slice and Contract Gates
Validated via:
- `tests/test_v3_rollout_record_schema.py` (protocol trace gates)
- `tests/test_report.py` (protocol normalization gates)
- `tests/test_v3_single_path_protocol_execution.py`
- `tests/test_v3_protocol_namespace_import_audit.py`
- `tests/test_v3_protocol_namespace_hard_removal.py`

### CI-Facing Contract Checks
Validated by assertions that:
- protocol stage traces are promoted and stable in rollout/report surfaces
- runtime harness protocol flow remains seam-mediated and single-path
- legacy protocol namespace/import drift fails fast
- removed protocol module paths remain hard-removed

---

## Net State After V3.21.15

- protocol trace promotion is active in rollout and report outputs
- runtime protocol execution contracts are guarded by single-path and namespace hard checks
- deferred compatibility bridges are explicitly marked with owner/expiry metadata
- blocking CI enforcement is in place for protocol trace and single-path regression prevention

V3.21.15 establishes the guardrailed baseline for post-V3.21 protocol trace/report consumption and downstream runtime simplification work.

## Validation Commands

Targeted gates for local/CI execution:
- `python -m pytest -q tests/test_v3_rollout_record_schema.py -k protocol`
- `python -m pytest -q tests/test_report.py -k protocol`
- `python -m pytest -q tests/test_v3_single_path_protocol_execution.py tests/test_v3_protocol_namespace_import_audit.py tests/test_v3_protocol_namespace_hard_removal.py`

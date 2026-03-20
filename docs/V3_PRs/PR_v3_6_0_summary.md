# V3.6.0 Summary - Rollout Engine and Record Schema Finalization

## Overview
V3.6.0 finalizes rollout records as a stable runtime-analysis boundary and adds deterministic replay identity gates.

Primary outcomes:
- introduced a locked V3 rollout record schema with explicit versioning/migration policy
- expanded rollout identity fields (`rollout_id`, `episode_id`, `segment_index`) at the record boundary
- added a deterministic replay harness that emits typed rollout records and stable stream hashes
- added a 10/10 replay determinism gate for fixed identity inputs
- enabled records-only report regeneration when `payload.json` is missing
- completed CI closure so rollout/records tests are enforced in the blocking workflow

This slice makes rollout artifacts more deterministic, more auditable, and less coupled to runtime payload reconstruction.

---

## Slice 1 - RolloutRecord Schema Lock

### Objective
Introduce and lock rollout record schema/version rules.

### Implemented
Added:
- `virtual_shaping_lab/vsl/records/types.py`
- `virtual_shaping_lab/vsl/records/__init__.py`
- `virtual_shaping_lab/vsl/rollout/records.py`
- `virtual_shaping_lab/vsl/rollout/__init__.py`

Updated:
- `virtual_shaping_lab/vsl/__init__.py`

Added tests:
- `tests/test_v3_rollout_record_schema.py`

Changes:
- introduced `RolloutRecord` typed boundary with deterministic serialization/hash
- introduced locked schema constants:
  - `ROLLOUT_RECORD_SCHEMA_VERSION = "v1"`
  - `SUPPORTED_ROLLOUT_RECORD_SCHEMA_VERSIONS = ("v1",)`
- added explicit migration-policy validator and schema-aware normalization helpers
- added `EnvironmentStep -> RolloutRecord` adapter path

---

## Slice 2 - Identity Field Expansion

### Objective
Add rollout/episode/segment identity at the record boundary.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/records/types.py`
- `virtual_shaping_lab/vsl/rollout/records.py`
- `tests/test_v3_rollout_record_schema.py`

Changes:
- added identity fields:
  - `rollout_id`
  - `episode_id`
  - `segment_index`
- added validation constraints for identity fields
- propagated identity through rollout-step adapter and test assertions

---

## Slice 3 - Replay Harness

### Objective
Implement deterministic replay harness for environment-based rollouts.

### Implemented
Added:
- `virtual_shaping_lab/vsl/rollout/replay.py`
- `tests/test_v3_rollout_replay_harness.py`

Updated:
- `virtual_shaping_lab/vsl/rollout/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`

Changes:
- added `ReplayHarness` that executes `IEnvironment` and emits `RolloutRecord` streams
- added `stable_rollout_hash(records)` stream hash helper
- added determinism gate:
  - fixed identity inputs must produce hash-identical outputs across 10/10 runs
- added identity sensitivity gate:
  - changing rollout identity changes stable stream hash

---

## Slice 4 - Records-Only Reporting

### Objective
Ensure reports can be regenerated from persisted records without runtime coupling.

### Implemented
Updated:
- `virtual_shaping_lab/api/services.py`
- `tests/test_run_api_contract.py`

Changes:
- `ReportService.create_default(...)` now supports regeneration when `payload.json` is absent
- regeneration now uses `records.json` + persisted status metadata fallback in records-only mode
- metadata output remains populated for:
  - `plan_hash`
  - `record_schema_version`
  - `seed_identity`
  - `operator_pipeline_identity`
  - `learner_identity`
- added explicit regeneration mode distinction:
  - `from_artifacts` (payload present)
  - `from_records` (payload missing)
- fixed records-only fallback preset to a valid report preset key (`acquisition`)

---

## Completion Pass - CI and Exit-Criteria Closure

### Objective
Close remaining partial criteria by enforcing rollout/records gates in blocking CI.

### Implemented
Updated:
- `.github/workflows/ci.yml`

Changes:
- added blocking `Run V3 rollout/records bucket` step running:
  - `tests/test_v3_rollout_record_schema.py`
  - `tests/test_v3_environment_rollout_harness.py`
  - `tests/test_v3_rollout_replay_harness.py`
  - `tests/test_run_api_contract.py`
  - `tests/test_report.py`

Net effect:
- schema/migration policy checks and replay determinism checks are now enforced by blocking CI, not only by local/full-suite runs

---

## Closeout Impact

After V3.6.0:
- rollout records are version-locked, identity-aware, and hash-stable
- replay determinism is explicitly test-gated at the rollout-record boundary
- report regeneration can proceed from records artifacts even when canonical payload artifact is unavailable
- rollout/records invariants are enforced in blocking CI

This slice completes the rollout/records finalization needed for stable downstream analysis and artifact replay behavior.

---

## Validation

### Slice and Completion Gates
Validated through targeted suites:
- `tests/test_v3_rollout_record_schema.py`
- `tests/test_v3_environment_rollout_harness.py`
- `tests/test_v3_rollout_replay_harness.py`
- `tests/test_run_api_contract.py`
- `tests/test_report.py`

### CI-Facing Contract Checks
Validated by assertions that:
- unsupported schema migrations hard-fail
- identity fields are preserved and validated at record boundary
- fixed identity replay is hash-identical for 10/10 runs
- records-only regeneration works when payload artifact is missing
- rollout/records gates are part of blocking workflow execution

---

## Net State After V3.6.0

- rollout/record schema governance is explicit and version-locked
- deterministic replay identity is measurable and enforced
- report regeneration is less coupled to runtime payload artifacts
- CI now blocks on rollout/records contract regressions

V3.6.0 therefore closes the rollout/records stability and replay-governance gap in the V3 sequence.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_rollout_record_schema.py tests/test_v3_environment_rollout_harness.py tests/test_v3_rollout_replay_harness.py`
- `python -m pytest -q tests/test_run_api_contract.py tests/test_report.py`

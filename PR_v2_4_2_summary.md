## Overview
V2.4.2 hardens the runtime record boundary by completing the first full `RecordFinalizationPipeline` pass:

- migrated record finalization to composable normalizer stages
- added optional strict-mode validation checks (off by default)
- added schema migration hook (`v1 -> v1` no-op, unsupported paths fail fast)

This establishes a stable foundation for future record-schema evolution and stronger runtime invariants.

---

## Delivered Changes

### 1) Record Finalization Pipeline Skeleton
Updated:
- `virtual_shaping_lab/experiment/runtime_records.py`

Added:
- `FinalizationContext`
- `RecordNormalizer` protocol
- `SchemaDefaultsNormalizer`
- `ProtocolMetadataNormalizer`
- `RecordFinalizationPipeline`
- `DEFAULT_FINALIZATION_PIPELINE`

Public API:
- `finalize_record(...)` retained as façade for behavior parity.

### 2) Strict-Mode Validation Stage
Added:
- `StrictModeValidator`

Behavior when `strict_mode=True`:
- tick records must include:
  - `t_s`
  - `dt_s`
  - `trial_step`
- optional monotonic checks via metadata:
  - `metadata.prev_tick`
  - `metadata.prev_t_s`

Default mode remains backward-compatible (`strict_mode=False`).

### 3) Version Migration Stage
Added:
- `VersionMigrator`

Current migration behavior:
- `v1 -> v1`: no-op
- other paths: explicit `ValueError` until future migrations are implemented

Public API updates:
- `finalize_record(..., from_version='v1', to_version='v1')`

---

## Test Coverage

Updated:
- `tests/test_runtime_records.py`

Now covers:
- façade parity and pipeline parity
- strict-mode required-field checks
- strict-mode monotonicity checks
- default-mode compatibility
- migration no-op (`v1 -> v1`)
- unsupported migration rejection

Validation run:
- `python -m pytest -q tests/test_runtime_records.py tests/test_runner_protocol.py`

---

## Compatibility Notes

- No breaking change to existing runner/protocol execution paths.
- Strict validation is opt-in.
- Migration stage currently enforces explicit failure for unsupported version jumps by design.


# PR Summary: V2.2 Runtime Finalization and Hard-Cut Migration

## Overview
This PR completes the V2.2 runtime architecture program end-to-end:

- made intra-trial time **executable** (not just contractual)
- migrated all phases to native runnable-unit contracts
- unified protocol execution on runnable composition semantics
- made plans fully resolved/serializable/replay-stable
- introduced stable record and runtime extension contracts (hooks/sinks)
- completed structure reshaping and then performed hard-cut cleanup
- removed legacy fallback/shims and realigned tests/CI accordingly

This is the completion pass from “time-ready” to “time-true + strict runtime.”

---

## Goals Delivered

### 1. Intra-Trial Time Execution
- Added `TrialSchedule` and tick-level `TrialExecutor`.
- Runner supports:
  - `update_mode`: `trial | tick`
  - `record_mode`: `trial | tick`
- Tick loop now handles:
  - event/window activation over `t=0..duration` by `dt`
  - observation updates with `t_s`, `dt_s`, `trial_step`, `trial_id`
  - optional per-tick learning updates
  - optional per-tick record emission

### 2. Native Runnable Migration (All Phases)
- All phase classes now implement native runnable hooks:
  - `reset(ctx)`
  - `iter_steps(ctx)`
  - optional `build_trial_schedule(ctx, trial_index)`
- No phase remains dependent on legacy `has_next_trial + step` execution in runner.

### 3. Strict Runtime Semantics
- Runner now executes runnable units only.
- Legacy phase fallback path has been removed.
- Error path is explicit: units must implement `iter_steps(context)`.

### 4. Unified Protocol Composition
- `BaseProtocol` now composes child runnable units via `iter_steps(ctx)` only.
- Protocol iteration no longer depends on phase internals (`phase.step()` logic in protocol loop removed).
- Standardized protocol metadata propagation:
  - `protocol_name`
  - `subphase`
  - `subphase_name`
  - `unit_path`

### 5. Fully Resolved Immutable Plans
- `ExperimentPlan` now supports:
  - deterministic `to_dict()`
  - `from_dict()`
  - stable `stable_hash()` fingerprint
- Plan building now resolves representation contexts and inferred phase contexts up front.
- `assemble_experiment(plan)` respects resolved plans and skips runtime inference paths.

### 6. Stable TrialRecord Contract
- Added stable typed `TrialRecord` schema contract in experiment domain types.
- `finalize_record(...)` now enforces schema defaults so all emitted records have required base keys.
- Analysis/reporting receives consistent core fields independent of emitting unit.

### 7. Hooks / Events Extensibility
- Added `RunnerHooks` with lifecycle callbacks:
  - `on_unit_start`, `on_unit_end`
  - `on_trial_start`, `on_trial_end`
  - `on_tick`
- Runner and tick executor emit these hooks without embedding subscriber logic.

### 8. Sink Expansion
- Added:
  - `JsonlSink` (append-only durable stream output)
  - `CompositeSink` (fan-out to multiple sinks)
- Retained `InMemorySink`.
- Added runtime and sink unit tests for ordering/fan-out/write behavior.

### 9. Structure Reshaping and Hard-Cut Cleanup
- Implemented namespace reshaping compatibility layer during migration.
- Completed hard-cut cleanup:
  - removed legacy runtime fallback execution path
  - removed compatibility shim namespaces
  - removed shim compatibility tests
  - added hard-cut guard tests preventing reintroduction of legacy shim imports/modules

---

## Major Files/Areas Touched

### Runtime Core
- `virtual_shaping_lab/experiment/runner.py`
- `virtual_shaping_lab/experiment/trial_executor.py`
- `virtual_shaping_lab/experiment/hooks.py`
- `virtual_shaping_lab/experiment/runtime_records.py`
- `virtual_shaping_lab/experiment/sinks.py`

### Domain Contracts
- `virtual_shaping_lab/experiment/domain/types.py`
- `virtual_shaping_lab/experiment/domain/interfaces.py`

### Assembly / Planning
- `virtual_shaping_lab/experiment/plan_builder.py`
- `virtual_shaping_lab/experiment/assemble.py`

### Phase and Protocol Runtime Contracts
- `virtual_shaping_lab/experiment/phases/*` (all canonical phases migrated)
- `virtual_shaping_lab/protocols/base.py`

### CI / Test Gates
- `.github/workflows/ci.yml`
- New/updated tests including:
  - `tests/test_trial_executor.py`
  - `tests/test_runner_protocol.py`
  - `tests/test_sinks.py`
  - `tests/test_runtime_records.py`
  - `tests/test_experiment_hardcut_guards.py`
  - updates to `tests/test_phases.py`, `tests/test_config.py`, others as needed

---

## Breaking Changes

1. Runner no longer supports legacy non-runnable phase execution.
2. Compatibility namespace shims introduced during transition were removed in hard-cut phases.
3. Tests and CI now enforce post-legacy runtime semantics and guard against shim reintroduction.

---

## Validation and Test Gates

During implementation, the following gates were repeatedly run and passed:

- Runner/protocol/runtime slices:
  - `tests/test_runner_protocol.py`
  - `tests/test_protocols.py`
  - `tests/test_trial_executor.py`
  - `tests/test_runtime_records.py`
  - `tests/test_sinks.py`
- Phase and assembly slices:
  - `tests/test_phases.py`
  - `tests/test_config.py`
  - `tests/test_assemble_coverage.py`
- Integration/API behavioral slices:
  - `tests/test_full_payloads.py`
  - `tests/test_run_api_contract.py`

Observed warnings are limited to existing visualization tick-label warnings and do not indicate runtime contract failures.

---

## Net Architectural State After V2.2

- Runtime execution is contract-first and runnable-only.
- Intra-trial timing is executable and configurable.
- Protocols are pure runnable compositions.
- Plan objects are deterministic, serializable, and replay-oriented.
- Record schema is stable at runtime boundaries.
- Hooks and sinks provide clean extension points.
- Legacy compatibility paths have been removed and guarded in tests.

V2.2 is complete as a runtime architecture milestone.

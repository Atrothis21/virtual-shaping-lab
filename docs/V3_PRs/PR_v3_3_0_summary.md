# V3.3.0 Summary - First-Class Environment Contract and TrialState Runtime Path

## Overview
V3.3.0 makes environment stepping a first-class runtime contract and introduces typed `TrialState` as the canonical carrier for environment-side state coordinates.

Primary outcomes:
- `vsl/environment` now defines explicit typed environment contracts and termination/reset semantics
- `TrialState` is introduced with canonical coordinates `s,x,z,w,a,u,y,m`
- persistent vs derived state boundaries are enforced (`m.persistent` vs `m.derived`)
- action-field semantics are unified, including classical null/singleton behavior
- runner now supports an end-to-end `IEnvironment` stepping path
- environment-path runtime records now carry typed `TrialState` metadata and deterministic replay checks

This slice transitions V3 runtime shape from phase-only stepping assumptions to an explicit environment contract path suitable for later full migration.

---

## Slice 1 - Environment Contract Types

### Objective
Introduce `IEnvironment` and typed environment objects.

### Implemented
Added:
- `virtual_shaping_lab/vsl/environment/contracts.py`
- `virtual_shaping_lab/vsl/environment/harness.py`
- `virtual_shaping_lab/vsl/environment/__init__.py`

Updated:
- `virtual_shaping_lab/vsl/__init__.py`

Added tests:
- `tests/test_v3_environment_rollout_harness.py`
- `tests/test_v3_environment_contract_types.py`

Changes:
- introduced typed contract objects:
  - `IEnvironment`
  - `EnvironmentReset`
  - `EnvironmentTermination`
  - `EnvironmentStep`
- added deterministic test-mode environment/harness:
  - `CompiledProgramTestEnvironment`
  - `RolloutHarness`

---

## Slice 2 - TrialState Carrier

### Objective
Add `TrialState` with canonical coordinates `s,x,z,w,a,u,y,m`.

### Implemented
Added:
- `virtual_shaping_lab/vsl/environment/trial_state.py`

Updated:
- `virtual_shaping_lab/vsl/environment/contracts.py`
- `virtual_shaping_lab/vsl/environment/harness.py`
- `virtual_shaping_lab/vsl/environment/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`

Added tests:
- `tests/test_v3_trial_state.py`

Changes:
- added typed `TrialState` carrier with required coordinate schema
- wired environment-step emission to include `trial_state` payload
- enforced coordinate-presence gate for `TrialState.from_dict(...)`

---

## Slice 3 - Persistent vs Derived Semantics

### Objective
Encode/validate boundary between persistent coordinates and derived outputs (`prediction`, `error`).

### Implemented
Updated:
- `virtual_shaping_lab/vsl/environment/trial_state.py`
- `virtual_shaping_lab/vsl/environment/harness.py`
- `tests/test_v3_trial_state.py`
- `tests/test_v3_environment_contract_types.py`

Changes:
- enforced split:
  - `m.persistent` for persistent metadata
  - `m.derived` for derived outputs
- added validation rules:
  - `prediction`/`error` forbidden in `m.persistent`
  - only `prediction`/`error` allowed in `m.derived`
- added helpers:
  - `TrialState.from_components(...)`
  - `TrialState.persistent_metadata()`
  - `TrialState.derived_outputs()`

---

## Slice 4 - Action Field Unification

### Objective
Enforce always-present `u` field with null/singleton behavior for classical paths.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/environment/trial_state.py`
- `virtual_shaping_lab/vsl/environment/harness.py`
- `tests/test_v3_trial_state.py`
- `tests/test_v3_environment_rollout_harness.py`

Changes:
- added action-semantic constructor:
  - `TrialState.with_action_semantics(...)`
- enforced action invariants:
  - classical null/singleton behavior (`a=[None], u=None`)
  - operant path allows non-null `u` with explicit action support list
- stabilized derived schema shape by always emitting `prediction` and `error` keys

---

## Slice 5 - Runtime Stepping Migration

### Objective
Route runner/trial stepping through `IEnvironment` end-to-end.

### Implemented
Updated:
- `virtual_shaping_lab/experiment/runner.py`

Added tests:
- `tests/test_v3_runner_environment_integration.py`

Changes:
- added runner environment path:
  - `_run_environment_unit(...)`
  - `Runner.run()` now accepts `IEnvironment` units in addition to runnable-unit protocol
- runner now requires typed `TrialState` on environment steps
- runner environment records now include environment-owned semantics:
  - reward
  - termination metadata
  - typed trial-state payload
- added 10/10 replay determinism integration gate for environment path

---

## Closeout Impact

After V3.3.0:
- environment stepping is now an explicit runtime path, not only a planning abstraction
- typed `TrialState` is established as the canonical environment-state carrier
- persistent vs derived state semantics are enforced in code and tests
- action semantics are unified across classical and operant representations
- runner can execute through `IEnvironment` end-to-end while preserving existing runnable-unit compatibility

This provides the environment contract substrate needed for deeper runtime migration in later V3 slices.

---

## Validation

### Slice Gates
Validated via targeted tests:
- `tests/test_v3_environment_contract_types.py`
- `tests/test_v3_environment_rollout_harness.py`
- `tests/test_v3_trial_state.py`
- `tests/test_v3_runner_environment_integration.py`

### CI-Facing Contract Checks
Validated through integration assertions:
- environment stepping path executes end-to-end through runner
- typed `TrialState` is required on environment step outputs
- replay determinism for identical seed/input holds across 10/10 environment-path runs
- terminal behavior and horizon controls are exercised in rollout harness tests

---

## Net State After V3.3.0

- V3 runtime now includes a first-class environment contract path
- typed `TrialState` is present and validated at environment and runner boundaries
- persistent/derived metadata boundaries are explicit and test-protected
- action semantics are unified and schema-stable
- runner supports both legacy runnable-unit stepping and environment-contract stepping during migration

V3.3.0 therefore completes the first environment-contract runtime cut for V3.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_environment_contract_types.py tests/test_v3_environment_rollout_harness.py`
- `python -m pytest -q tests/test_v3_trial_state.py`
- `python -m pytest -q tests/test_v3_runner_environment_integration.py`
- `python -m pytest -q tests/test_v3_runner_environment_integration.py tests/test_v3_environment_rollout_harness.py tests/test_v3_trial_state.py tests/test_v3_environment_contract_types.py tests/test_runner_protocol.py`

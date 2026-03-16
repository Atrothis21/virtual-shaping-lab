## Overview
V2.4.1 delivers the first semantic-runtime upgrade for operant timing:

- introduced tick-native operant schedule runtime composites
- integrated optional schedule-runtime execution into `TrialExecutor`
- wired operant phase schedule metadata to carry runtime schedule objects
- added deterministic schedule semantics tests and upgraded FI/FR behavioral assertions

This closes the first part of the V2.4 gap: schedule mechanics are now explicitly modelable at tick resolution (while remaining backward-compatible with existing trial-level paths).

---

## Delivered Changes

### 1) Tick-Native Schedule Runtime Composites
Added:
- `virtual_shaping_lab/protocols/schedule_runtime.py`

Includes:
- contracts:
  - `AvailabilityProcess`
  - `ReinforcementGate`
  - `ConsequenceMapper`
- runtime I/O types:
  - `ScheduleTickInput`
  - `ScheduleTickResult`
  - `Consequence`
- concrete strategies:
  - `AlwaysAvailable`
  - `FixedIntervalAvailability`
  - `VariableIntervalAvailability`
  - `FirstResponseGate`
  - `FixedRatioGate`
  - `VariableRatioGate`
  - `ConstantConsequenceMapper`
- composition root:
  - `TickScheduleRuntime`

Test:
- `tests/test_schedule_runtime.py`

### 2) TrialExecutor Integration (Backward-Compatible)
Updated:
- `virtual_shaping_lab/experiment/trial_executor.py`

Behavior:
- if `TrialSchedule.metadata["schedule_runtime"]` is present:
  - runtime is reset per trial with seeded context RNG
  - runtime stepped once per tick
  - runtime reward is combined with event-window reward
  - runtime metadata/event type are added to tick record metadata
- if absent:
  - behavior remains unchanged

Test:
- `tests/test_trial_executor.py` (`test_trial_executor_uses_schedule_runtime_when_provided`)

### 3) Operant Wiring to Emit Schedule Runtime
Updated:
- `virtual_shaping_lab/protocols/reward_schedules.py`
  - each schedule class now exposes `build_tick_runtime(time_spec)` adapter
  - mapped FR/VR/FI/VI schedule parameters to tick-native runtime strategies
- `virtual_shaping_lab/experiment/phases/operant_acquisition.py`
  - `build_trial_schedule(...)` now attaches schedule runtime object in metadata when available

Tests:
- `tests/test_factories.py` (schedule tick-runtime adapter coverage)
- `tests/test_operant_contract_harness.py` (phase attaches `schedule_runtime`)

### 4) Behavioral Signature Upgrade
Updated:
- `tests/behavioral_signatures/test_fi_vs_fr.py`

Now includes:
- existing FR/FI reinforcement-density proxy (kept as secondary signal)
- new deterministic tick-level schedule invariant:
  - FR-1 can reinforce immediately on first response
  - FI is time-gated (first reinforcement delayed by interval)

---

## Validation

Executed and passing:
- `python -m pytest -q tests/test_schedule_runtime.py`
- `python -m pytest -q tests/test_trial_executor.py`
- `python -m pytest -q tests/test_operant_contract_harness.py`
- `python -m pytest -q tests/test_factories.py`
- `python -m pytest -q tests/behavioral_signatures/test_fi_vs_fr.py`
- combined gate:
  - `python -m pytest -q tests/test_schedule_runtime.py tests/test_trial_executor.py tests/test_operant_contract_harness.py tests/test_factories.py tests/test_protocols.py tests/behavioral_signatures/test_fi_vs_fr.py`

---

## Compatibility Notes

- Existing non-tick operant/classical paths remain valid.
- Tick-native schedule execution is opt-in through trial schedule metadata.
- No public API break in runner entrypoints.

---

## Remaining Work (Next PRs)

Deferred to later V2.4 slices:
- migrate additional operant protocols to rely primarily on tick-native schedule semantics
- record finalization pipeline decomposition (V2.4.2)
- report pipeline decomposition and assembly composition root cleanup (V2.4.3)
- config parsing/validation decomposition and hardening (V2.4.4)

# PR Summary: V2.1 Experiment Runtime Refactor

## Overview
This PR completes the V2.1 refactor of the `experiment/` layer into a contract-first runtime architecture that mirrors the v2 agent design.

Primary outcomes:
- explicit experiment domain contracts and interfaces
- plan-based assembly path (`ExperimentConfig -> ExperimentPlan -> assemble_experiment(...)`)
- runner execution centered on `iter_steps(context)` with deterministic context/RNG handling
- record sink abstraction integrated into runtime
- initial native phase migrations to runnable-unit contracts
- protocol composition upgraded to native runnable-unit execution

## Scope Completed (Phases 1-10)

### Phase 1: Foundation Contracts
Added experiment domain scaffolding:
- `experiment/domain/types.py`
- `experiment/domain/interfaces.py`

Introduced:
- `ExperimentPlan`, `ExperimentContext`, `StepResult`, `RunResult`
- `IRunnableUnit`, `IPhase`, `IProtocol`, `IRunner`, `IRecordSink`

### Phase 2: Compatibility Adapters
Added temporary runnable adapters for legacy phase/protocol units and parity tests.
(These were later removed in Phase 10 cleanup.)

### Phase 3: Plan Builder + Plan-Compatible Assembly
Added:
- `experiment/plan_builder.py`
- `ExperimentConfig.to_plan()`

Updated `assemble_experiment(...)` to accept either:
- normalized config object, or
- `ExperimentPlan`

### Phase 4: Runner Contract Upgrade
Runner now supports native runnable-unit path:
- `reset(context)`
- `iter_steps(context)`

Legacy phase execution remained available as fallback.

### Phase 5: Context and Deterministic RNG Plumbing
Runner now threads a shared `ExperimentContext` through execution paths, with deterministic seed handling and context-driven RNG propagation where appropriate.

### Phase 6: Record Sink Abstraction
Added sink layer:
- `experiment/sinks.py` with `InMemorySink`

Runner now emits finalized records through sink while preserving existing return behavior.

### Phase 7: Intra-Trial Time Contracts
Added validated timing contracts in `experiment/domain/types.py`:
- `EventSpec`
- `WindowSpec`
- `TrialTimeSpec`

Validation includes:
- positive duration/dt
- ITI non-negative
- time-grid alignment policy
- event/window bounds within trial duration

### Phase 8: Native Unit Migration (One Pavlovian + One Operant)
Migrated to native runnable hooks:
- `AcquisitionPhase`
- `OperantAcquisitionPhase`

Added direct contract tests for `iter_steps(context)` and `reset(context)` behavior.

### Phase 9: Protocol Composition Upgrade
Upgraded `BaseProtocol` to native runnable-unit composition:
- `iter_steps(context)` is now first-class
- `run()` delegates to runnable flow

Runner preserves protocol subphase metadata on finalization.

### Phase 10: Cleanup
Removed deprecated compatibility layer:
- deleted `experiment/domain/adapters.py`
- deleted adapter parity tests

Runner tightened to contract-first execution (`iter_steps(context)` path), while retaining atomic phase fallback compatibility.

Documentation updated:
- `documentation/architecture_v2.md`

## Key Architectural State After This PR
- Runtime contracts are explicit and centralized.
- Protocols are composition-first runnable units.
- Runner is contract-driven and sink-aware.
- Config path supports immutable plan generation.
- Time-aware trial contracts exist at the domain layer for future tick-level evolution.

## Behavior and Compatibility Notes
- Existing test suite and payload-driven workflows remain operational.
- Atomic phase fallback remains in runner for compatibility.
- Structural directory reshaping (`assembly/`, `runtime/`, `units/`) intentionally deferred to a follow-up PR to keep this PR focused on behavior/contracts.

## Validation
Full CI-style test suite executed and passing:
- `python -m pytest -q`

Additional phase gates run during implementation included:
- config/assembly/runner gates
- phase/protocol behavioral gates
- report/visualization smoke slices

## Files of Note
- `virtual_shaping_lab/experiment/domain/types.py`
- `virtual_shaping_lab/experiment/domain/interfaces.py`
- `virtual_shaping_lab/experiment/plan_builder.py`
- `virtual_shaping_lab/experiment/assemble.py`
- `virtual_shaping_lab/experiment/runner.py`
- `virtual_shaping_lab/experiment/sinks.py`
- `virtual_shaping_lab/protocols/base.py`
- `virtual_shaping_lab/experiment/phases/acquisition.py`
- `virtual_shaping_lab/experiment/phases/operant_acquisition.py`
- `virtual_shaping_lab/documentation/architecture_v2.md`

## Follow-Up (Post-Merge)
- Optional structure-only PR for directory reshaping.
- Optional stricter enforcement pass to remove remaining phase fallback once all units are native runnable contracts.

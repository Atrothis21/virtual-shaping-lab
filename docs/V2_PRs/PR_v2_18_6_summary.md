# V2.18.6 Summary - Runtime Determinism and RNG Governance

## Overview
V2.18.6 makes runtime replay determinism an explicit contract and centralizes stochastic execution under the runtime-owned RNG.

Primary outcomes:
- runtime replay now has an explicit deterministic-execution guarantee
- seeded runs reproduce identical record order, policy choices, prediction-error trajectories, and learner updates
- tick-native schedule stochasticity is explicitly driven by the shared runtime RNG
- legacy variable reward schedules now accept seeded RNG reset instead of using module-level randomness
- API run/report metadata now expose `seed_identity`

This slice converts replay determinism from an implementation property into a documented and test-protected runtime contract.

---

## Deterministic Replay Contract

### Runtime Guarantee
V2.18.6 defines the replay invariant explicitly:

- identical canonical payload
- identical version metadata
- identical seed

must reproduce identical:

- record emission order
- prediction-error values
- learner weight-update trajectories
- seeded policy action selection
- seeded schedule stochasticity

This guarantee is now documented in the runtime layer and in the behavioral acceptance specification.

### Runtime Path Clarification
The runner/trial-executor path now makes the intended ownership explicit:

- `Runner` creates the shared runtime RNG from the resolved seed
- `TrialExecutor` passes that RNG into policy selection
- `TrialExecutor` also resets tick-schedule runtimes from that same RNG

Net effect:
- replay semantics are tied to the runtime-owned `ExperimentContext.rng`, not to incidental local generators

---

## RNG Governance

### Centralized Runtime RNG
V2.18.6 tightens the allowed stochastic path inside runtime execution:

- policy stochasticity is runtime-governed
- schedule stochasticity is runtime-governed

The shared RNG now serves as the authoritative source for seeded runtime variation in the core execution path.

### Legacy Reward Schedule Cleanup
The legacy reward-schedule adapters were the main remaining leak in this area.

What changed:
- `VariableRatioSchedule` no longer uses module-level `random.random()`
- `VariableIntervalSchedule` no longer uses module-level `random.expovariate(...)`
- reward schedules now accept `reset(rng)` and keep deterministic behavior under seeded reset
- `OperantAcquisitionPhase` now resets reward schedules from the phase/runtime RNG

This matters because legacy operant schedule paths can still participate in runtime execution and therefore must obey the same seed-governed replay contract.

### Plan Seed as Runtime Seed
`run_from_plan(...)` now uses `plan.seed` by default when no explicit override is provided.

This closes a real determinism gap:
- previously, plan resolution could infer/store a seed without runtime execution necessarily using it

Now:
- resolved plan seed and runtime seed identity are aligned by default

---

## Metadata and Auditability

### Seed Identity in Run Metadata
Run services and regenerated report metadata now expose:

- `seed_identity`

This is emitted alongside:

- `plan_hash`
- `record_schema_version`
- `template_version_used`
- `mechanism_provenance`

Net effect:
- seeded replay is now auditable from run artifacts and API status/report responses

### Acceptance Documentation
`docs/behavioral_correctness_spec.md` now includes a `Runtime Determinism` section that defines the replay contract in normative terms.

This keeps the execution guarantee in the same acceptance surface as:
- behavioral fixtures
- null/default semantics
- interaction assumptions
- provenance requirements

---

## Validation

### Determinism Gates
Validated through:
- `tests/test_runner_protocol.py`
- `tests/test_trial_executor.py`
- `tests/test_runtime_records.py`

These cover:
- runner-level seeded replay for full record streams
- deterministic policy action selection under shared RNG
- deterministic prediction-error and learner-update replay
- deterministic tick-schedule replay
- deterministic record finalization for identical inputs

### RNG Governance Gates
Validated through:
- `tests/test_runner_protocol.py`
- `tests/test_schedule_runtime.py`
- `tests/test_run_api_contract.py`

These cover:
- schedule runtime determinism under seeded reset
- legacy variable schedule determinism under seeded reset
- default use of `plan.seed` during runtime execution
- propagation of `seed_identity` through run and report metadata

---

## Net State After V2.18.6

- deterministic replay is now an explicit runtime contract
- stochastic execution paths in policy and schedule runtime are centralized under the shared runtime RNG
- legacy variable reward schedules no longer rely on module-level randomness
- resolved plan seed and runtime seed identity are aligned by default
- run/report metadata now expose seed identity for replay auditability

V2.18.6 therefore closes the main runtime determinism and stochastic-governance gap still remaining in the V2 closeout path.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_runner_protocol.py tests/test_trial_executor.py tests/test_runtime_records.py`
- `python -m pytest -q tests/test_runner_protocol.py tests/test_schedule_runtime.py tests/test_run_api_contract.py`

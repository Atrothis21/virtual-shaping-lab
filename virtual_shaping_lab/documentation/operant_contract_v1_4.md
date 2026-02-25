# VSL v1.4 Operant Architecture Contract

## Purpose

This document defines the implementation contract for `v1.4` (Operant Architecture Split).
It is the source of truth for interfaces, invariants, and boundaries used by all later `1.4.*` slices.

## Scope

`v1.4` adds a dedicated operant path while preserving classical behavior.

In scope:
- Operant agent interface hardening
- Action-value learner expectations (`td_value`, `q_learner`)
- Reinforcement / punishment / extinction outcome semantics
- Matching law, shaping, resurgence, superextinction, spontaneous recovery support

Out of scope (v1.4):
- Neural approximators (`v1.5`)
- New representation families
- Runner/report pipeline rewrites

## Architectural Split Rule

Classical and operant paths must be explicit in assembly and validation.

- Classical path: `classical_agent` + classical learner + no policy-required action selection.
- Operant path: `operant_agent` + action-value learner + policy-driven action selection.

No implicit cross-wiring is allowed.

## Interface Contracts

### Operant Agent Contract

`operant_agent` must support:
- `observe(observation) -> state`
- `value(state, action=None) -> float | dict[action,float]`
- `act(state) -> action`
- `update(state, reward, action=None, next_state=None, done=False) -> None`

Rules:
- `act` must always return an action label in operant mode.
- `update` must consume action-aligned outcomes.
- Operant agent must own policy usage; phases should not call policy directly.

### Action-Value Learner Contract

Learners used by operant agent must support:
- action-conditioned value update
- deterministic behavior when seeds/config require it
- stable handling of positive, zero, and negative rewards

Minimum shared params:
- `alpha`
- `gamma`
- `actions` (explicit action set)

### Policy Contract

Policies must:
- select from configured action space only
- be side-effect free w.r.t learner parameters
- operate on provided value estimates only

## Outcome Semantics (Normative)

Outcome interpretation for operant updates:
- `reward > 0`: reinforcement
- `reward == 0`: extinction / omission
- `reward < 0`: punishment

All three branches are required behavioral paths and must be test-covered.

### Consequence-Mode Scope (v1.4)

`operant_conditioning` may expose consequence mode labels
(`positive_reinforcement`, `negative_reinforcement`,
`positive_punishment`, `negative_punishment`).

In `v1.4`, these labels are **sign-tracked classes** only:
- reinforcement modes map to appetitive (`reward > 0`) updates
- punishment modes map to aversive (`reward < 0`) updates

`v1.4` does **not** claim full process-level differentiation of:
- positive vs negative reinforcement
- positive vs negative punishment

Full event/state-process distinction is deferred to a later version.

## Schedule Contract

Operant schedules must expose deterministic step/reset semantics:
- `reset()`
- `step(action, t) -> reward`

Schedules must not mutate agent/learner state directly.

## Phase/Protocol Responsibilities (Operant)

Phases remain responsible for:
- trial timing
- schedule invocation
- outcome construction
- record emission

Learners remain responsible for:
- value updates
- temporal credit assignment

Protocols remain responsible for:
- composition/order of phases only

## Assembly Invariants

1. Operant protocol requires operant-compatible agent+learner+policy wiring.
2. Classical protocol must not require policy.
3. Payload validation must reject invalid path combinations early.
4. Existing valid classical payloads must remain valid unchanged.

## UI/Schema Invariants

Builder and presets must emit equivalent operant payload semantics:
- explicit action set
- explicit schedule definitions
- explicit outcome signal path

No hidden defaults that alter action space or reward sign conventions.

## Testing Invariants (to be implemented in later slices)

Required 1.4 test categories:
- assembly routing contracts (classical vs operant)
- outcome branch tests (`+`, `0`, `-`)
- learner update consistency tests (TD/Q)
- behavioral directional tests:
  - matching law
  - shaping
  - resurgence
  - superextinction
  - spontaneous recovery

## Backward Compatibility

Must preserve:
- existing `v1.3.1` preset and builder flows
- existing run/report APIs
- existing classical phenomenon behavior

## Contract Mapping (Implementation Traceability)

### Architectural split and assembly invariants

- Split orchestration and path-specific wiring:
  - `virtual_shaping_lab/experiment/assemble.py`
  - `virtual_shaping_lab/experiment/factories/agent_factory.py`
  - `virtual_shaping_lab/experiment/factories/protocol_factory.py`
- Validation gate for operant path requirements:
  - `virtual_shaping_lab/ui/validate_payload.py`
- Coverage:
  - `tests/test_assemble_coverage.py`
  - `tests/test_validate_payload.py`

### Operant agent and learner interface contracts

- Agent interface and policy ownership:
  - `virtual_shaping_lab/agents/operant_agent.py`
- Action-value learners:
  - `virtual_shaping_lab/agents/learners/td_value.py`
  - `virtual_shaping_lab/agents/learners/q_learner.py`
- Policy implementations:
  - `virtual_shaping_lab/agents/policies/epsilon_greedy.py`
  - `virtual_shaping_lab/agents/policies/softmax.py`
  - `virtual_shaping_lab/agents/policies/fixed_policy.py`
- Coverage:
  - `tests/test_agents.py`
  - `tests/test_learners.py`

### Outcome semantics and schedule/phase responsibilities

- Operant outcome branch semantics (`reinforcement`, `extinction`, `punishment`):
  - `virtual_shaping_lab/experiment/phases/operant_acquisition.py`
  - `virtual_shaping_lab/experiment/phases/concurrent_schedule.py`
- Schedule construction and validation:
  - `virtual_shaping_lab/experiment/factories/reward_schedule_factory.py`
- Coverage:
  - `tests/test_phases.py`
  - `tests/test_protocols.py`

### Operant protocol support set

- Protocol implementations:
  - `virtual_shaping_lab/protocols/operant.py`
  - `virtual_shaping_lab/protocols/matching_law.py`
  - `virtual_shaping_lab/protocols/shaping.py`
  - `virtual_shaping_lab/protocols/resurgence.py`
  - `virtual_shaping_lab/protocols/superextinction.py`
  - `virtual_shaping_lab/protocols/spontaneous_recovery.py`
- Coverage:
  - `tests/test_protocols.py`
  - `tests/test_behavioral_phenomena_defaults.py`

### UI/schema invariants for operant payload semantics

- Operant payload semantics and policy guards:
  - `virtual_shaping_lab/ui/validate_payload.py`
  - `virtual_shaping_lab/ui/schema/policy.schema.json`
- Preset editors and action-space controls:
  - `virtual_shaping_lab/ui/js/react/operant_conditioning_editor.jsx`
  - `virtual_shaping_lab/ui/js/react/matching_law_editor.jsx`
  - `virtual_shaping_lab/ui/js/react/shaping_editor.jsx`
  - `virtual_shaping_lab/ui/js/react/resurgence_editor.jsx`
  - `virtual_shaping_lab/ui/js/react/superextinction_editor.jsx`
  - `virtual_shaping_lab/ui/js/react/spontaneous_recovery_editor.jsx`
- Shared action catalog:
  - `virtual_shaping_lab/ui/js/react/operant_actions.js`
- Coverage:
  - `tests/test_validate_payload.py`
  - `tests/test_ui_teaching_contract.py`
  - `tests/preset_payloads.py`

### Report/output compatibility and canonical report path

- Report generation/output:
  - `virtual_shaping_lab/analysis/report/report.py`
  - `virtual_shaping_lab/analysis/report/presets.py`
  - `virtual_shaping_lab/analysis/metrics/operant.py`
  - `virtual_shaping_lab/analysis/visualizations/operant.py`
  - `virtual_shaping_lab/analysis/visualizations/matching_law.py`
- API report hosting and run response:
  - `virtual_shaping_lab/api/run.py`
- Canonical shared paths:
  - `virtual_shaping_lab/paths.py`
- Coverage:
  - `tests/test_report.py`
  - `tests/test_visualizations.py`
  - `tests/test_run_api_contract.py`

## Definition of Done for Contract

This contract is considered active when:
1. All `1.4.*` code changes reference these interface/invariant rules.
2. Violations are enforced by validation/tests rather than convention.
3. Final `1.4` PR maps each completed slice back to one or more sections here.

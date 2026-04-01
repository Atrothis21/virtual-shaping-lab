# V3.21.10 Summary - Runtime Protocol Seam and Harness Integration

## Overview
V3.21.10 introduces a canonical runtime protocol adapter seam and routes runtime harness execution through that seam while preserving strict protocol-agent causal ownership boundaries from `agent_protocol_interaction.md`.

Primary outcomes:
- added canonical runtime protocol seam (`RuntimeProtocolAdapter`) for protocol-owned environment stages
- integrated harness flow to use protocol runtime seam for emission and consequence/advance/stop resolution
- enforced protocol-agent boundary invariants and causal ordering contracts
- added runtime parity coverage between protocol bundle execution and runtime adapter execution
- added blocking CI bucket for runtime protocol seam, ordering contracts, and boundary leak prevention

This slice closes the V3.21.10 milestone for protocol runtime seam integration and harness cutover.

---

## Slice 1 - Runtime Protocol Adapter

### Objective
Add one canonical runtime protocol adapter seam that normalizes phase payloads into executable protocol bundle inputs.

### Implemented
Added:
- `virtual_shaping_lab/vsl/runtime/protocol_adapter.py`

Updated:
- `virtual_shaping_lab/vsl/runtime/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `V3.21.10_plan.md`

Changes:
- introduced runtime protocol seam APIs:
  - `RuntimeProtocolAdapter`
  - `build_runtime_protocol_adapter(...)`
- added normalized runtime phase payload handling:
  - `t`, `phase_step`, `dt_s`, `elapsed_s`, `cumulative_reward`
  - stimulus/context/available-actions normalization
- added runtime state carry-forward through protocol stages:
  - `emit(...)`
  - `resolve(...)`
  - `step(...)`

---

## Slice 2 - Harness Integration (Single Protocol Seam)

### Objective
Route runtime harness protocol execution through one protocol runtime seam while keeping agent-side ownership in `CompositionalAgent`.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/rollout/harness.py`
- `V3.21.10_plan.md`

Changes:
- added protocol seam wiring in harness:
  - optional injected `protocol_adapter`
  - protocol preset routing and adapter cache
- replaced harness-local protocol sequencing with seam calls:
  - `protocol_adapter.emit(...)`
  - `protocol_adapter.resolve(...)`
- preserved agent-side ownership:
  - pre-outcome via `CompositionalAgent.pre_outcome_step(...)`
  - post-outcome via `CompositionalAgent.learn(...)` and `advance_internal_time(...)`
- mapped reward/done/timing from protocol stage outputs into environment step and learner outcome
- ensured explicit injected protocol adapter is honored during runtime step selection (no preset override drift)

---

## Slice 3 - Boundary Invariants (Protocol-Agent)

### Objective
Add invariant checks to enforce protocol-agent separation and prevent cross-seam leakage.

### Implemented
Updated:
- `tests/test_v3_agent_protocol_boundary_invariants.py`
- `V3.21.10_plan.md`

Changes:
- added runtime invariant coverage for:
  - no protocol-side learner internals (`prediction_error`, `delta`, `weights`)
  - actioned ordering contract:
    - `protocol_emit -> policy -> protocol_resolve -> learner`
  - no hidden learn dispatch in pre-outcome wrappers
- added runtime source checks ensuring protocol runtime seam stays learner-internal-token clean

---

## Slice 4 - Runtime Parity and Ordering Tests

### Objective
Prove runtime protocol seam behavior matches protocol bundle behavior and enforce harness ordering contracts.

### Implemented
Added:
- `tests/test_v3_runtime_protocol_adapter.py`
- `tests/test_v3_protocol_runtime_parity.py`

Updated:
- `tests/test_v3_agent_protocol_loop_contract.py`
- `V3.21.10_plan.md`

Changes:
- added runtime protocol adapter coverage for normalized payload/state progression
- added parity assertions against direct protocol bundle outputs for normalized inputs
- added harness loop-ordering guardrails:
  - protocol seam import/runtime usage checks
  - protocol emission/resolve ordering around agent pre/post-outcome flow

---

## Slice 5 - CI Bucket for Runtime Protocol Seam

### Objective
Add blocking CI enforcement for protocol runtime seam usage, ordering, and boundary contracts.

### Implemented
Updated:
- `.github/workflows/ci.yml`
- `V3.21.10_plan.md`

Changes:
- added blocking CI step:
  - `Run V3.21.10 runtime protocol seam`
- CI bucket enforces:
  - runtime protocol seam and parity tests
  - protocol-agent boundary invariants and contract validators
  - runtime observation/learner/policy companion seam smoke checks
- bucket fails on:
  - harness protocol seam bypass
  - causal ordering regressions across pre/post-outcome boundaries
  - protocol-agent boundary leakage

---

## Closeout Impact

After V3.21.10:
- runtime harness protocol flow is mediated by one canonical runtime protocol seam
- causal boundary order is explicit and guardrailed:
  - protocol emission
  - agent observe/predict/act
  - protocol consequence/advance/stop
  - agent learn
- protocol runtime surfaces remain free of learner-internal semantics
- runtime parity and CI guardrails prevent seam bypass and ordering regressions

V3.21.10 therefore completes runtime protocol seam integration for the V3.21 line.

---

## Validation

### Slice and Contract Gates
Validated via:
- `tests/test_v3_runtime_protocol_adapter.py`
- `tests/test_v3_protocol_runtime_parity.py`
- `tests/test_v3_agent_protocol_loop_contract.py`
- `tests/test_v3_agent_protocol_boundary_invariants.py`
- `tests/test_v3_agent_protocol_boundary_contracts.py`
- `tests/test_v3_agent_protocol_boundary_validator.py`
- `tests/test_v3_runtime_observation_adapter.py`
- `tests/test_v3_runtime_learner_adapter.py`
- `tests/test_v3_runtime_policy_adapter.py`

### CI-Facing Contract Checks
Validated by assertions that:
- runtime harness uses protocol seam methods for protocol-owned stages
- protocol-agent ordering remains causal and explicit
- protocol runtime seam excludes learner-internal computation concerns
- runtime protocol adapter behavior remains parity-aligned with executable protocol bundle outputs

---

## Net State After V3.21.10

- canonical runtime protocol seam is implemented and exported
- harness protocol staging is consolidated to one runtime seam path
- protocol-agent boundary invariants and loop-ordering contracts are test-enforced
- blocking CI bucket is active for runtime protocol seam regression prevention

V3.21.10 establishes the guardrailed runtime protocol-agent seam baseline for downstream V3.21.x integration work.

## Validation Commands

Targeted gates for local/CI execution:
- `python -m pytest -q tests/test_v3_runtime_protocol_adapter.py tests/test_v3_protocol_runtime_parity.py`
- `python -m pytest -q tests/test_v3_agent_protocol_loop_contract.py tests/test_v3_agent_protocol_boundary_contracts.py tests/test_v3_agent_protocol_boundary_validator.py`
- `python -m pytest -q tests/test_v3_agent_protocol_boundary_invariants.py`
- `python -m pytest -q tests/test_v3_runtime_observation_adapter.py tests/test_v3_runtime_learner_adapter.py tests/test_v3_runtime_policy_adapter.py`

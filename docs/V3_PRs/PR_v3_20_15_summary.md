# V3.20.15 Summary - Single-Path Compositional Agent Enforcement

## Overview
V3.20.15 hardens compositional agent ownership, introduces a thin orchestrator with explicit pre-outcome vs post-outcome interface boundaries, removes duplicate runtime orchestration in active environment stepping, and adds blocking CI guardrails for regression prevention.

Primary outcomes:
- added canonical compositional-agent legality and instantiation boundary (`AgentSpec`, validator, boundary materialization)
- added thin compositional orchestrator (`CompositionalAgent`) with explicit interface split:
  - pre-outcome: `observe/predict/act`
  - post-outcome: `learn/advance_internal_time`
- consolidated active runtime harness stepping onto one orchestrator path
- added blocking guardrail test suite and CI bucket for single-path compositional-agent enforcement
- published architecture closeout note and PR evidence checklist for ongoing change control

This slice closes the V3.20.15 milestone for single-path compositional-agent execution enforcement.

---

## Slice 1 - Agent Composition Contracts and Legality

### Objective
Define one canonical compositional-agent contract and fail-fast legality checks before runtime materialization.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/spec.py`
- `virtual_shaping_lab/vsl/agent/validation.py`
- `virtual_shaping_lab/vsl/agent/instantiate.py`

Updated:
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `V3.20.15_plan.md`

Changes:
- added compositional-agent typed spec:
  - `AgentSpec`
- added legality validator surface:
  - `AgentSpecValidationError`
  - `validate_agent_spec(...)`
- added legality-first instantiation boundary:
  - `AgentInstantiationArtifact`
  - `AgentInstantiationError`
  - `AGENT_INSTANTIATION_FAILURES`
  - `instantiate_agent_contracts(...)`
  - `instantiate_agent_from_boundary(...)`
- enforced compatibility checks across observation/learner/policy/protocol-action-space contracts

---

## Slice 2 - Thin Orchestrator Agent Execution

### Objective
Add one thin runtime orchestrator with explicit typed public interface and strict subsystem ownership.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/composite.py`

Updated:
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `V3.20.15_plan.md`

Changes:
- added orchestrator surface:
  - `CompositionalAgent`
- added typed step artifact:
  - `AgentStepResult`
- implemented explicit interface methods:
  - `observe(task_input)`
  - `predict(observation=None)`
  - `act(prediction=None)`
  - `learn(observation, prediction, action, outcome)`
  - `advance_internal_time(dt)`
  - `pre_outcome_step(task_input)` (convenience wrapper)
- constrained orchestration ownership:
  - observation through runtime observation seam
  - prediction/update through runtime learner seam
  - action selection through runtime policy seam

---

## Slice 3 - Remove Duplicate Agent Execution Paths

### Objective
Remove duplicate runtime orchestration branches and route active runtime stepping through the compositional-agent seam.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/rollout/harness.py`
- `V3.20.15_plan.md`

Changes:
- removed harness-local duplicate sequencing of:
  - direct observation adapter step calls
  - direct policy adapter step calls
  - direct learner adapter step calls
- replaced with single orchestrator-mediated path:
  - `CompositionalAgent.pre_outcome_step(...)`
  - `CompositionalAgent.learn(...)`
  - `CompositionalAgent.advance_internal_time(...)`
- retained constructor-level adapter injection as compatibility bridge, funneled through one orchestration seam

---

## Slice 4 - Guardrails and CI Enforcement

### Objective
Add blocking tests and CI bucket to prevent regressions back to multi-path agent execution.

### Implemented
Added:
- `tests/test_v3_agent_composition_validator.py`
- `tests/test_v3_agent_execution.py`
- `tests/test_v3_agent_runtime_parity.py`
- `tests/test_v3_single_path_agent_execution.py`
- `tests/test_v3_agent_public_interface_contract.py`
- `tests/test_v3_agent_protocol_boundary_invariants.py`
- `tests/test_v3_agent_namespace_import_audit.py`
- `tests/test_v3_agent_namespace_hard_removal.py`

Updated:
- `.github/workflows/ci.yml`
- `virtual_shaping_lab/vsl/agent/composite.py`
- `V3.20.15_plan.md`

Changes:
- added blocking CI step:
  - `Run V3.20.15 single-path compositional agent enforcement`
- CI bucket enforces:
  - compositional legality checks
  - public-interface and protocol-boundary invariants
  - single-path harness execution guardrails
  - namespace import/hard-removal drift checks
  - runtime adapter and rollout/report coupling checks
- fixed circular-import and adapter-stub compatibility issues in `CompositionalAgent` for stable collection/execution

---

## Slice 5 - Closeout Documentation and Evidence

### Objective
Publish architecture closeout and PR-ready evidence standards for V3.20.15.

### Implemented
Added:
- `docs/v3_20_15_single_path_agent_architecture.md`
- `docs/v3_20_15_pr_evidence_checklist.md`

Updated:
- `V3.20.15_plan.md`

Changes:
- documented canonical compositional-agent execution seam and ownership boundaries
- documented non-canonical/runtime-bypass surfaces and change-control requirements
- provided explicit PR evidence checklist mapped to guardrail tests and CI bucket requirements

---

## Closeout Impact

After V3.20.15:
- runtime agent execution is explicitly constrained to one compositional orchestration seam
- active harness execution no longer duplicates observation/policy/learner sequencing outside orchestrator ownership
- guardrail tests and blocking CI now fail fast on multi-path regressions
- architecture closeout and evidence checklist provide auditable standards for downstream refactors

V3.20.15 therefore completes single-path compositional-agent enforcement for the V3.20 line.

---

## Validation

### Slice and Contract Gates
Validated via:
- `tests/test_v3_agent_composition_validator.py`
- `tests/test_v3_agent_execution.py`
- `tests/test_v3_agent_runtime_parity.py`
- `tests/test_v3_single_path_agent_execution.py`
- `tests/test_v3_agent_public_interface_contract.py`
- `tests/test_v3_agent_protocol_boundary_invariants.py`
- `tests/test_v3_agent_namespace_import_audit.py`
- `tests/test_v3_agent_namespace_hard_removal.py`

### CI-Facing Contract Checks
Validated by assertions that:
- compositional legality remains fail-fast and deterministic
- pre-outcome vs post-outcome public interface boundaries remain explicit
- harness runtime path remains single-path and orchestrator-owned
- namespace/import drift back to legacy agent paths fails fast
- runtime/report coupling surfaces remain intact after orchestration refactor

---

## Net State After V3.20.15

- canonical compositional-agent legality and instantiation boundaries are in place
- thin compositional-agent runtime interface is exported and integrated
- active runtime stepping is consolidated to single-path orchestrator flow
- blocking CI bucket enforces single-path compositional-agent contracts
- architecture and PR-evidence closeout docs are published

V3.20.15 establishes the guardrailed baseline for post-V3.20 agent/runtime simplification work.

## Validation Commands

Targeted gates for local/CI execution:
- `python -m pytest -q tests/test_v3_agent_composition_validator.py tests/test_v3_agent_execution.py tests/test_v3_agent_runtime_parity.py`
- `python -m pytest -q tests/test_v3_single_path_agent_execution.py tests/test_v3_agent_public_interface_contract.py tests/test_v3_agent_protocol_boundary_invariants.py`
- `python -m pytest -q tests/test_v3_agent_namespace_import_audit.py tests/test_v3_agent_namespace_hard_removal.py`
- `python -m pytest -q tests/test_v3_runtime_observation_adapter.py tests/test_v3_runtime_learner_adapter.py tests/test_v3_runtime_policy_adapter.py`
- `python -m pytest -q tests/test_v3_rollout_record_schema.py tests/test_report.py -k "observation or learner or policy or agent"`

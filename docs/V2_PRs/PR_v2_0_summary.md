# PR: v2 Agent Architecture Refactor Summary

## Overview
This change set completes the v2 agent-architecture redesign toward a composition-first, strategy-driven system.

Core outcome:
- single `ComposedAgent` orchestrator (`observe -> act -> learn`)
- single learner update contract (`update(Transition)`)
- strict mechanism ownership split
- time-ready shared domain contracts for intra-trial modeling

## Architectural Goals Implemented

### 1. Shared Domain Contracts
Added and standardized domain types used across agents/protocols:
- `Observation`
- `EncodedState`
- `Transition`

Time-related support added to `Observation` and `Transition`:
- `t_s`, `dt_s`
- `trial_step`, `trial_id`

Validation added:
- `dt_s >= 0`
- `trial_step >= 0`

Metadata keys standardized:
- `META_CUE_LABELS`
- `META_EVENT_TYPE`

## 2. Single Learner Update Path
Refactor completed to remove override-based update APIs.

Now:
- public learning path is `update(Transition)` only
- `update_with_alpha(...)` removed from learner hierarchy
- attention modulation applied internally by learner through transition metadata (`META_CUE_LABELS`)

## 3. Agent/Policy/Learner Separation
Maintained/enforced:
- Agent remains a thin orchestrator
- Policy is read-only and does not mutate learner state
- Learner owns all value-function parameters and learning math

## 4. Time-Ready Transition Flow
Phase helper/learning helper path now passes standardized transition fields:
- `t_s`, `dt_s`, `trial_step`, `trial_id`
- `event_type` via metadata when needed

No timing/schedule logic was added into the agent class.

## 5. Mechanism Ownership Split (Implemented)
Mechanisms are now explicitly split by responsibility:

Representation-owned:
- context (feature namespacing/gating)
- similarity (generalization spread)
- salience (feature scaling)

Learner-owned:
- attention (effective plasticity / update gain)

Deterministic representation order is enforced:
- `context -> similarity -> salience`

Implemented by introducing shared representation mechanism pipeline code and routing vector representations through it.

## 6. Guardrails and Enforcement
Hard guardrails added to prevent mechanism leakage:
- representation params reject `attention` and `attention_compound`
- `ExperimentConfig` rejects representation-level attention fields
- UI payload validation rejects representation-level attention fields

This ensures attention remains learner-owned everywhere.

## 7. Test Updates and Additions
Updated/added tests to align with v2 contracts and new guardrails, including:
- domain type/time contract validation
- learner update path behavior
- representation mechanism order and behavior
- payload/config guardrails for mechanism ownership
- integration sanity for representation-vs-learner split

## 8. Documentation Update
Updated architecture docs to reflect:
- expanded time-capable domain contracts
- explicit mechanism ownership split
- deterministic representation mechanism order

## Validation Status
Focused suites executed and passing during refactor:
- `tests/test_domain_types.py`
- `tests/test_learners.py`
- `tests/test_learning_helpers.py`
- `tests/test_agents.py`
- `tests/test_phases.py`
- `tests/test_representations.py`
- `tests/test_v2_architecture_sanity.py`
- `tests/test_config.py`
- `tests/test_validate_payload.py`
- `tests/test_assemble_coverage.py`

## Net Effect
The codebase is now aligned to the intended v2 architecture:
- composition-first agent model
- stable transition-based learner contract
- clear SOLID boundaries
- explicit mechanism ownership
- intra-trial time-ready contracts without embedding timing rules into agent logic

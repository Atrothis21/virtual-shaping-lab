# V3.20.15 Single-Path Compositional Agent Architecture

## Purpose
This document defines the V3.20.15 canonical agent execution seam and records which surfaces are canonical vs compatibility-only.

## Canonical Execution Path
The only approved compositional-agent execution path is:
1. `virtual_shaping_lab/vsl/rollout/harness.py`
2. `CompiledProgramTestEnvironment.step(...)`
3. `virtual_shaping_lab/vsl/agent/composite.py`
4. `CompositionalAgent.pre_outcome_step(...)`
5. `CompositionalAgent.learn(...)`
6. `CompositionalAgent.advance_internal_time(...)`

Subsystem execution ownership remains:
- Observation: `RuntimeObservationAdapter.step(...)`
- Policy: `RuntimePolicyAdapter.step(...)`
- Learner: `RuntimeLearnerAdapter.step(...)`

## Canonical Contract Ownership
- Compositional legality/instantiation ownership:
  - `virtual_shaping_lab/vsl/agent/spec.py`
  - `virtual_shaping_lab/vsl/agent/validation.py`
  - `virtual_shaping_lab/vsl/agent/instantiate.py`
- Thin orchestrator ownership:
  - `virtual_shaping_lab/vsl/agent/composite.py`
- Runtime test-environment seam ownership:
  - `virtual_shaping_lab/vsl/rollout/harness.py`

## Public Interface Contract
Pre-outcome agent boundary:
- `observe(task_input)`
- `predict(observation)`
- `act(prediction)`

Post-outcome agent boundary:
- `learn(observation, prediction, action, outcome)`
- `advance_internal_time(dt)`

Allowed convenience wrapper:
- `pre_outcome_step(task_input)` (must not perform learning/update mutations)

## Explicitly Non-Canonical Surfaces
The following are not canonical compositional-agent execution paths and must not be used for runtime stepping:
- protocol-side direct calls to observation/policy/learner adapters bypassing `CompositionalAgent`
- hidden update branches that compute learner internals outside learner/runtime learner seam
- any reintroduction of update-only fallback execution semantics

Compatibility surfaces may remain for transition, but active runtime execution must stay on the canonical seam above.

## Runtime Trace Contract
Runtime step metadata must preserve:
- observation output and stage provenance
- policy decision traces (`action`, `available_actions`, scores/probabilities, metadata)
- learner traces (`prediction`, `error`, update features, attention/eligibility state)

## Guardrail Requirements
Single-path compositional-agent enforcement requires:
- legality guardrails for observation/learner/policy composition
- interface contract tests for pre-vs-post outcome split
- runtime parity checks between environment loop and compositional-agent seam
- namespace import audit and hard-removal checks for legacy agent paths
- blocking CI bucket coverage for all of the above

## Change Control
Any future agent execution change must:
1. modify canonical path files listed above
2. update V3.20.15 guardrail tests and CI bucket
3. include before/after evidence in PR checklist and summary

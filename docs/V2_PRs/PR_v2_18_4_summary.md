# V2.18.4 Summary - Typed ExperimentPlan Promotion and Canonical-First Replay Identity

## Overview
V2.18.4 promotes `ExperimentPlan` from a settings-heavy transport object into a typed architectural plan and shifts replay identity toward canonical payload state.

Primary outcomes:
- `ExperimentPlan` now carries typed architecture-relevant envelope fields
- plan serialization and round-trip behavior include typed program/agent/runtime/analysis structure
- canonical payload is now a first-class plan field
- stable plan hashing is now canonical-first
- runtime plan consumers now prefer typed plan fields over ad hoc `settings` reads in key execution paths
- determinism and config tests are green under the typed plan model

This slice is the first real step toward making the plan layer reflect the runtime architecture directly instead of acting mainly as a compatibility container.

---

## Typed Plan Envelope

### New First-Class Plan Fields
`ExperimentPlan` now carries explicit typed envelope fields for:
- `program_spec`
- `agent_spec`
- `runtime_spec`
- `analysis_spec`

These fields now sit alongside:
- `units`
- `canonical_payload`
- `record_schema_version`

Net effect:
- architecture-relevant plan state no longer lives only inside `plan.settings`

### Builder Population
The plan builder now populates those typed fields directly from `ExperimentConfig`.

Typed envelope responsibilities are now split as:
- `program_spec`
  - resolved phase/unit program
  - resolved phase contexts
- `agent_spec`
  - learner
  - agent
  - representation
  - policy
  - stimuli/salience/attention state
- `runtime_spec`
  - runtime settings
  - context inference
  - composed parameters needed for execution
- `analysis_spec`
  - report preset

This gives the plan layer a clearer architectural grammar.

---

## Canonical Replay Identity

### Canonical Payload as First-Class Plan State
V2.18.4 adds `canonical_payload` as a top-level `ExperimentPlan` field.

This matters because the plan now has a single explicit replay artifact representing:
- canonical experiment ownership
- canonical report configuration

instead of hiding that identity inside `plan.settings`.

### Stable Hash Cleanup
`ExperimentPlan.stable_hash()` now depends on:
- `canonical_payload`
- `record_schema_version`

and no longer depends on arbitrary non-identity `settings` content.

Net effect:
- replay identity is now canonical-first
- incidental settings changes no longer destabilize plan hashes

This is the main replay/determinism improvement introduced in V2.18.4.

---

## Runtime Consumption Shift

### Public Plan Validation
Plan validation now prefers typed runtime fields when checking:
- `composed_parameters`

Compatibility fallback to `plan.settings` remains, but the primary read path is now typed-plan-first.

### Plan Execution Settings
`run_from_plan(...)` now prefers:
- `runtime_spec["runtime"]`
- `runtime_spec["composed_parameters"]`

before consulting legacy `settings` paths.

### Plan-to-Config Reconstruction
`assemble._plan_to_config(...)` now reconstructs execution config primarily from:
- `program_spec`
- `agent_spec`
- `runtime_spec`

with `settings` retained only as compatibility fallback.

Net effect:
- runtime-critical plan consumers are less dependent on `plan.settings`
- typed plan fields now participate directly in execution flow

---

## Compatibility Strategy

### Settings Retained for Transitional Stability
V2.18.4 does not remove `plan.settings`.

Instead, it:
- adds typed plan structure
- redirects important runtime reads toward typed fields
- keeps `settings` as a compatibility layer for remaining consumers

This is the right shape for a commit-sized migration because:
- the architecture improves immediately
- the runtime is not destabilized by a hard cut

---

## Validation

### Typed Envelope Gates
Validated through:
- `tests/test_domain_types.py`
- `tests/test_config.py`
- `tests/test_parameter_composer.py`

These cover:
- typed plan envelope serialization
- typed-field population from config build
- round-trip integrity
- stable hashing across typed plan reconstruction

### Replay Identity Gates
Validated through:
- `tests/v2_11_contract/test_plan_determinism.py`
- `tests/test_config.py`

These cover:
- deterministic public plan builds
- plan round-trip stable-hash preservation
- canonical-first replay identity behavior

---

## Net State After V2.18.4

- `ExperimentPlan` now carries a typed architectural envelope
- canonical payload is first-class plan state
- stable hash is now tied to canonical replay identity rather than incidental settings state
- runtime plan consumers are beginning to read typed fields directly
- `plan.settings` is no longer the sole source of architecture-relevant plan information

V2.18.4 therefore establishes the foundation for treating plans as architectural objects instead of transport wrappers.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_domain_types.py tests/test_config.py tests/test_parameter_composer.py`
- `python -m pytest -q tests/v2_11_contract/test_plan_determinism.py tests/test_config.py`

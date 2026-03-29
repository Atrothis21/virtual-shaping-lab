# V3.18.0 Summary - Canonical Learner Surface and Contract Hardening

## Overview
V3.18.0 consolidates learner composition ownership into one canonical grammar surface, adds an explicit instantiation boundary, and hardens runtime/CI contracts to prevent drift.

Primary outcomes:
- declared `vsl/agent/learning/spec.py` as canonical learner composition contract ownership
- reduced `vsl/spec/contracts.py` learner role to runtime transport semantics, with explicit aliasing
- added canonical<->runtime learner adapter mapping with deterministic roundtrip coverage
- introduced explicit runtime `attention_state` to remove action/attention ambiguity in trial-state contracts
- added learner instantiation boundary scaffold (`instantiate.py`) with legality-first enforcement and typed null placeholders for optional `A`/`E`
- added blocking CI ownership bucket and namespace drift guards for learner contract hardening

This slice closes the V3.18.0 contract-hardening milestone for learner spec ownership, runtime state naming clarity, and executable boundary scaffolding.

---

## Slice 1 - Canonical Learner Spec Decision

### Objective
Make learner grammar the single canonical composition source and constrain runtime contract surfaces to transport/adapter scope.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/learning/adapters.py`
- `tests/test_v3_learner_spec_adapters.py`
- `docs/v3_18_0_learner_contract_ownership.md`

Updated:
- `virtual_shaping_lab/vsl/agent/learning/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `virtual_shaping_lab/vsl/spec/contracts.py`
- `virtual_shaping_lab/vsl/spec/__init__.py`

Changes:
- added adapter APIs:
  - `grammar_to_runtime_learner_config(...)`
  - `runtime_to_grammar_learner_spec(...)`
- clarified runtime learner contract ownership in typed specs
- introduced `RuntimeLearnerConfig` alias for runtime-facing learner transport config
- exported adapter/alias surfaces through public package facades

---

## Slice 2 - Runtime State Naming Correction

### Objective
Introduce explicit attention state in runtime carrier contracts and remove semantic overlap with action state.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/rollout/trial_state.py`
- `virtual_shaping_lab/vsl/rollout/operator_pipeline.py`
- `tests/test_v3_trial_state.py`
- `tests/test_v3_operator_pipeline_types.py`
- `tests/test_v3_environment_contract_types.py`
- `tests/test_v3_runner_environment_integration.py`

Changes:
- added explicit `attention_state` coordinate to `TrialState`
- retained one-release compatibility adapter:
  - `TrialState.from_dict(...)` accepts legacy `attention` and normalizes to `attention_state`
- updated normative pipeline contracts:
  - `A` stage produces `attention_state`
  - `Update` and `Measure` require `attention_state`
  - `PIPELINE_BASE_FIELDS` includes `attention_state`
- expanded runtime serialization tests to enforce explicit attention-state shape

---

## Slice 3 - Executable Materialization Boundary

### Objective
Add a legality-first learner instantiation boundary from canonical grammar tuples to typed executable contracts.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/learning/instantiate.py`
- `tests/test_v3_learner_instantiation.py`
- `docs/v3_18_0_learner_instantiation_boundary.md`

Updated:
- `virtual_shaping_lab/vsl/agent/learning/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`

Changes:
- added instantiation APIs:
  - `instantiate_learner_contracts(...)`
  - `instantiate_learner_from_boundary(...)`
- added typed materialization artifact:
  - `LearnerInstantiationArtifact`
- added typed placeholders:
  - `NullAttentionOperator` (optional `A`)
  - `NullTraceOperator` (optional `E`)
- added machine-readable failure catalog/codes:
  - `INST_E_INVALID_SPEC_INPUT`
  - `INST_E_LEGALITY`
  - `INST_E_BOUNDARY_RESOLUTION`
- added legal-universe materialization coverage over registry-derived tuple space

---

## Slice 4 - CI/Namespace Hardening

### Objective
Block learner contract ownership drift, shadow import surfaces, and legacy namespace regression in CI.

### Implemented
Added:
- `tests/test_v3_learner_contract_ownership.py`

Updated:
- `.github/workflows/ci.yml`
- `tests/test_v3_namespace_import_audit.py`
- `tests/test_v3_namespace_hard_removal.py`

Changes:
- added blocking CI step:
  - `Run V3.18.0 learner contract ownership`
- bucket enforces:
  - canonical-vs-runtime learner ownership constraints
  - trial-state attention naming contract
  - namespace import and hard-removal drift guards
- added no-new-legacy-surface coverage for learner runtime-contract shadow paths

---

## Closeout Impact

After V3.18.0:
- learner composition semantics have one canonical owner in `vsl/agent/learning/spec.py`
- runtime learner transport surface is explicitly separated and adapter-bound
- runtime state now carries explicit attention-state identity with compatibility normalization
- legal learner tuples can be materialized through one typed boundary API with null optional-operator placeholders
- CI blocks ownership drift and legacy/shadow learner namespace regressions

V3.18.0 therefore completes canonical learner surface hardening and prepares downstream execution implementation work for V3.18.5+.

---

## Validation

### Slice and Contract Gates
Validated via:
- `tests/test_v3_learner_grammar_spec.py`
- `tests/test_v3_learner_validator.py`
- `tests/test_v3_learner_registry.py`
- `tests/test_v3_learner_presets.py`
- `tests/test_v3_learner_spec_adapters.py`
- `tests/test_v3_learner_instantiation.py`
- `tests/test_v3_learner_contract_ownership.py`
- `tests/test_v3_trial_state.py`
- `tests/test_v3_operator_pipeline_types.py`
- `tests/test_v3_namespace_import_audit.py`
- `tests/test_v3_namespace_hard_removal.py`

### CI-Facing Contract Checks
Validated by assertions that:
- canonical learner composition and runtime transport ownership remain non-duplicated
- adapter boundary remains explicit and deterministic
- trial-state attention naming remains explicit and compatibility-normalized
- legal tuple materialization and optional-operator placeholder semantics remain stable
- namespace drift and shadow learner surfaces fail fast in CI

---

## Net State After V3.18.0

- canonical learner composition ownership is established and exported
- runtime learner contract ambiguity is reduced to transport-only semantics
- explicit learner instantiation boundary scaffold exists with typed contracts and failure catalog
- runtime trial-state naming is unambiguous for attention vs action surfaces
- blocking CI ownership bucket is active for V3.18.0 learner contract hardening

V3.18.0 establishes the hardened learner contract baseline for subsequent executable/operator cleanup work across V3.18.x.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_learner_grammar_spec.py tests/test_v3_learner_validator.py tests/test_v3_learner_registry.py tests/test_v3_learner_presets.py`
- `python -m pytest -q tests/test_v3_typed_specs.py -k "learner or runtime"`
- `python -m pytest -q tests/test_v3_learner_spec_adapters.py tests/test_v3_learner_instantiation.py tests/test_v3_learner_contract_ownership.py`
- `python -m pytest -q tests/test_v3_trial_state.py tests/test_v3_operator_pipeline_types.py`
- `python -m pytest -q tests/test_v3_namespace_import_audit.py tests/test_v3_namespace_hard_removal.py`

# V3.20.0 Summary - Policy Contract Ownership and Legality Foundation

## Overview
V3.20.0 establishes canonical policy contract ownership, separates canonical policy grammar from runtime policy transport semantics, and adds legality-first instantiation and CI guardrails. It also formalizes typed experiment-agent interaction boundary contracts.

Primary outcomes:
- added canonical policy grammar ownership surface under `vsl/agent/policy/spec.py`
- added policy validator, registry, and preset surfaces with deterministic hashing/payload APIs
- added grammar/runtime adapter boundary for policy with explicit runtime aliasing
- added legality-first policy instantiation boundary with machine-readable failure catalog
- added typed interaction boundary contracts (`TaskInput`, `Action`, `Outcome`, `TrialRecord`)
- added blocking CI bucket for V3.20.0 policy ownership and boundary guardrails

This slice closes the V3.20.0 milestone for policy contract ownership hardening.

---

## Slice 1 - Canonical Policy Spec Surface

### Objective
Add one canonical symbolic policy grammar ownership surface.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/policy/spec.py`

Updated:
- `virtual_shaping_lab/vsl/agent/policy/__init__.py`
- `V3.20.0_plan.md`

Changes:
- introduced canonical declarative policy grammar:
  - `PolicySpec`
- added deterministic policy identity helpers:
  - `to_dict()`
  - `from_dict(...)`
  - `to_json()`
  - `stable_hash()`
- established canonical tuple fields:
  - `selection_rule`
  - `action_space_mode`
  - `parameters`
  - optional `tie_break_rule`
  - optional `availability_rule`
  - `metadata`

---

## Slice 2 - Validation, Registry, Presets, and Typed Boundary Contracts

### Objective
Add legality validation, machine-readable registry/preset surfaces, and typed experiment-agent boundary contracts.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/policy/validation.py`
- `virtual_shaping_lab/vsl/agent/policy/registry.py`
- `virtual_shaping_lab/vsl/agent/policy/presets.py`
- `virtual_shaping_lab/vsl/contracts/interaction.py`
- `virtual_shaping_lab/vsl/contracts/__init__.py`

Updated:
- `virtual_shaping_lab/vsl/agent/policy/spec.py`
- `virtual_shaping_lab/vsl/agent/policy/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `V3.20.0_plan.md`

Changes:
- added typed legality validator and failure codes:
  - `PolicySpecValidationError`
  - `validate_policy_spec(...)`
- added deterministic registry APIs:
  - `slot_registries()`
  - `compatibility_matrix()`
  - `policy_registry_payload()`
  - `policy_registry_hash()`
- added deterministic policy preset expansion and hashing:
  - `expand_policy_preset(...)`
  - `policy_preset_payload(...)`
  - `policy_preset_hash(...)`
- formalized typed interaction boundary contracts:
  - `TaskInput`
  - `Action`
  - `Outcome`
  - `TrialRecord`
  - `validate_interaction_boundary(...)`

---

## Slice 3 - Grammar/Runtime Adapter Ownership Split

### Objective
Separate canonical policy grammar semantics from runtime transport contracts.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/policy/adapters.py`

Updated:
- `virtual_shaping_lab/vsl/agent/policy/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `virtual_shaping_lab/vsl/spec/contracts.py`
- `virtual_shaping_lab/vsl/spec/__init__.py`
- `V3.20.0_plan.md`

Changes:
- added adapter APIs:
  - `grammar_to_runtime_policy_config(...)`
  - `runtime_to_grammar_policy_spec(...)`
- clarified runtime transport alias:
  - `RuntimePolicyConfig = PolicySpec` (runtime contract alias in `vsl.spec.contracts`)
- exported adapter surfaces through public package facades

---

## Slice 4 - Instantiation Boundary and Failure Catalog

### Objective
Add legality-first policy materialization boundary from grammar tuples to typed executable/runtime contracts.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/policy/instantiate.py`

Updated:
- `virtual_shaping_lab/vsl/agent/policy/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `V3.20.0_plan.md`

Changes:
- added machine-readable failure catalog:
  - `POLICY_INSTANTIATION_FAILURES`
- added typed error and artifacts:
  - `PolicyInstantiationError`
  - `PolicyOperatorHandle`
  - `PolicyInstantiationArtifact`
- added instantiation APIs:
  - `instantiate_policy_contracts(...)`
  - `instantiate_policy_from_boundary(...)`

---

## Slice 5 - Ownership Guardrails and CI Bucket

### Objective
Add policy contract ownership tests and blocking CI guardrail bucket.

### Implemented
Added:
- `tests/test_v3_policy_grammar_spec.py`
- `tests/test_v3_policy_validator.py`
- `tests/test_v3_policy_registry.py`
- `tests/test_v3_policy_presets.py`
- `tests/test_v3_policy_instantiation.py`
- `tests/test_v3_policy_contract_ownership.py`
- `tests/test_v3_agent_protocol_boundary_contracts.py`
- `tests/test_v3_agent_protocol_boundary_validator.py`

Updated:
- `.github/workflows/ci.yml`
- `virtual_shaping_lab/vsl/agent/policy/validation.py`
- `V3.20.0_plan.md`

Changes:
- added blocking CI step:
  - `Run V3.20.0 policy contract ownership`
- CI bucket enforces:
  - policy grammar/validation/registry/preset contract stability
  - legality-first policy instantiation behavior
  - canonical-vs-runtime policy ownership separation
  - typed interaction boundary contract validity
- tightened validator check ordering so specific null/classical mismatch surfaces first:
  - `POL_E_NULL_REQUIRES_CLASSICAL_NONE`

---

## Closeout Impact

After V3.20.0:
- policy composition now has one canonical symbolic owner in `vsl/agent/policy/spec.py`
- runtime policy transport is explicitly adapter-bound and alias-scoped
- policy instantiation is legality-first with typed failure catalog
- typed experiment-agent interaction boundary contracts are formalized and validated
- CI blocks policy ownership drift and boundary regressions

V3.20.0 establishes the hardened policy contract baseline required for executable policy operators and runtime policy seam integration in V3.20.5+.

---

## Validation

### Slice and Contract Gates
Validated via:
- `tests/test_v3_policy_grammar_spec.py`
- `tests/test_v3_policy_validator.py`
- `tests/test_v3_policy_registry.py`
- `tests/test_v3_policy_presets.py`
- `tests/test_v3_policy_instantiation.py`
- `tests/test_v3_policy_contract_ownership.py`
- `tests/test_v3_agent_protocol_boundary_contracts.py`
- `tests/test_v3_agent_protocol_boundary_validator.py`

### CI-Facing Contract Checks
Validated by assertions that:
- policy canonical grammar and runtime transport ownership remain separated
- policy validation/registry/preset semantics remain deterministic
- policy boundary instantiation remains legality-first and typed
- typed interaction boundary contracts remain narrow and causal

---

## Net State After V3.20.0

- canonical policy ownership, validator, registry, presets, adapters, and instantiation boundary are in place
- runtime policy transport aliasing and adapter split are explicit
- typed experiment-agent boundary contracts are available and test-covered
- blocking CI bucket is active for V3.20.0 policy contract hardening

V3.20.0 therefore completes the policy contract ownership phase of the V3.20 line.

## Validation Commands

Targeted gates for local/CI execution:
- `python -m pytest -q tests/test_v3_policy_grammar_spec.py tests/test_v3_policy_validator.py tests/test_v3_policy_registry.py tests/test_v3_policy_presets.py`
- `python -m pytest -q tests/test_v3_policy_instantiation.py tests/test_v3_policy_contract_ownership.py`
- `python -m pytest -q tests/test_v3_agent_protocol_boundary_contracts.py tests/test_v3_agent_protocol_boundary_validator.py`

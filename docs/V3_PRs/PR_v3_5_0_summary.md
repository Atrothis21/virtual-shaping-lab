# V3.5.0 Summary - Learner Grammar Validation, Registry Contracts, and Boundary Enforcement

## Overview
V3.5.0 makes learner composition a first-class validated algebra and enforces tuple legality at both plan-build and runtime assembly seams.

Primary outcomes:
- introduced typed learner grammar objects (`LearnerSpec`) for trace/predictor/error/attention/updater/policy tuples
- added fail-fast legality validation with named error codes (`LearnerSpecValidationError`)
- published machine-readable slot registries and compatibility matrix payload/hash outputs
- added named learner preset registry with deterministic expansion and alias support
- enforced learner validation at spec-build and runtime assembly boundaries
- completed closure pass items:
  - runtime-vs-registry compatibility parity test
  - learner identity (`preset_name`, `spec_hash`) propagation into run/report metadata and artifact identity
  - dedicated V3 learner CI bucket in workflow

This slice turns learner tuple legality from informal convention into a machine-enforced architecture contract.

---

## Slice 1 - Learner Grammar Type

### Objective
Introduce a typed learner grammar declaration for V3.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/learning/spec.py`

Added tests:
- `tests/test_v3_learner_grammar_spec.py`

Changes:
- added `LearnerSpec(trace, predictor, error, attention, updater, policy, metadata)`
- added deterministic serialization + hash (`to_json`, `stable_hash`)
- established strict slot-level non-empty validation

---

## Slice 2 - Mandatory Validator

### Objective
Make learner tuple legality fail fast with named error codes.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/learning/validator.py`

Updated exports:
- `virtual_shaping_lab/vsl/agent/learning/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`

Added tests:
- `tests/test_v3_learner_validator.py`

Changes:
- implemented `validate_learner_spec(spec)` and `LearnerSpecValidationError`
- enforced predictor/error/policy/trace/attention/updater compatibility rules
- standardized named error codes for invalid tuples

---

## Slice 3 - Slot Registries and Compatibility Matrix

### Objective
Publish machine-readable learner registries and legality matrix.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/learning/registry.py`
- `tests/test_v3_learner_registry.py`

Changes:
- exposed:
  - `SLOT_REGISTRIES`
  - `COMPATIBILITY_MATRIX`
  - `learner_registry_payload()`
  - `learner_registry_hash()`
- added parity checks against validator constants for registry correctness

---

## Slice 4 - Preset Registry

### Objective
Provide deterministic named learner presets with alias support.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/learning/presets.py`
- `tests/test_v3_learner_presets.py`

Changes:
- added preset families:
  - classical
  - operant_value
- added deterministic expansion + payload/hash outputs:
  - `expand_learner_preset(...)`
  - `learner_preset_payload(...)`
  - `learner_preset_hash(...)`
- added family smoke gate (minimum 3 fixtures per supported family)

---

## Slice 5 - Dual Enforcement Boundaries

### Objective
Enforce learner validator at spec-build and runtime assembly seams.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/learning/boundary.py`
- `tests/test_v3_learner_boundary_enforcement.py`

Updated:
- `virtual_shaping_lab/experiment/plan_builder.py`
- `virtual_shaping_lab/experiment/assemble.py`

Changes:
- introduced `resolve_learner_spec(...)` boundary resolver (explicit spec/preset + legacy mapping)
- plan build now embeds validated `learning.learner_spec` and `learner_spec_hash`
- runtime assembly now hard-fails when learner tuple resolution/validation fails
- runtime seam now respects composed policy when explicit policy config is absent

---

## Completion Pass - Testing/Exit Criteria Closure

### Objective
Close remaining partial items from V3.5.0 testing/exit criteria.

### Implemented
Added:
- `tests/test_v3_learner_runtime_parity.py`

Updated:
- `virtual_shaping_lab/vsl/agent/learning/validator.py`
- `virtual_shaping_lab/vsl/agent/learning/registry.py`
- `tests/test_v3_learner_registry.py`
- `virtual_shaping_lab/api/services.py`
- `virtual_shaping_lab/analysis/report/report.py`
- `tests/test_run_api_contract.py`
- `.github/workflows/ci.yml`

Changes:
- added runtime acceptance parity gate:
  - runtime-accepted tuples must equal registry-matrix-accepted tuples
- expanded matrix payload to include explicit hard-rule constraints for parity testing
- propagated learner identity into run/report metadata and `artifact_identity.json`:
  - `preset_name`
  - `spec_hash`
- added dedicated V3 learner CI bucket for grammar/validator/registry/presets/boundary/parity tests

---

## Closeout Impact

After V3.5.0:
- learner legality is centralized, deterministic, and fail-fast
- runtime cannot bypass learner validation via assembly seams
- compatibility surface is machine-readable and parity-tested against runtime acceptance
- preset expansion is deterministic and traceable
- learner identity is now artifact-visible in run/report metadata
- CI includes a dedicated learner-grammar guard bucket

This slice establishes the learner algebra governance layer required for subsequent V3 cognitive/runtime composition work.

---

## Validation

### Slice and Completion Gates
Validated through targeted suites:
- `tests/test_v3_learner_grammar_spec.py`
- `tests/test_v3_learner_validator.py`
- `tests/test_v3_learner_registry.py`
- `tests/test_v3_learner_presets.py`
- `tests/test_v3_learner_boundary_enforcement.py`
- `tests/test_v3_learner_runtime_parity.py`
- `tests/test_run_api_contract.py`

### CI-Facing Contract Checks
Validated by assertions that:
- illegal tuples fail with named codes
- runtime assembly cannot construct learners without validated grammar tuples
- registry matrix remains machine-readable and validator-parity aligned
- runtime acceptance set equals compatibility matrix acceptance set
- learner identity is propagated through API metadata and artifact identity files

---

## Net State After V3.5.0

- learner tuple composition is now a typed and validated contract
- boundary-level enforcement is active at both spec-build and runtime assembly seams
- registry + matrix outputs are stable, machine-readable, and parity-tested
- preset expansion is deterministic and CI-guarded
- learner identity is traceable in run/report metadata and artifact identity

V3.5.0 therefore closes the learner-grammar legality and governance gap in the V3 architecture sequence.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_learner_grammar_spec.py tests/test_v3_learner_validator.py tests/test_v3_learner_registry.py tests/test_v3_learner_presets.py`
- `python -m pytest -q tests/test_v3_learner_boundary_enforcement.py tests/test_v3_learner_runtime_parity.py`
- `python -m pytest -q tests/test_run_api_contract.py`


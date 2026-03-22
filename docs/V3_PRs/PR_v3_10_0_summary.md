# V3.10.0 Summary - UI Registry Foundation Contracts

## Overview
V3.10.0 establishes the canonical UI contract foundation for Preset Mode by turning TrialState, operator, dependent-variable, and preset bindings into machine-validated registries.

Primary outcomes:
- added canonical TrialState field registry with schema validation and loader APIs
- added canonical operator registry with enforced TrialState cross-references
- added canonical dependent-variable registry with TrialState/operator cross-reference validation
- added a thin Acquisition-first preset registry contract with registry-ID reference checks
- added a combined registry integrity surface for UI/report consumers
- added a blocking CI bucket for all V3 UI registry contract gates

This slice converts proposal-level UI registry definitions into enforceable contract code paths.

---

## Slice 1 - TrialState Field Registry Contract

### Objective
Create canonical TrialState registry artifacts and enforce schema invariants.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/trialstate_registry.py`
- `tests/test_v3_ui_trialstate_registry.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- introduced canonical `TRIALSTATE_FIELD_REGISTRY` payload
- added validator/loader APIs:
  - `validate_trialstate_field_registry(...)`
  - `get_trialstate_field_registry()`
  - `list_trialstate_field_ids()`
  - `get_trialstate_field(...)`
- enforced required groups/fields, uniqueness, and required metadata keys

---

## Slice 2 - Operator Registry Contract + Field Cross-Refs

### Objective
Define canonical operator registry and enforce TrialState ID cross-references.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/operator_registry.py`
- `tests/test_v3_ui_operator_registry.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`
- `virtual_shaping_lab/ui/contracts/trialstate_registry.py`

Changes:
- introduced canonical `OPERATOR_REGISTRY` payload
- added validator/loader APIs:
  - `validate_operator_registry(...)`
  - `get_operator_registry()`
  - `list_operator_ids()`
  - `get_operator(...)`
- enforced:
  - unknown `reads_trialstate` / `writes_trialstate` rejection
  - stage-index constraints
  - operator-id consistency and upstream/downstream operator references
- aligned TrialState contract with operator writes by adding canonical `associability` field

---

## Slice 3 - Dependent Variable Registry Contract + Cross-Refs

### Objective
Define canonical dependent-variable registry and enforce cross-registry references.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/dependent_variable_registry.py`
- `tests/test_v3_ui_dependent_variable_registry.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- introduced canonical `DEPENDENT_VARIABLE_REGISTRY` payload with category/display-policy sections
- added validator/loader APIs:
  - `validate_dependent_variable_registry(...)`
  - `get_dependent_variable_registry()`
  - `list_dependent_variable_ids()`
  - `get_dependent_variable(...)`
  - `validate_dependent_variable_ids(...)`
  - `validate_preset_results_contract(...)`
- enforced:
  - unknown `source_fields` rejection against TrialState registry
  - unknown `related_trialstate_fields` rejection
  - unknown `related_operators` rejection against operator registry
  - preset-facing dependent-variable ID validation

---

## Slice 4 - Registry Integration Surface + CI Bucket

### Objective
Provide one stable integration surface and enforce contract gates in CI.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/preset_registry.py`
- `virtual_shaping_lab/ui/contracts/registry_integrity.py`
- `tests/test_v3_ui_registry_integrity.py`
- `tests/test_v3_ui_preset_registry_contract.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`
- `.github/workflows/ci.yml`

Changes:
- added thin Acquisition-first preset contract:
  - canonical `PRESET_REGISTRY`
  - shape validation for required keys and registry ID references
- added combined integrity entrypoint:
  - `load_ui_registries()`
  - `validate_ui_registry_integrity(...)`
- enforced preset boundary checks:
  - preset results contract variable IDs must be valid dependent-variable IDs
  - results contract cannot include undeclared dependent variables
- fixed preset validation error boundary so preset validation failures are surfaced as `PresetRegistryValidationError`
- added blocking CI bucket `Run V3 UI registry contracts` with all five registry suites

---

## Closeout Impact

After V3.10.0:
- V3 now has canonical UI contract registries for TrialState, operators, dependent variables, and presets
- cross-registry reference integrity is enforced at test time
- UI/report consumers can resolve all registry metadata through one stable integration surface
- CI now blocks invalid UI registry drift before merge

This slice establishes the contract substrate required for Preset Mode implementation slices (starting Acquisition-first) without leaking preset-specific semantics into core registry foundations.

---

## Validation

### Slice and Integration Gates
Validated through:
- `tests/test_v3_ui_trialstate_registry.py`
- `tests/test_v3_ui_operator_registry.py`
- `tests/test_v3_ui_dependent_variable_registry.py`
- `tests/test_v3_ui_registry_integrity.py`
- `tests/test_v3_ui_preset_registry_contract.py`

### CI-Facing Contract Checks
Validated by assertions that:
- all required registry schema keys and baseline entities are present
- operator/dependent-variable contracts reject unknown TrialState/operator references
- preset registry enforces shape + registry ID integrity with Acquisition-only scope
- combined registry integration load path is stable and rejects broken constituent registries

---

## Net State After V3.10.0

- canonical V3 UI registry contracts are implemented and validated
- preset contract shape is enforced early with thin Acquisition-first scope
- cross-registry validation is centralized for consumers
- CI enforces the V3 UI registry contract bucket as a blocking gate

V3.10.0 therefore completes the UI registry foundation milestone.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_ui_trialstate_registry.py`
- `python -m pytest -q tests/test_v3_ui_operator_registry.py`
- `python -m pytest -q tests/test_v3_ui_dependent_variable_registry.py`
- `python -m pytest -q tests/test_v3_ui_registry_integrity.py tests/test_v3_ui_preset_registry_contract.py`
- `python -m pytest -q tests/test_v3_ui_trialstate_registry.py tests/test_v3_ui_operator_registry.py tests/test_v3_ui_dependent_variable_registry.py tests/test_v3_ui_registry_integrity.py tests/test_v3_ui_preset_registry_contract.py`


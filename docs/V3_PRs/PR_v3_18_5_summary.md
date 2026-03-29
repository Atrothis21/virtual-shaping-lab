# V3.18.5 Summary - Executable Learner Core (P, Delta, W)

## Overview
V3.18.5 delivers the first executable learner core on top of canonical V3 learner contracts, with concrete prediction (`P`), error (`Delta`), and update (`W`) operators plus deterministic step orchestration and numeric proofs.

Primary outcomes:
- added executable operator protocol surface and null optional operator defaults
- implemented linear/tabular/action-value prediction operators with a unified prediction output contract
- implemented RW and TD(0) error/update operators with strict update mutation ownership
- added canonical `LearnerBundle.step()` orchestration with persisted per-step measurement intermediates
- added executable preset materialization for `rescorla_wagner` and `td0`, including symbolic-spec to executable mapping
- added blocking CI bucket coverage for V3.18.5 executable learner core gates

This slice closes the V3.18.5 milestone for the first deterministic executable learner path over canonical contracts.

---

## Slice 1 - Operator Protocols and Null Objects

### Objective
Define executable learner operator interfaces and stable null optional operators.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/learning/operators/base.py`
- `tests/test_v3_learner_operators_base.py`

Updated:
- `virtual_shaping_lab/vsl/agent/learning/operators/__init__.py`
- `virtual_shaping_lab/vsl/agent/learning/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`

Changes:
- introduced runtime-checkable protocols:
  - `PredictionOperator`
  - `ErrorOperator`
  - `UpdateOperator`
  - `AttentionOperator`
  - `EligibilityOperator`
- added null optional operators:
  - `NullAttentionOperator`
  - `NullEligibilityOperator` / `NullTraceOperator`
- exported operator surfaces through public VSL package facades

---

## Slice 2 - Prediction Operators

### Objective
Materialize executable prediction operators with one normalized output contract.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/learning/operators/prediction.py`
- `tests/test_v3_learner_operators_prediction.py`

Updated:
- `virtual_shaping_lab/vsl/agent/learning/operators/__init__.py`
- `virtual_shaping_lab/vsl/agent/learning/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`

Changes:
- added prediction output contract:
  - `PredictionOutput`
- implemented predictors:
  - `LinearStateValuePredictionOperator`
  - `TabularStateValuePredictionOperator`
  - `LinearActionValuePredictionOperator`
- enforced deterministic output shape for state-value and action-value paths

---

## Slice 3 - Error and Update Operators

### Objective
Implement executable RW/TD(0) error and update paths with explicit mutation ownership.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/learning/operators/error.py`
- `virtual_shaping_lab/vsl/agent/learning/operators/update.py`
- `tests/test_v3_learner_operators_error.py`
- `tests/test_v3_learner_operators_update.py`

Updated:
- `virtual_shaping_lab/vsl/agent/learning/operators/__init__.py`
- `virtual_shaping_lab/vsl/agent/learning/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`

Changes:
- added error operators:
  - `RescorlaWagnerErrorOperator`
  - `TD0ErrorOperator`
- added update operators:
  - `RescorlaWagnerUpdateOperator`
  - `TD0UpdateOperator`
- kept parameter/state mutation in update operators only

---

## Slice 4 - LearnerBundle Execution Core

### Objective
Add canonical executable step orchestration for learner runtime behavior.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/learning/bundle.py`
- `tests/test_v3_learner_bundle_execution.py`

Updated:
- `virtual_shaping_lab/vsl/agent/learning/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`

Changes:
- added:
  - `LearnerBundle`
  - `LearnerStepResult`
- enforced canonical step order:
  1. predict
  2. error
  3. optional attention/eligibility hooks
  4. update
- persisted per-step intermediate fields required for measurement/reporting consumption
- added call-order and numeric path assertions for RW and TD(0)-style trajectories

---

## Slice 5 - Executable Presets, Numeric Proof, and CI Hardening

### Objective
Materialize executable core presets and enforce deterministic numeric/runtime parity in CI.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/learning/executable_presets.py`
- `tests/test_v3_learner_numeric_golden.py`
- `tests/test_v3_learner_executable_instantiation.py`

Updated:
- `tests/test_v3_learner_presets.py`
- `tests/test_v3_learner_runtime_parity.py`
- `virtual_shaping_lab/vsl/agent/learning/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `.github/workflows/ci.yml`
- `V3.18.5_plan.md`

Changes:
- added executable preset surface:
  - `build_executable_learner_preset(...)`
  - `executable_learner_preset_names(...)`
  - `build_executable_learner_from_spec(...)`
  - `ExecutableLearnerPreset`
- materialized executable presets for:
  - `rescorla_wagner`
  - `td0`
- added deterministic golden numeric assertions for:
  - acquisition
  - extinction
  - TD propagation
- added symbolic-spec to executable mapping checks + unsupported-spec diagnostics
- added blocking CI step:
  - `Run V3.18.5 executable learner core`

---

## Closeout Impact

After V3.18.5:
- canonical learner grammar now has a concrete executable core path for RW/TD0
- operator stages (`P`, `Delta`, `W`) are implemented with strict mutation boundaries
- learner step orchestration is deterministic and measurement-facing intermediate data is preserved
- executable preset paths and symbolic-spec executable mapping are test-enforced
- CI blocks regressions across operator contracts, bundle execution, numeric goldens, and executable parity

V3.18.5 therefore completes the first executable learner-core cutover milestone on top of V3.18.0 contract hardening.

---

## Validation

### Slice and Core Gates
Validated via:
- `tests/test_v3_learner_operators_base.py`
- `tests/test_v3_learner_operators_prediction.py`
- `tests/test_v3_learner_operators_error.py`
- `tests/test_v3_learner_operators_update.py`
- `tests/test_v3_learner_bundle_execution.py`
- `tests/test_v3_learner_numeric_golden.py`
- `tests/test_v3_learner_executable_instantiation.py`
- `tests/test_v3_learner_presets.py`
- `tests/test_v3_learner_runtime_parity.py`

### CI-Facing Contract Checks
Validated by assertions that:
- executable operator protocol implementations conform to stable contract shapes
- `LearnerBundle.step()` preserves deterministic stage ordering and runtime intermediates
- executable RW/TD0 trajectories remain numerically stable on golden paths
- legal symbolic specs map to executable core implementations for supported tuples
- V3.18.5 executable learner core bucket remains blocking in CI

---

## Net State After V3.18.5

- V3 learner runtime now includes an executable core for prediction/error/update loops
- executable bundle orchestration and step-result contracts are public and test-covered
- executable preset and symbolic-spec instantiation surfaces are available for RW/TD0
- CI now enforces V3.18.5 executable-core guarantees as a blocking quality gate

V3.18.5 establishes the executable learner baseline for subsequent attention/eligibility and broader tuple execution expansion.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_learner_operators_base.py tests/test_v3_learner_operators_prediction.py tests/test_v3_learner_operators_error.py tests/test_v3_learner_operators_update.py`
- `python -m pytest -q tests/test_v3_learner_bundle_execution.py`
- `python -m pytest -q tests/test_v3_learner_numeric_golden.py`
- `python -m pytest -q tests/test_v3_learner_executable_instantiation.py`
- `python -m pytest -q tests/test_v3_learner_presets.py tests/test_v3_learner_runtime_parity.py -k "executable or runtime_acceptance_parity_matches_registry_matrix"`

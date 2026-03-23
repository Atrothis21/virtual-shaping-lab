# V3.12.5 Summary - Basis Compiler and Legality Engine

## Overview
V3.12.5 implements the legality and compiler layer that turns operator-basis subset contracts into deterministic, plan-ready payload sections.

Primary outcomes:
- added a rule-based legality engine with explicit cross-slot compatibility matrix and machine-readable error codes
- added a selection compiler that normalizes subset/default/disabled slot states into frozen compile artifacts
- added deterministic compile hashing and parity coverage across repeated runs
- added a materialization mapper from compiled basis artifacts into canonical payload sections
- enforced compiler guardrails for runtime-boundary imports and registry-driven legality behavior
- added canonical fixture inventory, legality-matrix artifact drift checks, and compiler hardening tests
- integrated a blocking CI bucket for V3 operator-basis compiler gates

This slice completes the legality/compiler foundation required for basis-driven assembly integration.

---

## Slice 1 - Legality Rule Engine

### Objective
Implement rule-based legality checks over operator-basis subsets with explicit diagnostics.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/operator_legality_engine.py`
- `tests/test_v3_operator_legality_engine.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- added slot-level and cross-slot legality validation APIs
- added explicit compatibility matrix:
  - `OPERATOR_COMPATIBILITY_MATRIX`
- added machine-readable legality error contract:
  - `OperatorLegalityError(code, details)`
- added deterministic error-code coverage tests for required/conditional and incompatible combinations

---

## Slice 2 - Selection Compiler

### Objective
Compile validated subset contracts into deterministic frozen artifacts.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/operator_selection_compiler.py`
- `tests/test_v3_operator_selection_compiler.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`
- `tests/test_v3_operator_legality_engine.py` (rule-order coverage fix)

Changes:
- added compile API:
  - `compile_operator_selection_artifact(...)`
- added deterministic compile identity:
  - `stable_selection_compile_json(...)`
  - `stable_selection_compile_hash(...)`
- added normalization for:
  - subset-selected slots
  - default-selected slots
  - disabled slots
- added strict compile-time registry-universe enforcement for slot selections

---

## Slice 3 - Plan Materialization Mapper

### Objective
Map compiled basis artifacts into canonical experiment payload sections.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/operator_plan_materialization.py`
- `tests/test_v3_operator_plan_materialization.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- added materialization APIs:
  - `materialize_compiled_operator_plan_sections(...)`
  - `compile_and_materialize_operator_plan(...)`
- materialized canonical sections:
  - `experiment.agent`
  - `experiment.runtime`
  - `experiment.program.phases` attachments
- added protocol-family support:
  - `acquisition`
  - `extinction`
  - `differential_acquisition`
- added explicit route mapping snapshots from UI selection IDs to internal builder families

---

## Slice 4 - Compiler Guardrails

### Objective
Enforce architecture boundaries and registry-driven compiler behavior.

### Implemented
Added:
- `tests/test_v3_operator_compiler_boundaries.py`

Changes:
- added AST/import boundary checks for compiler modules
- added guard ensuring legality/compiler modules are not preset-hardcoded
- added explicit unsupported-selection and unknown-slot error-path contract checks

---

## Slice 5 - Compiler Hardening Pass

### Objective
Add fixture inventory, deterministic hardening, legality-matrix artifact checks, and CI integration.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/operator_compiler_fixtures.py`
- `tests/test_v3_operator_compiler_hardening.py`
- `tests/test_v3_operator_legality_matrix_drift.py`
- `docs/v3_12_5_legality_matrix.json`
- `docs/v3_12_5_legality_matrix.md`

Updated:
- `docs/v3_12_5_operator_basis_migration_notes.md`
- `.github/workflows/ci.yml`
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- added canonical compiled fixture inventory for:
  - acquisition
  - extinction
  - differential acquisition
- added deterministic regression sweep over repeated compile/materialization runs
- added performance guardrail test for compile latency stability
- published legality-matrix artifact with drift check against engine matrix
- added blocking CI bucket:
  - `Run V3 operator basis compiler`

---

## Closeout Impact

After V3.12.5:
- operator subset legality is enforced by explicit rule contracts and stable error codes
- basis selections compile into deterministic frozen artifacts with normalized slot states
- compiled artifacts materialize into canonical payload sections through a typed mapper path
- compiler boundaries and registry-driven behavior are test-enforced
- legality matrix and canonical fixture inventory are published and CI-guarded

V3.12.5 therefore completes the legality/compiler phase for basis-first plan materialization.

---

## Validation

### Slice and Hardening Gates
Validated via:
- `tests/test_v3_operator_legality_engine.py`
- `tests/test_v3_operator_selection_compiler.py`
- `tests/test_v3_operator_plan_materialization.py`
- `tests/test_v3_operator_compiler_boundaries.py`
- `tests/test_v3_operator_compiler_hardening.py`
- `tests/test_v3_operator_legality_matrix_drift.py`

### CI-Facing Contract Checks
Validated by assertions that:
- legality matrix codes remain explicit and stable
- selection compiler is deterministic and registry-constrained
- materialized plan sections remain canonical and route-mapped
- compiler modules remain decoupled from runtime execution paths
- published legality artifact remains in sync with engine matrix

---

## Net State After V3.12.5

- legality + compile + materialization contract path is implemented and test-covered
- canonical fixture sweep and deterministic regression checks are in place
- legality matrix is published with drift protection
- blocking CI coverage exists for the full V3.12.5 compiler surface

V3.12.5 closes the basis compiler and legality-engine milestone for the V3 line.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_operator_legality_engine.py`
- `python -m pytest -q tests/test_v3_operator_selection_compiler.py`
- `python -m pytest -q tests/test_v3_operator_plan_materialization.py`
- `python -m pytest -q tests/test_v3_operator_compiler_boundaries.py`
- `python -m pytest -q tests/test_v3_operator_compiler_hardening.py`
- `python -m pytest -q tests/test_v3_operator_legality_matrix_drift.py`
- `python -m pytest -q tests/test_v3_operator_legality_engine.py tests/test_v3_operator_selection_compiler.py tests/test_v3_operator_plan_materialization.py tests/test_v3_operator_compiler_boundaries.py tests/test_v3_operator_compiler_hardening.py tests/test_v3_operator_legality_matrix_drift.py`

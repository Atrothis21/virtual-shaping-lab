# V3.12.5 Migration Notes - Operator Basis Compiler Phase

## Context

V3.12.0 introduces foundation contracts for operator-basis-first preset authoring:
- maximal schema
- basis selection registry
- preset subset contract

V3.12.5 will add legality and compile layers that transform selections into plan-ready artifacts.

## What Changes in V3.12.5

### 1. Legality matrix becomes explicit executable policy

Cross-slot compatibility checks move from static guidance into enforced compile-time rules:
- required/conditional slot constraints
- incompatible selection combinations
- deterministic error codes

### 2. Compiler becomes first transform boundary

Selections will compile into typed intermediate artifacts before assembly:
- normalized slot selections
- resolved defaults/disabled states
- routed builder-family metadata carried forward

### 3. Materialization path becomes deterministic

Compiler outputs become the source for plan materialization:
- canonical payload sections
- stable compile identity/hash
- predictable diagnostics on invalid subsets

### 4. Legality matrix is published and drift-guarded

- authoritative artifact: `docs/v3_12_5_legality_matrix.json`
- human-readable companion: `docs/v3_12_5_legality_matrix.md`
- CI drift guard: `tests/test_v3_operator_legality_matrix_drift.py`

## Migration Guidance for Contributors

### Do

- read selection options from `operator_basis_registry`
- validate subset surfaces with `operator_subset_contract`
- keep builder routing metadata explicit (`internal_builder_family`)
- add legality rules as data-driven checks with stable codes

### Do Not

- hard-code selectable operator lists in UI/editor code
- infer runtime routing from display labels
- bypass registry parity checks
- mix selection-oriented and runtime-instantiation schemas in one payload object

## Pre-Migration Checklist (before V3.12.5 coding)

- [ ] Foundation tests are green:
  - `tests/test_v3_operator_basis_schema.py`
  - `tests/test_v3_operator_registry_contract.py`
  - `tests/test_v3_operator_subset_contract.py`
- [ ] CI foundation bucket is active and blocking
- [ ] Any new selection IDs are added to both:
  - `OPERATOR_BASIS_MASTER_TABLE`
  - `OPERATOR_BASIS_REGISTRY` parity checks

## Forward-Compatibility Notes

- Keep `version` fields stable and bump intentionally.
- Treat selection IDs as contract identifiers.
- Keep error codes and compile diagnostics deterministic for snapshot-based CI.
- Keep legality matrix artifact in lockstep with engine registry.

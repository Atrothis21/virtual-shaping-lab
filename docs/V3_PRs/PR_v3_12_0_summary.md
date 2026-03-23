## Overview
V3.12.0 establishes the first-class operator-basis contract foundation for V3 preset authoring and compile inputs, without changing runtime execution semantics.

Primary outcomes:
- introduced a typed maximal operator basis schema for `phi,c,g,e,p,delta,a,w,pi,omega,m`
- added a canonical master table of allowed selections per operator slot
- added a basis selection registry with per-selection parameter schemas
- separated UI-selectable implementation IDs from internal builder-family routing metadata
- introduced a validated `PresetDefinition` subset contract and registry-generated UI universe guard
- added a typed deterministic intermediate compile artifact (`OperatorAssemblySpec`)
- added documentation for ownership/boundaries and V3.12.5 migration guidance
- added a blocking CI bucket for operator-basis foundation contracts

This slice provides the contract substrate required for legality/compiler and assembly cutover work in V3.12.5+.

---

## Slice 1 - Typed Operator Basis Schema

### Objective
Define a typed maximal schema for operator-basis preset payloads.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/operator_basis_schema.py`
- `tests/test_v3_operator_basis_schema.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- added typed schema contract for maximal basis slots
- enforced uniform slot shape (`enabled`, `selection`, `params`)
- added canonical master table for allowed selections per slot
- added deterministic schema JSON/hash helpers

---

## Slice 2 - Operator Registry Unification Layer

### Objective
Create a canonical basis registry with per-selection schemas and explicit UI/internal routing split.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/operator_basis_registry.py`
- `tests/test_v3_operator_registry_contract.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- added basis registry covering all basis slots
- added per-selection `params_schema`
- added explicit `ui_selectable_implementations` and `internal_builder_family`
- added registry validation and lookup APIs for compiler/UI surfaces

---

## Slice 3 - Preset Subset Contract

### Objective
Define and enforce legal preset subsets over the maximal basis.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/operator_subset_contract.py`
- `tests/test_v3_operator_subset_contract.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- added `PresetDefinition` subset validation (`operator_subset`, `defaults`, `locked`, `optional`)
- enforced required-slot presence and selection legality
- added guard policy and validator requiring UI selectable universe to be registry-generated

---

## Slice 4 - Basis-to-Plan Intermediate Spec

### Objective
Introduce typed deterministic intermediate compile artifact for basis subsets.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/operator_assembly_spec.py`
- `tests/test_v3_operator_assembly_spec.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`
- `.github/workflows/ci.yml`

Changes:
- added `compile_operator_subset_to_assembly_spec(...)`
- added typed `OperatorAssemblySpec` validation
- enforced registry-ID-only parity in compiled selections
- added deterministic JSON/hash helpers for compiled artifact
- wired assembly-spec test into V3 basis foundation CI bucket

---

## Slice 5 - Foundation Hardening Pass

### Objective
Finalize docs and CI hardening for foundation contracts.

### Implemented
Added:
- `docs/v3_operator_basis_foundation.md`
- `docs/v3_12_5_operator_basis_migration_notes.md`

Updated:
- `.github/workflows/ci.yml`

Changes:
- documented contract boundaries and ownership split
- documented canonical master table and selection-schema references
- documented UI-selectable vs internal builder-family distinction
- added V3.12.5 migration guidance for legality/compiler phase
- added blocking CI bucket:
  - `Run V3 operator basis foundation`

---

## Closeout Impact

After V3.12.0:
- operator basis is defined as a typed, versioned, test-enforced contract surface
- preset subsets are validated against registry-defined selectable universes
- deterministic intermediate compile artifact exists for acquisition subset path
- CI blocks regressions across schema, registry, subset, and intermediate compile contracts

V3.12.0 therefore completes the operator-basis contract foundation needed for V3.12.5 legality/compiler implementation.

---

## Validation

### Slice Gates
Validated via:
- `tests/test_v3_operator_basis_schema.py`
- `tests/test_v3_operator_registry_contract.py`
- `tests/test_v3_operator_subset_contract.py`
- `tests/test_v3_operator_assembly_spec.py`

### CI-Facing Contract Checks
Validated by assertions that:
- basis slot universe is complete and stable
- per-selection schema/routing metadata is explicit and valid
- subset legality and registry-generated UI universe guard are enforced
- intermediate compile output is deterministic and registry-ID constrained

---

## Net State After V3.12.0

- maximal operator basis schema contract is in place and test-covered
- basis registry + subset contract + intermediate compile spec are implemented
- foundation docs and migration notes are published
- blocking CI coverage exists for basis foundation contracts

V3.12.0 establishes the foundation for basis-driven legality, compilation, and assembly cutover in subsequent slices.

## Validation Commands

Targeted gates for this slice:
- `python -m pytest -q tests/test_v3_operator_basis_schema.py`
- `python -m pytest -q tests/test_v3_operator_registry_contract.py`
- `python -m pytest -q tests/test_v3_operator_subset_contract.py`
- `python -m pytest -q tests/test_v3_operator_assembly_spec.py`
- `python -m pytest -q tests/test_v3_operator_basis_schema.py tests/test_v3_operator_registry_contract.py tests/test_v3_operator_subset_contract.py tests/test_v3_operator_assembly_spec.py`

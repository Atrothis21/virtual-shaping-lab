# V3 Operator Basis Foundation Contract (V3.12.0)

## Purpose

Define the canonical foundation for operator-basis-first preset authoring and compiler inputs, while preserving existing runtime behavior.

This document covers:
- contract boundaries
- ownership split
- canonical master table source
- UI-selectable vs internal-builder-family distinction
- test and CI guardrails

## Canonical Contract Modules

- Basis schema:
  - `virtual_shaping_lab/ui/contracts/operator_basis_schema.py`
- Basis registry:
  - `virtual_shaping_lab/ui/contracts/operator_basis_registry.py`
- Subset contract:
  - `virtual_shaping_lab/ui/contracts/operator_subset_contract.py`

## Contract Boundaries

### Selection-Oriented (UI/authoring boundary)

Inputs are preset/operator selections, not runtime objects:
- slot-level toggles and selections
- per-selection params
- lock/default/optional subset rules

Contracts:
- maximal schema shape (`operator_basis_schema`)
- canonical slot universe (`phi,c,g,e,p,delta,a,w,pi,omega,m`)
- preset subset legality surface (`operator_subset_contract`)

### Instantiation-Oriented (compiler/runtime boundary)

Compiler and assembly consume typed normalized contracts:
- per-selection parameter schema metadata
- routed builder-family metadata
- deterministic normalized artifacts and identities

Contracts:
- basis selection registry (`operator_basis_registry`)
- future compile artifact contracts (V3.12.5+)

## Ownership Split

### Representation family
- slots: `phi`, `c`, `g`
- internal builder family: `representation`

### Learner family
- slots: `e`, `p`, `delta`, `a`, `w`
- internal builder family: `learner`

### Agent control family
- slot: `pi`
- internal builder family: `agent_control`

### Environment/protocol family
- slot: `omega`
- internal builder family: `environment_protocol`

### Report/readout family
- slot: `m`
- internal builder family: `report_readout`

## Canonical Master Table Source

The canonical master table for slot universe and allowed selections is:
- `OPERATOR_BASIS_MASTER_TABLE` in `operator_basis_schema.py`

The basis registry must remain consistent with this table:
- `operator_basis_registry.py` validates exact parity for:
  - slot coverage
  - selection IDs
  - UI selectable implementations

## UI-Selectable vs Internal Builder Distinction

Each selection contract carries both:
- UI-selectable implementation identity:
  - `ui_selectable_implementations` per slot
  - `selection.id`
- Internal routed builder family:
  - `selection.internal_builder_family`

Policy:
- UI lists are generated from registry-only sources
- internal builder routing is explicit metadata, not inferred from UI labels

## Registry-Only UI Universe Policy

Policy statement source:
- `UI_SELECTABLE_UNIVERSE_POLICY` in `operator_subset_contract.py`

Enforced by:
- `build_registry_generated_ui_universe()`
- `validate_registry_generated_ui_universe()`

This prohibits hand-authored operator option lists in preset/editor surfaces.

## Test Gates

- `tests/test_v3_operator_basis_schema.py`
- `tests/test_v3_operator_registry_contract.py`
- `tests/test_v3_operator_subset_contract.py`

## CI Gate

Blocking bucket step in `.github/workflows/ci.yml`:
- `Run V3 operator basis foundation`

This bucket protects:
- schema shape and slot completeness
- registry parity and mapping integrity
- subset legality and registry-generated UI universe policy

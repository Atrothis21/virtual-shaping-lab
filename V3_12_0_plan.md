# V3.12.0 Plan - Operator Basis Contract Foundation

## Objective

Establish the operator basis set as a typed, canonical contract that can be compiled into `ExperimentPlan` inputs, without changing runtime behavior yet.

## Source Inputs

- `payload_refactor.md`
- `docs/V3_operator_info/operator_basis_set.md`
- `virtual_shaping_lab/api/run.py`
- `virtual_shaping_lab/experiment/plan_builder.py`
- `virtual_shaping_lab/experiment/assemble.py`

## Entry Criteria

- V3.11.5 preset replication work is merged and green.
- Canonical payload path is stable (`experiment.program/agent/runtime`).
- Existing operator pipeline defaults are stable and test-covered.

## Commit-Sized Slices

## Slice 1 - Typed Operator Basis Schema

Deliver:

- typed schema for maximal basis contract (`phi,c,g,e,p,delta,a,w,pi,omega,m`)
- uniform operator slot shape (`enabled`, `selection`, `params`)
- explicit master table of allowed selections per operator slot
- schema-level IDs/versioning for forward compatibility

Tests:

- schema acceptance tests
- malformed slot rejection tests
- deterministic serialization/hash tests
- master-table completeness tests (all basis slots represented)

## Slice 2 - Operator Registry Unification Layer

Deliver:

- canonical operator registry map for all basis slots
- per-selection parameter schema metadata (not only per slot)
- explicit split for each selection:
  - `ui_selectable_implementations`
  - `internal_builder_family` routing metadata
- registry APIs for UI + compiler lookup

Tests:

- registry completeness tests (all slots present)
- uniqueness/stability tests for selection IDs
- unknown-selection rejection tests
- per-selection parameter-schema validation tests
- UI-visible vs internal-family mapping integrity tests

## Slice 3 - Preset Subset Contract

Deliver:

- `PresetDefinition` contract for legal subset selection from maximal basis
- lock/optional/default semantics moved into subset contract
- subset shape validator (selection-oriented, not runtime-oriented)
- statement + contract guard: UI selectable universe is generated only from registry data

Tests:

- subset validation tests
- required-operator presence tests
- lock/editability contract tests
- no-hand-authored-operator-list assertions for preset/editor surfaces

## Slice 4 - Basis-to-Plan Intermediate Spec

Deliver:

- typed intermediate compile target (`OperatorAssemblySpec`)
- deterministic transform from subset schema to intermediate spec
- no runtime assembly ownership changes yet

Tests:

- transform determinism tests
- snapshot tests for canonical presets (acquisition first)
- contract parity tests (intermediate spec references registry IDs only)

## Slice 5 - Foundation Hardening Pass

Deliver:

- docs: contract boundaries and ownership tables
- docs: canonical operator master table and per-selection parameter schema references
- docs: explicit UI-selectable vs internal-builder-family distinction
- migration notes for V3.12.5 compiler phase
- CI bucket for operator-basis contract tests

Tests:

- full foundation test sweep
- no-legacy-field leakage assertions in basis contract path

## Testing Plan

- `python -m pytest -q tests/test_v3_operator_basis_schema.py`
- `python -m pytest -q tests/test_v3_operator_registry_contract.py`
- `python -m pytest -q tests/test_v3_operator_subset_contract.py`
- `python -m pytest -q tests/test_v3_operator_assembly_spec.py`

## CI Updates

Add blocking bucket:

- `Run V3 operator basis foundation`
  - basis schema tests
  - operator registry contract tests
  - subset contract tests
  - assembly-spec determinism tests

## Exit Criteria

- maximal operator basis contract is typed, versioned, and validated
- canonical operator master table exists and is test-enforced
- per-selection parameter schemas exist and are test-enforced
- UI-selectable implementations are explicitly separated from internal builder families
- preset subset model is defined and enforced by tests
- deterministic basis->intermediate transform exists for acquisition path
- runtime behavior remains unchanged while foundation contracts are introduced

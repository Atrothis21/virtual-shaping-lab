# V3.8.0 Summary - Phenomenon Registry and Minimal Operator Bundle Enforcement

## Overview
V3.8.0 turns scientific phenomenon coverage from descriptive docs into executable registry contracts.

Primary outcomes:
- introduced a typed phenomenon registry schema with enforceable fields for:
  - recipe
  - operator bundles
  - operator constraints
  - readouts
  - fixture binding
  - caveat tier
- populated canonical phenomenon entries in the V3 registry
- enforced required-operator constraints at plan/build and run execution boundaries
- bound each registry entry to runnable fixture builders with 100% matrix coverage checks
- added bundle-ablation gates to validate minimal-bundle necessity claims
- wired V3.8 registry tests into blocking CI

This slice establishes a machine-auditable scientific coverage contract instead of relying on narrative alignment alone.

---

## Slice 1 - Registry Schema

### Objective
Define typed schema contracts for registry entries.

### Implemented
Added:
- `virtual_shaping_lab/vsl/registry/phenomenon_registry.py`
- `virtual_shaping_lab/vsl/registry/__init__.py`
- `tests/test_v3_phenomenon_registry_schema.py`

Updated:
- `virtual_shaping_lab/vsl/__init__.py`

Changes:
- introduced typed contracts:
  - `OperatorBundleSpec`
  - `ConstraintSpec`
  - `ReadoutSpec`
  - `PhenomenonRegistryEntry`
- added deterministic payload/hash helpers:
  - `phenomenon_registry_payload(...)`
  - `phenomenon_registry_hash(...)`
- added strict caveat tier policy (`none | minor | moderate | major`)
- added schema validation for key consistency and required fields

---

## Slice 2 - Canonical Registry Population

### Objective
Populate canonical V3 phenomenon registry entries.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/registry/phenomenon_registry.py`
- `tests/test_v3_phenomenon_registry_schema.py`

Changes:
- added canonical entries for:
  - `blocking`
  - `conditioned_inhibition`
  - `renewal_aba`
  - `renewal_abc`
  - `renewal_aab`
  - `extinction`
  - `rapid_reacquisition`
  - `occasion_setting`
  - `operant_conditioning`
  - `matching_law`
  - `shaping`
  - `resurgence`
  - `superextinction`
  - `spontaneous_recovery`
- each entry now carries explicit:
  - protocol recipe binding
  - minimal bundle declaration
  - required operators
  - readout signatures
  - fixture reference
  - caveat tier

---

## Slice 3 - Operator Constraint Enforcement

### Objective
Fail run/build when registry-required operators are missing.

### Implemented
Updated:
- `virtual_shaping_lab/api/services.py`
- `virtual_shaping_lab/vsl/registry/phenomenon_registry.py`
- `virtual_shaping_lab/vsl/registry/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`

Added:
- `tests/test_v3_phenomenon_operator_constraints.py`

Changes:
- added protocol-to-registry matching helper:
  - `match_phenomenon_registry_entry_for_protocol(...)`
- added enforcement hook in `PlanService.resolve(...)` and `RunService.execute(...)`
- required-stage subset checks now raise explicit constraint violations when missing
- unregistered protocols remain ungated by registry constraints

---

## Slice 4 - Fixture Binding

### Objective
Bind every registry entry to runnable CI fixtures.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/registry/phenomenon_registry.py`
- `virtual_shaping_lab/vsl/registry/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`

Added:
- `tests/test_v3_phenomenon_fixture_binding.py`

Changes:
- added fixture matrix/link helpers:
  - `registry_fixture_matrix(...)`
  - `validate_registry_fixture_links(...)`
- enforced fixture link format contract (`<module>::<callable>`)
- added fixture-binding CI checks:
  - registry-to-fixture key coverage must be 100%
  - each fixture must resolve, validate, and build to `ExperimentPlan`
  - built protocol must match registry recipe protocol

---

## Completion Pass - CI and Minimal-Bundle Auditability

### Objective
Close remaining partial criteria for bundle necessity and blocking CI integration.

### Implemented
Added:
- `tests/test_v3_phenomenon_bundle_ablation.py`

Updated:
- `.github/workflows/ci.yml`

Changes:
- added ablation gate that perturbs each entry’s required operator keys and asserts enforcement failure
- added blocking CI bucket:
  - `tests/test_v3_phenomenon_registry_schema.py`
  - `tests/test_v3_phenomenon_operator_constraints.py`
  - `tests/test_v3_phenomenon_fixture_binding.py`
  - `tests/test_v3_phenomenon_bundle_ablation.py`

---

## Closeout Impact

After V3.8.0:
- phenomenon coverage is encoded as enforceable registry contracts
- required operator constraints are enforced in plan/run paths
- fixture coverage is explicit and test-auditable
- minimal-bundle claims are backed by ablation tests
- caveat-tier labeling is mandatory and schema-validated
- V3.8 registry gates are now part of blocking CI

This slice closes the contract gap between scientific phenomenon intent and executable runtime guarantees.

---

## Validation

### Slice and Completion Gates
Validated through:
- `tests/test_v3_phenomenon_registry_schema.py`
- `tests/test_v3_phenomenon_operator_constraints.py`
- `tests/test_v3_phenomenon_fixture_binding.py`
- `tests/test_v3_phenomenon_bundle_ablation.py`
- `tests/test_full_payloads.py`

### CI-Facing Contract Checks
Validated by assertions that:
- registry entry schema and caveat policies are strict and deterministic
- canonical registry entries are present and structurally valid
- operator constraints fail fast for missing required stages
- fixture links are complete and runnable end-to-end
- required operator ablation breaks registry contract checks

---

## Net State After V3.8.0

- V3 has a typed, enforceable phenomenon registry layer
- scientific claims are mapped to explicit operator/readout/fixture contracts
- operator constraints are enforced at plan and run seams
- fixture coverage and minimal-bundle necessity are CI-gated

V3.8.0 therefore completes the phenomenon-registry contract foundation for subsequent scientific coverage expansion.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_phenomenon_registry_schema.py tests/test_phenomena_catalog.py`
- `python -m pytest -q tests/test_v3_phenomenon_operator_constraints.py tests/test_v3_phenomenon_registry_schema.py tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_v3_phenomenon_fixture_binding.py tests/test_v3_phenomenon_registry_schema.py tests/test_full_payloads.py`
- `python -m pytest -q tests/test_v3_phenomenon_bundle_ablation.py tests/test_v3_phenomenon_registry_schema.py tests/test_v3_phenomenon_operator_constraints.py tests/test_v3_phenomenon_fixture_binding.py`

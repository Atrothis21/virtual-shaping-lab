# V3.13.0 Summary - First-Class Basis-Driven Assembly Cutover

## Overview
V3.13.0 makes basis compile/materialized artifacts the primary assembly contract for covered presets and propagates that identity through run/report metadata.

Primary outcomes:
- upgraded `ExperimentPlan` with typed basis compile/materialized surfaces for assembly consumption
- introduced builder-family routing contract (`representation`, `learner`, `agent_control`, `environment_protocol`, `report_readout`)
- enforced explicit protocol-vs-phase boundary rules with deterministic unit build keys
- integrated basis compile identity and measurement (`m`) provenance identity into `/run` and regenerated report metadata
- hardened cutover by removing duplicate legacy decision helpers, adding no-legacy-branch assertions, publishing assembly ownership docs, and finalizing CI bucket coverage

This slice completes the assembly cutover from mixed decision paths to first-class basis-driven routing for covered presets.

---

## Slice 1 - Assembly Input Contract Upgrade

### Objective
Extend typed plan surfaces and make assembly prefer basis artifacts over legacy config fields.

### Implemented
Updated:
- `virtual_shaping_lab/experiment/domain/types.py`
- `virtual_shaping_lab/experiment/assemble.py`

Added:
- `tests/test_v3_basis_assembly_contract.py`

Changes:
- added `ExperimentPlan` basis surfaces:
  - `basis_compile_artifact`
  - `basis_materialized_sections`
  - accessors for typed readback
- updated `_plan_to_config(...)` to prioritize basis materialized sections for:
  - program phases
  - agent/representation/learning/policy
  - runtime context inference
- preserved fallback behavior when basis sections are absent
- retained plan hash stability independent of basis metadata

---

## Slice 2 - Object Build Routing by Basis Family

### Objective
Establish explicit routing contract from slot selections to internal builder families.

### Implemented
Added:
- `virtual_shaping_lab/experiment/basis_routing.py`
- `tests/test_v3_assembly_routing_by_operator_family.py`

Changes:
- added canonical slot-to-family mapping:
  - `phi,c,g -> representation`
  - `e,p,delta,a,w -> learner`
  - `pi -> agent_control`
  - `omega -> environment_protocol`
  - `m -> report_readout`
- added deterministic routing contract artifact + stable hash/json helpers
- enforced UI selection ID vs builder-family distinction in contract shape
- added invalid-family rejection and core snapshot stability coverage

---

## Slice 3 - Protocol vs Phase Materialization Boundary

### Objective
Make protocol-vs-phase build boundary explicit and test-enforced.

### Implemented
Added:
- `virtual_shaping_lab/experiment/protocol_phase_boundary.py`
- `tests/test_v3_protocol_phase_boundary.py`

Updated:
- `virtual_shaping_lab/experiment/assemble.py`
- `virtual_shaping_lab/ui/contracts/operator_plan_materialization.py`

Changes:
- added boundary resolver:
  - `resolve_unit_build_boundary(...)`
  - `derive_unit_build_key(...)`
- enforced explicit boundary overrides and contract errors for invalid overrides
- acquisition remains atomic phase by default unless contract says otherwise
- emitted deterministic per-unit:
  - `build_boundary`
  - `unit_build_key`
- aligned materialized phase payloads with canonical `trials` requirements

---

## Slice 4 - API Run Path Integration

### Objective
Propagate basis-driven assembly identity through run/report paths.

### Implemented
Updated:
- `virtual_shaping_lab/api/services.py`
- `virtual_shaping_lab/analysis/report/report.py`
- `tests/test_run_api_contract.py`

Changes:
- `/run` metadata now includes:
  - `basis_compile_identity` (subset hash, selected slots, routing hash, routed objects)
  - `measurement_provenance_identity` (slot `m` selection/builder-family provenance)
- regenerated report metadata preserves identity parity from source run/payload artifacts
- `artifact_identity.json` now persists both identity surfaces
- added propagation and regeneration parity assertions in API contract tests

---

## Slice 5 - Assembly Cutover Hardening

### Objective
Finalize hardening, docs, and blocking CI for basis-driven assembly.

### Implemented
Updated:
- `virtual_shaping_lab/experiment/assemble.py`
- `tests/test_v3_basis_assembly_contract.py`
- `.github/workflows/ci.yml`

Added:
- `docs/v3_basis_driven_assembly_contract.md`

Changes:
- removed duplicate dead legacy routing helper branches in assembly
- added no-legacy-branch assertion for covered presets when basis sections exist
- documented first-class assembly ownership and builder-family keyed routing tables
- added blocking CI step:
  - `Run V3 basis-driven assembly`

---

## Closeout Impact

After V3.13.0:
- assembly object build decisions are basis-driven for covered presets
- routing decisions use internal builder-family metadata, not UI labels
- protocol/phase boundary behavior is explicit, deterministic, and test-enforced
- run/report artifacts expose basis compile + measurement provenance identities for traceability
- CI blocks regressions across basis assembly contract, routing, boundary, and API propagation paths

V3.13.0 therefore closes the first-class basis-driven assembly integration milestone.

---

## Validation

### Slice and Cutover Gates
Validated via:
- `tests/test_v3_basis_assembly_contract.py`
- `tests/test_v3_assembly_routing_by_operator_family.py`
- `tests/test_v3_protocol_phase_boundary.py`
- `tests/test_run_api_contract.py -k basis`

### CI-Facing Contract Checks
Validated by assertions that:
- basis materialized sections take precedence for covered preset assembly paths
- slot routing remains aligned to internal builder-family ownership
- boundary overrides are explicit and contract-validated
- run/report metadata consistently carries basis/measurement identity surfaces

---

## Net State After V3.13.0

- first-class basis-driven assembly contract is active for covered presets
- API/report identity surfaces now trace assembly provenance end-to-end
- no-legacy-branch guard exists for covered preset phase-source selection
- blocking CI coverage exists for the full V3.13 assembly cutover surface

V3.13.0 completes the assembly cutover phase and sets the runtime boundary for post-cutover simplification.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_basis_assembly_contract.py`
- `python -m pytest -q tests/test_v3_assembly_routing_by_operator_family.py`
- `python -m pytest -q tests/test_v3_protocol_phase_boundary.py`
- `python -m pytest -q tests/test_run_api_contract.py -k basis`
- `python -m pytest -q tests/test_v3_basis_assembly_contract.py tests/test_v3_assembly_routing_by_operator_family.py tests/test_v3_protocol_phase_boundary.py`

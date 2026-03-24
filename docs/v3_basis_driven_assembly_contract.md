# V3 Basis-Driven Assembly Contract (V3.13.0)

## Purpose

Define first-class assembly ownership for basis-driven plans and remove duplicate legacy decision paths for covered presets.

This document is the runtime counterpart to basis selection/compiler contracts:
- `docs/v3_operator_basis_foundation.md`
- `docs/v3_12_5_operator_basis_migration_notes.md`

## Assembly Ownership

For covered presets, assembly reads build decisions from basis artifacts in this order:
1. `ExperimentPlan.basis_materialized_sections`
2. `ExperimentPlan.basis_compile_artifact` (routing identity/provenance)
3. Canonical payload/runtime typed fields only where basis sections do not provide data

Legacy phase/program fields remain fallback-only for non-covered flows.

## Builder-Family Routing Contract

Routing is keyed by internal builder family, not UI labels.

| Builder Family | Basis Slots | Assembly Surface |
| --- | --- | --- |
| `representation` | `phi,c,g` | representation object + params |
| `learner` | `e,p,delta,a,w` | learner spec and learning object |
| `agent_control` | `pi` | policy/agent control behavior |
| `environment_protocol` | `omega` | protocol-vs-phase build path |
| `report_readout` | `m` | report/readout provenance identity |

UI selection IDs are preserved for traceability, but routing decisions are made by `builder_family`.

## Protocol/Phase Boundary

Boundary decisions are explicit and validated:
- acquisition defaults to atomic phase
- protocol keys default to protocol build when registered
- explicit phase override on protocol-only keys is rejected by contract

Unit artifacts expose:
- `build_boundary`
- deterministic `unit_build_key`

## API Identity Surfaces

`/run` and regenerated `/runs/{id}/report` metadata include:
- `basis_compile_identity`
  - subset hash
  - selected slots
  - routing hash
  - routed objects by builder-family groups
- `measurement_provenance_identity`
  - slot `m` selection IDs
  - internal builder families
  - report-readout routes

`artifact_identity.json` includes the same identities.

## Hardening Policy

For covered presets:
- assembly should not branch on legacy phase/program decision paths when basis sections are present
- no routing inference from UI labels is allowed
- routing uses builder-family metadata only

## CI Gate

Blocking CI bucket:
- `Run V3 basis-driven assembly`
  - `tests/test_v3_basis_assembly_contract.py`
  - `tests/test_v3_assembly_routing_by_operator_family.py`
  - `tests/test_v3_protocol_phase_boundary.py`
  - `tests/test_run_api_contract.py -k basis`

# V3 Basis-First API Payload Contract

## Scope

This document defines the `/run` payload boundary for migrated V3 preset flows.

## Accepted Payload Modes

- `canonical_v3`
  - Payload provides canonical runtime shape only:
    - `experiment.program`
    - `experiment.agent`
    - `experiment.runtime`
    - `report`
- `canonical_v3_with_basis_authoring_metadata`
  - Same canonical runtime shape as above, plus optional basis authoring metadata:
    - `basis_authoring` (UI/compiler provenance only)

## Rejected Payload Modes

- `legacy_flat_experiment`
  - Legacy top-level experiment fields (for example `learner`, `phases`, `protocol`) are rejected.
- `mixed_legacy_and_canonical`
  - Mixing canonical runtime keys with legacy flat fields is rejected.

## API Diagnostics

When payload mode is rejected, `/run` returns `validation_error` with:

- actionable message: mixed/legacy mode not supported
- reason string from validator
- accepted payload modes list
- rejected payload modes list
- hint to submit canonical runtime shape only

## Artifact Metadata

Run and regenerated report metadata include:

- `payload_mode_identity.payload_mode`
- `payload_mode_identity.payload_contract_version`
- `payload_mode_identity.basis_authoring_present`
- `payload_mode_identity.basis_preset_id`

The same identity is persisted in `artifact_identity.json` for traceability.

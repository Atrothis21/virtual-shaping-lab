# V3 Operator-Basis-First Authoring Guide

## Purpose

This guide defines the supported authoring path for migrated preset UI routes.

## Authoring Contract

For migrated preset pages:

1. Author UI state as basis subset selections + declared edits.
2. Materialize via preset basis materialization API.
3. Submit only canonical runtime payload to `/run`.

## Required Payload Shape to `/run`

Accepted shape:

- `experiment.program`
- `experiment.agent`
- `experiment.runtime`
- `report`

Optional metadata for migrated routes:

- `basis_authoring` (provenance only)

Rejected shapes:

- legacy flat experiment payload
- mixed canonical + legacy payloads

## Registry-Driven Selectable Universe Rule

Selectable operator implementations and basis choices must be generated from registries:

- `operator_basis_registry`
- `preset_registry` contract surfaces

Do not hand-author selectable option lists in preset/editor code for migrated routes.

## Bridge Policy

- Migrated routes: legacy canonicalization bridge disabled.
- Unmigrated routes: explicit fallback bridge retained during migration window.

## Runtime/Artifact Traceability

Run/report artifacts carry payload mode identity:

- payload mode
- contract version
- basis authoring presence and preset id

This identity is emitted in API metadata and persisted in `artifact_identity.json`.

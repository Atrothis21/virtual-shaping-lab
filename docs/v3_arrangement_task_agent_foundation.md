# V3 Arrangement-Task-Agent Foundation

## Purpose

This document defines the V3 tuple foundation that composes:

- arrangement axis (`pavlovian`, `operant`)
- task implementation axis (arrangement-scoped task implementations)
- agent bundle axis (declarative operator bundle identity)

into a deterministic operator-subset artifact and provenance record.

## Contract Surfaces

- `ui.contracts.arrangement_contract`
  - owns arrangement identity and arrangement-level policy semantics
  - defines arrangement required/optional/forbidden slot constraints
- `ui.contracts.task_registry`
  - owns base phenomenon IDs and arrangement-scoped implementation IDs
  - defines implementation requirements and hybrid/deferred/forbidden tuple policy
- `ui.contracts.agent_bundle_registry`
  - owns declarative bundle identity (`operator_selections`)
  - enforces arrangement compatibility
  - keeps builder-family constraints as secondary metadata
- `ui.contracts.arrangement_task_agent_composition`
  - composes tuple axes into deterministic `operator_subset`
  - emits provenance with identity + axis contribution map + composition hash

## Legality Integration

`ui.contracts.operator_legality_engine` now supports two legality paths:

- preset path:
  - `validate_operator_legality(preset_definition=...)`
- tuple path:
  - `validate_operator_legality(arrangement_id=..., phenomenon_id=..., agent_bundle_id=...)`

Tuple path behavior:

- runs tuple composition first
- if composition fails, returns/raises `LGL_E_TUPLE_COMPOSITION`
- includes tuple context and violating axis in diagnostics
- if composition succeeds, runs existing slot/cross-slot legality checks on composed subset

## Ownership Boundary

- UI-visible selectable implementations remain registry-driven.
- Task and bundle contracts cannot define hand-authored selectable universes.
- Composition does not own runtime builders; it owns tuple-to-subset contract output only.

## Migration Compatibility

- Preset flows remain supported via thin preset task references and composition wrappers.
- Tuple path is additive and does not remove existing preset legality behavior.

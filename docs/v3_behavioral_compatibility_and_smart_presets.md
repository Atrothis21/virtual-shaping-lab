# V3 Behavioral Compatibility and Smart Presets

## Scope

V3.16.0 introduces a pre-run expected-outcome layer and a thin smart preset projection layer on top of tuple authoring.

Contract layers:

1. Legality layer (`operator_legality_engine`): structural composability only.
2. Behavioral compatibility layer (`behavioral_compatibility_registry` + `behavioral_compatibility_engine`): predicted outcome support for legal tuples.
3. Smart preset layer (`smart_preset_projection`): named tuple coordinates only, with no duplicated operator subset definitions.

## Expected Outcome Contract

Compatibility statuses:

- `success`
- `partial`
- `structurally_invalid`
- `behaviorally_unsupported`
- `novel`

UI behavior:

- run is blocked for `structurally_invalid`
- `behaviorally_unsupported` requires actionable unmet-requirement guidance
- explanation source is evaluator/registry-derived and not hand-authored in page logic
- key operator factors should prefer composition provenance when available

API surface:

- `POST /catalog/tuple-authoring/compatibility`

## Smart Preset Projection Contract

Smart presets are thin named projections over tuple identity:

- required:
  - `label`
  - `tuple_reference` (`arrangement_id`, `phenomenon_id`, `agent_bundle_id`)
- optional:
  - `description`
  - education metadata

Prohibited in smart presets:

- embedded operator payloads (`operator_subset`)
- hidden defaults layer (`hidden_defaults`)
- legacy preset template/default/lock payload duplication

API surface:

- `GET /catalog/smart-presets`
- `POST /catalog/smart-presets/{smart_preset_id}/project`

The projection endpoint emits tuple authoring payload shape (`arrangement`, `task`, `agent`, `edits`) and does not materialize or embed operator subset data.

## End-to-End Flow

1. User selects arrangement, task, agent tuple.
2. UI requests compatibility and renders expected outcome guidance before run.
3. Optional smart preset selection projects to tuple payload.
4. Tuple materialization composes operator subset through composition contracts.
5. Run executes with tuple identity and composition identity retained in run/report metadata.

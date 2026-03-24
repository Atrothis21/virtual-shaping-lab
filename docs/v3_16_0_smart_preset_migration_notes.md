# V3.16.0 Smart Preset Migration Notes

## Purpose

This migration note maps legacy core preset labels to V3.16.0 smart preset tuple projections.

The mapping is label-to-tuple only. It does not introduce a hidden defaults layer and does not duplicate operator payload definitions.

## Legacy Label to Smart Preset Mapping

- `acquisition` -> `classical_acquisition`
  - tuple: `(pavlovian, acquisition, rw_classical)`
- `extinction` -> `classical_extinction`
  - tuple: `(pavlovian, extinction, rw_classical)`
- `differential_acquisition` -> `classical_differential_acquisition`
  - tuple: `(pavlovian, differential_acquisition, rw_classical)`
- `operant_conditioning` -> `operant_acquisition`
  - tuple: `(operant, acquisition, rw_operant)`

## Authoring Boundary

Smart preset projection output remains tuple authoring payload:

- `arrangement`
- `task`
- `agent`
- `edits`

Tuple payloads are then composed/materialized through tuple contracts. Operator subset structure is still owned by composition and materialization layers.

## Migration Guidance

1. Replace direct legacy label usage with smart preset IDs where tuple-first UX is intended.
2. Use `POST /catalog/smart-presets/{smart_preset_id}/project` for conversion to tuple payload.
3. Preserve user-provided edits as explicit `edits`; do not introduce inferred hidden defaults.
4. If behavior differs, inspect tuple compatibility status and explanation from `POST /catalog/tuple-authoring/compatibility` before run.

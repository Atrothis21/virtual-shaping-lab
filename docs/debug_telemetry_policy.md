# Debug Telemetry Policy (V2.16 Slice 3.1)

## Purpose
Define runtime-level debug telemetry policy semantics so browser consumers and runtime emitters share one contract.

Primary rule:
- debug telemetry is opt-in and must not alter simulation semantics.

---

## Policy Object

Runtime policy contract:
- `DebugTelemetryPolicy` in `virtual_shaping_lab/experiment/debug_policy.py`

Fields:
- `enabled: bool`
- `mode: trial | tick | both`
- `max_active_features: int | None`
- `sample_every_n_ticks: int | None`

Defaults:
- `enabled = false`
- `mode = tick`
- `max_active_features = None`
- `sample_every_n_ticks = None`

---

## Emission Semantics

### Debug Disabled
- no `debug` field is emitted on records.
- runtime behavior and learning updates are unchanged.

### Debug Enabled, `mode = tick`
- debug payload is emitted on tick records only.
- trial-level records remain without debug unless explicitly requested by mode.

### Debug Enabled, `mode = trial`
- debug payload is emitted on trial-level records only.
- for tick-executed trials, trial debug is the latest aggregated/summary debug view for that trial.

### Debug Enabled, `mode = both`
- debug payload is emitted on both tick and trial records.

---

## Optional Volume Controls

### `max_active_features`
- when provided, `debug.active_features` must be capped to the first `N` features in deterministic order.

### `sample_every_n_ticks`
- when provided, tick debug payload is emitted only for ticks where:
  - `tick % sample_every_n_ticks == 0`

Both controls are telemetry-only controls and must not affect learning, action selection, or reward logic.

---

## Compatibility Contract

- Existing payloads with only `runtime.debug: bool` remain valid.
- `runtime.debug=true` with no policy fields maps to default policy behavior.
- policy parsing is backward-compatible and does not require UI changes.

---

## UI Consumption Notes

- UI should treat missing `debug` as expected when debug mode is off.
- UI should not infer policy from record count; read runtime settings or metadata when available.
- Large-run rendering should assume telemetry decimation/capping may be active.


# V3.22.0 Measurement Path Inventory

## Purpose
Inventory measurement-related execution and artifact paths before canonical V3.22 measurement contract ownership is introduced.

This inventory follows `agent_protocol_interaction.md` constraints:
- Measurement consumes records/traces after runtime execution.
- Measurement does not compute protocol/agent control logic.
- Measurement does not mutate protocol timeline or agent internal state.

---

## Scope Scanned
- `virtual_shaping_lab/analysis/report/*`
- `virtual_shaping_lab/vsl/records/*`
- `virtual_shaping_lab/vsl/rollout/*`
- `virtual_shaping_lab/experiment/runner.py`
- `tests/*` measurement/report/replay surfaces

---

## Ownership Matrix

### Keep (Canonical Ownership Targets)
- `virtual_shaping_lab/vsl/records/schema.py`
  - Keep as canonical rollout record boundary.
- `virtual_shaping_lab/vsl/records/adapters/rollout_records.py`
  - Keep as canonical promotion surface from runtime steps to trace-rich records.
- `virtual_shaping_lab/analysis/report/report.py`
  - Keep as report normalization and artifact writer surface.
- `virtual_shaping_lab/vsl/rollout/replay_harness.py`
  - Keep as deterministic replay harness and hash-contract boundary.

### Bridge (Compatibility Surface, Expiry Required)
- Legacy report payload normalization fallback branches in:
  - `virtual_shaping_lab/analysis/report/report.py`
  - Keep temporarily for backward compatibility with pre-trace payload shapes.
- Runner/report entrypoints that invoke analysis module-level routines directly:
  - `virtual_shaping_lab/experiment/runner.py` integration paths
  - Bridge until runtime measurement adapter seam lands in V3.22.10.

### Delete-Now (When Canonical Measurement Contract Lands)
- Ad-hoc metric/trace extraction logic duplicated outside canonical measurement contract modules.
- Any direct per-test custom shaping of protocol/policy traces that bypasses canonical record adapters.

### Delete-Later (After Runtime Measurement Seam and CI Guards Are Green)
- Compatibility-only fallback fields that duplicate canonical `measurement_traces` keys.
- Legacy report normalization branches not required by active UI/API payload modes.

---

## Boundary Rules (Locked for V3.22)
- Measurement input surface:
  - `TrialRecord` + promoted traces (`policy_traces`, `protocol_traces`, future `measurement_traces`)
- Measurement must not:
  - compute or mutate protocol consequence/advance/stop
  - compute or mutate agent learning internals directly
  - run inside environment step loop
- Measurement output surfaces:
  - metrics/figures/report artifacts
  - promoted trace summaries in records/reports only

---

## Risk Notes
- High risk: hidden coupling where report normalization performs runtime-semantics reconstruction.
- High risk: non-deterministic hash drift from unordered trace payloads.
- Medium risk: bridge branches that outlive migration window.
- Medium risk: measurement logic slipping into runtime loop helpers.

---

## Migration Guidance
- V3.22.0:
  - establish canonical `MeasurementSpec` + validation + registry ownership
- V3.22.5:
  - implement executable measurement operators and canonical bundle
- V3.22.10:
  - add runtime measurement adapter seam (post-run only)
- V3.22.15:
  - promote measurement traces to first-class record/report fields
- V3.22.20:
  - closeout CI aggregation + architecture/evidence documentation

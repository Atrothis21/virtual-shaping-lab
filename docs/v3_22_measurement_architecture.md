# V3.22 Measurement Architecture

## Purpose
This document records the V3.22 canonical measurement execution seam and the measurement runtime boundary contract used for change control.

## Canonical Boundary Contract
Boundary rules are aligned to `agent_protocol_interaction.md` and `behavior_measurement.md`.

Runtime protocol/agent owns:
- trial-time execution and state transitions
- observation/policy/learner causal loop
- rollout record emission and protocol/agent traces

Measurement owns:
- post-run analysis over emitted records/traces
- deterministic metric/figure/summary/provenance materialization
- report-facing measurement normalization

Measurement must be read-only with respect to runtime state.

## Canonical Measurement Execution Path
The only approved measurement runtime path is:
1. `virtual_shaping_lab/vsl/rollout/replay_harness.py`
2. `ReplayHarness.run_with_measurement(...)`
3. `virtual_shaping_lab/vsl/runtime/measurement_adapter.py`
4. `RuntimeMeasurementAdapter.step(...)`
5. `virtual_shaping_lab/vsl/measurement/bundle.py`
6. `MeasurementBundle.step(...)`
7. `virtual_shaping_lab/vsl/records/adapters/rollout_records.py`
8. `virtual_shaping_lab/analysis/report/report.py`

## Canonical Metadata and Trace Surfaces
Measurement traces are first-class:
- rollout record:
  - `metadata.measurement_traces.metrics`
  - `metadata.measurement_traces.figures`
  - `metadata.measurement_traces.summary`
  - `metadata.measurement_traces.provenance`
- rollout record identity:
  - `metadata.measurement_artifact_identity.hash_algorithm`
  - `metadata.measurement_artifact_identity.measurement_payload_hash`
  - `metadata.measurement_artifact_identity.preset_name`
- report normalization:
  - `measurement_metrics`
  - `measurement_figures`
  - `measurement_summary`
  - `measurement_provenance`

## Explicitly Non-Canonical / Banned Paths
The following are not allowed in active runtime flow:
- invoking measurement operators inside protocol/agent pre-outcome or post-outcome stepping
- mutating protocol or agent runtime state from measurement surfaces
- bypassing `RuntimeMeasurementAdapter` from runtime replay integration paths
- emitting ad-hoc measurement trace/report fields outside canonical metadata keys
- non-deterministic ordering of measurement payloads that affects replay/hash identity

## Guardrail Requirements
V3.22 closeout requires CI-enforced checks for:
- measurement ownership + grammar/validation/registry/preset stability
- executable measurement operator/bundle/preset/golden stability
- runtime measurement seam/parity/boundary stability
- measurement trace promotion/report normalization stability
- end-to-end integration matrix and measurement-inclusive replay/hash determinism

## Change Control
Any measurement-runtime change must:
1. update canonical seam files (`runtime/measurement_adapter.py`, `rollout/replay_harness.py`) if behavior changes
2. update rollout/report trace contracts when metadata shape changes
3. update guardrail tests and closeout CI bucket
4. provide PR evidence mapped to the checklist in `docs/v3_22_pr_evidence_checklist.md`


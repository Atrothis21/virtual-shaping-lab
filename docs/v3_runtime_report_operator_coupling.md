# V3 Runtime/Report Operator Coupling Contract

## Purpose

This contract defines how declared operator-basis selections are reflected in runtime execution metadata and report artifacts.

The goal is to keep runtime behavior, report alignment, and replay identity deterministic and traceable.

## Stage Realization Semantics

Each declared stage in `operator_pipeline` is classified as exactly one of:

- `executed`: stage has an active runtime execution step.
- `delegated`: stage behavior is delegated to another owned runtime surface.
- `metadata_only`: stage has no direct execution step but contributes identity/diagnostic metadata.

Runtime records emit:

- `metadata.operator_pipeline.stage_realization`
- `metadata.operator_pipeline.non_executing_declared_stages`

Run metadata emits:

- `metadata.operator_stage_diagnostics.realization_matrix`
- `metadata.operator_stage_diagnostics.pipeline_hashes`

## TrialState I/O Contract Binding

Declared stages are bound to operator IDs and validated against TrialState registry IDs.

Artifacts:

- `operator_stage_io_provenance.json`
  - `pipeline_hash`
  - `declared_stage_keys`
  - `stages[]` with `reads_trialstate` / `writes_trialstate`
  - `io_provenance_hash`

Unknown TrialState field references are contract violations and fail run execution.

## Measurement (`m`) to Report Alignment

Report alignment is driven by registry metadata attached to `m` readout selections.

Rules:

- no hand-authored metric mapping tables in report alignment code.
- `measurement_provenance_identity.selection_ids` drives strict readout coverage behavior.
- if strict mode is active and a metric has no readout coverage, alignment fails explicitly.
- multi-readout resolution is deterministic by `(priority, source_order, selection_id)`.

## Deterministic Artifact Contract

Report generation emits:

- `report_alignment.json`
- `report_alignment_identity.json`
- `report_alignment.sha256`

`report_alignment_identity.json` includes:

- `hash_algorithm` (`sha256`)
- `report_alignment_hash`

Run/report directories are collision-safe under timestamp ties by suffixing:

- `<timestamp>`
- `<timestamp>_01`, `<timestamp>_02`, ...

## Runtime-to-Report Identity Surfaces

Run metadata and regenerated report metadata carry:

- `basis_compile_identity`
- `measurement_provenance_identity`
- `operator_stage_diagnostics`

The same identity surfaces must remain stable across source run and regenerated report flows.


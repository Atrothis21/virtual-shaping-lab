# V2.18.7 Summary - Record Schema Guarantees and Artifact Identity

## Overview
V2.18.7 stabilizes the runtime record boundary and adds explicit reproducibility identity to persisted artifacts.

Primary outcomes:
- runtime records now carry a minimum guaranteed schema for analysis
- core missing fields are derived during record finalization instead of silently disappearing
- persisted `records.json` is normalized through the same record-finalization path as live runtime output
- report artifacts now include `artifact_identity.json`
- artifact identity now records engine, schema, plan, seed, and mechanism identity for replay/debugging

This slice makes the records-first analysis boundary more explicit and makes artifact reproducibility auditable without relying on scattered metadata fields alone.

---

## Minimum Record Schema Guarantee

### Stable Required Analysis Fields
V2.18.7 extends the stable `TrialRecord` boundary so the following minimum fields are always present after finalization:

- `step`
- `trial`
- `tick`
- `stimulus`
- `action`
- `reward`
- `prediction`
- `prediction_error`
- `policy_state`

The existing record-defaults contract remains extensible, but these fields can no longer silently disappear from persisted analysis inputs.

### Derived Fallback Semantics
The record finalization pipeline now derives missing core fields from common runtime data when possible:

- `step` from `trial_step`, otherwise `tick`
- `prediction_error` from debug telemetry when present
- `policy_state` from record metadata when present

Net effect:
- runtime producers do not need to redundantly populate the same field in every path
- the analysis boundary still receives a consistent minimum schema

### Persisted Record Normalization
Report generation now normalizes records through `finalize_record(...)` before writing `records.json`.

This is a significant boundary improvement:
- persisted records now obey the same finalization contract as in-memory runtime records
- the analysis boundary is therefore stabilized at artifact-write time, not only at runtime call sites

---

## Artifact Identity

### New Identity Artifact
V2.18.7 adds:

- `artifact_identity.json`

to generated report/run directories.

This file captures the reproducibility identity needed for replay/debugging:

- `engine_version`
- `record_schema_version`
- `plan_hash`
- `seed_identity`
- `mechanism_identity`

### Identity Sources
Artifact identity is resolved from the existing runtime/report state:

- engine version from the repository `VERSION`
- schema version from the resolved plan/report boundary
- plan hash from canonical plan identity
- seed identity from resolved plan/runtime seed
- mechanism identity from the resolved mechanism provenance stack

This consolidates previously scattered identity metadata into a single artifact-local contract.

### API Artifact Exposure
Run and regenerated-report artifact maps now include the path to:

- `artifact_identity.json`

This keeps the API envelope stable while making the new reproducibility artifact directly discoverable.

---

## Records-First Analysis Boundary

### Analysis Compatibility
The analysis contract tests now explicitly accept the new minimum record schema shape.

This matters because V2’s architectural boundary is not merely “records exist,” but:

- records are the stable public analysis input
- persisted records must be schema-complete enough for analysis to run without hidden runtime context

### Optional Extensibility Preserved
V2.18.7 does not collapse the record schema into a closed set.

Optional/extensible fields remain supported, including:
- weights
- attention
- feature vectors
- mechanism metadata

The change is therefore:
- stricter on minimum required analysis fields
- still open for richer runtime/debug payloads

---

## Validation

### Record Boundary Gates
Validated through:
- `tests/test_runtime_records.py`
- `tests/test_report.py`
- `tests/test_analysis_contracts.py`

These cover:
- minimum record schema defaults
- derived field fallback behavior
- persisted `records.json` normalization
- analysis-context compatibility with the minimum schema

### Artifact Identity Gates
Validated through:
- `tests/test_run_api_contract.py`
- `tests/test_api_contract_snapshots.py`
- `tests/test_full_payloads.py`

These cover:
- `artifact_identity.json` emission
- run/report artifact exposure
- identity-file presence in full-payload integrations
- compatibility with the existing API snapshot surface

---

## Net State After V2.18.7

- the runtime record boundary is more explicit and analysis-safe
- essential record fields can no longer silently disappear from persisted artifacts
- persisted records are normalized through the stable finalization pipeline
- artifacts now carry a dedicated reproducibility identity file
- engine/schema/plan/seed/mechanism identity is available directly from artifact output

V2.18.7 therefore closes the main record-boundary and artifact-identity gap still remaining in the V2 closeout path.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_runtime_records.py tests/test_report.py tests/test_analysis_contracts.py`
- `python -m pytest -q tests/test_run_api_contract.py tests/test_api_contract_snapshots.py tests/test_full_payloads.py`

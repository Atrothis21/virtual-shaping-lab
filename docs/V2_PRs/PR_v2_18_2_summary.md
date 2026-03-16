# V2.18.2 Summary - Canonical Payload Hard Cut and Artifact Canonicalization

## Overview
V2.18.2 makes the canonical payload shape the only accepted runtime contract and extends that rule through persisted artifacts and report regeneration.

Primary outcomes:
- runtime entrypoints now reject legacy-only payloads
- mixed canonical/legacy payloads are rejected deterministically
- runtime config and API execution paths no longer depend on canonical-to-legacy conversion
- persisted `payload.json` artifacts are canonical-only
- report regeneration now reads canonical payload artifacts only
- validation and artifact-boundary tests are green under the hard-cut contract

This is the first V2 slice that fully treats payload shape as an architectural boundary rather than a compatibility detail.

---

## Runtime Contract Lock

### Canonical-Only Runtime Ingestion
Runtime entrypoints now require the canonical ownership map:
- `experiment.program`
- `experiment.agent`
- `experiment.runtime`

Canonical program requirements are now enforced directly:
- `experiment.program.phases`
- `program.phases[].trials`

Rejected at runtime:
- legacy-only payloads
- mixed canonical/legacy payloads
- malformed canonical phase structures

Net effect:
- runtime behavior is now derived only from canonical ownership boundaries

### Deterministic Validation Failures
The hard-cut contract now produces stable failure cases for:
- missing canonical ownership sections
- mixed-shape payloads
- invalid phase arrays
- missing or invalid phase trial counts

This makes payload validation auditable and easier to debug during migration.

---

## Runtime Translation Removal

### Config and Plan Ingestion
Runtime-critical config parsing no longer round-trips canonical payloads through legacy flat fields.

What changed:
- `experiment.config` now parses canonical payload structure directly
- runtime/API plan resolution builds from canonical payloads directly
- parameter composition now locally flattens canonical payloads only as an internal adapter, rather than treating legacy payload shape as a runtime contract

Canonical sources now feed:
- program phases
- representation configuration
- learning configuration
- policy configuration
- runtime configuration
- context inference
- attention configuration
- prediction-error configuration

Net effect:
- no runtime execution path depends on legacy payload conversion

### Test Fixture Migration
Preset and contract payload fixtures used by runtime/API tests are now canonicalized before execution.

This matters because the runtime/API gates now validate the actual post-hard-cut contract instead of accidentally relying on migration-era fixture shape.

---

## Artifact Canonicalization

### Canonical `payload.json`
Persisted run artifacts now store `payload.json` in canonical shape only.

Canonical artifact invariant:
- the on-disk payload artifact must expose only:
  - `experiment.program`
  - `experiment.agent`
  - `experiment.runtime`

This means persisted artifacts now match the same ownership contract required at runtime.

### Canonical-Only Report Regeneration
Report regeneration now:
- reads canonical `payload.json`
- canonicalizes the loaded payload before plan reconstruction
- rejects legacy artifact payloads instead of silently regenerating through compatibility paths
- no longer falls back to legacy `experiment.phases` / `experiment.protocol` regeneration logic

Net effect:
- artifact replay and report regeneration now enforce the same contract as live runtime ingestion

### Provenance Preservation
Although `payload.json` is now canonical-only, report artifacts still preserve mechanism provenance emission through:
- `mechanism_provenance.json`

This keeps artifact reproducibility intact while still enforcing canonical payload persistence.

---

## Validation

### Payload Contract Gates
Validated through:
- `tests/test_payload_contract.py`
- `tests/test_validate_payload.py`

These cover:
- legacy payload rejection
- mixed-shape rejection
- canonical section requirements
- phase/trial validation

### Runtime and API Gates
Validated through:
- `tests/test_config.py`
- `tests/test_run_api_contract.py`
- `tests/test_full_payloads.py`

These cover:
- canonical config parsing
- canonical runtime plan building
- API run/report flows under canonical payloads
- runtime fixture compatibility after hard cut

### Artifact and Regeneration Gates
Validated through:
- `tests/test_report.py`
- `tests/test_run_api_contract.py`
- `tests/test_api_contract_snapshots.py`

These cover:
- canonical `payload.json` persistence
- canonical report regeneration
- rejection of legacy payload artifacts during regeneration
- stable API envelope behavior after artifact canonicalization

---

## Net State After V2.18.2

- runtime accepts canonical payloads only
- legacy payload conversion is no longer part of runtime execution semantics
- canonical ownership boundaries are enforced at both live runtime and artifact-replay boundaries
- persisted `payload.json` artifacts are canonical and schema-aligned
- report regeneration now depends on canonical artifacts only
- validation failures are more stable and migration mistakes are easier to diagnose

V2.18.2 therefore closes the main payload-contract ambiguity still left after the V2.18.0 and V2.18.1 architecture/behavior passes.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_payload_contract.py tests/test_validate_payload.py`
- `python -m pytest -q tests/test_config.py tests/test_run_api_contract.py tests/test_full_payloads.py`
- `python -m pytest -q tests/test_report.py tests/test_run_api_contract.py tests/test_api_contract_snapshots.py`

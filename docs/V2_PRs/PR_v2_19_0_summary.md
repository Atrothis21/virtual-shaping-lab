# V2.19.0 Summary - CI and Guard Hardening

## Overview
V2.19.0 makes the architecture-critical CI buckets an explicit proof surface for the V2 closeout contract.

Primary outcomes:
- closeout-critical contracts are now enforced directly in the `v2_11` guard/contract buckets
- canonical contract fixtures are guarded against regression to legacy payload shape
- typed plans, canonical payload presence, minimum record schema, artifact identity, and provenance are now covered through closeout-facing tests
- the `v2_11` guard bucket no longer relies on the deprecated `phase_factory` compatibility shim
- the architecture-critical CI gate now passes with warnings treated as errors

This slice moves V2 closer to its intended end state: architecture invariants are enforced by CI, not only described in plans and documentation.

---

## Slice 1 - Closeout Contract Coverage

### Canonical Fixture Guard
Added a dedicated guard to ensure `CONTRACT_FIXTURES` remain canonical-only.

This locks the fixture surface to:
- `experiment.program`
- `experiment.agent`
- `experiment.runtime`

and prevents regression to migration-era flat experiment payloads.

### Public Closeout Contract Tests
Added architecture-bucket coverage for the public/runtime boundary:
- typed plan envelope presence
- canonical payload presence on plans
- public rejection of legacy payload shape
- ownership-boundary rejection for phase param leaks

This matters because these are closeout-defining properties, not incidental unit-level behavior.

### Artifact and Analysis Contract Coverage
The new closeout contract test also verifies persisted runtime/report artifacts for:
- minimum record schema fields in `records.json`
- artifact identity fields in `artifact_identity.json`
- mechanism provenance emission in `mechanism_provenance.json`

Net effect:
- record schema, artifact identity, and provenance are now enforced from the architecture bucket level, not only from lower-level test files

---

## Slice 2 - Transitional Governance Retirement

### Guard Bucket No Longer Uses Compatibility Shim
The remaining warning in the `v2_11` buckets came from the guard suite importing:

- `experiment.factories.phase_factory`

which is intentionally deprecated.

V2.19.0 switches that guard to the authoritative phase surface instead:
- `experiment.phases.catalog_runtime`
- `experiment.phases.public`

This removes a migration-era dependency from the architecture-critical bucket itself.

### No Warning Filters Added
This slice deliberately does not solve the warning problem by muting it.

Instead:
- the deprecated path was removed from the guard suite
- the CI gate now passes under `-W error`

That is the correct closeout behavior because the bucket now reflects the final architecture more directly.

---

## CI Outcome

### Architecture-Critical Buckets
Validated through:
- `tests/v2_11_guards`
- `tests/v2_11_contract`
- `tests/test_run_api_contract.py`
- `tests/test_api_contract_snapshots.py`

These now enforce:
- canonical-only fixture shape
- public closeout contract behavior
- stable run/report artifact metadata
- stable API envelope expectations

### Warning-Strict Bucket
Validated through:
- `tests/v2_11_guards`
- `tests/v2_11_contract`
- `tests/behavioral_signatures`
- `-W error`

This confirms the architecture-critical CI surface is green without transitional warning allowlists.

---

## Net State After V2.19.0

- closeout-critical architecture rules are now represented directly in CI
- canonical fixtures are guarded against payload-shape regression
- typed plan, record schema, artifact identity, and provenance guarantees are enforced from the closeout buckets
- the `v2_11` guard suite no longer depends on a deprecated compatibility shim
- architecture-critical CI now passes with warnings treated as errors

V2.19.0 therefore closes the main CI/governance gap remaining in the V2 closeout path.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/v2_11_guards tests/v2_11_contract tests/test_run_api_contract.py tests/test_api_contract_snapshots.py`
- `python -m pytest -q tests/v2_11_guards tests/v2_11_contract tests/behavioral_signatures -W error`

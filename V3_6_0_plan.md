# V3.6.0 Plan - Rollout Engine and Record Schema Finalization

## Objective
Finalize rollout/records as the stable runtime-analysis boundary.

## Entry Criteria
- Environment-first stepping is complete (V3.3.0).
- Typed plan identity fields exist (V3.1.0).

## Entry Points
- `vsl/rollout/`
- `vsl/records/`
- Report generation path consuming saved records

## Source of Truth
- Glossary: `docs/v3_glossary.md`

## Commit-Sized Slices
### Slice 1 - RolloutRecord Schema Lock
- Introduce/lock `RolloutRecord` schema and versioning rules.

### Slice 2 - Identity Field Expansion
- Add rollout/episode/segment identity fields to record schema.

### Slice 3 - Replay Harness
- Implement deterministic replay harness for environment-based rollouts.

### Slice 4 - Records-Only Reporting
- Ensure reports are generated from persisted records without runtime coupling.

## Testing / CI Updates
- Replay determinism gate: stable record hashes for identical identity inputs (10/10).
- Schema compatibility gates for breaking/non-breaking version bumps.
- Report-from-records tests proving no runtime coupling.

## Exit Criteria
- Analysis/report consume records only.
- Replay harness confirms deterministic output under fixed identity inputs.
- Schema bump policy is enforced by CI.

## Migration Impact
- Downstream analysis consumers must pin schema version or migrate.

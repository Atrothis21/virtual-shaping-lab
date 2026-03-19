# V3.3.0 Plan - First-Class Environment Contract and TrialState

## Objective
Make environment semantics authoritative at runtime, with typed `TrialState` as the carrier.

## Entry Criteria
- Environment program compilers (V3.2.0) are merged.
- Rollout harness can execute environment stepping in test mode.

## Entry Points
- `vsl/environment/` contracts and implementations
- Runner/stepping path
- Trial state model definitions

## Source of Truth
- Glossary: `docs/v3_glossary.md`

## Commit-Sized Slices
### Slice 1 - Environment Contract Types
- Introduce `IEnvironment` and typed environment objects.

### Slice 2 - TrialState Carrier
- Add `TrialState` with canonical coordinates `s,x,z,w,a,u,y,m`.

### Slice 3 - Persistent vs Derived Semantics
- Encode/validate boundary between persistent coordinates and derived outputs (`prediction`, `error`).

### Slice 4 - Action Field Unification
- Enforce always-present `u` field with null/singleton action behavior for classical cases.

### Slice 5 - Runtime Stepping Migration
- Route runner/trial stepping through `IEnvironment` end-to-end.

## Testing / CI Updates
- Shared stepping API tests for both classical and operant fixtures.
- Replay determinism gate: normalized record stream hash-identical for 10/10 identical runs.
- Termination tests for terminal flags and horizon behavior.
- `TrialState` schema gate for required fields `s,x,z,w,a,u,y,m`.
- Action-field gate for null/singleton behavior in classical fixtures.

## Exit Criteria
- Runner executes through environment contract end-to-end.
- Reward/transition/termination semantics are environment-owned.
- Runtime consumes/emits typed `TrialState`.
- Persistent/derived state boundary is enforced.

## Migration Impact
- Phase-driven stepping APIs are deprecated behind environment-proxied shims.

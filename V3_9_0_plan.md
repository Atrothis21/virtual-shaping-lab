# V3.9.0 Plan - Namespace Reshape and Public API Stabilization

## Objective
Align physical package structure to finalized V3 semantics and complete public API stabilization.

## Entry Criteria
- V3.1.0 through V3.8.5 semantic contracts are merged and stable.
- Migration map is approved with release owners.

## Entry Points
- Target package roots:
  - `vsl/spec/`
  - `vsl/program/`
  - `vsl/environment/`
  - `vsl/agent/representation/`
  - `vsl/agent/learning/`
  - `vsl/agent/policy/`
  - `vsl/rollout/`
  - `vsl/records/`
  - `vsl/analysis/`
  - `vsl/registry/`
- Public facade modules and import paths

## Source of Truth
- Glossary: `docs/v3_glossary.md`

## Commit-Sized Slices
### Slice 1 - Migration Map Publication
- Publish complete module migration map (old -> new -> warning window -> removal release).

### Slice 2 - Namespace Alias Period
- Add alias imports and warnings with no hard removals.

### Slice 3 - Facade Stabilization
- Switch default public facade to new namespace while keeping alias warnings active.

### Slice 4 - Hard Removal Cut
- Remove alias paths per published removal schedule.

## Testing / CI Updates
- Deprecated import warning tests for all alias paths.
- Public facade contract tests with 100% parity against previous baseline snapshots.
- Import-audit tests: no internal legacy imports after hard-removal branch.

## Exit Criteria
- Public imports are stable and documented.
- Package ownership aligns with glossary and slice boundaries.
- Compatibility shims are either removed or scoped to active deprecation policy.

## Migration Impact
- High-impact multi-release migration for integrators.
- External adopters must follow alias -> stabilization -> removal timeline.

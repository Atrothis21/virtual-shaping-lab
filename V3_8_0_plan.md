# V3.8.0 Plan - Phenomenon Registry and Minimal Operator Bundles

## Objective
Encode scientific coverage as enforceable registry contracts (not descriptive documentation).

## Entry Criteria
- Learner registry/compatibility tables are available (V3.5.0).
- Rollout schema/readout contracts are stable (V3.6.0).

## Entry Points
- `vsl/registry/phenomenon_registry.py`
- Canonical fixture matrix
- Bundle ablation and readout validation harness

## Source of Truth
- Glossary: `docs/v3_glossary.md`

## Commit-Sized Slices
### Slice 1 - Registry Schema
- Define phenomenon registry entry schema with recipe, bundles, constraints, readouts, fixture link, and caveat tier.

### Slice 2 - Canonical Registry Population
- Add canonical phenomenon entries using the new schema.

### Slice 3 - Operator Constraint Enforcement
- Enforce required-operator subset checks at build/run time.

### Slice 4 - Fixture Binding
- Bind each registry entry to runnable CI fixtures.

## Testing / CI Updates
- Registry-fixture coverage must be 100%.
- Bundle-ablation checks validate minimal-bundle necessity claims.
- Operator-constraint gate fails run/build when required operators are missing.
- Caveat policy gate enforces tier labeling for each registry entry.

## Exit Criteria
- Canonical entries are runnable and CI-validated.
- Phenomenon constraints are enforceable.
- Minimal vs robust claims are explicit and auditable.

## Migration Impact
- Scientific docs and acceptance fixtures may be reclassified with caveat tiers.

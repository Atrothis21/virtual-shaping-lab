# V3.4.0 Plan - Universal Policy and Action-Space Semantics

## Objective
Remove architecture-level classical/operant branching from composition root by using universal policy/action-space contracts.

## Entry Criteria
- Environment contract (V3.3.0) is merged.
- Assembly fixtures are updated to typed plan inputs.

## Entry Points
- Composition root / assembly modules
- Policy package (`vsl/agent/policy/`)
- Action-space interfaces

## Source of Truth
- Glossary: `docs/v3_glossary.md`

## Commit-Sized Slices
### Slice 1 - Null Policy/Action-Space Primitives
- Add `NullActionSpace` (or `SingletonActionSpace`) and `NullPolicy`.

### Slice 2 - Unified Assembly Path
- Collapse classical and operant assembly into one composition-root path.

### Slice 3 - Branching Scope Guard
- Enforce no family branching at composition root/top-level assembly seams.

## Testing / CI Updates
- Assembly tests: classical and operant through one path.
- AST lint rule gate: `no_mode_branching_in_assembly`.
- Policy determinism tests for seeded stochastic policies.

## Exit Criteria
- One assembly path handles both families.
- Policy presence/absence is spec-driven.
- No classical/operant branching at composition-root scope.

## Migration Impact
- Family-specific assembly helpers move behind deprecated shims.

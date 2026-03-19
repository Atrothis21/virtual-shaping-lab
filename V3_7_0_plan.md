# V3.7.0 Plan - Temporal Representation and Episode/Horizon Semantics

## Objective
Make representation-time and execution-time explicit with typed temporal and episode contracts.

## Entry Criteria
- Rollout schema with episode identity is finalized (V3.6.0).
- Representation contract has temporal extension points.

## Entry Points
- `vsl/agent/representation/` temporal modules
- Runtime episode/horizon modules
- Record emission for episode terminal metadata

## Source of Truth
- Glossary: `docs/v3_glossary.md`

## Commit-Sized Slices
### Slice 1 - Temporal/Episode Types
- Introduce `TemporalBasisSpec`, `EpisodeSpec`, `HorizonSpec`, `TerminationCondition`.

### Slice 2 - Runtime/Representation Binding
- Bind temporal semantics at representation and runtime boundaries.

### Slice 3 - Record Surface Completion
- Emit episode identity and terminal flags in records.

## Testing / CI Updates
- Temporal fixture coverage: 100% of supported bases with at least 2 fixtures each.
- Episode boundary tests for terminal flags and horizon stop reasons.
- Deterministic temporal replay under fixed seed.

## Exit Criteria
- Temporal semantics are explicit and typed end-to-end.
- Episode identity and terminal state are present in records.

## Migration Impact
- Implicit temporal defaults may require preset updates.
- One-release defaulting adapter allowed for compatibility.

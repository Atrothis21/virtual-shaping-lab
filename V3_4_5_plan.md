# V3.4.5 Plan - Explicit Operator Pipeline Object

## Objective
Make operator composition order explicit, typed, and test-enforced via `OperatorPipeline`.

## Entry Criteria
- V3.3.0 environment contract is merged.
- V3.4.0 policy/action-space unification is merged.

## Entry Points
- Runtime assembly flow
- New pipeline declaration module
- Stage contract definitions

## Source of Truth
- Glossary: `docs/v3_glossary.md`

## Commit-Sized Slices
### Slice 1 - Pipeline Core Types
- Introduce `OperatorPipeline` and `OperatorStage`.

### Slice 2 - Normative Stage Ordering
- Declare/default pipeline order:
  `Phi -> C -> G -> E -> P -> Policy -> Env -> Err -> A -> Update -> Measure`.

### Slice 3 - Stage Contract Metadata
- Add `required_fields`/`produced_fields` metadata over `TrialState`.

### Slice 4 - TD/Lookahead Semantics
- Add explicit post-`Env` lookahead contract support for `Err`.

### Slice 5 - Declarative Execution Migration
- Execute runtime sequence from pipeline declaration, not implicit local call order.

## Testing / CI Updates
- Pipeline order contract test for declared sequence.
- Noncommutativity guard test by controlled stage-order mutation.
- Stage-contract gate: each stage declares inputs/outputs.
- Type-chain gate: stage outputs satisfy next-stage inputs.
- Assembly gate: runtime flow resolved via `OperatorPipeline` declaration.

## Exit Criteria
- Operator order is first-class and machine-checked.
- Runner/assembly execution uses declarative pipeline only.
- Pipeline stage identity is emitted in artifact metadata.

## Migration Impact
- Runtime sequencing internals shift from implicit flow to declarative stage execution.

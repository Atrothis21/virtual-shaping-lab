# V3.2.0 Plan - Compile Phases/Protocols into Environment Programs

## Objective
Treat phases/protocols as recipe generators that compile into typed environment programs.

## Entry Criteria
- Typed `ProgramSpec` and `EnvironmentProgramSpec` from V3.1.0 are available.
- Canonical fixture inventory is frozen for compile determinism.

## Entry Points
- `vsl/program/` (compiler layer)
- `vsl/environment/` program structures
- Existing phase/protocol recipe modules

## Source of Truth
- Glossary: `docs/v3_glossary.md`

## Commit-Sized Slices
### Slice 1 - Program Data Structures
- Add `EnvironmentProgram`, `EnvironmentSegment`, `TrialSpec`, and `EventSpec` types.

### Slice 2 - Core Family Compilers
- Implement compilers for acquisition and extinction families.

### Slice 3 - Extended Family Compilers
- Implement compilers for differential/probe/context-shift families.

### Slice 4 - Compiler Purity Guard
- Remove/forbid learner-math calls from phase compiler modules.

### Slice 5 - Compile Hash Determinism
- Add deterministic compile hashing for canonical fixtures.

## Testing / CI Updates
- Compile hash determinism: each canonical fixture compiles hash-identical for 20 repeated runs.
- Coverage gate: compiler supports all canonical phase families.
- Branch guard: no learner update calls from phase compiler modules.

## Exit Criteria
- Canonical phases compile to standardized segment outputs.
- Compiled environment program hashes are stable under identical input.
- Phase recipe layer is free of learner math.

## Migration Impact
- Phase recipe APIs continue to exist; internals become compiler-backed.
- Direct runtime logic in phase internals is deprecated.

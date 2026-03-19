# V3.2.0 Summary - Phase/Protocol Compilation into Typed Environment Programs

## Overview
V3.2.0 introduces the first compiler layer that treats phase/protocol definitions as recipe inputs and emits typed environment programs.

Primary outcomes:
- typed environment-program structures are now available for compiled execution plans
- core phase families (acquisition/extinction) compile into standardized segment/trial outputs
- extended phase families (differential/probe/context-shift) compile through the same typed path
- compiler purity is now guarded so compiler modules stay decoupled from learner/runtime behavior layers
- deterministic compile hashing is implemented and enforced across canonical preset fixtures
- compiler protocol coverage now includes canonical phase families plus canonical preset protocol-recipe families

This slice establishes a deterministic, typed compile boundary between plan semantics and runtime execution surfaces.

---

## Slice 1 - Program Data Structures

### Objective
Add typed structures for compiled environment programs.

### Implemented
Added:
- `virtual_shaping_lab/vsl/program/types.py`
- `virtual_shaping_lab/vsl/program/__init__.py`

Added tests:
- `tests/test_v3_program_types.py`

Changes:
- introduced:
  - `EventSpec`
  - `TrialSpec`
  - `EnvironmentSegment`
  - `EnvironmentProgram`
- added validation and dict roundtrip helpers for typed program artifacts

---

## Slice 2 - Core Family Compilers

### Objective
Compile acquisition/extinction families into typed environment program outputs.

### Implemented
Added:
- `virtual_shaping_lab/vsl/program/compiler.py`

Updated:
- `virtual_shaping_lab/vsl/program/__init__.py`

Added tests:
- `tests/test_v3_program_compilers_core.py`

Changes:
- implemented `compile_core_environment_program(...)`
- added deterministic phase normalization/validation for:
  - `acquisition`
  - `acquisition_template`
  - `nonreinforcement`
  - `nonreinforcement_template`
  - `extinction`
- emitted standardized segment/trial metadata (`family`, `phase_index`) from compile output

---

## Slice 3 - Extended Family Compilers

### Objective
Compile differential/probe/context-shift families through typed compiler output.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/program/compiler.py`
- `virtual_shaping_lab/vsl/program/__init__.py`

Added tests:
- `tests/test_v3_program_compilers_extended.py`

Changes:
- implemented `compile_extended_environment_program(...)`
- added support for:
  - `differential_acquisition`
  - `differential_acquisition_template`
  - `probe`
  - `probe_template`
  - `context_shift`
- added deterministic compile behavior checks for repeated identical inputs

---

## Slice 4 - Compiler Purity Guard

### Objective
Prevent compiler modules from importing runtime/cognition/analysis behavior layers.

### Implemented
Added tests:
- `tests/test_v3_program_compiler_purity.py`

Changes:
- added AST-based import-boundary guard over `virtual_shaping_lab/vsl/program/*compiler.py`
- explicitly forbids compiler imports from:
  - `experiment`
  - `agents`
  - `protocols`
  - `analysis`

---

## Slice 5 - Compile Hash Determinism

### Objective
Enforce deterministic compile hashing for canonical fixtures.

### Implemented
Updated:
- `virtual_shaping_lab/vsl/program/types.py`
- `virtual_shaping_lab/vsl/program/compiler.py`
- `virtual_shaping_lab/vsl/program/__init__.py`
- `tests/test_v3_program_types.py`

Added tests:
- `tests/test_v3_program_compile_hash_determinism.py`

Changes:
- added deterministic serialization and hashing on typed program outputs:
  - `EnvironmentProgram.to_json()`
  - `EnvironmentProgram.stable_hash()`
- added unified compiler entrypoint:
  - `compile_environment_program(...)`
- added protocol inventory helper:
  - `supported_compile_protocols()`
- tightened determinism gate:
  - all canonical preset fixtures must compile
  - each fixture must produce hash-identical output across 20 repeated compiles
- expanded compiler coverage to include:
  - remaining canonical phase families (`compound_*`, `criterion_shift`, template families)
  - canonical preset protocol-recipe families (`blocking`, `conditioned_inhibition`, `occasion_setting`, renewal, operant protocol families)

---

## Closeout Impact

After V3.2.0:
- phases/protocols can be compiled into typed, deterministic environment programs
- compile outputs have stable identity hashes suitable for CI and artifact checks
- compiler modules are protected against architecture drift into runtime learner behavior
- canonical preset fixture coverage is now enforced by compiler determinism gates

This slice creates the typed compilation layer required for subsequent environment/runtime contract evolution in V3.

---

## Validation

### Slice Gates
Validated via targeted tests:
- `tests/test_v3_program_types.py`
- `tests/test_v3_program_compilers_core.py`
- `tests/test_v3_program_compilers_extended.py`
- `tests/test_v3_program_compiler_purity.py`
- `tests/test_v3_program_compile_hash_determinism.py`

### CI-Facing Contract Checks
Validated via deterministic assertions:
- canonical preset protocol coverage is complete for compiler-supported families
- compile hashes are stable across 20 repeated runs per canonical preset fixture
- compiler modules remain free of runtime/cognition/analysis layer imports

---

## Net State After V3.2.0

- V3 now has a typed compiler boundary from phase/protocol plans to environment programs
- canonical phase and preset protocol families are compile-covered
- compile outputs have deterministic hashing for repeatable CI identity checks
- compiler purity is test-enforced

V3.2.0 therefore completes the compile-layer foundation for environment-program-driven execution in later V3 slices.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_program_types.py tests/test_v3_program_compilers_core.py tests/test_v3_program_compilers_extended.py`
- `python -m pytest -q tests/test_v3_program_compiler_purity.py`
- `python -m pytest -q tests/test_v3_program_compile_hash_determinism.py`
- `python -m pytest -q tests/test_v3_program_types.py tests/test_v3_program_compilers_core.py tests/test_v3_program_compilers_extended.py tests/test_v3_program_compile_hash_determinism.py tests/test_v3_program_compiler_purity.py`

# V3.5.0 Plan - Learner Grammar, Compatibility Validator, Preset Registry

## Objective
Make learner composition a first-class validated algebra with mandatory legality checks.

## Entry Criteria
- V3.3.0 and V3.4.0 runtime/policy semantics are finalized.
- V3.4.5 pipeline contracts are finalized.
- Learner source artifacts are approved (`operator_learner_conditions.md`, `operational_learner.md`).

## Entry Points
- `vsl/agent/learning/`
- Learner spec and preset modules
- Runtime assembly learner construction seam

## Source of Truth
- Glossary: `docs/v3_glossary.md`

## Commit-Sized Slices
### Slice 1 - Learner Grammar Type
- Implement `LearnerSpec(trace, predictor, error, attention, updater, policy)`.

### Slice 2 - Mandatory Validator
- Implement `validate_learner_spec(spec)` and wire fail-fast behavior.

### Slice 3 - Slot Registries and Compatibility Matrix
- Publish machine-readable slot registries and legality matrix.

### Slice 4 - Preset Registry
- Build named learner presets and deterministic preset expansion.

### Slice 5 - Dual Enforcement Boundaries
- Enforce validator at spec-build and runtime assembly seams.

## Testing / CI Updates
- Legality tests with named error codes for all invalid tuples.
- Constructor legality gate: illegal tuples cannot instantiate runtime learners.
- Preset expansion determinism tests (hash-stable).
- Family smoke tests: minimum 3 fixtures per supported family.
- Compatibility parity tests: runtime-accepted tuples equal registry matrix.

## Exit Criteria
- Invalid tuples fail centrally and fail fast.
- Runtime cannot construct learners without validator pass.
- Presets are deterministic and traceable in artifact metadata.
- Compatibility matrix and slot registries are machine-readable outputs.

## Migration Impact
- Legacy learner aliases handled through temporary alias map.
- Unregistered combinations move to hard-fail after deprecation window.

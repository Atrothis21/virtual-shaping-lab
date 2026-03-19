# V3.1.0 Plan - Typed Semantic Plan

## Objective
Promote planning from a dict container into typed semantic contracts (`ExperimentSpec` root with typed sub-specs).

## Entry Criteria
- `V3_0_0_plan.md` outputs are complete.
- V2->V3 mapping table is approved for `ExperimentConfig` and `ExperimentPlan`.

## Entry Points
- `vsl/spec/` (new package family)
- Plan build path currently producing `ExperimentPlan`
- Runtime modules currently reading `plan.settings[...]`
- Schema/contract tests for plan construction and serialization

## Source of Truth
- Glossary: `docs/v3_glossary.md`

## Commit-Sized Slices
### Slice 1 - Typed Spec Models
- Add typed models: `ExperimentSpec`, `ProgramSpec`, `AgentSpec`, `RepresentationSpec`, `LearnerSpec`, `PolicySpec`, `RuntimeSpec`, `AnalysisSpec`, `EnvironmentProgramSpec`.

### Slice 2 - Plan Builder Integration
- Update plan builder to construct and return typed sub-spec objects.
- Keep existing public build API signatures stable.

### Slice 3 - Deterministic Serialization/Hash
- Add typed serialization and parse paths.
- Preserve stable hash behavior across serialize/parse roundtrip.

### Slice 4 - Compatibility Adapter Layer
- Add V2 facade adapters that map old plan-access patterns to typed specs.
- Add deprecation notices for direct `plan.settings[...]` runtime reads.

## Testing / CI Updates
- Plan schema contract tests: required typed sections must exist.
- Stable hash roundtrip gate: 10/10 identical hashes for same canonical payload + seed.
- Serialization gate: `parse(serialize(x)) == x` for core fixtures.
- Static scan gate: no `dict[str, Any]` in core typed spec modules.
- Static scan gate: no direct `plan.settings[...]` reads in runtime allowlist modules.

## Exit Criteria
- `build_plan()` returns typed program/agent/runtime/analysis specs.
- Typed plan coverage is at least 95% of canonical fixture matrix.
- Serialization and stable hash gates are green.
- Missing typed sections fail schema validation.

## Migration Impact
- V2 compatibility adapters remain temporarily.
- Direct settings-based runtime access is deprecated.

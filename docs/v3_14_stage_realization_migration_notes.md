# V3.14+ Stage Realization Migration Notes

## Scope

These notes describe planned expansion work after V3.13.5 runtime/report coupling hardening.

## Current Baseline (V3.13.5)

- stage realization matrix is emitted and test-covered.
- non-executing declared stages are explicit in runtime metadata.
- TrialState I/O provenance is registry-validated.
- measurement readouts (`m`) drive report alignment in a registry-first path.

## V3.14 Migration Direction

1. Expand delegated stage execution surfaces

- Promote selected `metadata_only` stages to `executed` or `delegated` where runtime ownership exists.
- Keep stage realization classification explicit and backward compatible.

2. Tighten compile-time legality for stage/readout coverage

- Move more missing-readout and stage-coverage checks to compile/legality phases.
- Preserve runtime guardrails as fail-fast safety checks.

3. Strengthen identity and replay guarantees

- Extend deterministic artifact identities to additional derived report assets.
- Keep replay hash stability checks on basis-driven acquisition and differential-acquisition paths.

4. Preserve registry-driven boundaries

- continue to source selectable/readout universe from registries only.
- avoid preset/editor special-case mapping logic for stage/report routing.

## Compatibility Policy

- Existing metadata fields (`operator_stage_diagnostics`, `operator_stage_io_provenance`, `measurement_provenance_identity`) remain stable.
- New stage realizations should add fields or enum values in backward-compatible ways.
- Any breaking behavior changes require explicit migration note updates and CI gate additions.


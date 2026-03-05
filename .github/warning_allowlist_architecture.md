# Architecture Suite Warning Allowlist (V2.14)

Purpose:
- enforce "fail on new/unexpected warnings" for architecture-critical CI suites
- document temporary allowlisted warnings with owner and review date

Policy location:
- `.github/workflows/ci.yml` architecture bucket pytest invocations

## Allowlisted warnings

1. `DeprecationWarning` from `experiment.factories.phase_factory` compatibility shim
- Message match:
  - `experiment.factories.phase_factory is a compatibility shim; use experiment.phases.catalog_runtime or experiment.phases.public.`
- Scope:
  - architecture bucket runs that may still touch shim paths during migration checks
- Owner:
  - Runtime Architecture
- Added:
  - 2026-03-05
- Review/remove by:
  - 2026-06-01
- Removal trigger:
  - when `experiment.factories.phase_factory` compatibility shim is removed in hard-cut follow-up

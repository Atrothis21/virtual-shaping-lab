# UI Test Tiers (First-Pass Refactor)

## Purpose
Define prioritized UI test tiers so quality gates are strong but practical for incremental delivery.

This is the rollout policy for first-pass UI work (`presets + constrained builder + run/report lifecycle`).

## Tier Policy

### Tier 1 - Contract and Lifecycle Critical
- Coverage:
  - API contract snapshot checks for UI-consumed envelopes
  - lifecycle transition tests for planning/running/reporting states
  - version mismatch handling entry points
- Why first:
  - protects backend/UI compatibility and core run safety

### Tier 2 - Builder and Constraint Correctness
- Coverage:
  - builder draft translation tests (`BuilderExperimentDraft -> draft_to_payload(...)`)
  - constraint behavior tests (`hide/disable/warn/auto-correct`)
  - draft validation and invalidation flow tests
- Why second:
  - prevents builder from drifting into raw payload editing and preserves semantic safety

### Tier 3 - Screen/Interaction Regression
- Coverage:
  - route/screen integration tests (presets, builder, run, report)
  - key interaction/regression tests for first-pass visible surfaces
- Why third:
  - stabilizes user-visible behavior after core correctness is protected

### Tier 4 - Advanced/Debug UX
- Coverage:
  - advanced debug panel behavior and bounded rendering tests
  - degraded-mode/report fallback interaction tests
- Why fourth:
  - important but not first-pass blocking for baseline usability

## Gating Rules
- No first-pass screen may become default-visible without at least Tier 1 coverage for its contract/lifecycle dependencies.
- Builder-related surfaces require Tier 2 coverage before being treated as feature-complete.
- Tier 3 and Tier 4 may follow incrementally, but must be planned at feature introduction time.

## Rollout Guidance
- Introduce Tier 1 in earliest UI integration PRs.
- Add Tier 2 when constrained builder editing is introduced.
- Add Tier 3 as route-level screens stabilize.
- Add Tier 4 when advanced debug/report degraded behaviors are implemented.

## Screen-to-Tier Minimums

| Screen/Surface | Minimum Required Tier Before Default Visible | Required Test Focus |
|---|---|---|
| Presets (`/presets`) | Tier 1 | catalog contract snapshot compatibility + version mismatch entry behavior |
| Constrained Builder (`/builder`) | Tier 2 | draft translation correctness + constraint behavior + plan invalidation on edits |
| Run (`/run/:runId?`) | Tier 1 | lifecycle transitions + polling/retry behavior + run-status contract rendering |
| Report (`/report/:runId`) | Tier 1 | report request/status transitions + mismatch/degraded handling entry behavior |
| Phenomenon metadata support (within presets/builder) | Tier 1 | metadata contract rendering + recommendation fields presence handling |
| Catalog/Help (`/catalog-help`) | Tier 1 | catalog version display + load failure handling |

## Critical Flow Test Obligations

### Flow A: Preset -> Plan -> Run -> Report
- Minimum test tiers:
  - Tier 1 required before first release of this flow
  - Tier 3 added once route interactions are stable
- Must assert:
  - preset selection seeds valid draft/plan input
  - run lifecycle reaches terminal state handling (`completed`/`failed`)
  - report request/result handling is consistent with run context

### Flow B: Phenomenon Select -> Constrained Edit -> Run
- Minimum test tiers:
  - Tier 1 + Tier 2 required before first release of builder-driven flow
  - Tier 3 added after UI interaction stabilization
- Must assert:
  - phenomenon metadata seed initializes constrained draft path
  - edits trigger expected plan invalidation/revalidation behavior
  - constraint guards and translation rules preserve semantic safety

## Release Readiness Rule
- A first-pass screen/flow is not release-ready unless:
  - its minimum tier is present and passing, and
  - at least one mapped critical flow test including that screen is passing.

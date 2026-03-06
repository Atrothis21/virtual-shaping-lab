# UI State Model (First-Pass Refactor)

## Purpose
Define canonical client-side state domains and ownership boundaries for the first UI refactor pass (`presets + constrained builder + run/report lifecycle`).

This document is implementation-facing and should be treated as the source of truth for UI state ownership.

## Ownership Classes
- `local-authoritative`: state originated and owned by the client UI.
- `server-derived`: state sourced from backend API responses and treated as truth.
- `derived/transient`: computed UI state; never persisted as backend truth.

## State Domains

### `planState`
- Ownership:
  - server-derived: resolved plan payload, stable hash, plan validation output
  - local-authoritative: selected preset/protocol/phenomenon seed, pending plan request status
  - derived/transient: plan freshness indicators
- Persistence:
  - persist selected preset/protocol locally (optional)
  - do not persist resolved plan as authoritative if catalog/version mismatch is detected

### `runState`
- Ownership:
  - server-derived: run id, lifecycle status, run timestamps, artifact pointers
  - derived/transient: polling status, last refresh timestamp, optimistic loading flags
- Persistence:
  - persist last viewed run id for navigation continuity (optional)
  - lifecycle truth must always be rehydrated from backend

### `reportState`
- Ownership:
  - server-derived: report status, report artifact pointers, template used
  - local-authoritative: selected report view/tab, user-triggered regenerate intent
  - derived/transient: report readiness flags
- Persistence:
  - local view/tab preference may persist
  - report availability must re-validate against current `runState`

### `builderDraftState`
- Ownership:
  - local-authoritative: `BuilderExperimentDraft`, edit history, draft validation errors
  - derived/transient: draft completeness/readiness flags
- Persistence:
  - may persist draft locally for recovery
  - must revalidate against latest catalog constraints before submission

### `catalogCacheState`
- Ownership:
  - server-derived: extensions/catalog payload, version stamps, fetched timestamp
  - local-authoritative: cache invalidation marker
  - derived/transient: stale/fresh status
- Persistence:
  - cache may persist with TTL policy
  - stale cache must not silently override fresh server values

### `debugAdvancedState`
- Ownership:
  - local-authoritative: debug panel visibility, advanced toggle state, display limits
  - server-derived: debug payload presence/absence in run outputs
  - derived/transient: debug truncation/sampling badges
- Persistence:
  - advanced visibility preference may persist
  - debug data itself should not be persisted as canonical run truth

## Persistence Rules (Summary)
- Safe to persist:
  - user view preferences
  - constrained draft-in-progress
  - last selected preset/phenomenon
- Must be server-rehydrated:
  - run lifecycle status
  - report generation status
  - catalog payload truth and version stamps
  - resolved plan validity under current catalog/version context

## Non-Goals
- This document does not define event transition tables (handled in the next slice).
- This document does not redefine backend API contracts; see `docs/ui_contract_manifest.md`.

## State Transition Table (First Pass)

| Event | Affected State Domains | Required State Changes |
|---|---|---|
| User selects preset/phenomenon seed | `builderDraftState`, `planState` | Initialize/replace draft scaffold; clear resolved plan hash/validation; mark plan as stale. |
| User edits builder draft field | `builderDraftState`, `planState`, `reportState` | Update draft; invalidate resolved plan snapshot; clear report readiness tied to previous plan. |
| Draft validation passes locally | `builderDraftState` | Set draft readiness flag true; keep plan stale until backend `POST /plan` succeeds. |
| Draft validation fails locally | `builderDraftState` | Set validation errors; set readiness false; block submit actions. |
| `POST /plan` success | `planState`, `builderDraftState` | Store resolved plan + stable hash; mark plan fresh for current draft version. |
| `POST /plan` failure | `planState` | Store error state and recovery hint; keep previous resolved plan invalid for current draft. |
| `GET /catalog/extensions` refresh (no version drift) | `catalogCacheState`, `builderDraftState` | Replace cache payload/version stamps; revalidate draft against refreshed constraints. |
| `GET /catalog/extensions` refresh (version drift) | `catalogCacheState`, `planState`, `builderDraftState` | Mark drift flag; invalidate resolved plan freshness; require plan recomputation before run. |
| User starts run (`POST /run`) | `runState`, `reportState` | Create new run request state; clear report generation state for prior run context. |
| `POST /run` success | `runState` | Store run id/status pointers; begin polling lifecycle transitions. |
| `POST /run` failure | `runState` | Store run error; keep prior run context only as historical navigation target. |
| Poll update (`GET /runs/{id}`) running/completed/failed | `runState`, `reportState` | Update lifecycle truth from server; on `completed/failed`, stop aggressive polling; report state becomes eligible for regeneration checks. |
| User changes active run id in UI | `runState`, `reportState`, `debugAdvancedState` | Rehydrate run/report context for selected run id; clear debug-derived transient UI from previous run. |
| User requests report (`POST /runs/{id}/report`) | `reportState` | Set report generation pending state for active run. |
| Report generation success | `reportState` | Store artifacts/template metadata; set report ready flags. |
| Report generation failure | `reportState` | Store error + retry affordance; keep existing artifacts if still valid. |
| User toggles debug/advanced visibility | `debugAdvancedState` | Update local visibility preferences only; no mutation to backend-derived run truth. |

## Legal Transition Rules
- `builderDraftState` mutation always invalidates current resolved `planState` freshness.
- `runState` context switch (new run id) resets `reportState` to that run's server-derived truth.
- `catalogCacheState` version drift always forces plan freshness invalidation.
- `reportState` must never remain "ready" after a run id change until rehydrated for that run.

## Page Refresh/Rehydrate Rules
- On refresh, rehydrate persisted local state (draft + view preferences) first.
- Immediately fetch server-derived sources (`catalog`, active `run`) before enabling run/report actions.
- If persisted draft conflicts with refreshed catalog constraints, keep draft but mark invalid until user resolves fields.

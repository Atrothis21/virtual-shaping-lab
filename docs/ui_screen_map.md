# UI Screen Map (First-Pass Refactor)

## Purpose
Provide an implementation-ready map of first-pass screens/surfaces, their data contracts, and backend dependencies.

First-pass scope:
- presets + constrained builder + run/report lifecycle
- lightweight phenomenon metadata support
- no full narrative teaching shell

## Screen Inventory

### 1) Presets
- Inputs:
  - protocol/preset catalog entries
  - phenomenon metadata (labels, descriptions, expected signals, recommended outputs)
  - catalog version stamps
- Outputs:
  - selected preset/phenomenon seed
  - transition intent to constrained builder or direct plan flow
- Backend dependencies:
  - `GET /catalog/extensions`

### 2) Constrained Builder
- Inputs:
  - `BuilderExperimentDraft`
  - phase/protocol/runtime/report constraints from catalog metadata
  - selected preset/phenomenon seed
- Outputs:
  - draft edits
  - local validation state
  - `POST /plan` request payload via `draft_to_payload(...)`
- Backend dependencies:
  - `GET /catalog/extensions`
  - `POST /plan`

### 3) Run
- Inputs:
  - resolved plan summary/hash
  - run lifecycle status
  - run artifact pointers
  - debug availability metadata
- Outputs:
  - run trigger requests
  - polling control (start/stop/retry)
  - lifecycle state display
- Backend dependencies:
  - `POST /run`
  - `GET /runs/{id}`

### 4) Report
- Inputs:
  - active run id/status
  - report template choice/default guidance
  - report generation status/artifacts
- Outputs:
  - report generation trigger
  - report artifact access state
- Backend dependencies:
  - `POST /runs/{id}/report`
  - `GET /runs/{id}`

### 5) Phenomenon Metadata Support Panel
- Inputs:
  - phenomenon entry metadata from extension catalog
  - recommended templates/figures
  - expected signal hints
- Outputs:
  - user guidance for preset/builder setup
  - optional prefill suggestions into builder draft
- Backend dependencies:
  - `GET /catalog/extensions`

## Cross-Screen Data Hand-offs
- Presets -> Builder:
  - preset/phenomenon seed initializes constrained draft scaffold.
- Builder -> Run:
  - run entry requires fresh resolved plan from `POST /plan`.
- Run -> Report:
  - report actions require active run context and server-derived lifecycle/report readiness.
- Catalog -> All screens:
  - catalog constraints and version stamps are shared dependencies; drift invalidates stale assumptions.

## Screen-Level Guardrails
- No screen may expose raw payload editing controls.
- Lifecycle truth is server-derived; UI state cannot invent execution states.
- Version mismatch handling must follow `docs/ui_version_mismatch_behavior.md`.
- Constraint rendering behavior must follow `docs/ui_constraint_behavior.md`.

## First-Pass Route Map

Suggested route set:
- `/presets`
  - primary entry for preset and phenomenon metadata selection
- `/builder`
  - constrained builder editor for `BuilderExperimentDraft`
- `/run/:runId?`
  - run lifecycle view (optional run id to support "start new run" then bind id)
- `/report/:runId`
  - report generation and artifact access for a specific run
- `/catalog-help`
  - catalog/help/version visibility surface

## Component Ownership Boundaries

Route-level containers (own server orchestration):
- `PresetsPage`
- `BuilderPage`
- `RunPage`
- `ReportPage`
- `CatalogHelpPage`

Shared/stateful components (own local UI state, not backend truth):
- `CatalogGate` (version drift + availability gating)
- `DraftEditor` (local draft edits + validation display)
- `LifecyclePanel` (renders server-derived status only)
- `ConstraintGuardedControl` (applies hide/disable/warn/auto-correct behavior)
- `VersionMismatchBanner` (policy-driven mismatch treatment)

Domain ownership constraints:
- Route containers own API calls and server-derived state sync.
- Shared controls must remain stateless with respect to backend truth (props-driven).
- No child component may mutate run/report lifecycle state directly.

## Navigation and State Handoff Rules

- Presets -> Builder:
  - pass selected preset/phenomenon seed into draft initialization
  - any seed change invalidates prior resolved plan freshness
- Builder -> Run:
  - navigation allowed only after successful `POST /plan`
  - handoff object: resolved plan summary/hash + draft version stamp
- Run -> Report:
  - navigation allowed when run id exists
  - report generation controls gated by server-derived run/report status
- Report -> Builder (edit and rerun loop):
  - entering builder from report/run context should preserve user draft when safe
  - any draft mutation invalidates plan and requires re-plan before rerun
- Global:
  - catalog/version refresh may trigger non-destructive invalidation banners on any route

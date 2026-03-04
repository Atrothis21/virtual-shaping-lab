# V2.10 PR Summary: Browser Lifecycle Console Recovery

## Overview
V2.10 restores a usable browser-driven simulator flow through a thin lifecycle console that runs directly against backend contracts:

- `PlanDraft -> PlanResolved -> RunInProgress -> RunComplete -> ReportComplete`
- API-first orchestration (`/plan`, `/run`, `/runs/{id}`, `/runs/{id}/report`)
- extension-catalog-driven options (`/catalog/extensions`)

This release prioritizes functional parity and contract safety over visual polish.

---

## What Is Production-Ready

### 1) End-to-End Browser Lifecycle
- Plan JSON draft editing and resolution (`POST /plan`)
- Run creation and status polling (`POST /run`, `GET /runs/{id}`)
- Report generation and artifact/provenance display (`POST /runs/{id}/report`)

### 2) Explicit UI Lifecycle State Model
- Central lifecycle store with guarded transitions:
  - `PlanDraft`
  - `PlanResolved`
  - `RunInProgress`
  - `RunComplete`
  - `ReportComplete`
- Actions are enabled/disabled from lifecycle guards, not ad hoc flags.

### 3) Dynamic Extension-Catalog Integration
- Catalog auto-loaded at startup.
- Plan selectors sourced from backend extensions:
  - protocols
  - learners
  - policies
  - representations
  - report templates (count visibility)

### 4) Session Run Browser
- In-session run history with state badges.
- Selecting prior run IDs reloads status/artifacts via `/runs/{id}`.

### 5) Preset Demo Surface
- Preset picker with one-click actions:
  - `Resolve + Run Preset`
  - `Resolve + Run + Report Preset`

### 6) Draft Payload Helper Controls
- Phase card editor (add/remove/reorder, name/protocol/n_trials).
- Typed bridge controls for key fields:
  - runtime mode (`update_mode`, `record_mode`)
  - context/timing (`context`, `dt_s`, `duration_s`)
  - operant reward schedule stub fields

---

## Intentionally Minimal (Not Full Builder Yet)
- No full schema-authored form system; backend remains source-of-truth for validation.
- No deep UX/editor ergonomics (advanced diffing, inline schema docs, rich table editing).
- No full visual redesign; current UI is utilitarian and contract-focused.
- No teaching/narrative mode in UI.

---

## API Contract Usage

### Contract Ownership
- The UI is a payload editor/orchestrator only; it does not own experiment semantics.
- All semantic normalization, validation, and parameter composition remain backend-owned (`/plan` and runtime services).
- Helper controls mutate draft payload JSON and then rely on backend contract responses; there is no parallel UI-side semantic override channel.

### Plan
- `POST /plan`
- Stores resolved `plan` + `stable_hash`
- Renders summary fields from resolved plan object (not raw draft assumptions)

### Run
- `POST /run`
- Displays `run_id`, lifecycle, next actions, metadata/artifacts
- Polls `GET /runs/{id}` while non-terminal

### Report
- `POST /runs/{id}/report`
- Handles explicit missing-run-id and run-not-ready guard errors in UI
- Renders artifact links plus provenance block:
  - `plan_hash`
  - `record_schema_version`
  - `template_version_used`

---

## Screen/Flow Notes

### Plan Screen
- Draft editor + resolve action
- Catalog-backed quick selectors
- Preset quick start actions
- Draft payload helper controls (phase cards + typed field editors)

### Run Screen
- Run creation from resolved draft
- Status polling and lifecycle/next-action display
- Provenance and artifacts visibility

### Report Screen
- Report generation from run ID
- Structured artifact panel (PDF + figures)
- Provenance panel

---

## Screenshot Checklist
Use this checklist when attaching PR screenshots:

1. Plan tab with resolved plan summary and `stable_hash`
2. Run tab with active polling state and completed state
3. Report tab with artifact links and provenance block
4. Catalog summary panel loaded from `/catalog/extensions`
5. Session run history selecting a prior run
6. Preset one-click `Resolve + Run + Report` flow success
7. Minimal phase builder editing multiple phases
8. Typed parameter bridge controls populated

---

## Validation Notes
Backend contract gate executed during implementation slices:

- `python -m pytest -q tests/test_run_api_contract.py` (passing)

Full-suite and manual browser smoke are part of Slice 10.2 closeout.

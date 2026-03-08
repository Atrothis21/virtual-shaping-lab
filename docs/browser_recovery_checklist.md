# Browser Recovery Checklist (V2.17.4)

## Goal
Verify the browser can complete the full lifecycle:
`PlanDraft -> PlanResolved -> RunComplete -> ReportComplete`.

Also verify first-pass route navigation:
`/presets -> /builder -> /run/:id -> /report/:id -> /catalog-help`.

---

## Preconditions
- API server running with V2.5 branch code.
- UI served from `/ui` route.
- Reports path writable (`/reports` mount active).

---

## Step 1 - Resolve Plan
Request:
- `POST /plan` with a valid preset payload.

Verify:
- HTTP `200`.
- Response fields:
  - `status = "success"`
  - `plan` object present
  - `stable_hash` string present
  - `lifecycle.state = "PlanResolved"`
  - `lifecycle.next_actions` includes `create_run`

Failure shape:
- HTTP `400` for invalid payload.
- Envelope fields: `code`, `message`, `details`.

UI smoke:
- from `/builder`, trigger **Resolve Plan** and confirm:
  - resolved summary block includes stable hash
  - stale/invalid state shows consistent route-state panel/banners

---

## Step 2 - Execute Run
Request:
- `POST /run` with valid payload.

Verify:
- HTTP `200`.
- Response fields:
  - `status = "success"`
  - `run_id` string present
  - `state = "completed"`
  - `artifacts.pdf` path present
  - `artifacts.figures` list present
  - `metadata.plan_hash` string present
  - `metadata.record_schema_version` present
  - `metadata.template_version_used` present
  - `lifecycle.state = "RunComplete"`
  - `lifecycle.next_actions` includes `create_report`

Filesystem:
- `reports/<run_id>/payload.json` exists.
- `reports/<run_id>/records.json` exists.

UI smoke:
- from `/run`, trigger run start and confirm:
  - lifecycle panel updates (running/completed)
  - provenance block includes `plan_hash`, `record_schema_version`, `template_version_used`

---

## Step 3 - Poll Run Status
Request:
- `GET /runs/{run_id}`.

Verify:
- HTTP `200`.
- Response fields:
  - `status = "success"`
  - `run_id` matches
  - `state` present
  - `artifacts` object present
  - `metadata.plan_hash` matches run response
  - `metadata.record_schema_version` present
  - `metadata.template_version_used` present
  - `lifecycle` object present

Negative:
- unknown run id -> HTTP `404` with envelope `code = "not_found"`.

---

## Step 4 - Generate/Regenerate Report
Request:
- `POST /runs/{run_id}/report` (optional payload with `preset` override).

Verify:
- HTTP `200`.
- Response fields:
  - `status = "success"`
  - `run_id` present (new report run id)
  - `artifacts` object present
  - `metadata.source_run_id` matches original run
  - `metadata.regenerated = true`
  - `metadata.regeneration_mode = "from_artifacts"`
  - `metadata.plan_hash` present
  - `metadata.record_schema_version` present
  - `metadata.template_version_used` present
  - `metadata.source_metadata_complete` present
  - `metadata.missing_source_metadata` present
  - `lifecycle.state = "ReportComplete"`
  - `lifecycle.next_actions` includes `view_report`

Negative:
- unknown run id -> HTTP `404` with envelope `code = "not_found"`.

UI smoke:
- from `/report/:run_id`, trigger report generation and confirm:
  - lifecycle panel + status chips update
  - artifacts (PDF/figures) are linked when available
  - degraded/template mismatch states render warning treatment, not silent failure

---

## Step 5 - Render Output in Browser
Open:
- `/reports/<run_id>/report.pdf`
- figure PNG links from artifacts response.

Verify:
- report and figures load in browser.
- no broken links in response artifacts.

---

## API Discovery Check
Request:
- `GET /catalog/extensions`.

Verify:
- HTTP `200`.
- response includes deterministic normalized lists:
  - `protocols`
  - `learners`
  - `policies`
  - `representations`
  - `report_templates`

---

## UI Architecture Sanity (V2.17.4)
- root HTML and root app shell are intentionally slimmed and split into route/components/services modules
- verify script/module load order succeeds with no missing global/module reference errors
- verify route transitions keep state-domain behavior intact (draft invalidation, resolve-before-run, run-before-report)

---

## Regression Gate
Minimum:
- `python -m pytest -q tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_full_payloads.py`

Release gate:
- `python -m pytest -q`


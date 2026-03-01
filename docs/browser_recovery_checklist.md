# Browser Recovery Checklist (V2.5)

## Goal
Verify the browser can complete the full lifecycle:
`PlanDraft -> PlanResolved -> RunComplete -> ReportComplete`.

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
  - `lifecycle.state = "RunComplete"`
  - `lifecycle.next_actions` includes `create_report`

Filesystem:
- `reports/<run_id>/payload.json` exists.
- `reports/<run_id>/records.json` exists.

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
  - `lifecycle.state = "ReportComplete"`
  - `lifecycle.next_actions` includes `view_report`

Negative:
- unknown run id -> HTTP `404` with envelope `code = "not_found"`.

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

## Regression Gate
Minimum:
- `python -m pytest -q tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_full_payloads.py`

Release gate:
- `python -m pytest -q`


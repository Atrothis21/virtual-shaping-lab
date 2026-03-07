# UI Error Handling Matrix (First-Pass)

## Purpose
Define deterministic UI treatment for backend/API failures and contract mismatch conditions in first-pass UI surfaces.

This matrix aligns with:
- `docs/ui_contract_manifest.md`
- `docs/ui_version_mismatch_behavior.md`

## Treatment Types
- `inline`: field-level or local control error.
- `banner`: non-blocking page-level warning/error.
- `blocking_panel`: screen-level blocking state with recovery actions.
- `toast`: short-lived notification for non-critical events (never sole treatment for blocking failures).

## Error Matrix

| Condition | Screen(s) | Treatment | User Message Requirements | Recovery Actions |
|---|---|---|---|---|
| Plan validation failure (`POST /plan` 4xx) | Builder | `inline` + `banner` | include invalid fields/reason and draft remains editable | edit draft fields, revalidate, retry plan |
| Run creation failure (`POST /run` 4xx/5xx) | Run | `banner` | include run request failure and retry guidance | retry run, return to builder/preset |
| Run polling/network failure (`GET /runs/{id}` transient) | Run | `banner` (non-blocking) | include stale status warning and last successful update time | retry polling, manual refresh |
| Run not found (`GET /runs/{id}` 404) | Run/Report | `blocking_panel` | include missing run id and likely cause | return to run list/start new run |
| Report request failure (`POST /runs/{id}/report` 4xx/5xx) | Report | `banner` | include report failure and run id context | retry report generation |
| Report artifact missing metadata | Report | `banner` + disable affected controls | identify missing artifact field(s) | refresh run/report, open available artifacts only |
| Catalog load failure (`GET /catalog/extensions` failure) | Preset/Builder/Catalog | `blocking_panel` if no cache, else `banner` degraded | include cache status and inability to guarantee valid options | retry fetch, continue with cached read-only mode if allowed |
| Catalog/version drift (`catalog_version` mismatch) | Preset/Builder | `banner` (escalate blocking on unrecoverable refresh) | include expected/received version | auto refresh then manual retry |
| Record schema mismatch (`record_schema_version`) | Run/Report detail | `blocking_panel` | include expected/received schema and unsupported view reason | open static artifacts, refresh, navigate to schema-independent summary |
| Template mismatch (`template_version_used`) | Report | `banner` degraded mode | include unsupported interactive controls notice | proceed with static artifacts, optionally refresh |
| Constraint violation from backend validation | Builder | `inline` + `banner` | include constraint symbol/context and affected control | adjust value, apply suggested correction if safe |
| Unknown/unmapped backend error | Any | `banner` | include correlation/run id when available and generic recovery path | retry action, reload page, escalate support path |

## Dismissibility Rules
- `blocking_panel` is non-dismissible until condition clears.
- `banner` is dismissible only when dismissal does not hide unresolved blocking risk.
- If dismissed, error state remains visible in an error summary region for the active screen.

## Recovery UX Requirements
- Every blocking state must include at least one primary recovery action.
- Every non-blocking warning must include either retry or navigate-back action.
- Messages must avoid internal stack traces; include stable identifiers (run id, field name, mismatch field) instead.

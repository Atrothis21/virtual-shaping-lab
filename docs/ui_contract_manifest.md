# UI Contract Manifest (V2.16)

## Purpose
This document is the canonical contract manifest for browser-facing integration.

Primary rule:
- UI consumes API and catalog contracts.
- UI does not depend on runtime internals or factory implementation details.

---

## Endpoint Inventory

### `GET /catalog/extensions`
Purpose:
- discover protocols, phenomena, learner/policy/representation options, and report template defaults.

Success envelope:
```json
{
  "status": "success",
  "extensions": {
    "protocols": [],
    "phenomena": {},
    "learners": [],
    "policies": [],
    "representations": [],
    "report_templates": {}
  }
}
```

### `POST /plan`
Purpose:
- validate payload and resolve plan + stable hash before run.

Success envelope:
```json
{
  "status": "success",
  "plan": {
    "settings": {},
    "units": []
  },
  "stable_hash": "...",
  "lifecycle": {
    "state": "PlanResolved",
    "next_actions": ["create_run"]
  }
}
```

### `POST /run`
Purpose:
- execute an experiment payload and create run artifacts.

Success envelope:
```json
{
  "status": "success",
  "run_id": "...",
  "state": "completed",
  "artifacts": {},
  "metadata": {
    "plan_hash": "...",
    "record_schema_version": "v1",
    "template_version_used": 1
  },
  "lifecycle": {
    "state": "RunComplete",
    "next_actions": ["get_run_status", "create_report"]
  }
}
```

### `GET /runs/{id}`
Purpose:
- fetch current run status and artifact pointers.

Success envelope:
```json
{
  "status": "success",
  "run_id": "...",
  "state": "completed",
  "artifacts": {},
  "metadata": {
    "plan_hash": "...",
    "record_schema_version": "v1",
    "template_version_used": 1
  },
  "error": null,
  "lifecycle": {
    "state": "RunComplete",
    "next_actions": ["create_report"]
  }
}
```

### `POST /runs/{id}/report`
Purpose:
- build default report artifacts for a completed run.

Success envelope:
```json
{
  "status": "success",
  "run_id": "...",
  "artifacts": {},
  "metadata": {
    "source_run_id": "...",
    "regenerated": false,
    "regeneration_mode": "..."
  },
  "lifecycle": {
    "state": "ReportComplete",
    "next_actions": ["view_report", "resolve_plan"]
  }
}
```

---

## Error Envelope

Errors use a normalized shape:

```json
{
  "code": "...",
  "message": "...",
  "details": {}
}
```

UI requirements:
- render `message` directly for user-facing feedback.
- include `code` and `details` in debug logs.

---

## Lifecycle States and Transitions

Canonical states:
- `PlanDraft`
- `PlanResolved`
- `RunInProgress`
- `RunComplete`
- `ReportComplete`
- `Failure`

Allowed transitions:
- `PlanDraft -> PlanResolved | Failure`
- `PlanResolved -> RunInProgress | RunComplete | Failure`
- `RunInProgress -> RunComplete | Failure`
- `RunComplete -> ReportComplete | Failure`
- `ReportComplete -> (terminal)`
- `Failure -> (terminal)`

UI requirements:
- drive buttons/actions from `lifecycle.next_actions`, not inferred local state.
- treat lifecycle states as authoritative over optimistic UI assumptions.

---

## Required Rendering Fields

### Plan View
- `status`
- `plan.settings`
- `plan.units`
- `stable_hash`
- `lifecycle.state`
- `lifecycle.next_actions`

### Run Start / Run Status View
- `status`
- `run_id`
- `state`
- `artifacts`
- `metadata.plan_hash`
- `metadata.record_schema_version`
- `metadata.template_version_used`
- `error`
- `lifecycle.state`
- `lifecycle.next_actions`

### Report View
- `status`
- `run_id`
- `artifacts`
- `metadata.source_run_id`
- `metadata.regenerated`
- `metadata.regeneration_mode`
- `lifecycle.state`
- `lifecycle.next_actions`

### Extensions View
- `status`
- `extensions.protocols`
- `extensions.phenomena`
- `extensions.learners`
- `extensions.policies`
- `extensions.representations`
- `extensions.report_templates`

---

## Forbidden Ownership Rules (UI)

UI must not invent or mutate backend-owned semantics.

Do not:
- encode runtime behavior rules in frontend-only maps when catalog/API provides the source of truth.
- inject cross-concern fields into phase payloads (for example, representation/learner-owned mechanism fields in phase params).
- infer lifecycle transitions client-side beyond `next_actions`.
- depend on internal modules such as factory internals for rendering or validation behavior.

Do:
- use API envelopes and catalog payloads as authoritative contracts.
- keep UI draft editing model separate from runtime internals.

---

## Versioning Policy

Contract versioning is snapshot-governed.

Rules:
- any change to top-level response keys for `/plan`, `/run`, `/runs/{id}`, `/runs/{id}/report`, or `/catalog/extensions` requires snapshot update.
- any change to required metadata keys requires snapshot update.
- lifecycle key shape changes require snapshot update.

Compatibility guidance:
- additive fields are preferred over breaking removal/renames.
- keep existing envelope keys stable unless explicitly planned as breaking.

---

## Snapshot Bump Rules

When API envelope contract changes:
1. update implementation.
2. update `tests/fixtures/api_contract_snapshots.json`.
3. update tests asserting snapshot behavior.
4. update this manifest if endpoint semantics changed.

Minimum test gate:
- `tests/test_api_contract_snapshots.py`
- `tests/test_run_api_contract.py`

---

## Source of Truth Priority

1. Runtime API responses (actual server output)
2. Snapshot tests (`tests/fixtures/api_contract_snapshots.json`)
3. This manifest
4. UI implementation assumptions

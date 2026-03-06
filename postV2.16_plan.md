# Post V2.16 Plan - UI Refactor Readiness (Pre-Implementation)

## Objective
Complete the minimum product/contract decisions required before major UI usability/refactor work begins, so implementation is not blocked by backend-contract ambiguity.

## Current Status
- V2.16 full regression is already confirmed green (`python -m pytest -q`).
- UI contract and draft translation foundations are in place from V2.16.

---

## What Should Be Done From This List

Do now (required before major UI refactor):
1. Freeze V2.17 UI scope.
2. Define canonical client state model.
3. Validate builder-draft workflow coverage against intended UX.
4. Decide debug telemetry UX policy.
5. Decide contract/version mismatch behavior.
6. Audit catalog metadata for UI usability completeness.
7. Define deterministic constraint handling behavior.
8. Produce a one-page screen map with backend dependencies.

Defer until active UI build starts:
- artifact presentation rules
- error presentation details
- terminology polish
- UI testing implementation details (plan now, implement in refactor PRs)

---

## Phase 1 - Scope and Invariants

### Slice 1.1 - Freeze first-pass UI scope
Deliverables:
- Add scope decision section:
  - `lifecycle + presets` vs `presets + constrained builder` vs broader.
- Explicitly mark out-of-scope features for first pass.

Done definition:
- Scope can be quoted in PRs without reinterpretation.

Scope decision (frozen for first pass):
- Selected scope: `presets + constrained builder` (with run/report lifecycle surfaces).

In-scope for first pass:
- Preset selection and execution path (plan -> run -> report).
- Constrained builder using `BuilderExperimentDraft` and draft translation adapter.
- Lifecycle state visibility (queued/running/completed/failed) and core run status.
- Report selection from backend-provided template/catalog guidance.

Out-of-scope for first pass:
- Full free-form builder shell that exposes raw payload semantics.
- Teaching-mode narrative/explanation UX beyond basic phenomenon metadata display.
- Advanced artifact curation/presentation redesign.
- Deep debug trace exploration workflows as default UX.

### Slice 1.2 - Lock contract invariants
Deliverables:
- Add “contract is law” section referencing:
  - endpoint envelopes
  - lifecycle states
  - version fields
  - ownership boundaries

Done definition:
- UI implementation cannot claim missing semantics for backend-owned fields.

Contract-is-law invariants (binding):
- Endpoint envelopes are canonical:
  - `POST /plan`, `POST /run`, `GET /runs/{id}`, `POST /runs/{id}/report`, `GET /catalog/extensions`
  - UI must consume documented request/response shapes only.
- Lifecycle states are backend-owned:
  - UI may map/present states, but must not invent new execution states.
- Version fields are mandatory compatibility inputs:
  - `catalog_version`, `record_schema_version`, `template_version_used`
  - mismatch handling must follow a defined policy (slice 3.2).
- Ownership boundaries are strict:
  - UI must not synthesize backend-resolved fields, runtime records, or protocol/report semantics.
  - UI may only submit editable draft fields and backend-supported options.

---

## Phase 2 - State and Builder Model Decisions

### Slice 2.1 - Define client-side state model
Deliverables:
- Add explicit state domains:
  - plan state
  - run state
  - report state
  - builder draft state
  - catalog cache state
  - debug/advanced state
- Define state ownership (local, server-derived, derived/transient).

Done definition:
- Every screen concern maps to one state domain.

Client state model (frozen):
- `planState` (server-derived + local selection):
  - server-derived: resolved plan payload, stable hash, validation output
  - local: selected preset/protocol, pending plan request status
- `runState` (server-derived + derived/transient):
  - server-derived: run id, lifecycle status, artifact pointers, timestamps
  - derived/transient: polling status, optimistic transition hints, last refresh time
- `reportState` (server-derived + local):
  - server-derived: report generation status, report artifact pointers, template used
  - local: selected report intent/view tab, user-triggered regenerate requests
- `builderDraftState` (local authoritative):
  - local: `BuilderExperimentDraft`, edit history, client-side validation errors
  - derived: draft completeness/readiness flags
- `catalogCacheState` (server-derived cache):
  - server-derived: extensions/catalog payload, version stamps, fetched-at timestamp
  - local: cache freshness status and invalidation marker
- `debugAdvancedState` (local policy + server-derived availability):
  - local: debug visibility mode, advanced panel expanded/collapsed, display limits
  - server-derived: presence/absence of debug fields in run records

State ownership rule:
- Local-authoritative state: draft edits and view preferences.
- Server-derived state: plan/run/report/catalog truth and lifecycle truth.
- Derived/transient state: UI computation only; must be reproducible from local + server-derived state and never persisted as backend truth.

### Slice 2.2 - Decide builder editability boundaries
Deliverables:
- Define, per workflow, what is:
  - directly editable
  - catalog-derived
  - backend-resolved only
- Include preset-to-draft behavior and phenomenon-to-draft behavior.

Done definition:
- Builder is constrained; not a raw payload editor.

Builder editability boundaries (frozen):
- Directly editable in UI:
  - high-level experiment identity (name/notes where supported)
  - phenomenon/preset selection
  - phase sequencing within allowed catalog constraints
  - runtime mode toggles exposed by product scope (`trial`/`tick`, debug visibility controls)
  - report intent/template selection from allowed catalog options
- Catalog-derived (not free-form):
  - protocol/phase labels, descriptions, defaults, examples
  - available parameter keys, value domains, constraints
  - machine-checkable constraint semantics used for gating
- Backend-resolved only (non-editable):
  - inferred/resolved plan internals
  - stable hash and provenance fields
  - runtime record schema/version semantics
  - lifecycle truth/state transitions

Preset and phenomenon mapping policy:
- Presets are loadable as editable drafts within constrained fields only.
- Phenomenon selections may seed a draft scaffold (recommended protocol/template/figures), but resulting draft remains constrained by catalogs and translator rules.
- UI must always submit through `BuilderExperimentDraft -> draft_to_payload(...)`; no direct raw payload assembly path is allowed.

---

## Phase 3 - Runtime UX Policy Decisions

### Slice 3.1 - Decide debug telemetry UX policy
Deliverables:
- Define defaults and advanced behavior:
  - default visibility (`off` vs basic summary)
  - trial vs tick exposure
  - large-run behavior (decimation/truncation)

Done definition:
- Debug UX is predictable and bounded for browser usage.

Debug telemetry UX policy (frozen):
- Default visibility:
  - debug panels are `off` by default in standard run view.
  - users may enable debug via an explicit advanced toggle.
- Trial vs tick display policy:
  - default debug display is trial-level summaries.
  - tick-level debug is advanced-only and only shown when runtime/debug mode supports it.
- Large-run behavior:
  - UI renders bounded debug subsets only (respecting backend decimation/cap outputs).
  - when debug payload is large, UI shows sampled/limited views with explicit "truncated/sampled" notice.
  - no attempt to render unbounded tick debug tables by default.

### Slice 3.2 - Decide version mismatch behavior
Deliverables:
- Define action matrix for mismatches:
  - `catalog_version`
  - `record_schema_version`
  - `template_version_used`
- For each: warn/block/degrade behavior and user message expectation.

Done definition:
- Version drift handling is deterministic and testable.

Version mismatch behavior matrix (frozen):
- `catalog_version` mismatch:
  - Behavior: `warn + soft refresh`.
  - UI action: show non-blocking banner, invalidate catalog cache, refetch catalogs.
  - Escalation: block only if refetch fails and required catalog data is unavailable.
- `record_schema_version` mismatch:
  - Behavior: `block render` for incompatible run detail/report views.
  - UI action: show explicit incompatibility error with expected vs received schema version.
  - Allowed fallback: high-level run status may still render if schema-independent.
- `template_version_used` mismatch:
  - Behavior: `degrade gracefully` with warning.
  - UI action: allow report artifact access and basic metadata display, disable unsupported interactive template-dependent widgets.

User messaging requirements:
- Always include:
  - field name (`catalog_version`, `record_schema_version`, `template_version_used`)
  - expected value/range (if known)
  - received value
  - next action (refresh, rerun, update client, or open static artifact)

---

## Phase 4 - Catalog and Constraint Usability Hardening

### Slice 4.1 - Catalog metadata usability audit
Deliverables:
- Add audit checklist and status for UI-consumed catalog entries:
  - label
  - description
  - defaults
  - schema
  - constraints
  - examples
- Identify concrete metadata gaps requiring backend follow-up.

Done definition:
- No UI-critical catalog entry is “technically present but unusable.”

### Slice 4.2 - Constraint handling behavior matrix
Deliverables:
- Define uniform UI response rules for machine constraints:
  - hide
  - disable
  - warn
  - auto-correct
- Cover phases, protocols, reports, runtime controls.

Done definition:
- Constraint behavior is consistent across the interface.

---

## Phase 5 - Screen Map and Test Planning

### Slice 5.1 - One-page screen/dependency map
Deliverables:
- Add screen map for:
  - Plan/Builder
  - Run
  - Report
  - Teaching/Phenomena
  - Catalog/Help
- For each screen: inputs, outputs, backend dependencies.

Done definition:
- Team can implement screens without rediscovering API dependencies.

### Slice 5.2 - UI test strategy for refactor phase
Deliverables:
- Define executable UI test plan categories:
  - contract snapshot checks
  - state transition tests
  - builder translation tests
  - critical flow tests
- Map each category to when it is introduced during UI refactor.

Done definition:
- UI refactor has a pre-agreed quality bar and test rollout order.

---

## Exit Criteria
- Scope is frozen for first UI pass.
- Contract/version/ownership rules are explicit.
- Client state model is complete and unambiguous.
- Builder boundaries are defined and constrained.
- Debug and mismatch UX policies are decided.
- Catalog usability gaps are identified with actionable follow-ups.
- Constraint handling is standardized.
- Screen map and UI test strategy are ready for execution.

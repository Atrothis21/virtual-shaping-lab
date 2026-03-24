# V3.15.5 Plan - Arrangement-Task-Agent UI/API Cutover

## Objective

Cut UI and API authoring paths from preset-first inputs to first-class `(arrangement, task, agent)` inputs, composed into basis subsets at runtime.

## Source Inputs

- `V3_15_0_plan.md`
- `payload_refactor.md`
- `docs/V3_operator_info/operator_basis_set.md`
- `virtual_shaping_lab/ui/js/react/teaching_panel.jsx`
- `virtual_shaping_lab/ui/contracts/preset_basis_authoring.py`
- `virtual_shaping_lab/api/run.py`

## Entry Criteria

- V3.15.0 arrangement/task/agent foundation is merged and green.
- Composition contract deterministically emits legal operator subsets.
- Existing core preset basis-first routes are stable (`acquisition`, `extinction`, `differential_acquisition`).
- tuple route migration strategy is decided before implementation starts:
  - new shared tuple page vs replacement of core pages vs overlay/adopted gradually
- selected strategy for V3.15.5: `overlay/adopted gradually` (tuple boundary wiring enabled; tuple-migrated preset route list may remain empty in this release)

## Commit-Sized Slices

## Slice 1 - Authoring Payload Contract Shift

Deliver:

- define new authoring payload shape:
  - `arrangement`
  - `task`
  - `agent`
  - `edits`
- add compatibility translator from old `preset_id` route payloads
- add explicit contract version and mode identity for tuple-based authoring
- require translator diagnostics contract:
  - translated tuple
  - legacy preset label (if available)
  - lossless vs heuristic translation flag
  - deprecation diagnostics

Tests:

- authoring payload schema tests
- translator compatibility tests
- translator diagnostics shape and semantics tests
- malformed tuple payload rejection tests

## Slice 2 - API Composition/Materialization Endpoints

Deliver:

- add API endpoints for tuple-driven authoring:
  - guided catalog contract endpoint for:
    - arrangements
    - valid tasks by arrangement
    - valid agents by `(arrangement, task implementation)`
    - available edits for current tuple projection
  - materialize endpoint for tuple + edits
- enforce that materialized payload contains composed subset identity
- preserve legacy preset endpoints as compatibility wrappers
- ensure API contract remains domain-shaped (tuple semantics), not UI-step-shaped

Tests:

- guided catalog endpoint shape tests
- task/agent filtering correctness tests
- tuple materialization smoke tests for pavlovian and operant examples
- compatibility wrapper parity tests

## Slice 3 - UI Flow Refactor (3-Step Selection)

Deliver:

- implement UI selection flow:
  1. arrangement
  2. task
  3. agent
- derive valid tasks/agents from registries and legality contracts
- load editor controls from tuple authoring contract (no hand-authored option universes)
- apply explicit visibility policy:
  - hide structurally impossible agents
  - show-disabled behaviorally invalid/partial agents with explanations

Tests:

- UI flow contract tests (arrangement filters task, task filters agent)
- hidden-vs-disabled policy tests
- no-hardcoded-selectable-universe assertions
- route-level migrated authoring path tests

## Slice 4 - Runtime/Metadata Identity Integration

Deliver:

- propagate tuple identity through `/run` metadata and report regeneration metadata:
  - arrangement identity
  - task identity
  - agent identity
  - composition hash
- persist tuple identity in `artifact_identity.json`

Tests:

- run API metadata identity tests
- report regeneration parity tests for tuple identity
- artifact identity contract tests

## Slice 5 - Bridge Hardening and Migration Boundaries

Deliver:

- disable legacy browser canonicalization bridge on tuple-migrated routes
- keep explicit fallback only for non-migrated routes
- add migration diagnostics when users post deprecated shapes to tuple routes
- implement chosen route migration strategy from entry criteria:
  - new shared tuple page, or
  - replacement of existing core pages, or
  - overlay/adopted gradual migration

Tests:

- migrated-route bridge rejection tests
- non-migrated fallback retention tests
- deprecated-shape diagnostic tests
- route migration boundary mapping tests (must match chosen strategy)

## Testing Plan

- `python -m pytest -q tests/test_v3_tuple_authoring_contract.py`
- `python -m pytest -q tests/test_v3_tuple_authoring_api.py`
- `python -m pytest -q tests/test_v3_ui_tuple_selection_flow.py`
- `python -m pytest -q tests/test_v3_ui_tuple_visibility_policy.py`
- `python -m pytest -q tests/test_run_api_contract.py -k "tuple_identity or regeneration_keeps_tuple_identity or arrangement or task or agent or composition_hash"`
- `python -m pytest -q tests/test_ui_teaching_contract.py -k "legacy_bridge or tuple_route_migration"`

## CI Updates

Add blocking bucket:

- `Run V3 arrangement-task-agent cutover`
  - tuple authoring contract tests
  - guided tuple catalog + API materialization tests
  - UI selection-flow tests
  - hidden-vs-disabled visibility policy tests
  - run/report tuple identity propagation tests
  - legacy-bridge migrated route tests

## Exit Criteria

- UI authoring supports first-class tuple input `(arrangement, task, agent)` on migrated routes
- V3.15.5 strategy conformance: overlay migration boundary is implemented and test-enforced (`TUPLE_ROUTE_MIGRATION_STRATEGY = overlay_gradual`), with explicit tuple-migrated route map support
- API materializes runnable canonical payloads from tuple input without hand-authored operator lists
- guided catalog contract provides valid tuple navigation without leaking legality logic to client code
- legacy preset translation diagnostics are explicit and test-enforced
- tuple identity is preserved across run artifacts and regenerated report metadata
- legacy bridge is disabled for tuple-migrated routes and explicitly retained for non-migrated routes
- route migration implementation matches the preselected strategy from entry criteria
- CI blocks tuple cutover regressions across UI, API, and metadata surfaces

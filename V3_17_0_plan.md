# V3.17.0 Plan - Comprehensive Preset UX Cutover

## Objective

Complete the preset experience cutover from legacy preset-centric UX to tuple-first, compatibility-guided UX while preserving deterministic materialization, explicit migration boundaries, and CI-enforced regressions.

UX contract invariants for this plan:

- `structurally_invalid` is a legality/composition failure signal, not a UX compatibility state.
- compatibility UX states are limited to:
  - `success`
  - `partial`
  - `behaviorally_unsupported`
  - `novel`
- smart preset selection and manual tuple selection must converge into one shared detail/edit/run flow.

## Source Inputs

- `V3_14_0_plan.md`
- `V3_15_5_plan.md`
- `V3_16_0_plan.md`
- `docs/v3_behavioral_compatibility_and_smart_presets.md`
- `docs/v3_16_0_smart_preset_migration_notes.md`
- `virtual_shaping_lab/ui/js/react/preset_catalog.jsx`
- `virtual_shaping_lab/ui/js/react/app.jsx`
- `virtual_shaping_lab/ui/js/react/tuple_authoring_flow.jsx`
- `virtual_shaping_lab/ui/js/react/teaching_panel.jsx`
- `virtual_shaping_lab/api/run.py`

## Entry Criteria

- V3.16.0 behavioral compatibility and smart preset projection contracts are merged and green.
- Tuple authoring API endpoints are stable:
  - `GET /catalog/tuple-authoring`
  - `POST /catalog/tuple-authoring/materialize`
  - `POST /catalog/tuple-authoring/compatibility`
  - `GET /catalog/smart-presets`
  - `POST /catalog/smart-presets/{smart_preset_id}/project`
- Basis-first payload boundaries remain enforced for migrated routes.
- Existing run/report identity artifacts remain stable and CI-enforced.

## Commit-Sized Slices

## Slice 1 - Preset Catalog IA Cutover

Deliver:

- replace static preset-card assumptions with contract-driven catalog sections powered by:
  - smart preset catalog
  - tuple compatibility status summaries
  - migration-safe route metadata
- define explicit catalog hierarchy and ordering:
  - top-level grouping: arrangement (`pavlovian`, `operant`)
  - second-level grouping: phenomenon class (`acquisition`, `extinction`, `discrimination`, `generalization`)
  - leaf grouping: smart preset variants / agent bundle variants
  - ordering inside each group: `success` first, `partial` second, `novel` third, `behaviorally_unsupported` last
- add explicit UX states:
  - recommended (`success`)
  - exploratory (`partial` / `novel`)
  - caution (`behaviorally_unsupported`)
- preserve teaching metadata while decoupling cards from hardcoded legacy preset payload identities
- add fallback behavior when API catalog is unavailable (read-only degraded catalog mode)
- do not render structurally invalid tuple combinations as catalog cards
- add catalog density controls to prevent overload:
  - collapse arrangement/phenomenon sections by default when card count exceeds threshold
  - show top 3 recommended presets first per visible section
  - provide explicit "show more" expansion for remaining presets

Tests:

- catalog IA contract tests for grouped section shape
- catalog ordering tests for status-prioritized ordering in each hierarchy branch
- smart preset to catalog card projection tests
- hidden structurally-invalid tuple suppression tests
- behaviorally_unsupported card caution-state tests
- density control tests (collapsed-by-default and top-3-first behavior)
- degraded catalog fallback tests

## Slice 2 - Tuple-First Preset Detail/Editor UX

Deliver:

- implement unified preset detail UX path:
  - smart preset click pre-fills tuple selection state
  - manual selection uses the same tuple selection state model
  - both paths land in the same detail/edit/run view
  - show expected outcome panel before run
  - surface editable fields derived from tuple contract only
- enforce run button rules:
  - block run only on legality/composition error state
  - allow `partial`/`novel` with explicit guidance banner
- make explanation and key-operator-factor rendering source-integrity constrained to evaluator/registry artifacts
- use composition provenance (`axis_to_slot_contribution`) as the primary explanation backbone for:
  - why this works
  - why this fails
  - which operators matter most
- add a thin provenance interpretation layer that converts raw provenance facts into readable statements while remaining provenance-derived
- if detail is reached with invalid tuple, show composition error view (not compatibility badge state)
- add explicit manual exploration entry CTA (`Explore Tuple Space`) alongside smart preset entry

Tests:

- preset detail render contract tests
- single-flow convergence tests for smart preset and manual entry paths
- run gating tests for legality/composition error vs compatibility-only states
- invalid-detail-path composition-error rendering tests
- expected outcome panel parity tests between catalog preview and detail view
- source-integrity rendering tests (no hand-authored override path)
- provenance-driven explanation rendering tests (axis contribution map is source)
- readable provenance interpretation tests (human-readable statements mapped to provenance facts)

## Slice 3 - Legacy Preset Page Routing and Migration Boundary

Deliver:

- define and enforce route strategy for preset UX:
  - migrated routes render tuple-first preset UX shell
  - unmigrated routes keep explicit compatibility bridge/fallback
- add route-level migration diagnostics for deprecated entry shapes
- add explicit route map contract for:
  - tuple-first preset routes
  - legacy fallback routes
  - hard-disabled legacy bridge routes

Tests:

- migrated route rendering tests
- legacy fallback retention tests on unmigrated routes
- deprecated-route-input diagnostics tests
- route map drift/snapshot tests

## Slice 4 - Run/Report UX Integration and Artifact Surfaces

Deliver:

- expose expected-outcome + tuple identity context in run confirmation and results entry points
- carry preset UX context through run/report metadata without altering simulation semantics:
  - smart preset ID (if used)
  - tuple identity
  - compatibility status at run-time selection (excluding structural-invalid as a compatibility state)
- ensure regenerated report retains tuple/smart preset provenance parity from run artifacts

Tests:

- run metadata contract tests for UX provenance fields
- report regeneration parity tests for UX provenance
- artifact identity tests for tuple/smart preset context persistence
- backward compatibility tests for runs that do not include smart preset origin

## Slice 5 - Accessibility, Copy, and Interaction Hardening

Deliver:

- add accessibility hardening for new preset UX:
  - keyboard focus order for catalog -> detail -> run actions
  - status badges with non-color semantic labels
  - ARIA labels for compatibility explanations and run gating reasons
- standardize copy deck for compatibility statuses and migration diagnostics
- enforce copy distinction:
  - compatibility guidance language for `success/partial/behaviorally_unsupported/novel`
  - composition failure language for invalid tuple construction paths
- explicitly set `behaviorally_unsupported` tone to exploration-supportive (not prohibitive), e.g. "unlikely to reproduce standard effect, may still yield interpretable behavior"
- remove ambiguous preset wording that implies hidden defaults or opaque legacy behavior

Tests:

- accessibility DOM contract tests (labels/roles/focus path)
- status copy snapshot tests
- run-disabled reason visibility tests
- composition-error copy tests (distinct from compatibility copy)
- behaviorally_unsupported tone tests (supportive/non-prohibitive language contract)
- legacy copy regression tests for migrated routes

## Slice 6 - CI/Docs/Closeout Hardening

Deliver:

- publish comprehensive preset UX cutover docs:
  - catalog IA and route strategy
  - expected outcome interaction model
  - migration playbook for remaining legacy preset routes
- wire blocking CI bucket for preset UX cutover contracts
- add post-cutover checklist for future preset additions

Tests:

- docs-linked contract tests
- aggregate preset UX flow gates
- smart preset + tuple compatibility API/UI integration gates

## Testing Plan

- `python -m pytest -q tests/test_v3_ui_preset_catalog_ux_contract.py`
- `python -m pytest -q tests/test_v3_ui_preset_detail_tuple_flow.py`
- `python -m pytest -q tests/test_v3_ui_preset_catalog_ordering.py`
- `python -m pytest -q tests/test_v3_ui_preset_catalog_density_controls.py`
- `python -m pytest -q tests/test_v3_ui_expected_outcome_panel.py`
- `python -m pytest -q tests/test_v3_ui_preset_route_migration.py`
- `python -m pytest -q tests/test_v3_smart_preset_projection.py`
- `python -m pytest -q tests/test_v3_ui_manual_tuple_exploration_entry.py`
- `python -m pytest -q tests/test_v3_ui_preset_accessibility_contract.py`
- `python -m pytest -q tests/test_v3_ui_provenance_explanation_readability.py`
- `python -m pytest -q tests/test_run_api_contract.py -k "tuple_compatibility or smart_preset or tuple_authoring_identity or preset_ux_identity"`
- `python -m pytest -q tests/test_v3_behavioral_compatibility_engine.py tests/test_v3_legality_behavior_separation.py`
- `python -m pytest -q tests/test_v3_preset_ux_docs_contract.py`

## CI Updates

Add blocking bucket:

- `Run V3 preset UX cutover`
  - preset catalog UX contract tests
- preset catalog hierarchy/ordering tests
- preset catalog density-control tests
- tuple-first preset detail/run gating tests
  - smart preset/manual single-flow convergence tests
  - manual exploration entry tests
  - route migration boundary tests
  - smart preset projection + compatibility integration tests
- run/report UX provenance identity tests
- provenance readability interpretation tests
- preset UX docs-linked contract tests

## Exit Criteria

- presets catalog and detail views are driven by tuple/smart preset contracts, not hardcoded legacy payload definitions
- catalog hierarchy/ordering is deterministic by arrangement -> phenomenon class -> smart preset, with status-prioritized ordering
- expected outcome guidance is shown pre-run using compatibility states (`success`, `partial`, `behaviorally_unsupported`, `novel`) and does not expose `structurally_invalid` as a compatibility badge
- structurally invalid tuple selections are suppressed in catalog and handled as composition error surfaces in detail when reached
- catalog density controls prevent overload on high-cardinality sections (collapsed sections + top recommended first)
- smart preset selection and manual tuple selection are one unified detail/edit/run flow
- manual tuple-space exploration entry exists and is test-covered
- migrated routes no longer rely on implicit legacy canonicalization behavior
- tuple/smart preset provenance is retained in run/report artifact metadata with regeneration parity
- accessibility and copy requirements are enforced for compatibility statuses and disabled actions
- `behaviorally_unsupported` messaging is guidance-oriented and exploration-supportive, not prohibitive
- provenance explanations are readable and derived from composition provenance (no hand-authored divergence path)
- legacy preset fallback behavior is explicit, bounded, and test-covered for unmigrated routes
- preset UX cutover regressions are blocked by dedicated CI bucket
- docs describe end-to-end user flow from catalog selection to run/report artifacts under tuple-first UX

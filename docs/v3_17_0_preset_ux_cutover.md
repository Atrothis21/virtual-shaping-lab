# V3.17.0 Preset UX Cutover

## Scope

V3.17.0 completes the tuple-first preset UX cutover from catalog selection through run/report artifacts.

The end-to-end user flow is:

1. Catalog selection (`/ui/presets.html`) from smart preset cards or manual tuple exploration.
2. Unified tuple-first detail/edit/run flow with a pre-run expected-outcome panel.
3. Run execution with tuple identity + smart preset origin metadata.
4. Report regeneration with parity for UX provenance identity surfaces.

## Catalog IA and Route Strategy

Preset catalog hierarchy is deterministic:

- arrangement (`pavlovian`, `operant`)
- phenomenon class (`acquisition`, `extinction`, `discrimination`, `generalization`)
- smart preset variants / agent bundle variants

Within each branch, ordering is status-prioritized:

- `success`
- `partial`
- `novel`
- `behaviorally_unsupported`

Route strategy:

- tuple-first migrated routes render tuple-first shells and reject legacy bridge behavior.
- explicit fallback routes remain bounded for unmigrated pages.
- structurally invalid tuple combinations are suppressed in catalog cards and shown as composition error detail surfaces only when directly reached.

## Expected Outcome Interaction Model

Compatibility UX statuses are:

- `success`
- `partial`
- `behaviorally_unsupported`
- `novel`

`structurally_invalid` is not a compatibility badge state. It is a legality/composition failure mode.

Run gating:

- blocked only for composition/legality failures (`structurally_invalid` or composition error surfaces)
- allowed for `partial`, `novel`, and `behaviorally_unsupported` with explicit guidance copy

Guidance language for `behaviorally_unsupported` must remain exploration-supportive:

- "unlikely to reproduce standard effect, may still yield interpretable behavior"

## API and Artifact Surfaces

Core contract endpoints:

- `GET /catalog/preset-ux`
- `GET /catalog/preset-route-migration`
- `GET /catalog/tuple-authoring`
- `POST /catalog/tuple-authoring/compatibility`
- `GET /catalog/smart-presets`
- `POST /catalog/smart-presets/{smart_preset_id}/project`

Run/report UX provenance identity surfaces:

- `tuple_authoring_identity`
- `preset_ux_identity`
- `basis_compile_identity`
- `measurement_provenance_identity`

Parity requirement:

- run response metadata
- run status metadata
- regenerated report metadata
- `artifact_identity.json`

## Migration Playbook for Remaining Legacy Routes

For each unmigrated preset route:

1. Add route entry to migration contract with explicit strategy (`tuple_first` or `legacy_fallback`).
2. Wire route into tuple-first detail shell.
3. Source selectable universe from catalog/registry endpoints only.
4. Remove legacy client-side canonicalization path for migrated route.
5. Add route-level diagnostics for deprecated entry shapes.
6. Add run/report identity assertions for tuple/smart preset provenance.

## Post-Cutover Checklist for New Presets

- preset appears in tuple-first catalog hierarchy under arrangement and phenomenon class
- status ordering follows `success -> partial -> novel -> behaviorally_unsupported`
- no `structurally_invalid` card badge is rendered
- smart preset and manual tuple paths converge to the same detail/edit/run flow
- expected-outcome guidance renders pre-run and uses evaluator/registry-derived sources
- run/report metadata includes `tuple_authoring_identity` and `preset_ux_identity` parity
- route migration contract updated and tested
- CI bucket `Run V3 preset UX cutover` includes relevant selectors

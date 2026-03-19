# V3.8.5 Plan - Layered UI Abstraction and Teaching Surface

## Objective
Deliver behavior-first UI with progressive reveal into mechanism/operators/algebra, aligned with runtime contracts.

## Entry Criteria
- Phenomenon registry is stabilized (V3.8.0).
- Learner grammar/compatibility registry is stabilized (V3.5.0).
- Records/readout schema is stable for graph overlays (V3.6.0).

## Entry Points
- `V_3_UI.md`
- UI mode surfaces (Preset/Teaching/Builder/Expert)
- Preset metadata schema and UI view models
- Operator pipeline visualization and graph overlay components

## Source of Truth
- Glossary: `docs/v3_glossary.md`

## Commit-Sized Slices
### Slice 1 - UI Mode Model
- Implement mode scaffolding for Preset, Teaching, Builder, and Expert modes.

### Slice 2 - Progressive Reveal Layers
- Implement layered reveal path: intuition -> mechanism -> operator -> full algebra.

### Slice 3 - Explainability Overlay
- Add behavior-to-operator graph overlays with trial-level explanation hooks.

### Slice 4 - Pipeline Visualization
- Add operator pipeline visualization with per-node `TrialState` read/write fields.

### Slice 5 - Control-Surface Guardrails
- Enforce no raw operator wiring controls in Preset/Builder modes.

## Testing / CI Updates
- UI contract tests: every canonical preset includes all reveal layers.
- Interaction tests: reveal toggles must not alter run payload identity.
- Explainability tests: graph points resolve to operator-level explanations.
- Control-surface guard: raw operator wiring blocked in Preset/Builder.
- Mode contract tests: full algebra editing exposed only in Expert mode.

## Exit Criteria
- Presets are runnable without exposing operator symbols by default.
- Canonical presets support full progressive reveal.
- Visualized pipeline matches runtime `OperatorPipeline` declaration.
- Builder mode remains controlled (model choices, not raw algebra wiring).

## Migration Impact
- UI navigation and preset metadata schema will expand for reveal layers/modes.
- No runtime semantic changes.

Virtual Shaping Lab — Version 1 Build Schedule (Phase-Centric)

Goal:
Finalize a stable, phase-centric architecture and ship canonical protocols, presets, and
schema-driven builder support.

PHASE 0 — Baseline Lock

Objective:
Freeze a known-good state for rollback.

Tasks:
- Tag current commit (e.g., v1.0-phase-centric-baseline).
- Remove or gate verbose debug prints.
- Run smoke tests:
  - Acquisition
  - Operant schedules (FR / VR / FI / VI)
- Confirm report artifacts are saved correctly.

Deliverable:
Stable baseline with operant support and rollback point.

PHASE 1 — Phase-Centric Contract (Core)

Objective:
Make phases the sole owners of trial logic.

Tasks:
- Ensure PhaseBase implements `sample_trial -> run_trial -> apply_learning -> record_trial`.
- Ensure protocols only orchestrate phases (no trial logic).
- Ensure Runner only calls `protocol.run()`.

Deliverable:
All trial logic lives in phases, protocols are thin.

PHASE 2 — Canonical Protocol Library (High Priority)

Objective:
Encode canonical phenomena using phase composition.

Tasks:
- Acquisition (single phase)
- Extinction (Acquisition -> NonReinforcement)
- Differential conditioning (Differential phase)
- Conditioned inhibition (Acquisition -> Compound NonReinforcement -> Probe)
- Operant acquisition (Operant phase)
- Overshadowing (two-phase variant)
- Overexpectation (two-phase variant)

Deliverable:
Canonically ordered protocols with minimal code.

PHASE 3 — Canonical Presets (UI)

Objective:
Populate presets.html using canonical protocols.

Tasks:
- Add canonical experiments to presets.html.
- Lock phase order in presets.
- Keep builder.html flexible.

Deliverable:
One-click canonical experiments + freeform builder.

PHASE 4 — Representation and Encoder Formalization

Objective:
Make encoding explicit without changing behavior.

Tasks:
- RepresentationBase contract.
- Observation encoder in representations/.
- Agent.observe -> representation.encode -> learner consumes encoded state.

Deliverable:
Encoder pipeline ready for vector learning.

PHASE 5 — Vectorized Learning (Optional)

Objective:
Enable vector RW or TD without protocol changes.

Tasks:
- Add vector RW learner.
- Add FeatureListEncoder or LinearStateEncoder.
- Validate blocking / overshadowing / overexpectation.

Deliverable:
Same protocols, richer behavioral outcomes.

PHASE 6 — Phase-Aware Reporting

Objective:
Make phase transitions visible in analysis.

Tasks:
- Phase markers in plots.
- Per-phase summaries.

Deliverable:
Reports that explain contingency changes.

PHASE 7 — Parametric Representation (Attention)

Objective:
Enable explicit attention as a parameterized learning-rate modulation.

Tasks:
- Add attention schema and payload support.
- Normalize attention maps at runtime.
- Ensure attention is logged in reports.

Deliverable:
Attention support is available across classical phases.

PHASE 8 — Similarity / Generalization

Objective:
Enable explicit similarity matrices for generalization.

Tasks:
- Add similarity schema and validation.
- Apply similarity to representation encoding.
- Provide builder UI for optional similarity.

Deliverable:
Similarity-driven generalization available without protocol changes.

PHASE 9 — Context Inference (Heuristic v1)

Objective:
Infer context labels for phases when not explicitly set.

Tasks:
- Add `context_inference` to experiment schema.
- Infer contexts during assembly.
- Record inferred context metadata in records.

Deliverable:
Context inference is enabled and traceable.

Final Notes

- Phases own trial logic.
- Protocols only orchestrate.
- No special backend paths for presets vs builder.
- Vectorization and generalization live in representation + learner only.

# Virtual Shaping Lab Roadmap

This roadmap lays out the post-v1 release sequence for Virtual Shaping Lab (VSL).
Each version is intended to be independently shippable and local-first by default.

Guiding principles:
- Zero-cost distribution and local-first execution.
- Schema-driven payloads with forward compatibility.
- Behavioral scope is explicit and validated per release.
- CI and regression tests are release gates, not optional.

---

## v1.1 — Distribution + Usability Stabilization (local-first)

**Goals**
- Reduce setup friction to a single command.
- Ensure CI regression coverage for all presets before adding new modeling depth.

**Scope**
- Zero-cost distribution
  - Docker image
  - Single-command startup
  - Clean CLI entrypoint (`vsl run`)
  - Improved install instructions
  - No infrastructure hosting required
- React Local UI (Phase 1)
  - React frontend (local)
  - JSON payload preview
  - Results display inside browser
- Preset regression CI as a release gate

**Definition of Done**
- `vsl run` works from a clean install.
- All presets pass in CI on every push/PR.
- Local UI can run, generate payload, and view results.

---

## v1.2 — Builder/Workflow Maturity

**Goals**
- Make the builder the default workflow for custom protocols.
- Provide schema evolution without breaking old payloads.

**Scope**
- React Local UI (Phase 2)
  - Dynamic builder mode
  - Learner/Protocol/Representation selectors
  - Phase chaining UI
- Schema migration/versioning

**Definition of Done**
- Builder can compose all v1 phases and generate valid payloads.
- Versioned schemas can load older payloads without error.

**Status**
- In progress.

---

## v1.3 — Cognitive Extensions (core science upgrade)

**Goals**
- Extend behavioral expressivity with attention and similarity.
- Formalize scope with explicit documentation.

**Scope**
- Attention-based learner
- Similarity-based generalization
- Refined context modeling
- Additional phenomenon validations
- Expanded test suite
- Model card / behavioral scope doc updated for the release

**Definition of Done**
- Attention and similarity behaviors are test-validated.
- Updated model card clearly states supported phenomena and limits.

---

## v1.4 — Operant Architecture Split (behavioral depth)

**Goals**
- Separate operant modeling into a dedicated architecture path.

**Scope**
- Operant agent interface
- Action-value learners (TD / Q-learning)
- Reinforcement / punishment / extinction
- Matching law / shaping / resurgence / superextinction / spontaneous recovery

**Definition of Done**
- Operant protocols run end-to-end with stable metrics/plots.
- Operant agents and learners are first-class choices in the UI.

---

## v1.5 — Neural Function Approximation

**Goals**
- Add neural approximators while preserving classical effects.

**Scope**
- NeuralNetLearner
- Seeded deterministic mode
- Gradient-based update
- Validation against classical effects
- Compatibility with existing protocols

**Definition of Done**
- Neural learner validated against a core set of classical protocols.
- Deterministic mode guarantees reproducibility.

---

## v2.0 — Desktop Packaging

**Goals**
- Ship a fully packaged app with no Python dependency.

**Scope**
- Packaged executable
- Optional bundled runtime
- Cross-platform builds
- Eliminate Python requirement entirely
- Still zero-cost distribution

**Definition of Done**
- Installable binaries for major platforms.
- No external services required for core workflows.

---

## Future Implementation (Post-v2)

- Change-point / full latent context modeling
- Extended neural variants and advanced inference


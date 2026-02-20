Virtual Shaping Lab — Design Evolution (Phase-Centric v1)

Date: Version 1
Scope: Phase-centric experiments, canonical protocols, schema-driven UI, attention,
similarity, and heuristic context inference.

1. Core Decision

The system is phase-centric.

- Phases own trial logic and learning gates.
- Protocols only orchestrate phases in a scientifically valid order.

This preserves clarity, supports both UI modes, and prevents duplication.

2. Phase-Centric Architecture

2.1 Phases (Primary)

A phase is:
- A contiguous block of trials.
- Fixed contingencies and stimulus availability.
- Responsible for trial execution.
- Responsible for learning gating and record creation.

A phase is not:
- A new learner.
- A new agent.
- A protocol.

2.2 Protocols (Orchestrators)

Protocols:
- Compose ordered lists of phases.
- Enforce canonical ordering constraints.
- Do NOT implement trial logic.
- Serve as behavioral phenomena wrappers.

This makes phenomena reusable and canonical experiments data-driven.

3. Two UI Modes, One Execution Model

Both modes produce the same payload format:
- Builder mode: author a custom phase list.
- Preset mode: load a canonical phase list.

Execution path is identical:

for phase in phases:
    protocol = build_protocol(phase)
    records += protocol.run()

No branching backend logic.

4. Representation and State Encoding

Representations own encoding.

- Observation encoders live in representations.
- Agent calls representation.encode(...) during observe.
- Learners only see encoded states (tabular or vector).

Vectorization is additive. No protocol or phase changes are required.

5. Mapping of Behavioral Concepts

Concept           Layer                 Rationale
Generalization    Representation        Similarity structure
Categorization    Representation+Learner
Attention         Learner/Representation Learning-rate modulation
Motivation        Outcome / reward schedule
Contingencies     Phase
History           Protocol (ordering)
Context           Phase / Inference

6. Stability Guarantees

No changes are required to:
- Runner execution model.
- UI payload schema shape.
- Reward schedules.
- Reporting pipeline.

Changes remain additive and isolated.

7. Canonical Phenomena Strategy

Protocols implement canonical phenomena by composing phases:
- Acquisition -> single AcquisitionPhase
- Extinction -> AcquisitionPhase -> NonReinforcementPhase
- Conditioned inhibition -> Acquisition -> Compound NonReinforcement -> Probe
- Blocking / Overshadowing / Overexpectation -> compound acquisition variants

All canonical experiments are data-driven phase lists.

8. Attention (Explicit v1)

Attention is modeled as explicit learning-rate modulation.
- Attention maps are normalized at runtime.
- Presets can provide default attention values.
- Builder can override attention explicitly.

9. Similarity / Generalization (Explicit v1)

Similarity is modeled via an explicit similarity matrix.
- Schema validates matrix shape.
- Representation encoders apply similarity to encoded features.
- Builder can supply similarity; presets use defaults.

10. Context Inference (Heuristic v1)

Context can be inferred for phases without explicit context selection.
- Inference runs during experiment assembly.
- Records include inferred context metadata for reporting.

11. Final Position

The architecture is stable and extensible.

Future learning models (vector RW, TD, latent causes) plug in through:
- Representation encoders.
- Learner implementations.

No changes to phases or protocols are required.

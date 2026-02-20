Virtual Shaping Lab — Architecture v1 (Agent-Centric, Phase-Oriented)

Purpose
This document describes the current architecture of Virtual Shaping Lab. The system is phase-oriented for behavioral logic and agent-centric for learning. Phases own trial logic, protocols orchestrate phases, and agents encapsulate learners, representations, and (when applicable) policies.

Behavioral Scope (Experimental)
The modeled phenomena are experimental in v1 and should be treated as work-in-progress. The system currently supports:
- Acquisition, extinction, nonreinforcement
- Differential acquisition (CS+ vs CS-)
- Compound learning (compound acquisition, blocking, overshadowing, overexpectation)
- Contextual effects (renewal AAB/ABA/ABC, context shift, rapid reacquisition)
- Conditioned inhibition (summation + retardation)
- Operant matching law with concurrent schedules

High-Level Pipeline (Single Trial)
1. Phase samples trial structure
2. Phase builds observation (stimuli + context)
3. Agent.observe(observation) ? encoded state
4. Agent.value(state) ? prediction
5. Agent.act(state) ? action (operant only; classical returns None)
6. Phase computes reward/outcome
7. Phase applies learning if allowed
8. Phase records the outcome

Execution Flow (Run)
- Runner executes protocol.run() or phase.step()
- Protocol composes ordered phases and enforces ordering constraints
- Phases are the only source of trial logic

Layer Responsibilities

API (run.py)
- Thin entrypoint
- Validates payload, assembles experiment, runs protocols/phases, generates report

Validation (validate_payload.py)
- Schema validation for experiment + report + phases/protocols
- Enforces protocol vs phase-mode routing
- Applies policy guard (policy only for operant protocols)
- Applies phase order constraints

Assembly (assemble.py)
- Builds representation ? policy (optional) ? learner ? agent
- Builds protocol(s) or phase sequences based on payload mode
- Infers contexts when enabled
- Injects attention and similarity into representation params

Experiment Config (config.py)
- Normalizes experiment payloads into PhaseConfig objects
- Validates similarity matrix shape
- Supports attention and context inference config

Protocol (Orchestrator)
- Composes ordered phases
- Enforces canonical ordering constraints
- Does not implement trial logic
- Reads all protocol settings from params

Phase (Primary Behavioral Unit)
- Defines trial logic and contingencies
- Controls learning gate (allows_learning)
- Produces trial records
- Knows nothing about protocol ordering

Agent (Core Learning Interface)
- Encapsulates representation + learner (+ policy for operant)
- observe(observation) ? encoded state
- value(state) ? prediction
- update(state, reward, action) ? learning update
- act(state) ? action (operant) or None (classical)

Agent Types
- ClassicalAgent: Pavlovian learner, no action selection
- OperantAgent: policy-driven action selection with operant learners

Learner (agents/learners/)
- Owns learnable parameters (weights/Q-values)
- Consumes encoded state (and action when needed)
- Examples: Rescorla-Wagner, TD-Value, Q-learner

Representation (agents/representations/)
- Encodes observation ? state vector
- Elemental, configural, hybrid encodings
- Supports:
  - Explicit attention (learning-rate scaling)
  - Similarity matrix (generalization)
  - Context-gated features

Policy (agents/policies/)
- Selects actions from value function or preferences
- Does not update values
- Examples: epsilon_greedy, softmax, fixed

Context Inference (Heuristic)
- Optional experiment-level setting
- Assigns contexts per phase based on phase changes
- Records inferred context in trial records

Similarity / Generalization (Representation-Level)
- Optional similarity matrix
- Blends feature activations by similarity weights
- Learners remain unchanged (SOLID-aligned)

Two UI Modes (Same Backend)
- Presets: canonical protocol compositions
- Builder: user-defined phase lists (schema-driven)
Both emit the same payload schema and use the same engine.

Known Limitations
- Context inference is heuristic only (no change-point or Bayesian latent causes)
- Similarity is static (no learned similarity or category induction)
- Attention is explicit only (no adaptive attention dynamics)
- Some behavioral effects are experimental and not fully validated

Future Implementation
- Change-point context inference
- Full latent-cause modeling
- Learned attention
- Learned similarity / generalization kernels

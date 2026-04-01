# V3.21 Single-Path Protocol Architecture

## Purpose
This document records the V3.21 canonical protocol execution seam and the protocol-agent causal boundary contract used for change control.

## Canonical Causal Split
Boundary rules are aligned to `agent_protocol_interaction.md`.

Protocol/environment owns:
- emission of externally visible task state
- consequence generation from action
- temporal advance and stopping logic
- protocol timeline progression and phase state

Agent owns:
- observation construction
- prediction/value computation
- policy/action selection
- post-outcome learning updates and internal state transitions

## Canonical Runtime Execution Path
The only approved runtime protocol path is:
1. `virtual_shaping_lab/vsl/rollout/harness.py`
2. `CompiledProgramTestEnvironment.step(...)`
3. `virtual_shaping_lab/vsl/runtime/protocol_adapter.py`
4. `RuntimeProtocolAdapter.emit(...)`
5. `CompositionalAgent.pre_outcome_step(...)`
6. `RuntimeProtocolAdapter.resolve(...)`
7. `CompositionalAgent.learn(...)`
8. `CompositionalAgent.advance_internal_time(...)`

## Boundary Objects
Cross-boundary interaction remains narrow and typed:
- `TaskInput`: environment -> agent (pre-outcome situation)
- `Action`: agent -> environment (behavior selection)
- `Outcome`: environment -> agent (post-action consequence)
- `TrialRecord`/rollout metadata: measurement/logging only

The environment must provide outcomes, not learner-internal error/update terms.

## Canonical Metadata and Trace Surfaces
Protocol traces are first-class:
- rollout record: `metadata.protocol_traces.*`
- report normalization:
  - `protocol_emission`
  - `protocol_consequence`
  - `protocol_advance`
  - `protocol_stop`
  - `protocol_timing`
  - `protocol_provenance`

## Explicitly Non-Canonical / Banned Paths
The following are not allowed in active runtime flow:
- direct harness computation of protocol consequence/advance/stop outside runtime protocol seam
- direct protocol operator invocation from runtime loop bypassing `RuntimeProtocolAdapter`
- protocol-side computation of learner internals (`prediction_error`, weight updates, trace updates)
- agent-side mutation of protocol timeline/state
- legacy protocol namespace imports from runtime surfaces (factory/phase/protocol legacy paths)

## Compatibility Bridges
When temporary compatibility is required, bridges must be explicit and time-bounded:
- include `owner` and `expiry` markers in runtime metadata
- include corresponding guardrail tests and CI checks
- remove bridge paths at or before expiry milestone

## Guardrail Requirements
V3.21 closeout requires CI-enforced checks for:
- protocol ownership + executable core stability
- runtime protocol seam/parity stability
- trace promotion/report normalization stability
- single-path protocol execution and namespace hard-removal
- end-to-end matrix + replay/hash determinism

## Change Control
Any protocol-runtime change must:
1. update canonical seam files (`runtime/protocol_adapter.py`, `rollout/harness.py`) if behavior changes
2. update trace/report contracts when metadata shape changes
3. update guardrail tests and closeout CI bucket
4. provide PR evidence mapped to the checklist in `docs/v3_21_pr_evidence_checklist.md`

# V3.19.15 Single-Path Observation Execution Architecture

## Purpose
This document defines the final observation execution boundary for V3.19.15 and records what is canonical vs compatibility-only.

## Canonical Execution Path
The only approved observation execution path is:
1. `virtual_shaping_lab/vsl/runtime/observation_adapter.py`
2. `RuntimeObservationAdapter.step(...)`
3. `virtual_shaping_lab/vsl/agent/observation/bundle.py`
4. `ObservationBundle.step(...)`

Runtime rollout integration occurs via:
- `virtual_shaping_lab/vsl/rollout/harness.py`

## Canonical Contract Ownership
- Symbolic observation grammar/spec ownership:
  - `virtual_shaping_lab/vsl/agent/observation/spec.py`
  - `virtual_shaping_lab/vsl/agent/observation/resolve.py`
- Executable preset ownership:
  - `virtual_shaping_lab/vsl/agent/observation/executable_presets.py`
- Runtime seam ownership:
  - `virtual_shaping_lab/vsl/runtime/observation_adapter.py`

## Explicitly Non-Canonical Surfaces
The following surfaces are not canonical observation execution and must not be used to introduce alternate runtime observation paths:
- phase-level ad hoc observation helper use in `virtual_shaping_lab/experiment/phases/*`
- direct runtime observation construction bypassing `RuntimeObservationAdapter`
- legacy observation helper surfaces under `virtual_shaping_lab/agents/representations/*` for new runtime wiring

These may remain temporarily as compatibility/deletion candidates, but runtime observation stepping must not pass through them.

## Runtime/Record Trace Contract
For V3.19.15 closeout, observation internals must remain visible in records/report normalization under:
- `metadata.observation`
- `metadata.observation.stage_traces`
- `metadata.observation.pipeline_order`

Observation vectors used for learner stepping must remain derivable from:
- `metadata.observation.output.features`
- `metadata.observation.output.feature_names`

## Guardrail Requirements
Single-path enforcement requires:
- no legacy observation import tokens in runtime surfaces
- no phase-level ad hoc observation construction reintroduced in active runtime paths
- deterministic observation registry/preset hash behavior
- blocking CI bucket coverage for runtime seam + guardrail + record/report observation trace checks

## Change Control
Any future observation execution change must:
1. modify canonical path files listed above
2. update the V3.19.15 observation guardrail tests
3. include before/after test evidence in PR description

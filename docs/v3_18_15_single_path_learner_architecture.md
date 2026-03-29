# V3.18.15 Single-Path Learner Execution Architecture

## Purpose
This document defines the final learner execution boundary for V3.18.15 and records what is canonical vs compatibility-only.

## Canonical Execution Path
The only approved learner execution path is:
1. `virtual_shaping_lab/vsl/runtime/learner_adapter.py`
2. `RuntimeLearnerAdapter.step(...)`
3. `virtual_shaping_lab/vsl/agent/learning/bundle.py`
4. `LearnerBundle.step(...)`

Runtime rollout integration occurs via:
- `virtual_shaping_lab/vsl/rollout/harness.py`

## Canonical Contract Ownership
- Symbolic learner grammar/spec ownership:
  - `virtual_shaping_lab/vsl/agent/learning/spec.py`
  - `virtual_shaping_lab/vsl/agent/learning/resolve.py`
- Executable preset ownership:
  - `virtual_shaping_lab/vsl/agent/learning/executable_presets.py`
- Runtime seam ownership:
  - `virtual_shaping_lab/vsl/runtime/learner_adapter.py`

## Explicitly Non-Canonical Surfaces
The following surfaces are not canonical learner execution and must not be used to introduce alternate runtime learning paths:
- `virtual_shaping_lab/agents/learners/*`
- `virtual_shaping_lab/experiment/factories/learner_factory.py`
- any update-only fallback dispatch in phase helpers

These may remain temporarily as compatibility/deletion candidates, but runtime learner stepping must not pass through them.

## Runtime/Measurement Trace Contract
For V3.18.15 closeout, learner internals must remain visible in records/report normalization under:
- `v`
- `delta`
- `theta`
- `attention`
- `memory`

Compatibility aliases (`prediction`, `prediction_error`) remain supported for existing report consumers.

## Guardrail Requirements
Single-path enforcement requires:
- no legacy learner import tokens in runtime surfaces
- no update-only fallback dispatch path
- deterministic learner contract hash behavior
- blocking CI bucket coverage for runtime seam + guardrail + metadata identity checks

## Change Control
Any future learner execution change must:
1. modify canonical path files listed above
2. update the V3.18.15 guardrail tests
3. include before/after test evidence in PR description

# V3.4.0 Summary - Universal Policy and Action-Space Semantics

## Overview
V3.4.0 removes classical/operant branching from the composition root by making policy/action-space semantics the runtime discriminator.

Primary outcomes:
- V3 now includes explicit null/singleton action-space primitives
- a V3 `NullPolicy` is available as a deterministic actionless control primitive
- assembly now routes both classical and operant families through one composed-agent kernel path
- composition-root mode branching is protected by an AST guard gate

This slice finishes the policy/action-space unification needed before deeper V3 runtime decomposition.

---

## Slice 1 - Null Policy/Action-Space Primitives

### Objective
Add `NullActionSpace` (and singleton variant) plus `NullPolicy` in V3 namespace.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/agent/policy/__init__.py`
- `virtual_shaping_lab/vsl/agent/policy/action_space.py`
- `virtual_shaping_lab/vsl/agent/policy/null_policy.py`
- `tests/test_v3_policy_action_space.py`

Updated:
- `virtual_shaping_lab/vsl/__init__.py`

Changes:
- introduced `ActionSpace` protocol
- introduced `NullActionSpace` (empty action-set semantics)
- introduced `SingletonActionSpace` (deterministic single-action semantics)
- introduced V3 `NullPolicy` with deterministic null action selection and stable distribution behavior

---

## Slice 2 - Unified Assembly Path

### Objective
Collapse classical and operant assembly through one composition-root path.

### Implemented
Updated:
- `virtual_shaping_lab/experiment/assemble.py`
- `tests/test_assemble_coverage.py`

Changes:
- added `UNIFIED_COMPOSED_AGENT_NAME = "composed_agent"`
- `_build_agent_stack(...)` now always calls `build_agent("composed_agent", ...)`
- family semantics are now carried by policy/action-space behavior, not by composition-root agent-name branching
- added regression:
  - `test_assemble_classical_and_operant_use_unified_agent_kernel`

---

## Slice 3 - Branching Scope Guard

### Objective
Enforce no classical/operant branching at composition-root assembly seams.

### Implemented
Added:
- `tests/test_v3_assembly_mode_branching_guard.py`

Changes:
- added AST guard:
  - `test_no_mode_branching_in_assembly`
- guard fails if `experiment/assemble.py` introduces `if`/`ifexp`/`match` mode branching on:
  - `classical_agent`
  - `operant_agent`
  - `classical`
  - `operant`

---

## Closeout Impact

After V3.4.0:
- policy/action-space semantics are explicit V3 primitives
- composition root now has one agent assembly kernel for both classical and operant families
- mode branching drift at assembly scope is CI-guarded

This narrows architecture-level behavior differences to policy/action-space semantics rather than top-level assembly paths.

---

## Validation

### Slice Gates
Validated via targeted tests:
- `tests/test_v3_policy_action_space.py`
- `tests/test_assemble_coverage.py::test_assemble_classical_and_operant_use_unified_agent_kernel`
- `tests/test_v3_assembly_mode_branching_guard.py`

### CI-Facing Contract Checks
Validated through guard/integration assertions:
- assembly kernel path is identical for classical and operant payload families
- composition-root mode branching literals are blocked by AST gate
- null/singleton action-space semantics remain deterministic

---

## Net State After V3.4.0

- V3 now has first-class policy/action-space primitives for universal control semantics
- classical and operant assembly now share one composition-root agent construction path
- assembly mode-branching regressions are prevented by an explicit AST guard

V3.4.0 therefore completes universal policy/action-space unification at composition-root scope.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_policy_action_space.py`
- `python -m pytest -q tests/test_assemble_coverage.py -k "unified_agent_kernel"`
- `python -m pytest -q tests/test_v3_assembly_mode_branching_guard.py`


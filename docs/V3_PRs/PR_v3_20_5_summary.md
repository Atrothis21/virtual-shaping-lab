# V3.20.5 Summary - Executable Policy Operator Core and Presets

## Overview
V3.20.5 introduces executable policy operators, adds a typed decision-input boundary for policy selection, and ships deterministic executable policy preset materialization with structural/golden CI enforcement.

Primary outcomes:
- added executable policy operator protocols and typed policy output contract
- implemented core selection operators (`greedy`, `epsilon_greedy`, `softmax`, `uniform_random`) plus null policy behavior
- added canonical typed `PolicyInput` boundary derived from `TaskInput -> ObservationOutput -> Prediction`
- added executable policy preset materialization from canonical policy specs
- added blocking CI bucket for executable policy core structural and golden contracts

This slice closes the V3.20.5 milestone for executable policy-core foundations.

---

## Slice 1 - Policy Operator Protocol Base

### Objective
Add executable policy operator protocols and null/default policy behavior.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/policy/operators/base.py`
- `virtual_shaping_lab/vsl/agent/policy/operators/__init__.py`

Updated:
- `virtual_shaping_lab/vsl/agent/policy/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `V3.20.5_plan.md`

Changes:
- added executable policy contracts:
  - `PolicyOperator`
  - `ActionAvailabilityOperator`
- added typed decision artifact:
  - `PolicyOutput`
- added null/default policy operator:
  - `NullPolicyOperator`

---

## Slice 2 - Core Selection Operators

### Objective
Implement first executable policy operator family for action selection.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/policy/operators/selection.py`

Updated:
- `virtual_shaping_lab/vsl/agent/policy/operators/__init__.py`
- `virtual_shaping_lab/vsl/agent/policy/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `V3.20.5_plan.md`

Changes:
- added executable selection operators:
  - `GreedyActionSelectionPolicy`
  - `EpsilonGreedyPolicy`
  - `SoftmaxPolicy`
  - `UniformRandomPolicy`
- enforced deterministic tie-break and explicit probability/output metadata semantics
- kept classical/no-action behavior through `NullPolicyOperator`

---

## Slice 3 - Typed Decision Context Boundary

### Objective
Add canonical typed policy-input boundary and prevent policy from consuming raw task payload internals.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/policy/input.py`

Updated:
- `virtual_shaping_lab/vsl/agent/policy/operators/selection.py`
- `virtual_shaping_lab/vsl/agent/policy/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `V3.20.5_plan.md`

Changes:
- introduced typed decision transport:
  - `PolicyInput`
- added canonical builder:
  - `build_policy_input(...)`
- enforced boundary semantics:
  - policy input is derived from typed boundary path (`TaskInput -> ObservationOutput -> Prediction`)
  - disallowed raw/boundary leakage keys in policy metadata
- updated selection operators to accept typed `PolicyInput` via mapping transport compatibility

---

## Slice 4 - Executable Policy Preset Materialization

### Objective
Map legal symbolic policy specs to executable policy operators through deterministic preset APIs.

### Implemented
Added:
- `virtual_shaping_lab/vsl/agent/policy/executable_presets.py`

Updated:
- `virtual_shaping_lab/vsl/agent/policy/__init__.py`
- `virtual_shaping_lab/vsl/agent/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `V3.20.5_plan.md`

Changes:
- added executable preset contract:
  - `ExecutablePolicyPreset`
- added preset materialization APIs:
  - `build_executable_policy_preset(...)`
  - `build_executable_policy_from_spec(...)`
  - `executable_policy_preset_names()`
- implemented initial executable preset set:
  - `no_policy`
  - `greedy`
  - `epsilon_greedy`
  - `softmax`
  - `uniform_random`

---

## Slice 5 - Structural/Golden Enforcement and CI Bucket

### Objective
Add executable policy-core structural/golden tests and block regressions in CI.

### Implemented
Added:
- `tests/test_v3_policy_operators_base.py`
- `tests/test_v3_policy_operators_selection.py`
- `tests/test_v3_policy_input_boundary.py`
- `tests/test_v3_policy_bundle_execution.py`
- `tests/test_v3_policy_executable_instantiation.py`
- `tests/test_v3_policy_golden.py`

Updated:
- `.github/workflows/ci.yml`
- `V3.20.5_plan.md`

Changes:
- added blocking CI step:
  - `Run V3.20.5 executable policy core`
- CI bucket enforces:
  - policy operator protocol and output-shape stability
  - selection/operator behavior stability
  - typed policy-input boundary guardrails
  - executable preset mapping and golden-output determinism

---

## Closeout Impact

After V3.20.5:
- policy execution now has explicit executable operator contracts with typed outputs
- selection behavior is implemented through deterministic executable policy operators
- policy selection is constrained to typed decision-context input, separate from raw task payload internals
- legal symbolic policy specs can be materialized to executable policy presets deterministically
- CI now blocks structural and golden regressions for the executable policy core

V3.20.5 therefore completes the executable policy-core baseline required for V3.20.10 runtime seam integration work.

---

## Validation

### Slice and Contract Gates
Validated via:
- `tests/test_v3_policy_operators_base.py`
- `tests/test_v3_policy_operators_selection.py`
- `tests/test_v3_policy_input_boundary.py`
- `tests/test_v3_policy_bundle_execution.py`
- `tests/test_v3_policy_executable_instantiation.py`
- `tests/test_v3_policy_golden.py`

### CI-Facing Contract Checks
Validated by assertions that:
- policy operator protocol and output contracts remain stable
- policy selection semantics remain deterministic for core operators
- typed policy-input boundary remains narrow and causal
- executable preset mappings and golden outputs remain deterministic

---

## Net State After V3.20.5

- executable policy operator base and core selection implementations are in place
- typed policy input boundary and boundary builder are exported and test-covered
- executable policy preset materialization is available for canonical policy presets
- blocking CI enforcement exists for executable policy structural and golden contracts

V3.20.5 establishes the policy execution substrate for runtime policy adapter and single-path policy integration in V3.20.10+.

## Validation Commands

Targeted gates exercised for V3.20.5:
- `python -m pytest -q tests/test_v3_policy_operators_base.py tests/test_v3_policy_operators_selection.py`
- `python -m pytest -q tests/test_v3_policy_input_boundary.py tests/test_v3_policy_bundle_execution.py`
- `python -m pytest -q tests/test_v3_policy_executable_instantiation.py tests/test_v3_policy_golden.py`

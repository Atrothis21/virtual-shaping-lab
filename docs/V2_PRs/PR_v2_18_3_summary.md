# V2.18.3 Summary - Canonical Config Parsing and Config-Layer Ownership Enforcement

## Overview
V2.18.3 refactors config parsing into an explicit compiler from canonical payload ownership boundaries to typed experiment configuration.

Primary outcomes:
- config parsing is now split into explicit ownership-local parser seams
- canonical payload sections are parsed by program, representation, learning, policy, and runtime ownership
- representation-derived metadata and learning-derived metadata are no longer gathered through one mixed parser path
- config-layer validation now catches key classical/operant policy misuse before assembly
- config tests and ownership tests are green under the new parser layout

This slice makes the config layer easier to reason about as a compiler instead of a transitional normalization bundle.

---

## Ownership Parser Split

### Explicit Parser Seams
Config parsing now has explicit ownership-local seams for:
- `parse_program()`
- `parse_representation()`
- `parse_learning()`
- `parse_policy()`
- `parse_runtime()`

This replaces the previous shape where multiple ownership concerns were still aggregated through broader mixed helpers.

### New Normalization Flow
The config normalizer now reads canonical experiment state by ownership boundary:
- program -> phases
- representation -> representation object plus stimuli/salience metadata
- learning -> attention map plus attention strategy config
- policy -> policy object
- runtime -> runtime settings plus context inference

Net effect:
- config construction is now readable in the same ownership language as the canonical payload contract

---

## Canonical Config Compilation

### Representation-Owned Parsing
Representation parsing remains responsible for:
- representation object shape
- similarity validation
- representation-owned metadata extraction such as:
  - stimuli
  - salience

This keeps representation concerns local instead of mixing them with learner/runtime parsing.

### Learning-Owned Parsing
Learning parsing now explicitly owns:
- attention initialization
- attention strategy config normalization

This is the main parser-level clarification introduced in V2.18.3:
- attention state/config is now visibly learner-owned at config build time, not just later in assembly/runtime behavior

### Program-Owned Parsing
Program parsing now explicitly owns:
- canonical phase extraction
- phase-level shape validation
- template-backed phase param ownership guards

This makes program parsing easier to follow independently from agent/runtime parsing.

---

## Config-Layer Ownership Enforcement

### Earlier Failure Boundary
V2.18.3 moves some important validation failures from assembly into config build.

Now rejected during config construction:
- `classical_agent` with a policy
- `operant_agent` without a policy

These were previously surfaced later through assembly-path checks.

Net effect:
- invalid ownership/control combinations now fail at the config boundary rather than during runtime object construction

### Reduced Runtime Fallback Reliance
The config layer now does more of the work that previously leaked into downstream runtime interpretation:
- ownership-local parsing happens up front
- agent/policy consistency is checked up front
- config tests now lock those expectations directly

This is not yet the full typed-plan promotion, but it materially reduces config ambiguity before assembly.

---

## Compatibility and Transition Strategy

### Thin Compatibility Wrappers Retained
To avoid unnecessary churn during the refactor, V2.18.3 keeps thin compatibility wrappers for:
- `parse_phases()`
- `parse_experiment_fields()`

These now delegate through the new ownership-local seams rather than remaining as the primary parsing model.

This means:
- the architectural direction is cleaner
- existing tests and call sites do not need to be rewritten all at once

---

## Validation

### Parser Split Gates
Validated through:
- `tests/test_config.py`
- `tests/test_parameter_validator.py`

These cover:
- direct parser seam behavior
- learning/attention normalization
- representation parsing
- policy/runtime parsing
- config pipeline behavior after the split

### Config-Boundary Enforcement Gates
Validated through:
- `tests/test_config.py`
- `tests/test_payload_contract.py`
- `tests/test_parameter_ownership_guards.py`
- `tests/test_assemble_coverage.py`
- `tests/test_operant_contract_harness.py`

These cover:
- config-layer agent/policy consistency checks
- canonical payload/config interaction
- ownership boundary protection
- tests that previously expected assembly-time failures now failing earlier at config build

---

## Net State After V2.18.3

- config build now consumes canonical structure through explicit ownership-local parser seams
- learning-owned, representation-owned, program-owned, and runtime-owned parsing are more clearly separated
- key invalid classical/operant policy combinations now fail during config construction
- config parsing is closer to a real canonical compiler and less dependent on transitional mixed helpers
- the config layer now better matches the canonical ownership model established in V2.18.2

V2.18.3 therefore closes a large part of the remaining ambiguity between canonical payload structure and config-layer implementation structure.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_config.py tests/test_parameter_validator.py`
- `python -m pytest -q tests/test_config.py tests/test_payload_contract.py tests/test_parameter_ownership_guards.py tests/test_assemble_coverage.py tests/test_operant_contract_harness.py`

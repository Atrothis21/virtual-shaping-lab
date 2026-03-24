# V3.15.0 Plan - Arrangement Axis and Registry Factorization Foundation

## Objective

Introduce first-class `Arrangement x Task x Agent` factorization in contracts and legality surfaces while preserving current preset-driven execution compatibility.

## Source Inputs

- `payload_refactor.md`
- `docs/V3_operator_info/operator_basis_set.md`
- `V3_14_0_plan.md`
- `virtual_shaping_lab/ui/contracts/operator_legality_engine.py`
- `virtual_shaping_lab/ui/contracts/preset_registry.py`
- `virtual_shaping_lab/ui/contracts/preset_basis_authoring.py`

## Entry Criteria

- V3.14.0 basis-first core preset cutover is merged and green.
- Core basis compiler/materialization/assembly contracts are stable.
- Current legality matrix and registry contracts are passing in CI.

## Commit-Sized Slices

## Slice 1 - Arrangement Contract Surface

Deliver:

- add explicit arrangement contract (`pavlovian`, `operant`) as first-class typed surface
- declare arrangement-level required/forbidden operator semantics (especially policy `pi`)
- add canonical arrangement IDs and deterministic hash/json helpers

Tests:

- arrangement schema/validation tests
- deterministic arrangement hash snapshot tests
- invalid arrangement ID/shape rejection tests

## Slice 2 - Task Registry Split (`Omega`)

Deliver:

- create task registry decoupled from preset identity
- introduce explicit task implementation identity model:
  - base phenomenon ID (for naming/teaching)
  - arrangement-scoped implementation ID (for executable semantics)
  - example: `acquisition` with `pavlovian_acquisition` and `operant_acquisition`
- each task implementation declares:
  - arrangement compatibility
  - required operators / optional operators
  - protocol family mapping
- add explicit hybrid/ambiguous task policy:
  - supported hybrid implementations
  - deferred hybrid implementations
  - forbidden tuple constructions until formalized
- keep preset registry compatible via thin references

Tests:

- task registry load/shape tests
- required task IDs tests for core phenomena
- task implementation ID uniqueness tests
- task-to-arrangement compatibility validation tests
- hybrid/deferred/forbidden policy enforcement tests

## Slice 3 - Agent Bundle Registry Split

Deliver:

- create agent bundle registry for reusable operator bundles
- keep agent bundle identity primarily declarative (operator bundle first)
- each agent bundle declares:
  - included operator selections
  - arrangement compatibility
  - builder-family compatibility constraints (secondary metadata only; not primary identity)
- enforce no hand-authored selectable universe drift from operator registry

Tests:

- agent registry load/shape tests
- declarative-identity-first contract tests
- bundle legality against operator registry tests
- arrangement mismatch rejection tests

## Slice 4 - Composition Contract (`Arrangement x Task x Agent -> Operator Subset`)

Deliver:

- add composition contract that deterministically composes:
  - arrangement constraints
  - task implementation constraints
  - agent bundle selections
- emit composed operator subset artifact for compiler input
- emit composition provenance artifact with:
  - arrangement identity
  - task implementation identity
  - agent bundle identity
  - composition hash
  - axis-to-slot contribution map (which axis contributed which slot decisions)
- preserve compatibility wrappers for existing preset-based entrypoints

Tests:

- composition determinism tests
- known valid tuple acceptance tests
- known invalid tuple rejection tests with machine-readable error codes
- composition provenance shape/hash determinism tests

## Slice 5 - Legality Engine Integration and Docs

Deliver:

- integrate arrangement/task/agent composition into legality pipeline
- ensure error reporting includes tuple context and violating axis
- publish foundation docs for:
  - arrangement axis
  - task registry
  - agent registry
  - composition flow

Tests:

- legality engine tuple-path tests
- compatibility matrix consistency tests
- regression tests for existing preset legality behavior

## Testing Plan

- `python -m pytest -q tests/test_v3_arrangement_contract.py`
- `python -m pytest -q tests/test_v3_task_registry.py`
- `python -m pytest -q tests/test_v3_agent_bundle_registry.py`
- `python -m pytest -q tests/test_v3_agent_bundle_declarative_contract.py`
- `python -m pytest -q tests/test_v3_arrangement_task_agent_composition.py`
- `python -m pytest -q tests/test_v3_arrangement_task_agent_provenance.py`
- `python -m pytest -q tests/test_v3_operator_legality_engine.py -k "arrangement or task or agent"`

## CI Updates

Add blocking bucket:

- `Run V3 arrangement-task-agent foundation`
  - arrangement contract tests
  - task registry tests
  - agent bundle registry tests
  - declarative agent bundle contract tests
  - composition contract tests
  - composition provenance tests
  - legality tuple integration tests

## Exit Criteria

- arrangement is first-class and validated independently of presets
- task registry and agent bundle registry exist and are test-enforced
- arrangement-scoped task implementation IDs are explicit and test-enforced
- hybrid/deferred/forbidden task policy is explicit and contract-enforced
- agent bundle identity remains declarative with builder-family metadata as secondary
- deterministic composition from `(arrangement, task, agent)` to operator subset is implemented
- composition provenance artifact is emitted deterministically with axis contribution mapping
- legality engine accepts/rejects tuple combinations with explicit diagnostics
- existing preset flows remain compatible through wrappers during migration window

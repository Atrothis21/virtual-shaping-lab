# V3.15.0 Summary - Arrangement x Task x Agent Foundation Contracts

## Overview
V3.15.0 introduces first-class `Arrangement x Task x Agent` contract factorization and integrates tuple-aware legality diagnostics while preserving preset compatibility wrappers.

Primary outcomes:
- added explicit arrangement contract surface for `pavlovian` and `operant`
- split task identity into base phenomenon IDs + arrangement-scoped implementation IDs
- added declarative agent bundle registry with arrangement compatibility and registry-driven selection constraints
- added deterministic tuple composition contract that emits operator subset + provenance artifact
- integrated tuple-path legality evaluation with axis-aware diagnostics and machine-readable tuple composition errors
- added blocking CI coverage for arrangement/task/agent foundation tests

This slice establishes the contract substrate for tuple-based authoring/composition while preserving migration compatibility with preset entrypoints.

---

## Slice 1 - Arrangement Contract Surface

### Objective
Add first-class arrangement contract and arrangement-level policy semantics.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/arrangement_contract.py`
- `tests/test_v3_arrangement_contract.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- introduced canonical arrangement IDs:
  - `pavlovian`
  - `operant`
- added arrangement policy semantics for slot `pi` (required/forbidden behavior)
- added arrangement required/optional/forbidden operator slot requirements
- added deterministic arrangement JSON/hash helpers and schema validation

---

## Slice 2 - Task Registry Split (`Omega`)

### Objective
Decouple task registry from preset identity and add arrangement-scoped implementations.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/task_registry.py`
- `tests/test_v3_task_registry.py`

Updated:
- `virtual_shaping_lab/ui/contracts/preset_registry.py`
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- added phenomenon-level task IDs and arrangement-scoped implementation IDs
- each implementation now declares:
  - arrangement compatibility
  - required/optional operators
  - protocol family mapping
- added hybrid policy surface:
  - supported hybrid implementations
  - deferred hybrid implementations
  - forbidden tuple rules
- added thin preset compatibility references (`task_reference`) validated against task registry

---

## Slice 3 - Agent Bundle Registry Split

### Objective
Introduce declarative agent bundle registry for reusable operator bundles.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/agent_bundle_registry.py`
- `tests/test_v3_agent_bundle_registry.py`
- `tests/test_v3_agent_bundle_declarative_contract.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- added declarative bundle identity surface (`operator_selections` as primary identity)
- added arrangement compatibility validation per bundle
- added builder-family compatibility constraints as secondary metadata
- enforced registry-sourced selectable universe (`operator_basis_registry`) for bundle selections

---

## Slice 4 - Composition Contract (`Arrangement x Task x Agent -> Operator Subset`)

### Objective
Add deterministic tuple composition contract and provenance artifact.

### Implemented
Added:
- `virtual_shaping_lab/ui/contracts/arrangement_task_agent_composition.py`
- `tests/test_v3_arrangement_task_agent_composition.py`
- `tests/test_v3_arrangement_task_agent_provenance.py`

Updated:
- `virtual_shaping_lab/ui/contracts/__init__.py`

Changes:
- added deterministic tuple composition entrypoint:
  - `compose_arrangement_task_agent_to_operator_subset(...)`
- added preset compatibility wrapper:
  - `compose_from_preset_reference(...)`
- added composition provenance with:
  - arrangement ID
  - phenomenon/task implementation ID
  - agent bundle ID
  - protocol family
  - axis-to-slot contribution map
  - deterministic composition hash
- added machine-readable composition error codes (`COMP_E_*`)

---

## Slice 5 - Legality Integration and Foundation Docs

### Objective
Integrate tuple composition into legality pipeline and publish tuple foundation docs.

### Implemented
Updated:
- `virtual_shaping_lab/ui/contracts/operator_legality_engine.py`
- `tests/test_v3_operator_legality_engine.py`
- `.github/workflows/ci.yml`

Added:
- `docs/v3_arrangement_task_agent_foundation.md`

Changes:
- legality engine now supports tuple-path evaluation:
  - `evaluate_operator_legality(arrangement_id=..., phenomenon_id=..., agent_bundle_id=...)`
  - `validate_operator_legality(arrangement_id=..., phenomenon_id=..., agent_bundle_id=...)`
- added tuple-level legality code:
  - `LGL_E_TUPLE_COMPOSITION`
- tuple diagnostics now include:
  - tuple context
  - violating axis
  - composition error metadata
- added blocking CI step:
  - `Run V3 arrangement-task-agent foundation`

---

## Closeout Impact

After V3.15.0:
- arrangement/task/agent are explicit first-class contract axes
- tuple composition to operator subset is deterministic and provenance-emitting
- legality pipeline can evaluate tuple inputs and return axis-aware diagnostics
- preset compatibility remains available through thin wrapper references
- CI now blocks regressions on arrangement/task/agent contract surfaces

V3.15.0 therefore completes the tuple foundation contract phase needed for downstream runtime/authoring expansion.

---

## Validation

### Slice and Foundation Gates
Validated via:
- `tests/test_v3_arrangement_contract.py`
- `tests/test_v3_task_registry.py`
- `tests/test_v3_agent_bundle_registry.py`
- `tests/test_v3_agent_bundle_declarative_contract.py`
- `tests/test_v3_arrangement_task_agent_composition.py`
- `tests/test_v3_arrangement_task_agent_provenance.py`
- `tests/test_v3_operator_legality_engine.py`

### CI-Facing Contract Checks
Validated by assertions that:
- arrangement/task/agent registries remain schema-valid and registry-driven
- tuple composition is deterministic and rejects invalid tuples with machine-readable codes
- provenance artifact shape and hash behavior are stable
- legality engine surfaces tuple context and violating axis for tuple-path failures

---

## Net State After V3.15.0

- arrangement, task, and agent bundle registries are implemented and exported
- tuple composition contract and provenance artifact are in place
- tuple-path legality integration is active with `LGL_E_TUPLE_COMPOSITION` diagnostics
- blocking CI bucket coverage exists for the arrangement-task-agent foundation

V3.15.0 establishes the contract baseline for tuple-driven runtime and UI expansion in subsequent slices.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_v3_arrangement_contract.py`
- `python -m pytest -q tests/test_v3_task_registry.py`
- `python -m pytest -q tests/test_v3_agent_bundle_registry.py`
- `python -m pytest -q tests/test_v3_agent_bundle_declarative_contract.py`
- `python -m pytest -q tests/test_v3_arrangement_task_agent_composition.py`
- `python -m pytest -q tests/test_v3_arrangement_task_agent_provenance.py`
- `python -m pytest -q tests/test_v3_operator_legality_engine.py -k "tuple_path or TUPLE_COMPOSITION"`

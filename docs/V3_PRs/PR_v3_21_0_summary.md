# V3.21.0 Summary - Canonical Protocol Contract Ownership

## Overview
V3.21.0 establishes canonical protocol contract ownership under `vsl/protocol`, separates protocol grammar from runtime transport semantics, and adds legality-first boundary materialization with CI ownership guardrails.

Primary outcomes:
- added canonical protocol grammar ownership surface (`ProtocolSpec`) and fail-fast legality validator
- added deterministic protocol registry/preset payload and hash APIs
- added explicit grammar/runtime protocol adapter mapping and runtime aliasing
- added legality-first protocol instantiation boundary with typed failure catalog
- added blocking CI ownership bucket and protocol drift guardrail tests

This slice closes the V3.21.0 milestone for protocol contract ownership hardening.

---

## Slice 1 - Protocol Path Inventory and Ownership Matrix

### Objective
Inventory protocol-like execution paths and classify ownership/removal status using protocol-agent boundary rules.

### Implemented
Added:
- `docs/v3_21_0_legacy_protocol_path_inventory.md`

Updated:
- `V3.21.0_plan.md`

Changes:
- captured protocol-path inventory across experiment/runtime surfaces
- classified paths into `keep`, `bridge`, `delete-now`, `delete-later`
- documented ownership constraints from `agent_protocol_interaction.md`:
  - protocol owns emission/consequence/advance/stop
  - agent owns observe/predict/act/learn
  - boundary remains narrow and typed

---

## Slice 2 - Canonical Protocol Spec and Validator

### Objective
Define one canonical symbolic protocol grammar tuple and fail-fast legality checks.

### Implemented
Added:
- `virtual_shaping_lab/vsl/protocol/spec.py`
- `virtual_shaping_lab/vsl/protocol/validation.py`
- `virtual_shaping_lab/vsl/protocol/__init__.py`

Updated:
- `V3.21.0_plan.md`

Changes:
- introduced canonical declarative protocol grammar:
  - `ProtocolSpec`
- added deterministic identity helpers:
  - `to_dict()`
  - `from_dict(...)`
  - `to_json()`
  - `stable_hash()`
- added fail-fast legality validator:
  - `ProtocolSpecValidationError`
  - `validate_protocol_spec(...)`

---

## Slice 3 - Registry, Presets, and Grammar/Runtime Adapter Split

### Objective
Add deterministic protocol registry/preset surfaces and explicit grammar/runtime adapter separation.

### Implemented
Added:
- `virtual_shaping_lab/vsl/protocol/registry.py`
- `virtual_shaping_lab/vsl/protocol/presets.py`
- `virtual_shaping_lab/vsl/protocol/adapters.py`

Updated:
- `virtual_shaping_lab/vsl/protocol/__init__.py`
- `virtual_shaping_lab/vsl/spec/contracts.py`
- `virtual_shaping_lab/vsl/spec/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `V3.21.0_plan.md`

Changes:
- added deterministic registry APIs:
  - `slot_registries()`
  - `compatibility_matrix()`
  - `protocol_registry_payload()`
  - `protocol_registry_hash()`
- added deterministic preset APIs:
  - `expand_protocol_preset(...)`
  - `protocol_preset_payload(...)`
  - `protocol_preset_hash(...)`
- added adapter boundary APIs:
  - `grammar_to_runtime_protocol_config(...)`
  - `runtime_to_grammar_protocol_spec(...)`
- added runtime transport alias:
  - `RuntimeProtocolConfig = ProtocolSpec` (runtime contract alias in `vsl.spec.contracts`)

---

## Slice 4 - Legality-First Instantiation Boundary

### Objective
Add legality-first protocol materialization boundary from grammar tuples to typed executable/runtime contracts.

### Implemented
Added:
- `virtual_shaping_lab/vsl/protocol/instantiate.py`

Updated:
- `virtual_shaping_lab/vsl/protocol/__init__.py`
- `virtual_shaping_lab/vsl/__init__.py`
- `V3.21.0_plan.md`

Changes:
- added machine-readable failure catalog:
  - `PROTO_INSTANTIATION_FAILURES`
- added typed error and artifacts:
  - `ProtocolInstantiationError`
  - `ProtocolOperatorHandle`
  - `ProtocolInstantiationArtifact`
- added instantiation APIs:
  - `instantiate_protocol_contracts(...)`
  - `instantiate_protocol_from_boundary(...)`

---

## Slice 5 - Ownership Guardrails and CI Bucket

### Objective
Add protocol ownership tests and blocking CI guardrail bucket.

### Implemented
Added:
- `tests/test_v3_protocol_grammar_spec.py`
- `tests/test_v3_protocol_validator.py`
- `tests/test_v3_protocol_registry.py`
- `tests/test_v3_protocol_presets.py`
- `tests/test_v3_protocol_instantiation.py`
- `tests/test_v3_protocol_contract_ownership.py`

Updated:
- `.github/workflows/ci.yml`
- `virtual_shaping_lab/vsl/protocol/validation.py`
- `V3.21.0_plan.md`

Changes:
- added blocking CI step:
  - `Run V3.21.0 protocol contract ownership`
- CI bucket enforces:
  - protocol grammar legality and deterministic identity
  - registry/preset payload/hash stability
  - legality-first instantiation behavior
  - canonical-vs-runtime ownership separation and runtime-import boundaries
- tightened validator check ordering so specific operant/action-space mismatch surfaces first:
  - `PROTO_E_OPERANT_REQUIRES_ACTION_SPACE`

---

## Closeout Impact

After V3.21.0:
- protocol composition now has one canonical symbolic owner in `vsl/protocol/spec.py`
- runtime protocol transport is explicitly adapter-bound and alias-scoped
- protocol instantiation is legality-first with typed failure catalog
- CI blocks protocol ownership drift and boundary regressions

V3.21.0 establishes the hardened protocol contract baseline required for protocol runtime seam integration work in V3.21.5+.

---

## Validation

### Slice and Contract Gates
Validated via:
- `tests/test_v3_protocol_grammar_spec.py`
- `tests/test_v3_protocol_validator.py`
- `tests/test_v3_protocol_registry.py`
- `tests/test_v3_protocol_presets.py`
- `tests/test_v3_protocol_instantiation.py`
- `tests/test_v3_protocol_contract_ownership.py`

### CI-Facing Contract Checks
Validated by assertions that:
- canonical protocol grammar and runtime transport ownership remain separated
- protocol validation/registry/preset semantics remain deterministic
- protocol boundary instantiation remains legality-first and typed
- runtime import boundaries for protocol contracts remain explicit and narrow

---

## Net State After V3.21.0

- canonical protocol ownership, validator, registry, presets, adapters, and instantiation boundary are in place
- runtime protocol transport aliasing and adapter split are explicit
- blocking CI bucket is active for V3.21.0 protocol contract hardening
- protocol-agent ownership boundaries remain aligned with `agent_protocol_interaction.md`

V3.21.0 therefore completes the protocol contract ownership phase of the V3.21 line.

## Validation Commands

Targeted gates for local/CI execution:
- `python -m pytest -q tests/test_v3_protocol_grammar_spec.py tests/test_v3_protocol_validator.py`
- `python -m pytest -q tests/test_v3_protocol_registry.py tests/test_v3_protocol_presets.py`
- `python -m pytest -q tests/test_v3_protocol_instantiation.py tests/test_v3_protocol_contract_ownership.py`

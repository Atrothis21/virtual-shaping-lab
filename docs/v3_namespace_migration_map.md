# V3 Namespace Migration Map (Slice 1)

This is the published migration map for V3.9.0 namespace reshape and public API stabilization.

Policy:
- Alias warning window: `V3.9.0` through `V3.9.2`
- Hard removal release target: `V3.10.0`
- Facade parity required during alias window

## Module Migration Table

| Legacy Import Path | Target Import Path | Warning Window | Removal Release | Release Owner | Notes |
|---|---|---|---|---|---|
| `virtual_shaping_lab.vsl.operator.pipeline` | `virtual_shaping_lab.vsl.rollout.operator_pipeline` | `V3.9.0-V3.9.2` | `V3.10.0` | Core Runtime | Operator pipeline semantics move under rollout ownership. |
| `virtual_shaping_lab.vsl.operator` | `virtual_shaping_lab.vsl.rollout.operator_pipeline` | `V3.9.0-V3.9.2` | `V3.10.0` | Core Runtime | Preserve legacy stage-key/public-type access through alias window. |
| `virtual_shaping_lab.vsl.rollout.records` | `virtual_shaping_lab.vsl.records.adapters.rollout_records` | `V3.9.0-V3.9.2` | `V3.10.0` | Records | Move rollout record transforms under records package. |
| `virtual_shaping_lab.vsl.rollout.replay` | `virtual_shaping_lab.vsl.rollout.replay_harness` | `V3.9.0-V3.9.2` | `V3.10.0` | Core Runtime | Normalize replay entrypoint naming. |
| `virtual_shaping_lab.vsl.environment.harness` | `virtual_shaping_lab.vsl.rollout.harness` | `V3.9.0-V3.9.2` | `V3.10.0` | Core Runtime | Harness ownership consolidates with rollout execution surface. |
| `virtual_shaping_lab.vsl.environment.episode` | `virtual_shaping_lab.vsl.rollout.episode` | `V3.9.0-V3.9.2` | `V3.10.0` | Core Runtime | Episode contracts remain behaviorally stable. |
| `virtual_shaping_lab.vsl.environment.trial_state` | `virtual_shaping_lab.vsl.rollout.trial_state` | `V3.9.0-V3.9.2` | `V3.10.0` | Core Runtime | TrialState remains canonical; path changes only. |
| `virtual_shaping_lab.vsl.spec.binding` | `virtual_shaping_lab.vsl.spec.bindings` | `V3.9.0-V3.9.2` | `V3.10.0` | API/Contracts | Pluralized module naming for consistency. |
| `virtual_shaping_lab.vsl.spec.models` | `virtual_shaping_lab.vsl.spec.contracts` | `V3.9.0-V3.9.2` | `V3.10.0` | API/Contracts | Keep schema model payloads unchanged. |
| `virtual_shaping_lab.vsl.agent.learning.boundary` | `virtual_shaping_lab.vsl.agent.learning.resolve` | `V3.9.0-V3.9.2` | `V3.10.0` | Learning | Rename to explicit role-based module. |
| `virtual_shaping_lab.vsl.agent.learning.validator` | `virtual_shaping_lab.vsl.agent.learning.validation` | `V3.9.0-V3.9.2` | `V3.10.0` | Learning | Validation error codes remain unchanged. |
| `virtual_shaping_lab.vsl.agent.representation.temporal` | `virtual_shaping_lab.vsl.agent.representation.temporal_basis` | `V3.9.0-V3.9.2` | `V3.10.0` | Representation | Temporal-basis naming aligned with glossary. |
| `virtual_shaping_lab.vsl.records.types` | `virtual_shaping_lab.vsl.records.schema` | `V3.9.0-V3.9.2` | `V3.10.0` | Records | Keep rollout record schema version contract stable. |
| `virtual_shaping_lab.vsl.registry.phenomenon_registry` | `virtual_shaping_lab.vsl.registry.phenomena` | `V3.9.0-V3.9.2` | `V3.10.0` | Registry | Preserve fixture matrix and hash payload parity. |

## Root Ownership Alignment

Final V3.9 ownership roots:
- `vsl/spec/`
- `vsl/program/`
- `vsl/environment/`
- `vsl/agent/representation/`
- `vsl/agent/learning/`
- `vsl/agent/policy/`
- `vsl/rollout/`
- `vsl/records/`
- `vsl/analysis/`
- `vsl/registry/`

## Facade Requirements

During alias window:
- `virtual_shaping_lab.vsl` public exports must remain parity-compatible.
- Alias imports must emit deprecation warnings with:
  - old path
  - new path
  - removal release (`V3.10.0`)

At hard removal:
- aliases removed per table
- internal legacy imports must be zero
- public facade docs updated to post-removal namespace only

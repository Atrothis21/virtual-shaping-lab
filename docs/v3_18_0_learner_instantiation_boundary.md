# V3.18.0 Learner Instantiation Boundary

## Boundary API
- `instantiate_learner_contracts(...)`
- `instantiate_learner_from_boundary(...)`

Defined in:
- `virtual_shaping_lab/vsl/agent/learning/instantiate.py`

## Contract
- Input must be canonical learner grammar (`LearnerSpec`) or equivalent object payload.
- Legality is enforced before any materialization output is emitted.
- Output is a typed `LearnerInstantiationArtifact` containing:
  - canonical learner spec
  - runtime transport config
  - typed operator handles for predictor/error/updater/policy
  - typed placeholders for optional operators:
    - `NullAttentionOperator` for fixed/no-op attention
    - `NullTraceOperator` for no-trace path

## Failure Mode Catalog
- `INST_E_INVALID_SPEC_INPUT`
- `INST_E_LEGALITY`
- `INST_E_BOUNDARY_RESOLUTION`


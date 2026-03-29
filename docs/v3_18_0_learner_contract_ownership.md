# V3.18.0 Learner Contract Ownership

## Canonical Ownership
- Canonical learner composition contract: `virtual_shaping_lab.vsl.agent.learning.spec.LearnerSpec`
- Runtime transport learner contract: `virtual_shaping_lab.vsl.spec.contracts.LearnerSpec` (`RuntimeLearnerConfig` alias)

## Why
- Composition legality, preset expansion, and tuple semantics belong with learner grammar.
- Runtime transport should carry executable runtime-facing fields (`rule`, `params`, attention transport fields) without redefining grammar semantics.

## Adapter Boundary
- `grammar_to_runtime_learner_config(...)`
- `runtime_to_grammar_learner_spec(...)`

Defined in:
- `virtual_shaping_lab/vsl/agent/learning/adapters.py`

## Policy
- New learner composition logic must be added only in `vsl/agent/learning`.
- Runtime modules must consume canonical composition via adapters instead of re-deriving tuple semantics.

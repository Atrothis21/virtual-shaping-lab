# V3 Glossary (Canonical)

This is the canonical glossary for V3 planning and implementation documents.

All V3 docs should reference this file instead of redefining terms locally.

## Operator Glossary

| Symbol | Meaning | Primary Owner | Target Package/Module Family |
|---|---|---|---|
| Phi | representation / encoding | Representation | `vsl/agent/representation/*` |
| Ctx | context modulation | Representation | `vsl/agent/representation/context/*` |
| Sim | similarity / generalization | Representation | `vsl/agent/representation/similarity/*` |
| Trace | temporal credit / eligibility | Learner | `vsl/agent/learning/traces/*` |
| Pred | prediction operator | Learner | `vsl/agent/learning/predictors/*` |
| Err | error computation | Learner | `vsl/agent/learning/errors/*` |
| Attn | attention / associability | Learner | `vsl/agent/learning/attention/*` |
| Update | plasticity / update rule | Learner | `vsl/agent/learning/updaters/*` |
| Policy | action selection | Policy / Agent Control | `vsl/agent/policy/*` |
| Env | environment / contingency dynamics | Environment | `vsl/environment/*` |
| Measure | measurement / readout | Records + Analysis | `vsl/records/*`, `vsl/analysis/*` |

## Notation Rule

- use ASCII names in code and implementation docs
- allow symbolic notation only in conceptual docs

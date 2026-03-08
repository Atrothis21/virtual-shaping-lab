# Mathematical Structure of the VSL Engine

Your plan builds something slightly more general than a single function from stimulus space to response space. It builds a **composed dynamical operator** that induces such a mapping.

---

## 1) The Classic Behavioral Formalization

In the simplest mathematical view, a behavioral system is:

`F: S -> R`

Where:
- `S` = stimulus space
- `R` = response space

This is the classical stimulus -> response formulation.

But real learning systems are not static functions; they evolve over time.

---

## 2) What Your Architecture Actually Defines

Your plan decomposes the system into objects with formal mappings such as:

- `ContextMap: O x K -> O_c`
- `SimilarityKernel: X x X -> R`
- `SalienceOperator: X -> X`
- `TemporalBasis: T -> R^{d_t}`
- `PredictionErrorRule: (...) -> delta_t`
- `AttentionMechanism: (A_t, x_t, r_t, y_hat_t, cuewise_contributions) -> A_{t+1}`
- `Policy: (x_t, theta_t, A) -> Delta(A)`

These compose into:

`representation -> learning -> control`

---

## 3) The Mathematical Object Your Plan Creates

The system is not just:

`F: S -> R`

Instead it is:

`F_theta: S -> R`

where `theta` evolves over time.

More formally:

Representation:
`x_t = R(o_t, k_t, t)`

Learning:
`theta_{t+1} = theta_t + L(x_t, r_t, theta_t, A_t)`

Control:
`a_t ~ pi(a | x_t, theta_t)`

So the engine is a **stateful operator**:

`F: (S_t, theta_t) -> (R_t, theta_{t+1})`

This is a dynamical system, not just a static function.

---

## 4) How the Seven Mechanisms Fit

Each mechanism contributes to that dynamical operator.

- Context: stimulus partition operator
- Similarity: kernel over stimulus space
- Salience: linear transform on features
- Time: temporal embedding
- Prediction error: residual functional
- Attention: stateful plasticity modulation operator with `A_t \in [0,1]^n`
- Policy: stochastic decision kernel

Together they transform:

`(o_t, theta_t) -> (a_t, theta_{t+1})`

---

## 5) The Composed Behavioral Operator

The VSL engine is:

`F = pi o L o R`

Where:

Representation operator:
`R = T o Sigma o S o C`

Learning operator:
`L(x_t, theta_t, A_t) = theta_t + beta * (A_t \odot x_t) * delta_t`

Equivalent diagonal-operator form:
`L(x_t, theta_t, A_t) = theta_t + beta * D(A_t) * x_t * delta_t`

Attention state update (inside learning):
`A_{t+1} = G(A_t, x_t, r_t, y_hat_t, cuewise_contributions)`

Control operator:
`pi: (x_t, theta_t) -> Delta(A)`

---

## 6) Conceptual Meaning

The system represents a **behavioral dynamical system**, not a simple `S -> R` function.

It models:

`Stimuli_t -> Internal State_t -> Response_t`

while updating internal state over time.

---

## 7) The Induced Stimulus -> Response Mapping

If learning is frozen:

`theta = constant`

then the system collapses to a pure function:

`F_theta: S -> R`

So your architecture does contain the stimulus -> response mapping, but as a special case inside a larger learning system.

---

## 8) Best Formal Description of the Engine

Most precise statement:

**The VSL defines a parameterized dynamical operator over stimulus space whose induced policy produces a mapping from stimuli to responses.**

Mathematically:

`(o_t, theta_t) --F--> (a_t, theta_{t+1})`

---

## 9) Why This Formulation Is Correct

This stateful form matches modern learning models, including:
- reinforcement learning
- associative learning
- predictive coding
- neural networks

They all describe stateful transformations, not static mappings.

---

## 10) Key Takeaway

Your plan does represent a mathematical object that transforms stimulus space into response space. More precisely, it represents:

**a composed dynamical operator that learns the stimulus -> response mapping.**

That is exactly what a behavioral simulator should be.

If useful, a further extension is to show that the seven mechanisms correspond closely to a minimal operator basis for much of the associative learning literature.

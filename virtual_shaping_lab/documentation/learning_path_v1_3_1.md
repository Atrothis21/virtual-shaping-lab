# VSL Learning Path (v1.3.1)

This path is designed for new users to learn the engine through presets, then transition to Builder.

## 1. Baseline Foundations

1. `Acquisition`
2. `Extinction`
3. `Differential Acquisition`

What to learn:
- Phase sequencing basics
- Prediction growth and reduction
- CS+ vs CS- separation

Builder follow-up:
- Modify `alpha`, trial counts, and stimulus identity.

## 2. Salience and Cue Competition

1. `Compound Acquisition`
2. `Blocking`
3. `Overshadowing`
4. `Overexpectation`
5. `Conditioned Inhibition`

What to learn:
- Cue competition and weighting
- Primary vs secondary cue influence
- Inhibitory structures

Builder follow-up:
- Sweep salience values per cue.
- Compare compound behavior under different acquisition lengths.

## 3. Similarity and Generalization

1. `Differential Acquisition` (with similarity enabled in Builder)

What to learn:
- How representational overlap changes discrimination and transfer

Builder follow-up:
- Enable similarity matrix and vary off-diagonal values.

## 4. Context and Retrieval

1. `ABA Renewal`
2. `ABC Renewal`
3. `AAB Renewal`
4. `Rapid Reacquisition`
5. `Occasion Setting`

What to learn:
- Context-dependent retrieval and recovery effects
- Explicit context shifts vs inferred context toggles

Builder follow-up:
- Toggle context inference and compare against explicit context-only runs.

## 5. Operant Decision Learning

1. `Operant Conditioning`
2. `Matching Law`

What to learn:
- Action-value adaptation under schedules
- Choice allocation under concurrent reinforcement

Builder follow-up:
- Alter schedule parameters and inspect action allocation changes.

## Teaching Mode Rules

- Presets run in mechanism-focus mode by default.
- Non-focus mechanisms are held neutral unless user enables `Unlock all mechanisms`.
- Preset pages include:
  - Teaching panel
  - Previous/next preset navigation
  - `Open In Builder With This Payload` handoff

# Virtual Shaping Lab Model Card (v1.3)

## Release Scope

v1.3 extends core Pavlovian modeling with four orthogonal mechanisms:

- `salience`: representation-level cue strength scaling
- `attention`: learner-level alpha modulation by cue label
- `similarity`: representation-level activation spread via similarity matrix
- `context_inference`: heuristic latent context assignment across phases

Baseline invariance target:

- `salience=1`, `attention=1`, identity/no similarity spread, context inference disabled
- expected behavior matches pre-extension defaults

## Mechanism Placement

- Salience is applied during representation encoding.
- Attention is applied by learner update logic using original cue identities.
- Similarity spreads cue activation in encoded state vectors.
- Context inference is applied during assembly as forward-only phase labeling.

## Supported Behavioral Phenomena (Validated)

Default phenomenon baseline suite:

- `tests/test_behavioral_phenomena_defaults.py`

Mechanism-specific variant suites:

- `tests/test_behavioral_salience_variants.py`
- `tests/test_behavioral_attention_variants.py`
- `tests/test_behavioral_similarity_variants.py`
- `tests/test_behavioral_context_variants.py`

## Current Limits

- Context inference is heuristic (`A/B/C` assignment), not latent-cause inference.
- Similarity matrix is explicit/static; no adaptive similarity learning.
- Attention is explicit/static; no learned attentional dynamics.
- Validation targets directional behavioral signatures, not fitted quantitative datasets.

## Recommended Verification Command

```bash
python -m pytest -q \
  tests/test_behavioral_phenomena_defaults.py \
  tests/test_behavioral_salience_variants.py \
  tests/test_behavioral_attention_variants.py \
  tests/test_behavioral_similarity_variants.py \
  tests/test_behavioral_context_variants.py
```

# Tests

This test suite covers:
- Core unit tests (config parsing, factories, helpers)
- Phase smoke tests
- Full payload regression tests for presets
- Behavioral phenomenon defaults baseline (`test_behavioral_phenomena_defaults.py`)

## Running

```bash
pip install -r virtual_shaping_lab/requirements.txt
pip install -r requirements-dev.txt
pytest
```

## Full payload regression

The full payload suite validates:
1. Schema validation
2. Experiment assembly
3. Runtime execution
4. Report generation

It uses `tests/preset_payloads.py` to mirror preset defaults.

## 1.3 Baseline Lock

The `1.3.a` baseline checkpoint is the default-parameter behavioral suite:

- `tests/test_behavioral_phenomena_defaults.py`

This suite is the regression anchor for cognitive-extension work. During 1.3:

- keep this suite passing as-is while adding mechanism-specific variants
- preserve baseline invariance when mechanisms are effectively disabled

## 1.3 Cognitive Extension Variant Suites

Mechanism-specific behavioral validations:

- `tests/test_behavioral_salience_variants.py`
- `tests/test_behavioral_attention_variants.py`
- `tests/test_behavioral_similarity_variants.py`
- `tests/test_behavioral_context_variants.py`

Recommended v1.3 verification command:

```bash
python -m pytest -q \
  tests/test_behavioral_phenomena_defaults.py \
  tests/test_behavioral_salience_variants.py \
  tests/test_behavioral_attention_variants.py \
  tests/test_behavioral_similarity_variants.py \
  tests/test_behavioral_context_variants.py
```

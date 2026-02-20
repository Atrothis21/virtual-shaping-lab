# Tests

This test suite covers:
- Core unit tests (config parsing, factories, helpers)
- Phase smoke tests
- Full payload regression tests for presets

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

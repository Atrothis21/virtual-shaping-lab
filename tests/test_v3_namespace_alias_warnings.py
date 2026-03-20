from __future__ import annotations

import importlib
import warnings

import pytest


ALIAS_MAP = [
    ("virtual_shaping_lab.vsl.operator.pipeline", "virtual_shaping_lab.vsl.rollout.operator_pipeline"),
    ("virtual_shaping_lab.vsl.rollout.records", "virtual_shaping_lab.vsl.records.adapters.rollout_records"),
    ("virtual_shaping_lab.vsl.rollout.replay", "virtual_shaping_lab.vsl.rollout.replay_harness"),
    ("virtual_shaping_lab.vsl.environment.harness", "virtual_shaping_lab.vsl.rollout.harness"),
    ("virtual_shaping_lab.vsl.environment.episode", "virtual_shaping_lab.vsl.rollout.episode"),
    ("virtual_shaping_lab.vsl.environment.trial_state", "virtual_shaping_lab.vsl.rollout.trial_state"),
    ("virtual_shaping_lab.vsl.spec.binding", "virtual_shaping_lab.vsl.spec.bindings"),
    ("virtual_shaping_lab.vsl.spec.models", "virtual_shaping_lab.vsl.spec.contracts"),
    ("virtual_shaping_lab.vsl.agent.learning.boundary", "virtual_shaping_lab.vsl.agent.learning.resolve"),
    ("virtual_shaping_lab.vsl.agent.learning.validator", "virtual_shaping_lab.vsl.agent.learning.validation"),
    ("virtual_shaping_lab.vsl.agent.representation.temporal", "virtual_shaping_lab.vsl.agent.representation.temporal_basis"),
    ("virtual_shaping_lab.vsl.records.types", "virtual_shaping_lab.vsl.records.schema"),
    ("virtual_shaping_lab.vsl.registry.phenomenon_registry", "virtual_shaping_lab.vsl.registry.phenomena"),
]


@pytest.mark.parametrize("legacy_path,new_path", ALIAS_MAP)
def test_v3_slice2_legacy_import_paths_emit_deprecation_warnings(legacy_path: str, new_path: str):
    module = importlib.import_module(legacy_path)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        importlib.reload(module)
    messages = [str(item.message) for item in caught if issubclass(item.category, DeprecationWarning)]
    assert any(legacy_path in msg for msg in messages)
    assert any(new_path in msg for msg in messages)
    assert any("V3.10.0" in msg for msg in messages)


@pytest.mark.parametrize("legacy_path,new_path", ALIAS_MAP)
def test_v3_slice2_new_namespace_alias_paths_import_without_deprecation_warning(legacy_path: str, new_path: str):
    module = importlib.import_module(new_path)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        importlib.reload(module)
    messages = [str(item.message) for item in caught if issubclass(item.category, DeprecationWarning)]
    assert not any(legacy_path in msg for msg in messages)

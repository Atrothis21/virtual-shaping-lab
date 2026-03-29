from __future__ import annotations

import importlib

import pytest


REMOVED_IMPORT_PATHS = [
    "virtual_shaping_lab.vsl.operator",
    "virtual_shaping_lab.vsl.operator.pipeline",
    "virtual_shaping_lab.vsl.rollout.records",
    "virtual_shaping_lab.vsl.rollout.replay",
    "virtual_shaping_lab.vsl.environment.harness",
    "virtual_shaping_lab.vsl.environment.episode",
    "virtual_shaping_lab.vsl.environment.trial_state",
    "virtual_shaping_lab.vsl.spec.binding",
    "virtual_shaping_lab.vsl.spec.models",
    "virtual_shaping_lab.vsl.agent.learning.boundary",
    "virtual_shaping_lab.vsl.agent.learning.validator",
    "virtual_shaping_lab.vsl.agent.learning.runtime_contracts",
    "virtual_shaping_lab.vsl.agent.representation.temporal",
    "virtual_shaping_lab.vsl.records.types",
    "virtual_shaping_lab.vsl.registry.phenomenon_registry",
]


@pytest.mark.parametrize("path", REMOVED_IMPORT_PATHS)
def test_v3_slice4_removed_legacy_import_paths_fail_fast(path: str):
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(path)

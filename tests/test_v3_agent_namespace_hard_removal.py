from __future__ import annotations

import importlib

import pytest


REMOVED_IMPORT_PATHS = [
    "virtual_shaping_lab.vsl.agent.runtime",
    "virtual_shaping_lab.vsl.agent.boundary",
    "virtual_shaping_lab.vsl.agent.execution",
    "virtual_shaping_lab.vsl.agent.protocol_loop",
]


@pytest.mark.parametrize("path", REMOVED_IMPORT_PATHS)
def test_v3_20_15_removed_legacy_agent_import_paths_fail_fast(path: str):
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(path)

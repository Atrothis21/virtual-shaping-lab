from __future__ import annotations

import importlib

import pytest


REMOVED_IMPORT_PATHS = [
    "virtual_shaping_lab.vsl.protocol.runtime",
    "virtual_shaping_lab.vsl.protocol.execution",
    "virtual_shaping_lab.vsl.protocol.phase_loop",
    "virtual_shaping_lab.vsl.protocol.boundary",
]


@pytest.mark.parametrize("path", REMOVED_IMPORT_PATHS)
def test_v3_21_15_removed_legacy_protocol_import_paths_fail_fast(path: str):
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(path)

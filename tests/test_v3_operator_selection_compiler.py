from __future__ import annotations

import copy

import pytest

from ui.contracts.operator_selection_compiler import (
    OperatorSelectionCompilerError,
    compile_operator_selection_artifact,
    stable_selection_compile_hash,
    stable_selection_compile_json,
)
from ui.contracts.operator_subset_contract import PRESET_DEFINITION_TEMPLATE


def _preset() -> dict:
    return copy.deepcopy(PRESET_DEFINITION_TEMPLATE)


def test_selection_compiler_is_deterministic():
    payload = _preset()
    reordered = {
        "description": payload["description"],
        "id": payload["id"],
        "label": payload["label"],
        "operator_subset": {
            "m": payload["operator_subset"]["m"],
            "omega": payload["operator_subset"]["omega"],
            "w": payload["operator_subset"]["w"],
            "delta": payload["operator_subset"]["delta"],
            "p": payload["operator_subset"]["p"],
            "phi": payload["operator_subset"]["phi"],
        },
        "defaults": dict(payload["defaults"]),
        "locked": list(payload["locked"]),
        "optional": list(reversed(payload["optional"])),
    }
    assert stable_selection_compile_json(payload) == stable_selection_compile_json(reordered)
    assert stable_selection_compile_hash(payload) == stable_selection_compile_hash(reordered)


def test_selection_compiler_hash_parity_across_repeated_runs():
    payload = _preset()
    first = stable_selection_compile_hash(payload)
    for _ in range(20):
        assert stable_selection_compile_hash(payload) == first


def test_selection_compiler_normalizes_defaulted_and_disabled_slots():
    payload = _preset()
    payload["defaults"]["pi"] = "none"
    artifact = compile_operator_selection_artifact(payload)
    assert artifact["normalized_slots"]["pi"]["source"] == "default"
    assert artifact["normalized_slots"]["pi"]["effective_selection_ids"] == ["none"]
    assert artifact["normalized_slots"]["c"]["source"] == "disabled"
    assert artifact["normalized_slots"]["c"]["effective_selection_ids"] == []
    assert artifact["normalized_slots"]["c"]["disabled"] is True
    assert artifact["frozen"] is True
    assert isinstance(artifact["frozen_compiled_hash"], str) and artifact["frozen_compiled_hash"]


def test_selection_compiler_rejects_unknown_hand_authored_selection():
    payload = _preset()
    payload["operator_subset"]["phi"] = "hand_authored_option"
    with pytest.raises(OperatorSelectionCompilerError, match="CMP_E_UNKNOWN_SELECTION"):
        compile_operator_selection_artifact(payload)


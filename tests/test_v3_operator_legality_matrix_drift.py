from __future__ import annotations

import json
from pathlib import Path

from ui.contracts.operator_legality_engine import (
    OPERATOR_LEGALITY_RULES_VERSION,
    get_operator_compatibility_matrix,
)


def test_legality_matrix_artifact_matches_engine_registry():
    artifact_path = Path(__file__).resolve().parents[1] / "docs" / "v3_12_5_legality_matrix.json"
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["version"] == OPERATOR_LEGALITY_RULES_VERSION
    assert payload["matrix"] == get_operator_compatibility_matrix()


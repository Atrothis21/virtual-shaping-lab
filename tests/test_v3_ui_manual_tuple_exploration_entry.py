from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_manual_tuple_exploration_entry_is_exposed_in_preset_cards():
    src = _read(JS_DIR / "app.jsx")
    assert "Explore Tuple Space" in src
    assert "entry=manual_tuple_explore" in src


def test_manual_tuple_entry_converges_to_shared_detail_flow_model():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "deriveDetailFlowStateFromManualTupleSelection(" in src
    assert "deriveUnifiedDetailFlowModel(" in src
    assert "\"manual_tuple_explore\"" in src

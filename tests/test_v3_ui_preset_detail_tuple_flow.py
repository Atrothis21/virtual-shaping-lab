from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_tuple_detail_flow_declares_single_converged_entry_modes():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "DETAIL_ENTRY_MODES" in src
    assert "\"smart_preset_prefill\"" in src
    assert "\"manual_tuple_explore\"" in src
    assert "deriveUnifiedDetailFlowModel(" in src
    assert "deriveDetailFlowStateFromSmartPresetProjection(" in src
    assert "deriveDetailFlowStateFromManualTupleSelection(" in src


def test_tuple_detail_flow_blocks_run_on_composition_error_not_compatibility_badge():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "canRunForDetailFlow(" in src
    assert "compositionError" in src
    assert "deriveCompositionErrorPanelModel(" in src
    assert "type: \"composition_error\"" in src


def test_tuple_detail_flow_uses_provenance_readability_layer():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "deriveReadableProvenanceFactors(" in src
    assert "required_operators" in src
    assert "task_implementation_id" in src
    assert "forbidden_slots" in src


def test_preset_cards_offer_manual_exploration_entry():
    src = _read(JS_DIR / "app.jsx")
    assert "entry=smart_preset_prefill" in src
    assert "entry=manual_tuple_explore" in src
    assert "Explore Tuple Space" in src

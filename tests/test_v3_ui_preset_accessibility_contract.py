from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_preset_catalog_cards_expose_non_color_semantic_labels_and_aria_copy():
    src = _read(JS_DIR / "app.jsx")
    assert "UX_STATUS_LABEL" in src
    assert "role=\"article\"" in src
    assert "aria-label={`Compatibility status:" in src
    assert "aria-label=\"Compatibility explanation from evaluator output\"" in src
    assert "aria-label=\"Compatibility guidance\"" in src
    assert "aria-label={`Open preset" in src
    assert "aria-label={`Explore tuple space for" in src


def test_tuple_detail_copy_distinguishes_compatibility_guidance_from_composition_failure():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "COMPATIBILITY_COPY_DECK" in src
    assert "COMPOSITION_ERROR_COPY" in src
    assert "deriveRunDisabledReason(" in src
    assert "deriveA11yLabels(" in src
    assert "unlikely to reproduce the standard effect, but may still yield interpretable behavior" in src
    assert "tuple composition failure" in src


def test_tuple_detail_a11y_labels_include_run_gating_reason_channel():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "compatibility_badge_label" in src
    assert "compatibility_explanation_label" in src
    assert "run_gating_reason_label" in src

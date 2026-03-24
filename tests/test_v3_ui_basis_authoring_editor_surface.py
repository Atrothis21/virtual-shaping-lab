from __future__ import annotations

from pathlib import Path


def test_acquisition_editor_emits_basis_subset_payload_shape():
    src = Path("virtual_shaping_lab/ui/js/react/acquisition_editor.jsx").read_text(encoding="utf-8")
    assert "function buildBasisAuthoringPayload" in src
    assert "operator_subset" in src
    assert "edits" in src
    assert "preset_id: \"acquisition\"" in src


def test_acquisition_editor_uses_basis_materialization_route_not_legacy_canonicalization():
    src = Path("virtual_shaping_lab/ui/js/react/acquisition_editor.jsx").read_text(encoding="utf-8")
    assert "/catalog/presets/acquisition/basis-authoring" in src
    assert "/catalog/presets/acquisition/materialize-basis" in src
    assert "toCanonicalPayload(" not in src


def test_acquisition_editor_avoids_legacy_experiment_blob_emission():
    src = Path("virtual_shaping_lab/ui/js/react/acquisition_editor.jsx").read_text(encoding="utf-8")
    assert "experiment:" not in src.split("function buildBasisAuthoringPayload", 1)[1].split("function validate", 1)[0]
    assert "learner:" not in src
    assert "representation:" not in src
    assert "context_inference" not in src


def test_acquisition_editor_phi_choices_are_registry_sourced():
    src = Path("virtual_shaping_lab/ui/js/react/acquisition_editor.jsx").read_text(encoding="utf-8")
    assert "contract?.operator_choices?.phi" in src
    assert "<option value=\"vector_elemental\">" not in src

from __future__ import annotations

from pathlib import Path


def _read(name: str) -> str:
    return Path(f"virtual_shaping_lab/ui/js/react/{name}").read_text(encoding="utf-8")


def test_acquisition_editor_emits_basis_subset_payload_shape():
    src = _read("acquisition_editor.jsx")
    assert "function buildBasisAuthoringPayload" in src
    assert "operator_subset" in src
    assert "edits" in src
    assert "preset_id: \"acquisition\"" in src


def test_acquisition_editor_uses_basis_materialization_route_not_legacy_canonicalization():
    src = _read("acquisition_editor.jsx")
    assert "/catalog/presets/acquisition/basis-authoring" in src
    assert "/catalog/presets/acquisition/materialize-basis" in src
    assert "toCanonicalPayload(" not in src


def test_acquisition_editor_avoids_legacy_experiment_blob_emission():
    src = _read("acquisition_editor.jsx")
    assert "experiment:" not in src.split("function buildBasisAuthoringPayload", 1)[1].split("function validate", 1)[0]
    assert "learner:" not in src
    assert "representation:" not in src
    assert "context_inference" not in src


def test_acquisition_editor_phi_choices_are_registry_sourced():
    src = _read("acquisition_editor.jsx")
    assert "contract?.operator_choices?.phi" in src
    assert "contract?.defaults?.editable?.learning_rule_choices" in src
    assert "<option value=\"vector_elemental\">" not in src


def test_extinction_editor_uses_basis_materialization_route_not_legacy_canonicalization():
    src = _read("extinction_editor.jsx")
    assert "function buildBasisAuthoringPayload" in src
    assert "preset_id: \"extinction\"" in src
    assert "/catalog/presets/extinction/basis-authoring" in src
    assert "/catalog/presets/extinction/materialize-basis" in src
    assert "toCanonicalPayload(" not in src
    assert "experiment:" not in src.split("function buildBasisAuthoringPayload", 1)[1].split("function validate", 1)[0]
    assert "context_inference" not in src


def test_differential_editor_uses_basis_materialization_route_not_legacy_canonicalization():
    src = _read("differential_acquisition_editor.jsx")
    assert "function buildBasisAuthoringPayload" in src
    assert "preset_id: \"differential_acquisition\"" in src
    assert "/catalog/presets/differential_acquisition/basis-authoring" in src
    assert "/catalog/presets/differential_acquisition/materialize-basis" in src
    assert "toCanonicalPayload(" not in src
    assert "experiment:" not in src.split("function buildBasisAuthoringPayload", 1)[1].split("function validate", 1)[0]
    assert "context_inference" not in src

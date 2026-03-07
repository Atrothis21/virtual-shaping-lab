from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
READ_MODELS = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "preset_read_models.js"
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_preset_read_model_module_exports_adapters_and_selectors():
    text = _read(READ_MODELS)
    assert "window.VSLReact.presetReadModels" in text
    assert "adaptPhenomenonSpecToPresetViewModel" in text
    assert "selectPresetCatalogReadModel" in text
    assert "filterPresetViewModels" in text
    assert "sortPresetViewModels" in text
    assert "selectPresetFromReadModels" in text


def test_index_app_consumes_read_models_not_raw_catalog_shapes():
    text = _read(INDEX_APP)
    assert "window.VSLReact.presetReadModels" in text
    assert "selectPresetCatalogReadModel(catalogState)" in text
    assert "filterPresetViewModels(viewModel.items, searchQuery, runModeFilter)" in text
    assert "sortPresetViewModels(filtered, sortBy)" in text
    assert "extensions.phenomena" not in text


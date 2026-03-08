from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORM_SCHEMA = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "builder_form_schema.js"
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
BUILDER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "builder_route.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_builder_form_schema_module_exposes_adapter_contract():
    text = _read(FORM_SCHEMA)
    assert "BUILDER_SECTION_SCHEMA" in text
    assert "getBuilderSectionSchema" in text
    assert "buildBuilderSectionViewModels" in text
    assert "toDraftPatch" in text
    assert "constraintBehaviorByField" in text
    assert "VSLReact.builderFormSchema" in text


def test_builder_route_uses_schema_adapter_not_hardcoded_controls():
    text = _read(INDEX_APP) + _read(BUILDER_ROUTE)
    assert "builderFormSchema" in text
    assert "getBuilderSectionSchema" in text
    assert "buildBuilderSectionViewModels" in text
    assert "toDraftPatchBySchema" in text
    assert "builderSectionViewModels.map((sectionVm)" in text
    assert "renderBuilderFieldControl" in text

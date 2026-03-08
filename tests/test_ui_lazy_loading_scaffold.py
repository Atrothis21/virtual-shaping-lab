from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_APP = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "index_app.jsx"
LAZY_LOADER = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "lazy_route_loader.js"
INDEX_HTML = ROOT / "virtual_shaping_lab" / "ui" / "index.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_lazy_loader_defines_builder_dependency_contract():
    text = _read(LAZY_LOADER)
    assert "BUILDER_DEPENDENCY_PATHS" in text
    assert "/ui/js/react/builder_draft_translator.js" in text
    assert "/ui/js/react/builder_constraint_controls.js" in text
    assert "/ui/js/react/builder_form_schema.js" in text
    assert "/ui/js/react/builder_submission_guards.js" in text
    assert "ensureBuilderModulesLoaded" in text
    assert "isBuilderDependenciesReady" in text
    assert "VSLReact.lazyRouteLoader = {" in text


def test_index_app_uses_lazy_loader_for_builder_route():
    text = _read(INDEX_APP)
    assert "const lazyRouteLoaderApi = window.VSLReact.lazyRouteLoader || {};" in text
    assert "const [builderModulesState, setBuilderModulesState] = React.useState(() => ({" in text
    assert "if (activeRoute !== routes.builder.key) return;" in text
    assert "ensureBuilderModulesLoaded()" in text
    assert "Loading builder modules..." in text
    assert "Builder modules failed to load." in text


def test_index_html_loads_lazy_route_loader_before_app():
    html = _read(INDEX_HTML)
    loader_idx = html.find('/ui/js/react/lazy_route_loader.js')
    app_idx = html.find('/ui/js/react/index_app.jsx')
    assert loader_idx != -1
    assert app_idx != -1
    assert loader_idx < app_idx

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRESETS_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "presets_route.jsx"
BUILDER_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "builder_route.jsx"
RUN_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "run_route.jsx"
REPORT_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "report_route.jsx"
CATALOG_HELP_ROUTE = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react" / "routes" / "catalog_help_route.jsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_route_component_files_register_in_shared_route_registry():
    assert "VSLReact.routeContainers" in _read(PRESETS_ROUTE)
    assert "routeContainers.PresetsRouteContainer" in _read(PRESETS_ROUTE)
    assert "routeContainers.BuilderRouteContainer" in _read(BUILDER_ROUTE)
    assert "routeContainers.RunRouteContainer" in _read(RUN_ROUTE)
    assert "routeContainers.ReportRouteContainer" in _read(REPORT_ROUTE)
    assert "routeContainers.CatalogHelpRouteContainer" in _read(CATALOG_HELP_ROUTE)

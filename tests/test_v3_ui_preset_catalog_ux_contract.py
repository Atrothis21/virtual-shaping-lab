from __future__ import annotations

from pathlib import Path

from api import run as api_run


ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_preset_ux_catalog_endpoint_shape_and_states():
    body = api_run.preset_ux_catalog_api()
    assert body["registry_generated"] is True
    assert isinstance(body["contract_version"], str) and body["contract_version"]
    assert body["compatibility_states"] == [
        "success",
        "partial",
        "behaviorally_unsupported",
        "novel",
    ]
    assert isinstance(body["arrangements"], list)
    assert body["arrangements"]


def test_preset_ux_catalog_hierarchy_and_structural_invalid_suppression():
    body = api_run.preset_ux_catalog_api()
    for arrangement in body["arrangements"]:
        assert "arrangement_id" in arrangement
        assert isinstance(arrangement.get("phenomenon_groups"), list)
        for group in arrangement["phenomenon_groups"]:
            assert "phenomenon_class" in group
            assert isinstance(group.get("smart_presets"), list)
            for card in group["smart_presets"]:
                status = card["compatibility"]["status"]
                assert status != "structurally_invalid"
                assert status in {"success", "partial", "novel", "behaviorally_unsupported"}


def test_preset_ux_catalog_ordering_by_status_priority():
    body = api_run.preset_ux_catalog_api()
    order = {"success": 0, "partial": 1, "novel": 2, "behaviorally_unsupported": 3}
    for arrangement in body["arrangements"]:
        for group in arrangement["phenomenon_groups"]:
            seen = [order[item["compatibility"]["status"]] for item in group["smart_presets"]]
            assert seen == sorted(seen)


def test_preset_ux_catalog_declares_density_controls_and_degraded_fallback():
    body = api_run.preset_ux_catalog_api()
    controls = body["ui_density_controls"]
    assert isinstance(controls["collapse_sections_when_card_count_gt"], int)
    assert isinstance(controls["top_recommended_limit"], int)
    assert controls["show_more_enabled"] is True
    fallback = body["degraded_fallback"]
    assert fallback["enabled"] is True
    assert fallback["mode"] == "read_only_static_catalog"


def test_presets_app_uses_preset_ux_catalog_contract_with_degraded_fallback():
    src = _read(JS_DIR / "app.jsx")
    assert "/catalog/preset-ux" in src
    assert "degraded fallback" in src.lower()
    assert "ui_density_controls" in src
    assert "Show More" in src

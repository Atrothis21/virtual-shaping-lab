from __future__ import annotations

from pathlib import Path

from api import run as api_run


ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_tuple_selection_flow_contract_filters_arrangement_to_task_to_agent():
    catalog = api_run.tuple_authoring_catalog_api(arrangement="operant", task="acquisition")
    tasks = {entry["id"]: entry for entry in catalog["tasks"]}
    assert tasks["acquisition"]["enabled"] is True
    assert tasks["extinction"]["enabled"] is True

    agents = {entry["id"]: entry for entry in catalog["agents"]}
    assert agents["rw_operant"]["enabled"] is True
    assert agents["rw_classical"]["enabled"] is False


def test_tuple_selection_flow_js_declares_three_step_order_and_catalog_endpoint():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "STEP_ORDER" in src
    assert "\"arrangement\"" in src
    assert "\"task\"" in src
    assert "\"agent\"" in src
    assert "/catalog/tuple-authoring" in src


def test_tuple_selection_flow_has_no_hardcoded_selectable_universe():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "SELECTABLE_UNIVERSE_SOURCE" in src
    assert "registry_generated" in src
    assert "elemental" not in src
    assert "rescorla_wagner" not in src


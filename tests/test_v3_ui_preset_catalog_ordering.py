from __future__ import annotations

from api import run as api_run


def test_preset_ux_catalog_orders_cards_by_status_priority_within_each_group():
    body = api_run.preset_ux_catalog_api()
    order = {"success": 0, "partial": 1, "novel": 2, "behaviorally_unsupported": 3}
    for arrangement in body.get("arrangements", []):
        for group in arrangement.get("phenomenon_groups", []):
            statuses = [
                order[item["compatibility"]["status"]]
                for item in group.get("smart_presets", [])
            ]
            assert statuses == sorted(statuses)


def test_preset_ux_catalog_orders_by_arrangement_then_phenomenon_hierarchy_shape():
    body = api_run.preset_ux_catalog_api()
    arrangements = body.get("arrangements", [])
    assert isinstance(arrangements, list)
    for arrangement in arrangements:
        assert isinstance(arrangement.get("arrangement_id"), str)
        groups = arrangement.get("phenomenon_groups")
        assert isinstance(groups, list)
        for group in groups:
            assert isinstance(group.get("phenomenon_class"), str)
            assert isinstance(group.get("smart_presets"), list)

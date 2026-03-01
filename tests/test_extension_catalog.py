from api.extensions import ExtensionCatalog


def test_extension_catalog_snapshot_has_expected_keys():
    snap = ExtensionCatalog.snapshot()
    assert set(snap.keys()) == {
        "protocols",
        "learners",
        "policies",
        "representations",
        "report_templates",
    }


def test_extension_catalog_lists_are_sorted():
    snap = ExtensionCatalog.snapshot()
    assert snap["protocols"] == sorted(snap["protocols"])
    assert snap["learners"] == sorted(snap["learners"])
    assert snap["policies"] == sorted(snap["policies"])
    assert snap["representations"] == sorted(snap["representations"])


def test_extension_catalog_contains_known_entries():
    snap = ExtensionCatalog.snapshot()
    assert "operant_conditioning" in snap["protocols"]
    assert "rescorla_wagner" in snap["learners"]
    assert "epsilon_greedy" in snap["policies"]
    assert "vector_elemental" in snap["representations"]
    assert "operant_conditioning" in snap["report_templates"]


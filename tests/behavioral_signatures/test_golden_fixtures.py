from golden_behavior_fixtures import GOLDEN_BEHAVIOR_FIXTURES


def test_golden_fixture_registry_contains_canonical_behavior_set():
    assert {
        "acquisition_rise",
        "extinction_decline",
        "blocking_present",
        "overshadowing_salience_sensitivity",
        "generalization_gradient_decline",
        "renewal_recovery_context_switch_aba",
        "renewal_recovery_context_switch_abc",
        "fi_vs_fr_separation",
        "rapid_reacquisition_recovery",
    }.issubset(GOLDEN_BEHAVIOR_FIXTURES.keys())


def test_golden_fixture_registry_entries_have_payload_factories_and_expectations():
    for key, fixture in GOLDEN_BEHAVIOR_FIXTURES.items():
        assert fixture.key == key
        assert callable(fixture.payload_factory)
        assert isinstance(fixture.qualitative_expectation, str) and fixture.qualitative_expectation
        assert isinstance(fixture.thresholds, dict)

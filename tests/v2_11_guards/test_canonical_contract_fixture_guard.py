from preset_payloads import CONTRACT_FIXTURES


def test_contract_fixtures_are_canonical_only():
    for name, payload in CONTRACT_FIXTURES.items():
        experiment = payload.get("experiment", {})
        assert set(experiment.keys()) == {"program", "agent", "runtime"}, (
            f"{name} must expose canonical experiment ownership keys only"
        )
        assert isinstance(experiment["program"].get("phases"), list) and experiment["program"]["phases"], (
            f"{name} must include canonical program phases"
        )


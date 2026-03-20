from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.registry import (
    PHENOMENON_REGISTRY,
    SUPPORTED_CAVEAT_TIERS,
    ConstraintSpec,
    OperatorBundleSpec,
    PhenomenonRegistryEntry,
    ReadoutSpec,
    phenomenon_registry_hash,
    phenomenon_registry_payload,
    validate_phenomenon_registry,
)


def _sample_entry() -> PhenomenonRegistryEntry:
    return PhenomenonRegistryEntry(
        key="blocking",
        recipe={"protocol": "blocking", "variant": "canonical"},
        bundles=(
            OperatorBundleSpec(
                key="minimal",
                operators=("Phi", "C", "E", "A", "L", "Policy", "Reward", "Measure"),
                metadata={"claim": "minimal"},
            ),
        ),
        constraints=ConstraintSpec(
            required_operators=("E", "L"),
            forbidden_operators=(),
            metadata={"scope": "build_and_run"},
        ),
        readouts=(
            ReadoutSpec(
                key="blocked_cue_lower",
                metric="probe.blocked_cue_minus_pretrained_cue",
                metadata={"direction": "lt_zero"},
            ),
        ),
        fixture="tests/fixtures/verification/blocking_canonical.json",
        caveat_tier="minor",
        metadata={"family": "classical"},
    )


def test_v3_phenomenon_registry_entry_roundtrip():
    entry = _sample_entry()
    rebuilt = PhenomenonRegistryEntry.from_dict(entry.to_dict())
    assert rebuilt.to_dict() == entry.to_dict()


def test_v3_phenomenon_registry_entry_rejects_invalid_caveat_tier():
    with pytest.raises(ValueError, match="caveat_tier"):
        PhenomenonRegistryEntry(
            key="k",
            recipe={"protocol": "acquisition"},
            bundles=(OperatorBundleSpec(key="b", operators=("Phi",)),),
            constraints=ConstraintSpec(required_operators=("Phi",)),
            readouts=(ReadoutSpec(key="r", metric="m"),),
            fixture="tests/fixtures/verification/acquisition.json",
            caveat_tier="unknown",
        )


def test_v3_phenomenon_registry_entry_requires_non_empty_fields():
    with pytest.raises(ValueError, match="bundles"):
        PhenomenonRegistryEntry(
            key="k",
            recipe={"protocol": "acquisition"},
            bundles=(),
            constraints=ConstraintSpec(),
            readouts=(ReadoutSpec(key="r", metric="m"),),
            fixture="tests/fixtures/verification/acquisition.json",
            caveat_tier="none",
        )
    with pytest.raises(ValueError, match="readouts"):
        PhenomenonRegistryEntry(
            key="k",
            recipe={"protocol": "acquisition"},
            bundles=(OperatorBundleSpec(key="b", operators=("Phi",)),),
            constraints=ConstraintSpec(),
            readouts=(),
            fixture="tests/fixtures/verification/acquisition.json",
            caveat_tier="none",
        )


def test_v3_phenomenon_registry_payload_and_hash_are_stable():
    registry = {"blocking": _sample_entry()}
    payload = phenomenon_registry_payload(registry)
    assert payload["version"] == "3.8.0"
    assert payload["supported_caveat_tiers"] == list(SUPPORTED_CAVEAT_TIERS)
    assert set(payload["entries"].keys()) == {"blocking"}

    hashes = [phenomenon_registry_hash(registry) for _ in range(20)]
    assert len(set(hashes)) == 1


def test_v3_phenomenon_registry_rejects_key_mismatch():
    entry = _sample_entry()
    with pytest.raises(ValueError, match="key mismatch"):
        validate_phenomenon_registry({"different_key": entry})


def test_v3_phenomenon_registry_canonical_population_is_present():
    expected_keys = {
        "blocking",
        "conditioned_inhibition",
        "renewal_aba",
        "renewal_abc",
        "renewal_aab",
        "extinction",
        "rapid_reacquisition",
        "occasion_setting",
        "operant_conditioning",
        "matching_law",
        "shaping",
        "resurgence",
        "superextinction",
        "spontaneous_recovery",
    }
    assert set(PHENOMENON_REGISTRY.keys()) == expected_keys
    for key, entry in PHENOMENON_REGISTRY.items():
        assert entry.key == key
        assert entry.readouts
        assert entry.bundles
        assert entry.constraints.required_operators
        assert entry.fixture.startswith("tests/preset_payloads.py::")
        assert entry.caveat_tier in SUPPORTED_CAVEAT_TIERS

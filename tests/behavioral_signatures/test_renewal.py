from __future__ import annotations

from preset_payloads import aab_renewal_payload, aba_renewal_payload, abc_renewal_payload
from golden_behavior_fixtures import first_last_n, mean_prediction, run_fixture_records


def test_signature_aba_renewal_probe_recovers_above_extinction_tail():
    records = run_fixture_records(aba_renewal_payload())
    ext = [r for r in records if r.get("subphase_name") == "nonreinforcement"]
    probe = [r for r in records if r.get("subphase_name") == "probe"]

    assert ext, "Expected nonreinforcement records."
    assert probe, "Expected probe records."

    ext_tail = first_last_n(ext, n=10)[1]
    probe_tail = first_last_n(probe, n=10)[1]
    assert mean_prediction(probe_tail) > mean_prediction(ext_tail) + 0.2


def test_signature_abc_renewal_probe_recovers_above_extinction_tail():
    records = run_fixture_records(abc_renewal_payload())
    ext = [r for r in records if r.get("subphase_name") == "nonreinforcement"]
    probe = [r for r in records if r.get("subphase_name") == "probe"]

    assert ext, "Expected nonreinforcement records."
    assert probe, "Expected probe records."

    ext_tail = first_last_n(ext, n=10)[1]
    probe_tail = first_last_n(probe, n=10)[1]
    assert mean_prediction(probe_tail) > mean_prediction(ext_tail) + 0.1


def test_signature_aab_renewal_probe_stays_near_extinction_level():
    records = run_fixture_records(aab_renewal_payload())
    ext = [r for r in records if r.get("subphase_name") == "nonreinforcement"]
    probe = [r for r in records if r.get("subphase_name") == "probe"]

    assert ext, "Expected nonreinforcement records."
    assert probe, "Expected probe records."

    ext_tail = first_last_n(ext, n=10)[1]
    probe_tail = first_last_n(probe, n=10)[1]
    assert abs(mean_prediction(probe_tail) - mean_prediction(ext_tail)) < 0.1

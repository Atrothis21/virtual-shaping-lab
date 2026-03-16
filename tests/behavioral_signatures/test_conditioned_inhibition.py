from __future__ import annotations

from preset_payloads import conditioned_inhibition_payload
from golden_behavior_fixtures import first_last_n, mean_prediction, run_fixture_records


def test_signature_conditioned_inhibition_compound_suppresses_prediction():
    records = run_fixture_records(conditioned_inhibition_payload())
    acquisition = [r for r in records if r.get("subphase_name") == "acquisition"]
    inhibition = [r for r in records if r.get("subphase_name") == "compound_nonreinforcement"]

    assert acquisition, "Expected acquisition records."
    assert inhibition, "Expected compound nonreinforcement records."

    acq_tail = first_last_n(acquisition, n=10)[1]
    inh_tail = first_last_n(inhibition, n=10)[1]
    assert mean_prediction(inh_tail) < mean_prediction(acq_tail) - 0.4


def test_signature_conditioned_inhibition_summation_probe_below_excitor_baseline():
    records = run_fixture_records(conditioned_inhibition_payload())
    summation_acq = [r for r in records if r.get("subphase_name") == "summation_acquisition"]
    summation_probe = [r for r in records if r.get("subphase_name") == "summation_probe"]

    assert summation_acq, "Expected summation acquisition records."
    assert summation_probe, "Expected summation probe records."

    acq_tail = first_last_n(summation_acq, n=10)[1]
    probe_mean = mean_prediction(summation_probe)
    assert probe_mean < mean_prediction(acq_tail) - 0.1


def test_signature_conditioned_inhibition_retardation_starts_lower_than_initial_acquisition():
    records = run_fixture_records(conditioned_inhibition_payload())
    acquisition = [r for r in records if r.get("subphase_name") == "acquisition"]
    retardation = [r for r in records if r.get("subphase_name") == "retardation"]

    assert acquisition, "Expected acquisition records."
    assert retardation, "Expected retardation records."

    acq_head = first_last_n(acquisition, n=10)[0]
    ret_head = first_last_n(retardation, n=10)[0]
    assert mean_prediction(ret_head) < mean_prediction(acq_head) - 0.1

from __future__ import annotations

from preset_payloads import extinction_payload, rapid_reacquisition_payload
from golden_behavior_fixtures import first_last_n, head_tail, mean_prediction, run_fixture_records


def test_signature_extinction_reduces_prediction_after_acquisition():
    records = run_fixture_records(extinction_payload())
    acq = [r for r in records if r.get("subphase_name") == "acquisition"]
    ext = [r for r in records if r.get("subphase_name") == "nonreinforcement"]

    assert acq, "Expected acquisition records."
    assert ext, "Expected extinction records."

    ext_early, ext_late = head_tail(ext, ratio=0.2)
    assert mean_prediction(ext_late) < mean_prediction(ext_early) - 0.2
    assert mean_prediction(ext_late) < mean_prediction(acq[-10:]) - 0.2


def test_signature_rapid_reacquisition_exceeds_extinction_tail():
    records = run_fixture_records(rapid_reacquisition_payload())
    rewards = [float(r.get("reward", 0.0) or 0.0) for r in records]

    first_zero = next((i for i, rv in enumerate(rewards) if rv == 0.0), None)
    last_zero = next((i for i in range(len(rewards) - 1, -1, -1) if rewards[i] == 0.0), None)
    assert first_zero is not None and last_zero is not None and first_zero <= last_zero

    extinction = records[first_zero:last_zero + 1]
    reacq = records[last_zero + 1:]
    assert extinction, "Expected extinction block."
    assert reacq, "Expected reacquisition block."

    ext_tail = first_last_n(extinction, n=10)[1]
    reacq_tail = first_last_n(reacq, n=min(10, len(reacq)))[1]

    assert mean_prediction(reacq_tail) > mean_prediction(ext_tail) + 0.2
    assert mean_prediction(reacq_tail) > 0.8

from __future__ import annotations

from preset_payloads import overshadowing_payload
from golden_behavior_fixtures import cue_predictions, mean, run_fixture_records, tail


def test_signature_overshadowing_retains_higher_salience_cue_dominance():
    records = run_fixture_records(overshadowing_payload())
    tone = cue_predictions(records, cue="tone")
    noise = cue_predictions(records, cue="noise")

    assert tone, "Expected tone predictions in overshadowing records."
    assert noise, "Expected noise predictions in overshadowing records."

    tone_tail = tail(tone, n=10)
    noise_tail = tail(noise, n=10)

    # Current default overshadowing dynamics preserve ordering under salience imbalance.
    assert mean(tone_tail) >= mean(noise_tail)

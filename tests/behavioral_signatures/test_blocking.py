from __future__ import annotations

from preset_payloads import blocking_payload
from golden_behavior_fixtures import cue_predictions, mean, run_fixture_records, tail


def test_signature_blocking_retains_primary_cue_dominance():
    block_records = run_fixture_records(blocking_payload())

    tone = cue_predictions(block_records, cue="tone")
    noise = cue_predictions(block_records, cue="noise")

    assert tone, "Expected primary-cue predictions for blocking condition."
    assert noise, "Expected blocked-cue predictions for blocking condition."

    tone_tail = tail(tone, n=10)
    noise_tail = tail(noise, n=10)

    # Current default blocking dynamics preserve primary-cue dominance.
    assert mean(tone_tail) >= mean(noise_tail)

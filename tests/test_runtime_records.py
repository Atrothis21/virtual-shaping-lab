from experiment.runtime_records import finalize_record


def test_finalize_record_sets_fields():
    record = {"phase": "acquisition"}
    finalize_record(
        record,
        phase_name="Phase 1",
        protocol_phase_index=0,
        protocol_phase_name="acquisition",
    )
    assert record["phase_name"] == "Phase 1"
    assert record["subphase"] == 0
    assert record["subphase_name"] == "acquisition"

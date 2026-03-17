import pytest

from experiment.runtime_records import (
    DebugTelemetrySchemaValidator,
    FinalizationContext,
    ProtocolMetadataNormalizer,
    RecordFinalizationPipeline,
    SchemaDefaultsNormalizer,
    StrictModeValidator,
    VersionMigrator,
    finalize_record,
)


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


def test_finalize_record_applies_stable_trial_record_schema_defaults():
    record = {"phase": "acquisition", "trial": 2, "reward": 1.0}
    out = finalize_record(record, phase_name="acquisition")
    for key in (
        "phase",
        "phase_name",
        "protocol_name",
        "unit_path",
        "subphase",
        "subphase_name",
        "trial",
        "step",
        "tick",
        "t_s",
        "dt_s",
        "trial_step",
        "trial_id",
        "context",
        "stimulus",
        "stimulus_type",
        "action",
        "policy_state",
        "response",
        "reward",
        "prediction",
        "prediction_error",
        "outcome_type",
        "schedule",
        "done",
        "learning_enabled",
        "metadata",
    ):
        assert key in out
    assert out["metadata"] == {}


def test_finalize_record_derives_minimum_schema_fields_from_common_runtime_data():
    record = {
        "phase": "timed",
        "trial": 0,
        "tick": 2,
        "trial_step": 2,
        "metadata": {"policy_state": {"mode": "epsilon_greedy"}},
        "debug": {"prediction_error": -0.25, "active_features": ["tone"]},
    }
    out = finalize_record(record)

    assert out["step"] == 2
    assert out["prediction_error"] == pytest.approx(-0.25)
    assert out["policy_state"] == {"mode": "epsilon_greedy"}


def test_record_finalization_pipeline_matches_finalize_record_contract():
    pipeline = RecordFinalizationPipeline(
        normalizers=[
            VersionMigrator(),
            SchemaDefaultsNormalizer(),
            ProtocolMetadataNormalizer(),
            StrictModeValidator(),
        ]
    )
    rec = {"phase": "acquisition", "trial": 1}
    out = pipeline.finalize(
        rec,
        FinalizationContext(
            phase_name="acquisition",
            protocol_phase_index=0,
            protocol_phase_name="acquisition",
        ),
    )
    assert out["phase_name"] == "acquisition"
    assert out["subphase"] == 0
    assert out["subphase_name"] == "acquisition"
    assert "metadata" in out


def test_finalize_record_strict_mode_rejects_incomplete_tick_record():
    record = {"phase": "timed", "trial": 0, "tick": 0}
    try:
        finalize_record(record, strict_mode=True)
        assert False, "Expected strict mode to reject missing tick timing fields."
    except ValueError as exc:
        assert "requires t_s" in str(exc)


def test_finalize_record_strict_mode_rejects_non_monotonic_tick():
    record = {
        "phase": "timed",
        "trial": 0,
        "tick": 0,
        "t_s": 0.0,
        "dt_s": 0.1,
        "trial_step": 0,
        "metadata": {"prev_tick": 1, "prev_t_s": 0.2},
    }
    try:
        finalize_record(record, strict_mode=True)
        assert False, "Expected strict mode to reject non-monotonic tick metadata."
    except ValueError as exc:
        assert "tick must be monotonic" in str(exc)


def test_finalize_record_default_mode_keeps_backward_compatibility():
    record = {"phase": "timed", "trial": 0, "tick": 0}
    out = finalize_record(record)
    assert out["tick"] == 0


def test_finalize_record_version_migration_noop_for_v1_to_v1():
    record = {"phase": "acquisition", "trial": 1}
    out = finalize_record(record, from_version="v1", to_version="v1")
    assert out["phase"] == "acquisition"


def test_finalize_record_version_migration_rejects_unsupported_paths():
    record = {"phase": "acquisition", "trial": 1}
    try:
        finalize_record(record, from_version="v1", to_version="v2")
        assert False, "Expected unsupported migration path to raise."
    except ValueError as exc:
        assert "Unsupported record schema migration" in str(exc)


def test_finalize_record_accepts_valid_debug_telemetry_schema():
    rec = {
        "phase": "timed",
        "trial": 1,
        "debug": {
            "value": 0.25,
            "prediction_error": -0.1,
            "active_features": ["tone", "context:A"],
            "attention_effective": {"tone": 0.8},
            "alpha_by_stimulus": {"tone": 0.7},
            "mean_alpha": 0.7,
            "cuewise_contributions": {"tone": 0.3},
            "salience_effective": {"tone": 0.5},
        },
    }
    out = finalize_record(rec)
    assert out["debug"]["active_features"] == ["tone", "context:A"]


def test_finalize_record_rejects_invalid_debug_telemetry_schema():
    rec = {
        "phase": "timed",
        "trial": 1,
        "debug": {
            "active_features": ["tone", 42],
        },
    }
    try:
        finalize_record(rec)
        assert False, "Expected debug telemetry schema validation failure."
    except ValueError as exc:
        assert "active_features" in str(exc)


def test_debug_telemetry_schema_validator_rejects_unknown_fields():
    validator = DebugTelemetrySchemaValidator()
    rec = {"debug": {"unknown_field": 1}}
    try:
        validator.apply(rec, FinalizationContext())
        assert False, "Expected unknown debug telemetry field to fail."
    except ValueError as exc:
        assert "Unknown debug telemetry field" in str(exc)


def test_finalize_record_is_deterministic_for_identical_inputs():
    rec_a = {
        "phase": "timed",
        "trial": 2,
        "tick": 1,
        "t_s": 0.5,
        "dt_s": 0.5,
        "trial_step": 1,
        "reward": 1.0,
        "debug": {
            "value": 0.25,
            "prediction_error": 0.75,
            "active_features": ["tone"],
            "attention_effective": {"tone": 1.0},
            "alpha_by_stimulus": {"tone": 1.0},
            "mean_alpha": 1.0,
            "cuewise_contributions": {"tone": 0.25},
            "salience_effective": {"tone": 1.0},
        },
    }
    rec_b = {
        "phase": "timed",
        "trial": 2,
        "tick": 1,
        "t_s": 0.5,
        "dt_s": 0.5,
        "trial_step": 1,
        "reward": 1.0,
        "debug": {
            "value": 0.25,
            "prediction_error": 0.75,
            "active_features": ["tone"],
            "attention_effective": {"tone": 1.0},
            "alpha_by_stimulus": {"tone": 1.0},
            "mean_alpha": 1.0,
            "cuewise_contributions": {"tone": 0.25},
            "salience_effective": {"tone": 1.0},
        },
    }

    out_a = finalize_record(rec_a, phase_name="timed", protocol_phase_index=0, protocol_phase_name="timed")
    out_b = finalize_record(rec_b, phase_name="timed", protocol_phase_index=0, protocol_phase_name="timed")

    assert out_a == out_b

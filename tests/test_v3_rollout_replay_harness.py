from __future__ import annotations

from virtual_shaping_lab.vsl.environment.contracts import EnvironmentStep, EnvironmentTermination
from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment
from virtual_shaping_lab.vsl.program import compile_environment_program
from virtual_shaping_lab.vsl.records.adapters.rollout_records import step_to_rollout_record
from virtual_shaping_lab.vsl.rollout import ReplayHarness, stable_rollout_hash
from ui.contracts.operator_plan_materialization import compile_and_materialize_operator_plan
from ui.contracts.operator_subset_contract import PRESET_DEFINITION_TEMPLATE


def _compiled_fixture() -> CompiledProgramTestEnvironment:
    program = compile_environment_program(
        {
            "phases": [
                {
                    "name": "Acq",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 3, "outcome": 1.0},
                },
                {
                    "name": "Ext",
                    "protocol": "extinction",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 2, "outcome": 0.0},
                },
            ]
        }
    )
    return CompiledProgramTestEnvironment(program)


def test_v3_replay_harness_emits_rollout_records_with_identity_fields():
    records = ReplayHarness().run(_compiled_fixture(), rollout_id="rollout_A", episode_id=2, seed=11)
    assert records
    assert all(record.schema_version == "v1" for record in records)
    assert all(record.rollout_id == "rollout_A" for record in records)
    assert all(record.episode_id == 2 for record in records)


def test_v3_replay_harness_is_hash_identical_for_10_of_10_runs_under_fixed_identity_inputs():
    hashes = []
    for _ in range(10):
        records = ReplayHarness().run(_compiled_fixture(), rollout_id="rollout_A", episode_id=0, seed=17)
        hashes.append(stable_rollout_hash(records))
    assert len(set(hashes)) == 1


def test_v3_replay_harness_hash_changes_when_identity_changes():
    baseline = ReplayHarness().run(_compiled_fixture(), rollout_id="rollout_A", episode_id=0, seed=17)
    changed = ReplayHarness().run(_compiled_fixture(), rollout_id="rollout_B", episode_id=0, seed=17)
    assert stable_rollout_hash(baseline) != stable_rollout_hash(changed)


def test_v3_replay_harness_is_hash_identical_for_basis_materialized_acquisition_runs():
    materialized = compile_and_materialize_operator_plan(
        PRESET_DEFINITION_TEMPLATE,
        protocol_family="acquisition",
        stimuli_catalog=["tone", "noise"],
    )
    program = compile_environment_program(materialized["experiment"]["program"])
    env = CompiledProgramTestEnvironment(program)

    hashes = []
    for _ in range(10):
        records = ReplayHarness().run(env, rollout_id="basis_rollout_A", episode_id=3, seed=29)
        hashes.append(stable_rollout_hash(records))
    assert len(set(hashes)) == 1


def test_v3_replay_harness_is_hash_identical_for_protocol_trace_inclusive_operant_runs():
    program = compile_environment_program(
        {
            "phases": [
                {
                    "name": "Operant",
                    "protocol": "operant_conditioning",
                    "stimuli": {"cs_plus": ["lever"]},
                    "params": {"n_trials": 3, "reward": 1.0},
                }
            ]
        }
    )
    hashes = []
    for _ in range(10):
        env = CompiledProgramTestEnvironment(program)
        records = ReplayHarness().run(env, rollout_id="operant_rollout_A", episode_id=5, seed=43)
        hashes.append(stable_rollout_hash(records))
    assert len(set(hashes)) == 1


def test_v3_rollout_record_hash_is_stable_when_protocol_trace_payload_keys_are_reordered():
    step_a = EnvironmentStep(
        step_index=0,
        segment_key="seg_protocol",
        protocol="operant_conditioning",
        trial_type="operant_trial",
        trial_index=0,
        action="leverpress",
        stimulus={"lever": 1.0},
        reward=1.0,
        done=False,
        termination=EnvironmentTermination(done=False, reason="running"),
        metadata={
            "protocol": {
                "preset_name": "operant_protocol",
                "emission": {"context": "A", "available_actions": ["leverpress"], "stimulus": {"lever": 1.0}},
                "consequence": {"done": False, "reward": 1.0},
                "advance": {"phase_step": 1, "dt_s": 1.0, "t": 1},
                "stop": {"reason": None, "should_stop": False},
                "pipeline_order": ["emit", "consequence", "advance", "stop", "finalize"],
            }
        },
    )
    step_b = EnvironmentStep(
        step_index=0,
        segment_key="seg_protocol",
        protocol="operant_conditioning",
        trial_type="operant_trial",
        trial_index=0,
        action="leverpress",
        stimulus={"lever": 1.0},
        reward=1.0,
        done=False,
        termination=EnvironmentTermination(done=False, reason="running"),
        metadata={
            "protocol": {
                "pipeline_order": ["emit", "consequence", "advance", "stop", "finalize"],
                "stop": {"should_stop": False, "reason": None},
                "advance": {"t": 1, "dt_s": 1.0, "phase_step": 1},
                "consequence": {"reward": 1.0, "done": False},
                "emission": {"stimulus": {"lever": 1.0}, "available_actions": ["leverpress"], "context": "A"},
                "preset_name": "operant_protocol",
            }
        },
    )
    rec_a = step_to_rollout_record(step_a, rollout_id="r", episode_id=0)
    rec_b = step_to_rollout_record(step_b, rollout_id="r", episode_id=0)
    assert rec_a.metadata["protocol_traces"] == rec_b.metadata["protocol_traces"]
    assert rec_a.stable_hash() == rec_b.stable_hash()


def test_v3_replay_harness_with_measurement_is_hash_identical_for_10_of_10_runs_under_fixed_identity_inputs():
    hashes = []
    measurement_hashes = []
    for _ in range(10):
        env = _compiled_fixture()
        records, measurement = ReplayHarness().run_with_measurement(
            env,
            rollout_id="rollout_A",
            episode_id=0,
            seed=17,
            measurement_preset_name="learning_curve_basic",
        )
        hashes.append(stable_rollout_hash(records))
        measurement_hashes.append(
            records[0].metadata["measurement_artifact_identity"]["measurement_payload_hash"]
        )
        assert records[0].metadata["measurement_traces"]["provenance"]["measurement_payload_hash"] == measurement_hashes[-1]
        assert measurement.metadata["runtime_measurement"]["preset_name"] == "learning_curve_basic"
    assert len(set(hashes)) == 1
    assert len(set(measurement_hashes)) == 1


def test_v3_replay_harness_with_measurement_promotes_deterministic_measurement_trace_identity_references():
    env = _compiled_fixture()
    records, _measurement = ReplayHarness().run_with_measurement(
        env,
        rollout_id="rollout_A",
        episode_id=0,
        seed=17,
        measurement_preset_name="learning_curve_basic",
    )
    assert records
    for record in records:
        measurement_traces = record.metadata.get("measurement_traces")
        assert isinstance(measurement_traces, dict)
        assert isinstance(measurement_traces.get("metrics"), dict)
        assert isinstance(measurement_traces.get("figures"), list)
        assert isinstance(measurement_traces.get("summary"), dict)
        provenance = measurement_traces.get("provenance", {})
        assert isinstance(provenance, dict)
        assert provenance.get("preset_name") == "learning_curve_basic"
        assert provenance.get("hash_algorithm") == "sha256"
        assert isinstance(provenance.get("measurement_payload_hash"), str) and provenance["measurement_payload_hash"]
        assert isinstance(provenance.get("metric_keys"), list)
        assert isinstance(provenance.get("figure_count"), int)

        identity = record.metadata.get("measurement_artifact_identity")
        assert isinstance(identity, dict)
        assert identity.get("hash_algorithm") == "sha256"
        assert identity.get("preset_name") == "learning_curve_basic"
        assert identity.get("measurement_payload_hash") == provenance.get("measurement_payload_hash")


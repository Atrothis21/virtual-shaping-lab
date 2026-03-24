from __future__ import annotations

from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment
from virtual_shaping_lab.vsl.program import compile_environment_program
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


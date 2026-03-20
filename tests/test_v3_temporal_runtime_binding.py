from __future__ import annotations

from experiment.config import ExperimentConfig
from virtual_shaping_lab.vsl.spec import bind_episode_spec, bind_temporal_basis_spec


def _payload() -> dict:
    return {
        "experiment": {
            "program": {
                "phases": [
                    {
                        "name": "Phase 1",
                        "protocol": "acquisition",
                        "stimuli": {"cs_plus": ["tone"]},
                        "params": {"n_trials": 5},
                        "trials": 5,
                    }
                ]
            },
            "agent": {
                "name": "classical_agent",
                "representation": {
                    "name": "vector_elemental",
                    "params": {
                        "stimuli": ["tone"],
                        "temporal_basis": {
                            "variant": "trace",
                            "dimension": 3,
                            "enabled": True,
                            "params": {"decay": 0.8},
                        },
                    },
                },
                "learning": {"rule": "rescorla_wagner", "params": {}},
                "policy": None,
            },
            "runtime": {
                "seed": 11,
                "episode": {
                    "episode_id": 7,
                    "rollout_id": "rollout_A",
                    "horizon": {"max_steps": 9, "stop_reason": "horizon_exhausted"},
                },
            },
        },
        "report": {"preset": "acquisition"},
    }


def test_v3_slice2_bind_temporal_basis_from_representation_contract():
    representation = _payload()["experiment"]["agent"]["representation"]
    temporal = bind_temporal_basis_spec(representation)
    assert temporal.variant == "traces"
    assert temporal.enabled is True
    assert temporal.dimension == 3
    assert temporal.params.get("decay") == 0.8


def test_v3_slice2_bind_episode_spec_from_runtime_contract():
    runtime = _payload()["experiment"]["runtime"]
    episode = bind_episode_spec(runtime, default_seed=123, default_max_steps=20)
    assert episode.episode_id == 7
    assert episode.rollout_id == "rollout_A"
    assert episode.seed == 11
    assert episode.horizon.max_steps == 9
    assert episode.horizon.stop_reason == "horizon_exhausted"


def test_v3_slice2_plan_builder_binds_temporal_and_episode_specs():
    plan = ExperimentConfig.plan_from_payload(_payload())
    representation = plan.agent_spec["representation"]
    temporal = representation["params"]["temporal_basis"]
    assert temporal["variant"] == "traces"
    assert temporal["enabled"] is True
    assert temporal["dimension"] == 3

    episode = plan.runtime_spec["episode"]
    assert episode["episode_id"] == 7
    assert episode["rollout_id"] == "rollout_A"
    assert episode["seed"] == 11
    assert episode["horizon"]["max_steps"] == 9


def test_v3_slice2_plan_builder_defaults_episode_horizon_when_missing():
    payload = _payload()
    payload["experiment"]["runtime"] = {"seed": 5}
    payload["experiment"]["agent"]["representation"]["params"].pop("temporal_basis", None)
    plan = ExperimentConfig.plan_from_payload(payload)

    temporal = plan.agent_spec["representation"]["params"]["temporal_basis"]
    assert temporal["variant"] == "identity"
    assert temporal["enabled"] is False

    episode = plan.runtime_spec["episode"]
    assert episode["episode_id"] == 0
    assert episode["rollout_id"] == "rollout_0"
    assert episode["seed"] == 5
    assert episode["horizon"]["max_steps"] == 5

from __future__ import annotations

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
import numpy as np
from ui.validate_payload import validate_payload

from protocols.schedule_runtime import (
    AlwaysAvailable,
    ConstantConsequenceMapper,
    FixedIntervalAvailability,
    FixedRatioGate,
    FirstResponseGate,
    ScheduleTickInput,
    TickScheduleRuntime,
)
from preset_payloads import operant_conditioning_payload


def _run_records(payload: dict) -> list[dict]:
    validate_payload(payload)
    config = ExperimentConfig.from_payload(payload)
    units, _agent, _representation = assemble_experiment(config)

    records: list[dict] = []
    for phase_index, unit in enumerate(units):
        unit_records = Runner(unit).run()
        for rec in unit_records:
            rec["phase"] = phase_index
            finalize_record(rec, phase_name=config.phases[phase_index].name)
        records.extend(unit_records)
    return records


def _operant_payload(schedule_type: str, schedule_value: int, n_trials: int = 120) -> dict:
    payload = operant_conditioning_payload()
    payload["experiment"]["params"]["n_trials"] = n_trials
    payload["experiment"]["params"]["reward_schedule"] = {
        "type": schedule_type,
        "value": schedule_value,
    }
    return payload


def _reinforcement_rate(records: list[dict]) -> float:
    rewards = [float(r.get("reward", 0.0) or 0.0) for r in records]
    if not rewards:
        raise ValueError("No rewards found in records.")
    return sum(1.0 for r in rewards if r > 0.0) / float(len(rewards))


def test_schedule_proxy_fixed_ratio_yields_higher_reinforcement_density_than_fixed_interval():
    fr_records = _run_records(_operant_payload("fixed_ratio", 1))
    fi_records = _run_records(_operant_payload("fixed_interval", 10))

    fr_rate = _reinforcement_rate(fr_records)
    fi_rate = _reinforcement_rate(fi_records)

    # Proxy signal only: this asserts schedule-level reinforcement density under
    # current operant implementation; it is not a within-trial FI hallmark test.
    assert fr_rate > fi_rate + 0.6


def _first_reinforcement_tick(runtime: TickScheduleRuntime, *, dt_s: float, max_ticks: int = 32) -> int | None:
    for tick in range(max_ticks):
        out = runtime.step(
            ScheduleTickInput(
                t_s=tick * dt_s,
                dt_s=dt_s,
                action="press",
                tick=tick,
                trial_id=0,
            )
        )
        if out.reward > 0.0:
            return tick
    return None


def test_tick_schedule_invariant_fi_reinforcement_is_time_gated_while_fr1_is_immediate():
    fi_runtime = TickScheduleRuntime(
        availability=FixedIntervalAvailability(interval_s=2.0),
        gate=FirstResponseGate(),
        consequence_mapper=ConstantConsequenceMapper(reward=1.0),
    )
    fr_runtime = TickScheduleRuntime(
        availability=AlwaysAvailable(),
        gate=FixedRatioGate(n=1),
        consequence_mapper=ConstantConsequenceMapper(reward=1.0),
    )

    seed = np.random.default_rng(11)
    fi_runtime.reset(seed)
    fr_runtime.reset(np.random.default_rng(11))

    fi_first = _first_reinforcement_tick(fi_runtime, dt_s=0.5)
    fr_first = _first_reinforcement_tick(fr_runtime, dt_s=0.5)

    assert fr_first == 0
    # 2.0s interval with dt=0.5 means reinforcement cannot occur before tick 3.
    assert fi_first is not None and fi_first >= 3

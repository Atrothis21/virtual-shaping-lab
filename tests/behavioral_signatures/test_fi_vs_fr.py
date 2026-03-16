from __future__ import annotations

import numpy as np

from virtual_shaping_lab.experiment.world.schedules import (
    AlwaysAvailable,
    ConstantConsequenceMapper,
    FixedIntervalAvailability,
    FixedRatioGate,
    FirstResponseGate,
    ScheduleTickInput,
    TickScheduleRuntime,
)
from golden_behavior_fixtures import operant_payload, reinforcement_rate, run_fixture_records


def test_schedule_proxy_fixed_ratio_yields_higher_reinforcement_density_than_fixed_interval():
    fr_records = run_fixture_records(operant_payload("fixed_ratio", 1))
    fi_records = run_fixture_records(operant_payload("fixed_interval", 10))

    fr_rate = reinforcement_rate(fr_records)
    fi_rate = reinforcement_rate(fi_records)

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

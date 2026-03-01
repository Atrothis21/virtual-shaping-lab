import numpy as np

from protocols.schedule_runtime import (
    AlwaysAvailable,
    ConstantConsequenceMapper,
    FirstResponseGate,
    FixedIntervalAvailability,
    FixedRatioGate,
    ScheduleTickInput,
    TickScheduleRuntime,
    VariableIntervalAvailability,
    VariableRatioGate,
)


def test_fixed_interval_collects_first_response_after_interval():
    runtime = TickScheduleRuntime(
        availability=FixedIntervalAvailability(interval_s=1.0),
        gate=FirstResponseGate(),
        consequence_mapper=ConstantConsequenceMapper(reward=1.0),
    )
    runtime.reset(np.random.default_rng(1))

    r0 = runtime.step(ScheduleTickInput(t_s=0.0, dt_s=0.5, action="press"))
    r1 = runtime.step(ScheduleTickInput(t_s=0.5, dt_s=0.5, action="press"))
    r2 = runtime.step(ScheduleTickInput(t_s=1.0, dt_s=0.5, action="press"))

    assert r0.reward == 0.0
    assert r1.reward == 1.0
    assert r1.collected is True
    assert r2.reward == 0.0


def test_fixed_ratio_collects_every_nth_response():
    runtime = TickScheduleRuntime(
        availability=AlwaysAvailable(),
        gate=FixedRatioGate(n=3),
        consequence_mapper=ConstantConsequenceMapper(reward=2.0),
    )
    runtime.reset(np.random.default_rng(2))

    rewards = []
    for i in range(7):
        out = runtime.step(ScheduleTickInput(t_s=float(i), dt_s=1.0, action="press"))
        rewards.append(out.reward)

    assert rewards == [0.0, 0.0, 2.0, 0.0, 0.0, 2.0, 0.0]


def test_variable_ratio_is_deterministic_under_seed():
    runtime_a = TickScheduleRuntime(
        availability=AlwaysAvailable(),
        gate=VariableRatioGate(mean_n=2.0),
        consequence_mapper=ConstantConsequenceMapper(reward=1.0),
    )
    runtime_b = TickScheduleRuntime(
        availability=AlwaysAvailable(),
        gate=VariableRatioGate(mean_n=2.0),
        consequence_mapper=ConstantConsequenceMapper(reward=1.0),
    )

    seed = 123
    runtime_a.reset(np.random.default_rng(seed))
    runtime_b.reset(np.random.default_rng(seed))

    out_a = [
        runtime_a.step(ScheduleTickInput(t_s=float(i), dt_s=1.0, action="press")).reward
        for i in range(10)
    ]
    out_b = [
        runtime_b.step(ScheduleTickInput(t_s=float(i), dt_s=1.0, action="press")).reward
        for i in range(10)
    ]
    assert out_a == out_b


def test_variable_interval_is_deterministic_under_seed():
    runtime_a = TickScheduleRuntime(
        availability=VariableIntervalAvailability(mean_interval_s=1.0),
        gate=FirstResponseGate(),
        consequence_mapper=ConstantConsequenceMapper(reward=1.0),
    )
    runtime_b = TickScheduleRuntime(
        availability=VariableIntervalAvailability(mean_interval_s=1.0),
        gate=FirstResponseGate(),
        consequence_mapper=ConstantConsequenceMapper(reward=1.0),
    )

    seed = 77
    runtime_a.reset(np.random.default_rng(seed))
    runtime_b.reset(np.random.default_rng(seed))

    seq_a = [
        runtime_a.step(ScheduleTickInput(t_s=0.5 * i, dt_s=0.5, action="press")).reward
        for i in range(12)
    ]
    seq_b = [
        runtime_b.step(ScheduleTickInput(t_s=0.5 * i, dt_s=0.5, action="press")).reward
        for i in range(12)
    ]
    assert seq_a == seq_b


import numpy as np

from virtual_shaping_lab.vsl.agent.policy import (
    NullActionSpace,
    NullPolicy,
    SingletonActionSpace,
)


def test_null_action_space_is_empty_and_unsampleable():
    action_space = NullActionSpace()
    assert action_space.actions() == ()
    assert action_space.sample(np.random.default_rng(7)) is None


def test_singleton_action_space_is_deterministic():
    action_space = SingletonActionSpace(action="noop")
    assert action_space.actions() == ("noop",)
    assert action_space.sample(np.random.default_rng(7)) == "noop"


def test_null_policy_select_action_is_deterministic():
    policy = NullPolicy()
    assert (
        policy.select_action(
            state={},
            action_space=NullActionSpace(),
            rng=np.random.default_rng(11),
        )
        is None
    )
    assert (
        policy.select_action(
            state={},
            action_space=SingletonActionSpace(),
            rng=np.random.default_rng(11),
        )
        is None
    )


def test_null_policy_distribution_matches_action_space():
    policy = NullPolicy()
    assert policy.action_distribution(state={}, action_space=NullActionSpace()) == {}
    assert policy.action_distribution(
        state={},
        action_space=SingletonActionSpace(),
    ) == {None: 1.0}
    assert policy.action_distribution(
        state={},
        action_space=SingletonActionSpace(action="noop"),
    ) == {"noop": 1.0}


from __future__ import annotations

from virtual_shaping_lab.vsl.protocol import (
    ActionConditionedConsequenceOperator,
    ClassicalNoActionConsequenceOperator,
    ConsequenceOutput,
    EmissionOutput,
)


def _emission() -> EmissionOutput:
    return EmissionOutput(stimulus={"tone": 1.0}, context="A")


def test_v3_21_5_action_conditioned_consequence_maps_action_rewards():
    op = ActionConditionedConsequenceOperator(
        reward_by_action={"leverpress": 1.0, "withhold": 0.0},
        default_reward=-0.5,
    )
    out = op.consequence(emission=_emission(), action="leverpress", state={"t": 0})
    assert isinstance(out, ConsequenceOutput)
    assert out.reward == 1.0
    assert out.done is False
    assert out.metadata["variant"] == "action_conditioned_consequence"


def test_v3_21_5_action_conditioned_consequence_uses_default_for_unknown_action():
    op = ActionConditionedConsequenceOperator(
        reward_by_action={"leverpress": 1.0},
        default_reward=-0.25,
        terminal_actions=("escape",),
    )
    out = op.consequence(emission=_emission(), action="unknown", state={"t": 0})
    assert out.reward == -0.25
    assert out.done is False


def test_v3_21_5_classical_no_action_consequence_ignores_action_and_uses_schedule():
    op = ClassicalNoActionConsequenceOperator(
        reward=1.0,
        reward_schedule=(1.0, 0.0, -1.0),
    )
    out = op.consequence(emission=_emission(), action="leverpress", state={"t": 2})
    assert out.reward == -1.0
    assert out.done is False
    assert out.metadata["variant"] == "classical_no_action_consequence"
    assert out.metadata["action_ignored"] == "leverpress"

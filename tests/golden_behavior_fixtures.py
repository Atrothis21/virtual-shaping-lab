from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from preset_payloads import (
    aba_renewal_payload,
    abc_renewal_payload,
    acquisition_payload,
    blocking_payload,
    differential_acquisition_payload,
    extinction_payload,
    operant_conditioning_payload,
    overshadowing_payload,
    rapid_reacquisition_payload,
)


PayloadFactory = Callable[[], dict]


@dataclass(frozen=True)
class GoldenBehaviorFixture:
    key: str
    payload_factory: PayloadFactory
    qualitative_expectation: str
    thresholds: dict[str, float] = field(default_factory=dict)


def run_fixture_records(payload: dict) -> list[dict]:
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


def mean_prediction(rows: list[dict]) -> float:
    values = [float(r["prediction"]) for r in rows if r.get("prediction") is not None]
    if not values:
        raise ValueError("No prediction values available.")
    return sum(values) / len(values)


def first_last_n(rows: list[dict], n: int = 10) -> tuple[list[dict], list[dict]]:
    if not rows:
        raise ValueError("Cannot split empty records.")
    window = max(1, min(n, len(rows)))
    return rows[:window], rows[-window:]


def head_tail(rows: list[dict], ratio: float = 0.2) -> tuple[list[dict], list[dict]]:
    if not rows:
        raise ValueError("Cannot split empty records.")
    window = max(1, int(len(rows) * ratio))
    return rows[:window], rows[-window:]


def cue_predictions(records: list[dict], cue: str) -> list[float]:
    out: list[float] = []
    for rec in records:
        by_stim = rec.get("prediction_by_stimulus")
        if isinstance(by_stim, dict) and cue in by_stim:
            out.append(float(by_stim[cue]))
    return out


def tail(values: list[float], n: int = 10) -> list[float]:
    if not values:
        raise ValueError("Cannot take tail of empty list.")
    return values[-min(n, len(values)) :]


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot average empty values.")
    return sum(values) / len(values)


def operant_payload(schedule_type: str, schedule_value: int, n_trials: int = 120) -> dict:
    payload = operant_conditioning_payload()
    phase = payload["experiment"]["program"]["phases"][0]
    phase["trials"] = n_trials
    phase.setdefault("params", {})
    phase["params"]["n_trials"] = n_trials
    phase["params"]["reward_schedule"] = {
        "type": schedule_type,
        "value": schedule_value,
    }
    return payload


def reinforcement_rate(records: list[dict]) -> float:
    rewards = [float(r.get("reward", 0.0) or 0.0) for r in records]
    if not rewards:
        raise ValueError("No rewards found in records.")
    return sum(1.0 for r in rewards if r > 0.0) / float(len(rewards))


GOLDEN_BEHAVIOR_FIXTURES: dict[str, GoldenBehaviorFixture] = {
    "acquisition_rise": GoldenBehaviorFixture(
        key="acquisition_rise",
        payload_factory=acquisition_payload,
        qualitative_expectation="late-trial prediction exceeds early-trial prediction",
        thresholds={"min_prediction_gain": 0.1},
    ),
    "extinction_decline": GoldenBehaviorFixture(
        key="extinction_decline",
        payload_factory=extinction_payload,
        qualitative_expectation="extinction tail falls below acquisition and early extinction levels",
        thresholds={
            "min_extinction_drop_vs_early": 0.2,
            "min_extinction_drop_vs_acquisition": 0.2,
        },
    ),
    "blocking_present": GoldenBehaviorFixture(
        key="blocking_present",
        payload_factory=blocking_payload,
        qualitative_expectation="primary cue remains dominant over the blocked cue",
        thresholds={"min_primary_minus_blocked": 0.0},
    ),
    "overshadowing_salience_sensitivity": GoldenBehaviorFixture(
        key="overshadowing_salience_sensitivity",
        payload_factory=overshadowing_payload,
        qualitative_expectation="higher-salience cue remains dominant in compound learning",
        thresholds={"min_dominance_margin": 0.0},
    ),
    "generalization_gradient_decline": GoldenBehaviorFixture(
        key="generalization_gradient_decline",
        payload_factory=differential_acquisition_payload,
        qualitative_expectation="generalization declines as similarity distance increases",
        thresholds={"min_cs_plus_minus_gap": 0.2},
    ),
    "renewal_recovery_context_switch_aba": GoldenBehaviorFixture(
        key="renewal_recovery_context_switch_aba",
        payload_factory=aba_renewal_payload,
        qualitative_expectation="probe prediction recovers above extinction under context switch",
        thresholds={"min_probe_recovery": 0.2},
    ),
    "renewal_recovery_context_switch_abc": GoldenBehaviorFixture(
        key="renewal_recovery_context_switch_abc",
        payload_factory=abc_renewal_payload,
        qualitative_expectation="probe prediction recovers above extinction under novel context",
        thresholds={"min_probe_recovery": 0.1},
    ),
    "fi_vs_fr_separation": GoldenBehaviorFixture(
        key="fi_vs_fr_separation",
        payload_factory=operant_conditioning_payload,
        qualitative_expectation="fixed ratio yields higher reinforcement density than fixed interval in the current operant path",
        thresholds={"min_reinforcement_density_gap": 0.6},
    ),
    "rapid_reacquisition_recovery": GoldenBehaviorFixture(
        key="rapid_reacquisition_recovery",
        payload_factory=rapid_reacquisition_payload,
        qualitative_expectation="reacquisition returns above extinction and back toward high responding after prior extinction",
        thresholds={
            "min_reacquisition_vs_extinction_gain": 0.2,
            "min_reacquisition_tail": 0.8,
        },
    ),
}

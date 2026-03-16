"""Canonical payload contract helpers with explicit legacy adapters."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def _is_non_empty_dict(value: Any) -> bool:
    return isinstance(value, dict) and bool(value)


def _is_canonical_experiment(exp: dict[str, Any]) -> bool:
    return all(key in exp for key in ("program", "agent", "runtime"))


def _is_legacy_experiment(exp: dict[str, Any]) -> bool:
    legacy_keys = {
        "learner",
        "representation",
        "phases",
        "protocol",
        "stimuli",
        "params",
        "salience",
        "attention",
        "attention_config",
    }
    return any(key in exp for key in legacy_keys)


def _assert_payload_shape(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("Payload must be an object.")
    if not isinstance(payload.get("experiment"), dict):
        raise ValueError("Payload missing 'experiment' object.")
    if not isinstance(payload.get("report"), dict):
        raise ValueError("Payload missing 'report' object.")


def _assert_no_mixed_shape(exp: dict[str, Any]) -> None:
    agent_field = exp.get("agent")
    has_canonical = (
        "program" in exp
        or (
            isinstance(agent_field, dict)
            and ("representation" in agent_field or "learning" in agent_field or "policy" in agent_field)
        )
    )
    has_legacy = _is_legacy_experiment(exp)
    if has_canonical and has_legacy:
        raise ValueError(
            "Mixed payload shape detected: provide either canonical "
            "experiment.program/experiment.agent/experiment.runtime or legacy flat experiment fields, not both."
        )


def normalize_phase_trials(
    phases: list[dict[str, Any]],
    *,
    allow_default_trials: bool = False,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for idx, phase in enumerate(phases):
        if not isinstance(phase, dict):
            raise ValueError(f"program.phases[{idx}] must be an object.")
        out = dict(phase)
        params = out.get("params")
        if params is None:
            params = {}
        if not isinstance(params, dict):
            raise ValueError(f"program.phases[{idx}].params must be an object.")
        out["params"] = dict(params)

        trials = out.get("trials")
        if trials is None and "n_trials" in out["params"]:
            trials = out["params"]["n_trials"]
        if trials is None:
            if allow_default_trials:
                trials = 1
            else:
                raise ValueError(
                    f"program.phases[{idx}] is missing required 'trials' "
                    "(or params.n_trials for compatibility backfill)."
                )
        try:
            trials = int(trials)
        except (TypeError, ValueError):
            raise ValueError(f"program.phases[{idx}].trials must be an integer.")
        if trials <= 0:
            raise ValueError(f"program.phases[{idx}].trials must be > 0.")
        out["trials"] = trials
        out["params"]["n_trials"] = trials
        normalized.append(out)
    return normalized


def _legacy_phases(exp: dict[str, Any]) -> list[dict[str, Any]]:
    has_protocol = "protocol" in exp and exp.get("protocol")
    has_phases_key = "phases" in exp
    has_phases = has_phases_key and isinstance(exp.get("phases"), list) and len(exp.get("phases", [])) > 0

    if has_protocol and has_phases:
        raise ValueError("experiment must provide either 'protocol' or 'phases', not both")
    if has_phases_key and not isinstance(exp.get("phases"), list):
        raise ValueError("experiment.phases must be an array")

    if isinstance(exp.get("phases"), list) and exp["phases"]:
        raw: list[dict[str, Any]] = []
        for idx, phase in enumerate(exp["phases"]):
            if not isinstance(phase, dict):
                raise ValueError(f"phase[{idx}] must be an object")
            if "protocol" not in phase or not isinstance(phase.get("protocol"), str):
                raise ValueError(f"phase[{idx}].protocol is required")
            if "params" in phase and not isinstance(phase.get("params"), dict):
                raise ValueError(f"phase[{idx}].params must be an object")
            if "stimuli" in phase and not isinstance(phase.get("stimuli"), dict):
                raise ValueError(f"phase[{idx}].stimuli must be an object")
            raw.append(dict(phase))
        return normalize_phase_trials(raw, allow_default_trials=True)

    protocol = exp.get("protocol")
    if not protocol:
        raise ValueError("experiment must provide either 'protocol' or 'phases'")
    if not isinstance(exp.get("protocol"), str):
        raise ValueError("experiment.protocol must be a string")
    if "params" in exp and not isinstance(exp.get("params"), dict):
        raise ValueError("experiment.params must be an object")
    if "stimuli" in exp and not isinstance(exp.get("stimuli"), dict):
        raise ValueError("experiment.stimuli must be an object")
    params = exp.get("params") if isinstance(exp.get("params"), dict) else {}
    single: dict[str, Any] = {
        "name": "Phase 0",
        "protocol": protocol,
        "params": dict(params),
    }
    if isinstance(exp.get("stimuli"), dict):
        single["stimuli"] = deepcopy(exp.get("stimuli"))
    return normalize_phase_trials([single], allow_default_trials=True)


def _canonical_phases(exp: dict[str, Any]) -> list[dict[str, Any]]:
    program = exp.get("program")
    if not isinstance(program, dict):
        raise ValueError("Canonical payload requires experiment.program object.")
    phases = program.get("phases")
    if not isinstance(phases, list) or not phases:
        raise ValueError("Canonical payload requires non-empty experiment.program.phases.")
    raw = [dict(p) for p in phases if isinstance(p, dict)]
    if len(raw) != len(phases):
        raise ValueError("experiment.program.phases entries must be objects.")
    return normalize_phase_trials(raw, allow_default_trials=False)


def is_legacy_payload(payload: dict[str, Any]) -> bool:
    _assert_payload_shape(payload)
    exp = payload["experiment"]
    _assert_no_mixed_shape(exp)
    return _is_legacy_experiment(exp)


def from_legacy_payload(payload: dict[str, Any]) -> dict[str, Any]:
    _assert_payload_shape(payload)
    src = deepcopy(payload)
    exp = src["experiment"]
    if not _is_legacy_experiment(exp):
        raise ValueError("from_legacy_payload requires a legacy payload shape.")

    phases = _legacy_phases(exp)
    representation = exp.get("representation")
    if isinstance(representation, str):
        representation = {"name": representation, "params": {}}
    if not isinstance(representation, dict):
        raise ValueError("Legacy experiment.representation must be a string or object.")
    rep_out = deepcopy(representation)
    rep_params = rep_out.get("params")
    if rep_params is None:
        rep_params = {}
    if not isinstance(rep_params, dict):
        raise ValueError("representation.params must be an object.")
    rep_out["params"] = dict(rep_params)
    if _is_non_empty_dict(exp.get("salience")):
        rep_out["salience"] = deepcopy(exp.get("salience"))
    if isinstance(exp.get("stimuli"), list) and exp["stimuli"]:
        rep_out["params"].setdefault("stimuli", list(exp["stimuli"]))

    learning: dict[str, Any] = {
        "rule": exp.get("learner"),
        "params": {},
    }
    if _is_non_empty_dict(exp.get("attention_config")) or _is_non_empty_dict(exp.get("attention")):
        learning["attention"] = {
            "config": deepcopy(exp.get("attention_config", {})),
            "initial": deepcopy(exp.get("attention", {})),
        }

    runtime = deepcopy(exp.get("runtime", {})) if isinstance(exp.get("runtime"), dict) else {}
    if _is_non_empty_dict(exp.get("context_inference")):
        runtime["context_inference"] = deepcopy(exp["context_inference"])

    canonical = {
        "experiment": {
            "program": {"phases": phases},
            "agent": {
                "name": exp.get("agent"),
                "representation": rep_out,
                "learning": learning,
                "policy": deepcopy(exp.get("policy")),
            },
            "runtime": runtime,
        },
        "report": deepcopy(src.get("report", {})),
    }
    return canonical


def to_legacy_payload(payload: dict[str, Any]) -> dict[str, Any]:
    _assert_payload_shape(payload)
    canonical = to_canonical_payload(payload)
    exp = canonical["experiment"]
    agent = exp["agent"]
    representation = deepcopy(agent.get("representation"))
    learning = agent.get("learning", {}) if isinstance(agent.get("learning"), dict) else {}
    attention = learning.get("attention", {}) if isinstance(learning.get("attention"), dict) else {}
    runtime = deepcopy(exp.get("runtime", {})) if isinstance(exp.get("runtime"), dict) else {}
    context_inference = runtime.pop("context_inference", {})

    legacy = {
        "experiment": {
            "learner": learning.get("rule"),
            "agent": agent.get("name") or ("operant_agent" if agent.get("policy") else "classical_agent"),
            "representation": representation,
            "policy": deepcopy(agent.get("policy")),
            "runtime": runtime,
            "salience": deepcopy(representation.get("salience", {}))
            if isinstance(representation, dict)
            else {},
            "attention": deepcopy(attention.get("initial", {})),
            "attention_config": deepcopy(attention.get("config")),
            "context_inference": context_inference if isinstance(context_inference, dict) else {},
            "phases": [],
        },
        "report": deepcopy(payload.get("report", {})),
    }

    phases = _canonical_phases(exp)
    for phase in phases:
        legacy["experiment"]["phases"].append(
            {
                "name": phase.get("name"),
                "protocol": phase.get("protocol"),
                "stimuli": deepcopy(phase.get("stimuli")),
                "params": deepcopy(phase.get("params", {})),
            }
        )
    if legacy["experiment"].get("attention_config") in ({}, None):
        legacy["experiment"]["attention_config"] = None
    return legacy


def to_canonical_payload(payload: dict[str, Any]) -> dict[str, Any]:
    _assert_payload_shape(payload)
    src = deepcopy(payload)
    exp = src["experiment"]
    _assert_no_mixed_shape(exp)

    if _is_legacy_experiment(exp):
        raise ValueError(
            "Legacy payload shape is no longer accepted at runtime; "
            "provide canonical experiment.program/experiment.agent/experiment.runtime."
        )

    if not _is_canonical_experiment(exp):
        raise ValueError(
            "Payload experiment must use canonical keys "
            "(program, agent, runtime)."
        )

    phases = _canonical_phases(exp)
    runtime = exp.get("runtime")
    if runtime is None:
        runtime = {}
    if not isinstance(runtime, dict):
        raise ValueError("experiment.runtime must be an object.")

    agent = exp.get("agent")
    if not isinstance(agent, dict):
        raise ValueError("experiment.agent must be an object.")
    if not isinstance(agent.get("representation"), dict):
        raise ValueError("experiment.agent.representation must be an object.")
    if not isinstance(agent.get("learning"), dict):
        raise ValueError("experiment.agent.learning must be an object.")

    out = {
        "experiment": {
            "program": {"phases": phases},
            "agent": {
                "name": agent.get("name"),
                "representation": deepcopy(agent.get("representation")),
                "learning": deepcopy(agent.get("learning")),
                "policy": deepcopy(agent.get("policy")),
            },
            "runtime": deepcopy(runtime),
        },
        "report": deepcopy(src.get("report", {})),
    }
    return out

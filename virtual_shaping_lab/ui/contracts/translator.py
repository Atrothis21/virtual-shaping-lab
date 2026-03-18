"""Translation adapters from typed UI builder drafts to API payload contracts."""

from __future__ import annotations

from typing import Any

from ui.contracts.builder_draft import BuilderExperimentDraft

_KNOWN_REPORT_PRESETS = {
    "aab_renewal",
    "aba_renewal",
    "abc_renewal",
    "acquisition",
    "basic_learning_curve",
    "blocking",
    "compound_acquisition",
    "conditioned_inhibition",
    "custom_protocol",
    "differential_acquisition",
    "extinction",
    "matching_law",
    "occasion_setting",
    "operant_conditioning",
    "rapid_reacquisition",
    "resurgence",
    "shaping",
    "spontaneous_recovery",
    "superextinction",
}


def _default_report_preset(draft: BuilderExperimentDraft) -> str:
    if draft.program.protocol and draft.program.protocol in _KNOWN_REPORT_PRESETS:
        return draft.program.protocol
    if len(draft.program.phases) == 1:
        protocol = draft.program.phases[0].protocol
        if protocol in _KNOWN_REPORT_PRESETS:
            return protocol
    return "custom_protocol"


def _collect_stimuli(value: Any, sink: set[str]) -> None:
    if isinstance(value, str):
        if value.strip():
            sink.add(value)
        return
    if isinstance(value, list):
        for item in value:
            _collect_stimuli(item, sink)
        return
    if isinstance(value, dict):
        for item in value.values():
            _collect_stimuli(item, sink)


def _infer_representation_stimuli(experiment: dict[str, Any]) -> list[str]:
    stimuli: set[str] = set()
    program = experiment.get("program", {})
    if isinstance(program, dict):
        _collect_stimuli(program.get("stimuli", {}), stimuli)
    for phase in (program.get("phases", []) if isinstance(program, dict) else []) or []:
        if isinstance(phase, dict):
            _collect_stimuli(phase.get("stimuli", {}), stimuli)

    agent = experiment.get("agent", {})
    policy = agent.get("policy") if isinstance(agent, dict) else None
    if isinstance(policy, dict):
        params = policy.get("params")
        if isinstance(params, dict):
            _collect_stimuli(params.get("actions", []), stimuli)
    _collect_stimuli((program.get("params", {}) if isinstance(program, dict) else {}).get("action_labels", []), stimuli)

    return sorted(stimuli)


def _normalize_representation(experiment: dict[str, Any]) -> dict[str, Any]:
    agent = experiment.get("agent")
    if not isinstance(agent, dict):
        raise ValueError("Builder draft requires experiment.agent object.")
    representation = agent.get("representation")
    if isinstance(representation, dict):
        return representation
    if isinstance(representation, str):
        inferred_stimuli = _infer_representation_stimuli(experiment)
        if not inferred_stimuli:
            raise ValueError(
                "Cannot infer representation.params.stimuli from builder draft; "
                "add experiment/phase stimuli or operant action labels."
            )
        return {
            "name": representation,
            "params": {
                "stimuli": inferred_stimuli,
                "max_compound_size": 2,
            },
        }
    raise ValueError("Builder draft representation must be a string or object.")


def _resolve_trials(params: dict[str, Any]) -> int:
    trials = params.get("n_trials", 1)
    try:
        trials = int(trials)
    except (TypeError, ValueError):
        raise ValueError("Builder draft phase params.n_trials must be an integer.")
    if trials <= 0:
        raise ValueError("Builder draft phase params.n_trials must be > 0.")
    return trials


def _canonical_phases(experiment: dict[str, Any]) -> list[dict[str, Any]]:
    program = experiment.get("program")
    if not isinstance(program, dict):
        raise ValueError("Builder draft requires experiment.program object.")
    phases = program.get("phases")
    if isinstance(phases, list) and phases:
        out: list[dict[str, Any]] = []
        for idx, phase in enumerate(phases):
            if not isinstance(phase, dict):
                raise ValueError(f"Builder phase[{idx}] must be an object.")
            params = dict(phase.get("params", {}) or {})
            trials = phase.get("trials")
            if trials is None:
                trials = _resolve_trials(params)
            out.append(
                {
                    "name": phase.get("name") or f"Phase {idx}",
                    "protocol": phase.get("protocol"),
                    "stimuli": dict(phase.get("stimuli", {}) or {}),
                    "params": params,
                    "trials": int(trials),
                }
            )
        return out

    raise ValueError("Builder draft requires non-empty experiment.program.phases.")


def draft_to_payload(
    draft: BuilderExperimentDraft | dict[str, Any],
    *,
    report_preset: str | None = None,
) -> dict[str, Any]:
    """
    Translate a typed builder draft into a canonical run-ready API payload.

    Translation scope is intentionally minimal:
    - preserve builder-authored field values
    - enforce protocol/phases mode contract from typed draft
    - add required `report.preset`
    """
    typed = BuilderExperimentDraft.from_dict(draft) if isinstance(draft, dict) else draft
    experiment = typed.to_dict()
    preset = report_preset if report_preset is not None else _default_report_preset(typed)

    return {
        "experiment": {
            "program": {
                "phases": _canonical_phases(experiment),
            },
            "agent": {
                "name": (experiment.get("agent") or {}).get("name"),
                "representation": _normalize_representation(experiment),
                "learning": {
                    **dict(((experiment.get("agent") or {}).get("learning") or {})),
                },
                "policy": (experiment.get("agent") or {}).get("policy"),
            },
            "runtime": dict(experiment.get("runtime", {}) or {}),
        },
        "report": {"preset": preset},
    }

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
    if draft.protocol and draft.protocol in _KNOWN_REPORT_PRESETS:
        return draft.protocol
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
    _collect_stimuli(experiment.get("stimuli", {}), stimuli)
    for phase in experiment.get("phases", []) or []:
        if isinstance(phase, dict):
            _collect_stimuli(phase.get("stimuli", {}), stimuli)

    policy = experiment.get("policy")
    if isinstance(policy, dict):
        params = policy.get("params")
        if isinstance(params, dict):
            _collect_stimuli(params.get("actions", []), stimuli)
    _collect_stimuli(experiment.get("params", {}).get("action_labels", []), stimuli)

    ordered = sorted(stimuli)
    return ordered


def draft_to_payload(
    draft: BuilderExperimentDraft | dict[str, Any],
    *,
    report_preset: str | None = None,
) -> dict[str, Any]:
    """
    Translate a typed builder draft into a run-ready API payload shape.

    Translation scope is intentionally minimal:
    - preserve builder-authored field values
    - enforce protocol/phases mode contract from typed draft
    - add required `report.preset`
    """
    typed = BuilderExperimentDraft.from_dict(draft) if isinstance(draft, dict) else draft
    experiment = typed.to_dict()
    # UI draft keeps representation as a simple key; runtime payload expects object form.
    representation_value = experiment.get("representation")
    if isinstance(representation_value, str):
        inferred_stimuli = _infer_representation_stimuli(experiment)
        if not inferred_stimuli:
            raise ValueError(
                "Cannot infer representation.params.stimuli from builder draft; "
                "add experiment/phase stimuli or operant action labels."
            )
        experiment["representation"] = {
            "name": representation_value,
            "params": {
                "stimuli": inferred_stimuli,
                "max_compound_size": 2,
            },
        }
    preset = report_preset if report_preset is not None else _default_report_preset(typed)
    return {
        "experiment": experiment,
        "report": {"preset": preset},
    }

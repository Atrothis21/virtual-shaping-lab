# analysis/report/presets.py

from analysis.report.config import ReportConfig


# -------------------------------------------------
# Report preset registry
# -------------------------------------------------

_REPORT_PRESETS = {
    # -------------------------------------------------
    # Classical / Pavlovian presets
    # -------------------------------------------------

    "differential_acquisition": ReportConfig(
        metrics=[
            "mean_prediction_by_stimulus",
            "final_prediction_by_stimulus",
            "mean_reward_by_stimulus",
            "trial_count_by_stimulus",
            "discrimination_index",
        ],
        visualizations=[
            "stimulus_bar_plot",
            "discrimination_curve_plot",
            "dual_time_series_plot",
        ],
        params={
            "discrimination_index": {
                "positive_key": "cs_plus",
                "negative_key": "cs_minus",
            }
        },
    ),

    "extinction": ReportConfig(
        metrics=[
            "prediction_time_series",
            "extinction_rate",
        ],
        visualizations=[
            "line_plot",
            "extinction_curve_plot",
        ],
        params={},
    ),

    "basic_learning_curve": ReportConfig(
        metrics=[
            "prediction_time_series",
        ],
        visualizations=[
            "line_plot",
        ],
        params={},
    ),

    "conditioned_inhibition": ReportConfig(
        metrics=[
            "prediction_time_series",
            "mean_prediction_by_stimulus",
            "final_prediction_by_stimulus",
            "mean_reward_by_stimulus",
            "trial_count_by_stimulus",
        ],
        visualizations=[
            "line_plot",
            "dual_time_series_plot",
            "summation_plot",
            "retardation_curve_plot",
        ],
        params={
            "line_plot": {
                "phase_names": ["acquisition"]
            },
            "dual_time_series_plot": {
                "phase_names": ["compound_nonreinforcement"]
            },
            "summation_plot": {
                "phase_names": ["summation_probe"]
            },
            "retardation_curve_plot": {
                "phase_names": ["retardation"]
            }
        },
    ),

    "compound_acquisition": ReportConfig(
        metrics=[
            "prediction_time_series",
        ],
        visualizations=[
            "dual_time_series_plot",
        ],
        params={},
    ),

    "aba_renewal": ReportConfig(
        metrics=[
            "prediction_time_series",
        ],
        visualizations=[
            "line_plot",
        ],
        params={
        },
    ),

    "abc_renewal": ReportConfig(
        metrics=[
            "prediction_time_series",
        ],
        visualizations=[
            "line_plot",
        ],
        params={},
    ),

    "aab_renewal": ReportConfig(
        metrics=[
            "prediction_time_series",
        ],
        visualizations=[
            "line_plot",
        ],
        params={},
    ),

    "rapid_reacquisition": ReportConfig(
        metrics=["prediction_time_series"],
        visualizations=["line_plot"],
        params={},
    ),

    "occasion_setting": ReportConfig(
        metrics=[
            "prediction_time_series",
            "final_prediction_by_stimulus",
        ],
        visualizations=[
            "line_plot",
            "stimulus_bar_plot",
        ],
        params={},
    ),

    "blocking": ReportConfig(
        metrics=[
            "prediction_time_series",
        ],
        visualizations=[
            "dual_time_series_plot",
        ],
        params={},
    ),

    # -------------------------------------------------
    # Aliases (UX-friendly names)
    # -------------------------------------------------

    # Canonical "acquisition" -> simple learning curve
    "acquisition": ReportConfig(
        metrics=[
            "prediction_time_series",
        ],
        visualizations=[
            "line_plot",
        ],
        params={},
    ),

    # -------------------------------------------------
    # Operant conditioning preset
    # -------------------------------------------------

    "operant_conditioning": ReportConfig(
        metrics=[
            "prediction_time_series",
            "reward_time_series",
            "cumulative_responses",
            "cumulative_rewards",
            "outcome_type_counts",
            "phase_reward_summary",
            "action_counts",
        ],
        visualizations=[
            "line_plot",
            "reward_time_series_plot",
            "cumulative_response_plot",
            "cumulative_reward_plot",
            "outcome_type_bar_plot",
            "phase_reward_bar_plot",
            "action_distribution_plot",
        ],
        params={},
    ),

    "matching_law": ReportConfig(
        metrics=[
            "prediction_time_series",
            "reward_time_series",
            "cumulative_responses",
            "cumulative_rewards",
            "action_counts",
            "phase_reward_summary",
        ],
        visualizations=[
            "matching_law_plot",
            "reward_time_series_plot",
            "action_distribution_plot",
            "cumulative_response_plot",
            "cumulative_reward_plot",
            "phase_reward_bar_plot",
        ],
        params={},
    ),

    "shaping": ReportConfig(
        metrics=[
            "prediction_time_series",
            "reward_time_series",
            "cumulative_responses",
            "cumulative_rewards",
            "phase_reward_summary",
            "outcome_type_counts",
            "action_counts",
        ],
        visualizations=[
            "line_plot",
            "reward_time_series_plot",
            "cumulative_response_plot",
            "cumulative_reward_plot",
            "phase_reward_bar_plot",
            "outcome_type_bar_plot",
            "action_distribution_plot",
        ],
        params={},
    ),

    "resurgence": ReportConfig(
        metrics=[
            "prediction_time_series",
            "reward_time_series",
            "cumulative_responses",
            "cumulative_rewards",
            "phase_reward_summary",
            "outcome_type_counts",
            "action_counts",
        ],
        visualizations=[
            "line_plot",
            "reward_time_series_plot",
            "cumulative_response_plot",
            "cumulative_reward_plot",
            "phase_reward_bar_plot",
            "outcome_type_bar_plot",
            "action_distribution_plot",
        ],
        params={},
    ),

    "superextinction": ReportConfig(
        metrics=[
            "prediction_time_series",
            "reward_time_series",
            "cumulative_responses",
            "cumulative_rewards",
            "phase_reward_summary",
            "outcome_type_counts",
            "action_counts",
        ],
        visualizations=[
            "line_plot",
            "reward_time_series_plot",
            "cumulative_response_plot",
            "cumulative_reward_plot",
            "phase_reward_bar_plot",
            "outcome_type_bar_plot",
            "action_distribution_plot",
        ],
        params={},
    ),

    "spontaneous_recovery": ReportConfig(
        metrics=[
            "prediction_time_series",
            "reward_time_series",
            "cumulative_responses",
            "cumulative_rewards",
            "phase_reward_summary",
            "outcome_type_counts",
            "action_counts",
        ],
        visualizations=[
            "line_plot",
            "reward_time_series_plot",
            "cumulative_response_plot",
            "cumulative_reward_plot",
            "phase_reward_bar_plot",
            "outcome_type_bar_plot",
            "action_distribution_plot",
        ],
        params={},
    ),

    "custom_protocol": ReportConfig(
        metrics=[
            "prediction_time_series",
        ],
        visualizations=[
            "auto_time_series_plot",
        ],
        params={},
    ),
}



# -------------------------------------------------
# Public API
# -------------------------------------------------

def get_report_preset(name: str) -> ReportConfig:
    """
    Retrieve a report preset by name.

    Parameters
    ----------
    name : str
        Name of the report preset.

    Returns
    -------
    ReportConfig
        Configuration describing metrics and visualizations.

    Raises
    ------
    KeyError
        If the preset name is unknown.
    """
    if name not in _REPORT_PRESETS:
        available = ", ".join(sorted(_REPORT_PRESETS.keys()))
        raise KeyError(
            f"Unknown report preset '{name}'. "
            f"Available presets: {available}"
        )

    return _REPORT_PRESETS[name]

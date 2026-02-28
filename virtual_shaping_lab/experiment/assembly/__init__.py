"""Assembly namespace (v2.2 structure reshape compatibility layer)."""

from experiment.assemble import assemble_experiment
from experiment.plan_builder import build_experiment_plan

__all__ = ["assemble_experiment", "build_experiment_plan"]

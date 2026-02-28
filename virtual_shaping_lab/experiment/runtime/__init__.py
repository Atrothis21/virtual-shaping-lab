"""Runtime namespace (v2.2 structure reshape compatibility layer)."""

from experiment.hooks import RunnerHooks
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from experiment.sinks import CompositeSink, InMemorySink, JsonlSink
from experiment.trial_executor import TrialExecutor

__all__ = [
    "Runner",
    "RunnerHooks",
    "TrialExecutor",
    "finalize_record",
    "InMemorySink",
    "JsonlSink",
    "CompositeSink",
]

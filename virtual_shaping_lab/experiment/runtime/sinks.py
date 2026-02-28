"""Runtime sinks compatibility module."""

from experiment.sinks import CompositeSink, InMemorySink, JsonlSink

__all__ = ["InMemorySink", "JsonlSink", "CompositeSink"]

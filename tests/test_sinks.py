import json

import pytest

from experiment.sinks import CompositeSink, InMemorySink, JsonlSink


def test_jsonl_sink_appends_lines(tmp_path):
    path = tmp_path / "sink.jsonl"
    sink = JsonlSink(path)
    sink.emit({"trial": 0, "reward": 0.5})
    sink.emit({"trial": 1, "reward": 1.0})
    sink.close()

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["trial"] == 0
    assert json.loads(lines[1])["reward"] == 1.0


def test_composite_sink_requires_children():
    with pytest.raises(ValueError):
        CompositeSink([])


def test_composite_sink_fans_out_and_closes_children(tmp_path):
    mem = InMemorySink()
    jsonl = JsonlSink(tmp_path / "sink.jsonl")
    sink = CompositeSink([mem, jsonl])
    sink.emit({"trial": 0, "reward": 0.1})
    sink.emit({"trial": 1, "reward": 0.2})
    sink.close()

    assert mem.closed is True
    assert len(mem.records) == 2
    lines = (tmp_path / "sink.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2

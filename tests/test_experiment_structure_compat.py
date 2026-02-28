import importlib


def test_assembly_namespace_imports():
    old_assemble = importlib.import_module("experiment.assemble")
    new_assemble = importlib.import_module("experiment.assembly.assemble")
    new_pkg = importlib.import_module("experiment.assembly")

    assert hasattr(new_assemble, "assemble_experiment")
    assert new_assemble.assemble_experiment is old_assemble.assemble_experiment
    assert new_pkg.assemble_experiment is old_assemble.assemble_experiment


def test_runtime_namespace_imports():
    old_runner = importlib.import_module("experiment.runner")
    old_sinks = importlib.import_module("experiment.sinks")
    old_hooks = importlib.import_module("experiment.hooks")
    old_records = importlib.import_module("experiment.runtime_records")
    old_exec = importlib.import_module("experiment.trial_executor")

    runtime_pkg = importlib.import_module("experiment.runtime")
    runtime_runner = importlib.import_module("experiment.runtime.runner")
    runtime_sinks = importlib.import_module("experiment.runtime.sinks")
    runtime_hooks = importlib.import_module("experiment.runtime.hooks")
    runtime_records = importlib.import_module("experiment.runtime.records")
    runtime_exec = importlib.import_module("experiment.runtime.trial_executor")

    assert runtime_runner.Runner is old_runner.Runner
    assert runtime_hooks.RunnerHooks is old_hooks.RunnerHooks
    assert runtime_records.finalize_record is old_records.finalize_record
    assert runtime_exec.TrialExecutor is old_exec.TrialExecutor

    assert runtime_sinks.InMemorySink is old_sinks.InMemorySink
    assert runtime_sinks.JsonlSink is old_sinks.JsonlSink
    assert runtime_sinks.CompositeSink is old_sinks.CompositeSink

    assert runtime_pkg.Runner is old_runner.Runner
    assert runtime_pkg.RunnerHooks is old_hooks.RunnerHooks


def test_units_namespace_imports():
    old_phase_base = importlib.import_module("experiment.phases.base")
    old_acq = importlib.import_module("experiment.phases.acquisition")
    old_probe = importlib.import_module("experiment.phases.probe")
    old_protocol_base = importlib.import_module("protocols.base")

    units_pkg = importlib.import_module("experiment.units")
    units_phases = importlib.import_module("experiment.units.phases")
    units_protocols = importlib.import_module("experiment.units.protocols")

    assert units_phases.PhaseBase is old_phase_base.PhaseBase
    assert units_phases.AcquisitionPhase is old_acq.AcquisitionPhase
    assert units_phases.ProbePhase is old_probe.ProbePhase
    assert units_protocols.BaseProtocol is old_protocol_base.BaseProtocol

    assert units_pkg.PhaseBase is old_phase_base.PhaseBase
    assert units_pkg.AcquisitionPhase is old_acq.AcquisitionPhase
    assert units_pkg.BaseProtocol is old_protocol_base.BaseProtocol

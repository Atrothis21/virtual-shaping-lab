from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.protocol import ProtocolSpec, ProtocolSpecValidationError
from virtual_shaping_lab.vsl.protocol.validation import validate_protocol_spec


def _base_spec() -> ProtocolSpec:
    return ProtocolSpec(
        emission_rule="classical_trial_emission",
        consequence_rule="deterministic_consequence",
        advance_rule="trial_increment",
        stop_rule="n_trials",
        protocol_family="acquisition",
        action_space_mode="classical_none",
        temporal_mode="trial_discrete",
    )


def test_v3_protocol_validator_accepts_valid_spec():
    validate_protocol_spec(_base_spec())


def test_v3_protocol_validator_rejects_unknown_emission_rule():
    with pytest.raises(ProtocolSpecValidationError, match="PROTO_E_UNKNOWN_EMISSION_RULE"):
        ProtocolSpec(
            emission_rule="unknown",
            consequence_rule="deterministic_consequence",
            advance_rule="trial_increment",
            stop_rule="n_trials",
            protocol_family="acquisition",
            action_space_mode="classical_none",
            temporal_mode="trial_discrete",
        )


def test_v3_protocol_validator_rejects_unknown_protocol_family():
    with pytest.raises(ProtocolSpecValidationError, match="PROTO_E_UNKNOWN_PROTOCOL_FAMILY"):
        ProtocolSpec(
            emission_rule="classical_trial_emission",
            consequence_rule="deterministic_consequence",
            advance_rule="trial_increment",
            stop_rule="n_trials",
            protocol_family="unknown_family",
            action_space_mode="classical_none",
            temporal_mode="trial_discrete",
        )


def test_v3_protocol_validator_rejects_family_action_space_mismatch():
    with pytest.raises(ProtocolSpecValidationError, match="PROTO_E_FAMILY_ACTION_SPACE_MISMATCH"):
        ProtocolSpec(
            emission_rule="classical_trial_emission",
            consequence_rule="deterministic_consequence",
            advance_rule="trial_increment",
            stop_rule="n_trials",
            protocol_family="acquisition",
            action_space_mode="discrete",
            temporal_mode="trial_discrete",
        )


def test_v3_protocol_validator_rejects_temporal_advance_mismatch():
    with pytest.raises(ProtocolSpecValidationError, match="PROTO_E_TEMPORAL_ADVANCE_MISMATCH"):
        ProtocolSpec(
            emission_rule="operant_offer_emission",
            consequence_rule="scheduled_consequence",
            advance_rule="event_increment",
            stop_rule="n_trials",
            protocol_family="operant_conditioning",
            action_space_mode="discrete",
            temporal_mode="trial_discrete",
        )

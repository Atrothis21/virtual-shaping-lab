# experiment/phases/catalog.py

"""
Canonical phase catalog + ordering constraints.

This is the single source of truth for:
- builder UI phase list
- backend validation
"""

PHASE_CATALOG = {
    "acquisition": {
        "display": "Acquisition",
        "requires_prior_learning": False
    },
    "nonreinforcement": {
        "display": "Nonreinforcement (Extinction)",
        "requires_prior_learning": True
    },
    "compound_acquisition": {
        "display": "Compound Acquisition",
        "requires_prior_learning": False
    },
    "compound_nonreinforcement": {
        "display": "Compound Nonreinforcement",
        "requires_prior_learning": True
    },
    "differential_acquisition": {
        "display": "Differential Acquisition",
        "requires_prior_learning": False
    },
    "probe": {
        "display": "Probe",
        "requires_prior_learning": True
    },
    "context_shift": {
        "display": "Context Shift",
        "requires_prior_learning": False
    },
    "criterion_shift": {
        "display": "Criterion Shift",
        "requires_prior_learning": True
    },
    "pavlovian_phase_template": {
        "display": "Pavlovian Template",
        "requires_prior_learning": False
    },
    "operant_phase_template": {
        "display": "Operant Template",
        "requires_prior_learning": False
    },
    "acquisition_template": {
        "display": "Acquisition (Template)",
        "requires_prior_learning": False
    },
    "nonreinforcement_template": {
        "display": "Nonreinforcement (Template)",
        "requires_prior_learning": True
    },
    "compound_acquisition_template": {
        "display": "Compound Acquisition (Template)",
        "requires_prior_learning": False
    },
    "compound_nonreinforcement_template": {
        "display": "Compound Nonreinforcement (Template)",
        "requires_prior_learning": True
    },
    "differential_acquisition_template": {
        "display": "Differential Acquisition (Template)",
        "requires_prior_learning": False
    },
    "probe_template": {
        "display": "Probe (Template)",
        "requires_prior_learning": True
    }
}

PHASE_CONSTRAINTS = {
    "requires_prior_learning": {
        "nonreinforcement",
        "compound_nonreinforcement",
        "probe",
        "criterion_shift"
        ,
        "nonreinforcement_template",
        "compound_nonreinforcement_template",
        "probe_template"
    },
    "requires_prior_acquisition": {
        "nonreinforcement",
        "compound_nonreinforcement",
        "probe",
        "criterion_shift"
        ,
        "nonreinforcement_template",
        "compound_nonreinforcement_template",
        "probe_template"
    },
    "can_appear_anywhere": {
        "context_shift"
    }
}

# Template-first policy:
# - Canonical protocol composition should prefer template-backed phase variants.
# - Phase-mode canonical keys remain class-based for behavioral compatibility.
# - Legacy class-based canonical variants are factory-only via explicit *_legacy keys.
# - Custom phase classes are still allowed only for true control-flow/runtime phases.
CUSTOM_PHASE_CLASS_ALLOWLIST = {
    "context_shift",
    "criterion_shift",
}

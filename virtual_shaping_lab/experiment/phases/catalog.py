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
    }
}

PHASE_CONSTRAINTS = {
    "requires_prior_learning": {
        "nonreinforcement",
        "compound_nonreinforcement",
        "probe",
        "criterion_shift"
    },
    "requires_prior_acquisition": {
        "nonreinforcement",
        "compound_nonreinforcement",
        "probe",
        "criterion_shift"
    },
    "can_appear_anywhere": {
        "context_shift"
    }
}

# Virtual Shaping Lab

Virtual Shaping Lab is a phase-oriented, agent-centric simulation environment for classical and operant learning. It supports preset behavioral protocols and a schema-driven builder UI for composing custom phase sequences.

> **Behavioral scope note:** The modeled phenomena are experimental in v1 and should be treated as work-in-progress.

## What It Models (Experimental)
- Pavlovian learning: acquisition, extinction, nonreinforcement
- Discrimination: differential acquisition (CS+ vs CS-)
- Compound learning: compound acquisition, blocking, overshadowing, overexpectation
- Contextual effects: renewal (AAB/ABA/ABC), context shift, rapid reacquisition
- Conditioned inhibition: summation + retardation tests
- Operant matching law with concurrent schedules

## Requirements
- Python 3.x
- See code for exact dependencies (requirements/pyproject if present)

## Running
- Presets: open `ui/presets.html`
- Builder: open `ui/builder.html`
- Backend run endpoint: see `api/run.py`

## Testing & CI
Local tests:
```bash
pip install -r virtual_shaping_lab/requirements.txt
pip install -r requirements-dev.txt
pytest
```

CI runs the full payload regression suite on every push/PR to `main` via
`.github/workflows/ci.yml`.

## Release Checklist (v1)
1. Run `pytest` locally and ensure green.
2. Confirm `reports/` and `__pycache__/` are not tracked.
3. Review `CHANGELOG.md` and `VERSION`.
4. Tag release as `v1.0.0`.

## Core Concepts
- **Phases** define trial logic and learning contingencies.
- **Protocols** orchestrate phase sequences.
- **Agents** wrap learner + representation (+ policy for operant).
- **Representations** encode stimuli into vectors.
- **Attention** (explicit) scales learning rate per stimulus.
- **Context inference** can assign latent contexts automatically.
- **Similarity** enables generalization via a stimulus similarity matrix.

## Known Limitations
- No change-point or full latent-cause modeling yet (heuristic context inference only).
- Similarity is representational only (no adaptive similarity learning).
- Attention is explicit, not learned.
- Some phenomena are experimental; results are not yet validated.

## License
MIT

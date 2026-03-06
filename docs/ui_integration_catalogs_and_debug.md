# UI Integration Guide: Catalogs, Phenomena, and Debug Telemetry (V2.15)

## Purpose
This guide describes the backend contracts the browser client should consume for discovery and teaching-mode integration.

Canonical contract entrypoint:
- `docs/ui_contract_manifest.md` (authoritative endpoint/envelope/lifecycle contract)
- this guide is integration guidance and examples that must remain consistent with the manifest.

Primary rule:
- UI should be catalog-driven and API-driven.
- UI should not import or mirror runtime internals.

---

## 1) Extension Catalog API

Endpoint:
- `GET /catalog/extensions`

Top-level response shape:
```json
{
  "status": "success",
  "extensions": {
    "protocols": [],
    "phenomena": {},
    "learners": [],
    "policies": [],
    "representations": [],
    "report_templates": {}
  }
}
```

Field semantics:
- `protocols`: canonical protocol keys (normalized).
- `phenomena`: UI/teaching layer entries keyed by phenomenon id.
- `learners`: available learner keys.
- `policies`: available policy keys.
- `representations`: available representation keys.
- `report_templates`: protocol -> default template mapping contract.

### Phenomena entry contract
Each `extensions.phenomena[phenomenon_key]` object includes:
- `name`: display name.
- `description`: short teaching description.
- `protocol_key`: protocol to run for this phenomenon.
- `expected_signatures`: qualitative outcomes UI can narrate/check.
- `default_template_key`: optional template alias (nullable).
- `recommended_presets`: optional prefilled payload fragments.

Example:
```json
{
  "name": "Blocking",
  "description": "Prior learning about cue A suppresses learning about cue X in AX+ compound training.",
  "protocol_key": "blocking",
  "expected_signatures": ["blocked_cue_lower_than_pretrained_cue"],
  "default_template_key": null,
  "recommended_presets": []
}
```

---

## 2) Catalog Metadata Expectations

Catalog metadata is defined server-side for:
- runtime phases
- protocols
- default report templates

Metadata fields:
- `label`
- `description`
- `params_schema`
- `defaults`
- `constraints`
- `examples`

UI usage pattern:
1. Use `label` + `description` for display/tooltips.
2. Use `params_schema` + `defaults` to generate form state.
3. Use `constraints` to conditionally show warnings/guards.
4. Use `examples` to seed quick-start snippets.

---

## 3) Debug Telemetry (Opt-In)

Debug telemetry is disabled by default.

Enable it in payload:
```json
{
  "experiment": {
    "runtime": {
      "debug": true,
      "update_mode": "tick",
      "record_mode": "tick"
    }
  }
}
```

When enabled:
- records may contain a `debug` object.
- when disabled, `debug` is omitted.

`debug` contract:
- `value`: numeric or null
- `prediction_error`: numeric or null
- `active_features`: list of strings
- `attention_effective`: object (string -> number), may be empty
- `salience_effective`: object (string -> number), may be empty

Example tick record fragment:
```json
{
  "trial": 0,
  "tick": 3,
  "reward": 1.0,
  "debug": {
    "value": 0.42,
    "prediction_error": 0.58,
    "active_features": ["tone", "context:A"],
    "attention_effective": {"tone": 0.8},
    "salience_effective": {"tone": 0.5}
  }
}
```

---

## 4) Recommended UI Data Flow

1. Call `GET /catalog/extensions` at app init.
2. Populate protocol and phenomenon selectors from catalog payload.
3. Build payload forms from catalog metadata (`defaults` + `params_schema`).
4. Run experiment via existing run API.
5. If teaching mode is enabled, set `experiment.runtime.debug=true` and render record-level debug overlays.

---

## 5) Boundary Notes

- Do not couple UI to `experiment.factories.phase_factory` or other runtime internals.
- Treat API contracts and catalog payloads as the source of truth.
- Any new UI behavior should first request a catalog/contract field instead of adding hardcoded frontend mapping.

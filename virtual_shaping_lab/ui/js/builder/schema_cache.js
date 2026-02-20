const phaseSchemaCache = {};
const phaseSchemaLoading = {};

function schemaPath(protocol) {
  return `/ui/schema/phases/${protocol}.schema.json`;
}

function ensurePhaseSchema(protocol) {
  if (phaseSchemaCache[protocol]) return phaseSchemaCache[protocol];
  if (phaseSchemaLoading[protocol]) return null;

  phaseSchemaLoading[protocol] = true;
  fetch(schemaPath(protocol))
    .then(res => {
      if (!res.ok) {
        throw new Error(`Schema fetch failed for ${protocol}`);
      }
      return res.json();
    })
    .then(schema => {
      phaseSchemaCache[protocol] = schema;
      phaseSchemaLoading[protocol] = false;
      if (typeof renderPhaseEditor === "function") {
        renderPhaseEditor();
      }
    })
    .catch(err => {
      phaseSchemaLoading[protocol] = false;
      debugLog("schema load error", { protocol, error: err.message });
    });

  return null;
}

function schemaParamProps(schema) {
  return schema?.properties?.params?.properties || {};
}

function schemaStimuliProps(schema) {
  return schema?.properties?.stimuli?.properties || {};
}

function schemaHasParam(schema, name) {
  const props = schemaParamProps(schema);
  return Object.prototype.hasOwnProperty.call(props, name);
}

function schemaStimuliType(schema) {
  const props = schemaStimuliProps(schema);
  if (Object.prototype.hasOwnProperty.call(props, "compound")) return "compound";
  if (Object.prototype.hasOwnProperty.call(props, "cs_plus")) return "cs";
  return "none";
}

function schemaTrialKey(schema) {
  const props = schemaParamProps(schema);
  if (Object.prototype.hasOwnProperty.call(props, "n_trials")) return "n_trials";
  const keys = Object.keys(props).filter(k => k.endsWith("_trials"));
  return keys.length ? keys[0] : null;
}

function schemaNumberBounds(schema, key, fallbackMin, fallbackMax) {
  const props = schemaParamProps(schema);
  const def = props[key] || {};
  const min = def.minimum != null ? def.minimum : fallbackMin;
  const max = def.maximum != null ? def.maximum : fallbackMax;
  return { min, max };
}

function schemaParamDefaults(schema) {
  const props = schemaParamProps(schema);
  const params = {};
  Object.entries(props).forEach(([key, def]) => {
    if (def && def.default !== undefined) {
      params[key] = def.default;
    }
  });
  return params;
}

function schemaStimuliDefaults(schema) {
  const stimType = schemaStimuliType(schema);
  if (stimType === "compound") {
    return { compound: [STIMULI[0], STIMULI[1]] };
  }
  if (stimType === "cs") {
    const props = schemaStimuliProps(schema);
    const stimuli = { cs_plus: [STIMULI[0]] };
    if (Object.prototype.hasOwnProperty.call(props, "cs_minus")) {
      stimuli.cs_minus = [STIMULI[1]];
    }
    return stimuli;
  }
  return {};
}

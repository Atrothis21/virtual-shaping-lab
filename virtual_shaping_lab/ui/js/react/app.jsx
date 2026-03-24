window.VSLReact = window.VSLReact || {};

const sections = window.VSLReact.presetSections || [];
const UX_STATUS_BADGE = Object.freeze({
  success: "badge-mechanism-operant",
  partial: "badge-mechanism-similarity",
  novel: "badge-mechanism-attention",
  behaviorally_unsupported: "badge-mechanism-salience",
});
const UX_STATUS_LABEL = Object.freeze({
  success: "Supported",
  partial: "Partially Supported",
  novel: "Novel",
  behaviorally_unsupported: "Exploratory",
});

function mechanismBadgeClass(name) {
  const key = String(name || "").trim().toLowerCase();
  if (key === "baseline") return "badge-mechanism-baseline";
  if (key === "attention") return "badge-mechanism-attention";
  if (key === "context") return "badge-mechanism-context";
  if (key === "similarity") return "badge-mechanism-similarity";
  if (key === "salience") return "badge-mechanism-salience";
  if (key === "operant") return "badge-mechanism-operant";
  return "badge-mechanism-default";
}

function PresetCard({ item }) {
  const mechanisms = Array.isArray(item.mechanisms) ? item.mechanisms : [];
  const briefDescription = item.teaches || item.description || "";
  return (
    <div className="card">
      <h3>{item.name}</h3>
      {briefDescription && <p>{briefDescription}</p>}
      {item.phaseSummary && (
        <p className="phase-summary">
          <strong>Phase Flow:</strong> {item.phaseSummary}
        </p>
      )}
      {mechanisms.length > 0 && (
        <div className="badge-block">
          <div className="badge-label">Mechanisms</div>
          <div className="badge-row">
            {mechanisms.map((name) => (
              <span
                key={`${item.href}-${name}`}
                className={`badge ${mechanismBadgeClass(name)}`}
              >
                {name}
              </span>
            ))}
          </div>
        </div>
      )}
      <div className="card-actions">
        <a className="button" href={item.href}>Open Preset</a>
      </div>
    </div>
  );
}

function PresetUxCard({ item }) {
  const status = String(item?.compatibility?.status || "behaviorally_unsupported");
  const uxState = String(item?.compatibility?.ux_state || "caution");
  const badgeClass = UX_STATUS_BADGE[status] || "badge-mechanism-default";
  const statusLabel = UX_STATUS_LABEL[status] || "Exploratory";
  const routeHref = item?.route?.href || "/ui/presets.html";
  const smartPresetHref = `${routeHref}?entry=smart_preset_prefill&smart_preset_id=${encodeURIComponent(String(item?.id || ""))}`;
  const manualExploreHref = `${routeHref}?entry=manual_tuple_explore&arrangement=${encodeURIComponent(String(item?.tuple_reference?.arrangement_id || ""))}&task=${encodeURIComponent(String(item?.tuple_reference?.phenomenon_id || ""))}`;
  const guidanceText = String(item?.compatibility?.guidance || "");
  return (
    <div
      className="card"
      data-ux-state={uxState}
      data-compatibility-status={status}
      role="article"
      aria-label={`Preset card ${item.label}`}
    >
      <h3>{item.label}</h3>
      {item.description && <p>{item.description}</p>}
      <p className="phase-summary">
        <strong>Arrangement:</strong> {item?.tuple_reference?.arrangement_id || "unknown"}{" "}
        <strong>Task:</strong> {item?.tuple_reference?.phenomenon_id || "unknown"}{" "}
        <strong>Agent:</strong> {item?.tuple_reference?.agent_bundle_id || "unknown"}
      </p>
      <div className="badge-block">
        <div className="badge-label">Expected Outcome</div>
        <div className="badge-row">
          <span className={`badge ${badgeClass}`} aria-label={`Compatibility status: ${statusLabel}`}>{statusLabel}</span>
          <span className="badge badge-mechanism-baseline" aria-label={`UX state: ${uxState}`}>{uxState}</span>
        </div>
      </div>
      {item?.compatibility?.explanation && (
        <p aria-label="Compatibility explanation from evaluator output">{item.compatibility.explanation}</p>
      )}
      {guidanceText && (
        <p aria-label="Compatibility guidance">{guidanceText}</p>
      )}
      <div className="card-actions">
        <a className="button" href={smartPresetHref} aria-label={`Open preset ${item.label}`}>Open Preset</a>
        <a className="button secondary" href={manualExploreHref} aria-label={`Explore tuple space for ${item.label}`}>Explore Tuple Space</a>
      </div>
    </div>
  );
}

function PresetSection({ title, items }) {
  return (
    <section>
      <h2>{title}</h2>
      <div className="grid">
        {items.map((item) => (
          <PresetCard key={item.href} item={item} />
        ))}
      </div>
    </section>
  );
}

function PresetUxArrangementSection({ arrangement }) {
  const uiControls = arrangement?.ui_density_controls || {};
  const collapseThreshold = Number(uiControls.collapse_sections_when_card_count_gt || 6);
  const topRecommendedLimit = Number(uiControls.top_recommended_limit || 3);
  const [expanded, setExpanded] = React.useState({});

  return (
    <section data-arrangement-id={arrangement.arrangement_id}>
      <h2>{arrangement.arrangement_id}</h2>
      {arrangement.phenomenon_groups.map((group) => {
        const allCards = Array.isArray(group.smart_presets) ? group.smart_presets : [];
        const recommended = allCards.filter((x) => x?.compatibility?.status === "success");
        const recommendedTop = recommended.slice(0, topRecommendedLimit);
        const recommendedIds = new Set(recommendedTop.map((x) => x.id));
        const nonRecommended = allCards.filter((x) => !recommendedIds.has(x.id));
        const ordered = [...recommendedTop, ...nonRecommended];
        const needsCollapse = ordered.length > collapseThreshold;
        const key = `${arrangement.arrangement_id}:${group.phenomenon_class}`;
        const isExpanded = Boolean(expanded[key]);
        const visible = !needsCollapse || isExpanded ? ordered : ordered.slice(0, topRecommendedLimit);
        return (
          <div key={key} data-phenomenon-class={group.phenomenon_class}>
            <h3>{group.phenomenon_class}</h3>
            <div className="grid">
              {visible.map((item) => (
                <PresetUxCard key={item.id} item={item} />
              ))}
            </div>
            {needsCollapse && (
              <div className="actions">
                <button
                  type="button"
                  className="btn secondary"
                  onClick={() => {
                    setExpanded((prev) => ({ ...prev, [key]: !isExpanded }));
                  }}
                >
                  {isExpanded ? "Show Less" : "Show More"}
                </button>
              </div>
            )}
          </div>
        );
      })}
    </section>
  );
}

function MechanismTabs({ mechanisms, selectedMechanisms, onSelectAll, onToggleMechanism }) {
  return (
    <div className="actions" style={{ marginTop: "0.75rem", marginBottom: "0.75rem" }}>
      <button
        className={`btn ${selectedMechanisms.length === 0 ? "" : "secondary"}`}
        onClick={onSelectAll}
        type="button"
      >
        All
      </button>
      {mechanisms.map((mechanism) => {
        const active = selectedMechanisms.includes(mechanism);
        return (
          <button
            key={mechanism}
            className={`btn ${active ? "" : "secondary"}`}
            onClick={() => onToggleMechanism(mechanism)}
            type="button"
          >
            {mechanism}
          </button>
        );
      })}
    </div>
  );
}

function buildMechanismSections(rawSections) {
  const grouped = new Map();
  const BASELINE_ONLY_PRESETS = new Set([
    "Acquisition",
    "Compound Acquisition",
    "Differential Acquisition",
    "Extinction",
  ]);

  rawSections.forEach((section) => {
    const items = Array.isArray(section.items) ? section.items : [];
    items.forEach((item) => {
      const mechanisms = Array.isArray(item.mechanisms) && item.mechanisms.length > 0
        ? item.mechanisms
        : ["Baseline"];
      const mechanismSet = new Set(mechanisms.map((m) => String(m)));

      // Only specific foundational phenomena should appear in Baseline.
      if (BASELINE_ONLY_PRESETS.has(String(item.name || "").trim())) {
        mechanismSet.add("Baseline");
      }

      Array.from(mechanismSet).forEach((mechanism) => {
        const key = String(mechanism);
        if (!grouped.has(key)) {
          grouped.set(key, new Map());
        }
        const perMechanism = grouped.get(key);
        perMechanism.set(item.href, item);
      });
    });
  });

  return Array.from(grouped.entries())
    .sort((a, b) => {
      if (a[0] === "Baseline" && b[0] !== "Baseline") return -1;
      if (b[0] === "Baseline" && a[0] !== "Baseline") return 1;
      return a[0].localeCompare(b[0]);
    })
    .map(([mechanism, itemMap]) => ({
      title: mechanism,
      items: Array.from(itemMap.values()).sort((a, b) => a.name.localeCompare(b.name)),
    }));
}

function App() {
  const modeModel = window.VSLReact?.uiModes;
  const mode = modeModel ? modeModel.activate("presets") : "preset";
  const mechanismSections = buildMechanismSections(sections);
  const mechanismTitles = mechanismSections.map((section) => section.title);
  const [selectedMechanisms, setSelectedMechanisms] = React.useState([]);
  const [presetUxCatalog, setPresetUxCatalog] = React.useState(null);
  const [presetUxLoadError, setPresetUxLoadError] = React.useState(null);

  React.useEffect(() => {
    let cancelled = false;
    async function loadPresetUxCatalog() {
      try {
        const response = await fetch("/catalog/preset-ux");
        if (!response.ok) {
          throw new Error(`preset-ux ${response.status}`);
        }
        const body = await response.json();
        if (!cancelled) {
          setPresetUxCatalog(body);
          setPresetUxLoadError(null);
        }
      } catch (error) {
        if (!cancelled) {
          setPresetUxCatalog(null);
          setPresetUxLoadError(String(error?.message || error));
        }
      }
    }
    loadPresetUxCatalog();
    return () => {
      cancelled = true;
    };
  }, []);

  const onSelectAll = React.useCallback(() => {
    setSelectedMechanisms([]);
  }, []);

  const onToggleMechanism = React.useCallback((mechanism) => {
    setSelectedMechanisms((prev) => {
      if (prev.includes(mechanism)) {
        const next = prev.filter((m) => m !== mechanism);
        return next;
      }
      return [...prev, mechanism];
    });
  }, []);

  const visibleSections = selectedMechanisms.length === 0
    ? mechanismSections
    : mechanismSections.filter((section) => selectedMechanisms.includes(section.title));
  const hasPresetUxCatalog = Boolean(
    presetUxCatalog
    && Array.isArray(presetUxCatalog.arrangements)
    && presetUxCatalog.registry_generated === true
  );
  const densityControls = hasPresetUxCatalog ? (presetUxCatalog.ui_density_controls || {}) : {};

  return (
    <>
      <h1>Experiment Presets</h1>
      <p>Select a preset to configure and run an experiment.</p>
      <p><strong>Mode:</strong> {mode}</p>
      <div style={{ color: "#555", marginBottom: "0.45rem" }}>
        <strong>Navigation:</strong> <a href="/ui/index.html">Menu</a> / Presets
      </div>
      {hasPresetUxCatalog && (
        <div style={{ color: "#94a3b8", marginBottom: "0.45rem" }}>
          <strong>Catalog Source:</strong> tuple-first preset UX contract
        </div>
      )}
      {!hasPresetUxCatalog && (
        <div style={{ color: "#fcd34d", marginBottom: "0.45rem" }}>
          <strong>Catalog Source:</strong> degraded fallback ({presetUxLoadError || "preset-ux unavailable"})
        </div>
      )}

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/index.html"; }}>
          Back to Menu
        </button>
      </div>

      {hasPresetUxCatalog ? (
        <>
          <div style={{ color: "#94a3b8", marginBottom: "0.45rem" }}>
            <strong>Density controls:</strong>{" "}
            collapse>{String(densityControls.collapse_sections_when_card_count_gt || 6)} | top-recommended={String(densityControls.top_recommended_limit || 3)}
          </div>
          {presetUxCatalog.arrangements.map((arrangement) => (
            <PresetUxArrangementSection
              key={arrangement.arrangement_id}
              arrangement={{
                ...arrangement,
                ui_density_controls: densityControls,
              }}
            />
          ))}
        </>
      ) : (
        <>
          <MechanismTabs
            mechanisms={mechanismTitles}
            selectedMechanisms={selectedMechanisms}
            onSelectAll={onSelectAll}
            onToggleMechanism={onToggleMechanism}
          />

          {visibleSections.map((section) => (
            <PresetSection key={section.title} title={section.title} items={section.items} />
          ))}
        </>
      )}
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);

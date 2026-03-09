window.VSLReact = window.VSLReact || {};

const sections = window.VSLReact.presetSections || [];

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
              <span key={`${item.href}-${name}`} className="badge">{name}</span>
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
  const mechanismSections = buildMechanismSections(sections);
  const mechanismTitles = mechanismSections.map((section) => section.title);
  const [selectedMechanisms, setSelectedMechanisms] = React.useState([]);

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

  return (
    <>
      <h1>Experiment Presets</h1>
      <p>Select a preset to configure and run an experiment.</p>
      <div style={{ color: "#555", marginBottom: "0.45rem" }}>
        <strong>Navigation:</strong> <a href="/ui/index.html">Menu</a> / Presets
      </div>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/index.html"; }}>
          Back to Menu
        </button>
      </div>

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
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);

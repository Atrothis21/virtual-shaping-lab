window.VSLReact = window.VSLReact || {};

const sections = window.VSLReact.presetSections || [];

function PresetCard({ item }) {
  const mechanisms = Array.isArray(item.mechanisms) ? item.mechanisms : [];
  return (
    <div className="card">
      <h3>{item.name}</h3>
      <p>{item.description}</p>
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
      {item.teaches && (
        <p className="teaches">
          <strong>What This Demonstrates:</strong> {item.teaches}
        </p>
      )}
      {item.builderNext && (
        <p className="builder-next">
          <strong>Try Next In Builder:</strong> {item.builderNext}
        </p>
      )}
      {item.nextPhenomenon && (
        <p className="next-phenomenon">
          <strong>Recommended Next Phenomenon:</strong> {item.nextPhenomenon}
        </p>
      )}
      <div className="card-actions">
        <a className="button" href={item.href}>Open Preset</a>
        <a className="button secondary" href={item.builderHref || "/ui/builder.html"}>Open Builder</a>
      </div>
    </div>
  );
}

function PresetSection({ section }) {
  return (
    <section>
      <h2>{section.title}</h2>
      <p className="section-note">{section.note}</p>
      <div className="grid">
        {section.items.map((item) => (
          <PresetCard key={item.href} item={item} />
        ))}
      </div>
    </section>
  );
}

function App() {
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

      {sections.map((section) => (
        <PresetSection key={section.title} section={section} />
      ))}
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);

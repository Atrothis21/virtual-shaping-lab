window.VSLReact = window.VSLReact || {};

const sections = window.VSLReact.presetSections || [];

function PresetCard({ item }) {
  return (
    <div className="card">
      <h3>{item.name}</h3>
      <p>{item.description}</p>
      <a className="button" href={item.href}>Open</a>
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

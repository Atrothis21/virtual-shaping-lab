function HomeCard({ title, description, cta, href }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <p>{description}</p>
      <button onClick={() => { window.location.href = href; }}>
        {cta}
      </button>
    </div>
  );
}

function IndexApp() {
  return (
    <>
      <h1>Virtual Shaping Lab</h1>
      <p>How would you like to design your experiment?</p>

      <HomeCard
        title="Lifecycle Console"
        description="Use the V2 lifecycle flow (Plan -> Run -> Report) with a thin API-first console."
        cta="Open Console"
        href="/ui/console.html"
      />

      <HomeCard
        title="Predefined Experiments"
        description="Choose from canonical behavioral experiments (Pavlovian conditioning, extinction, operant schedules)."
        cta="Browse Presets"
        href="/ui/presets.html"
      />

      <HomeCard
        title="Build Your Own"
        description="Construct custom multi-phase experiments with full control."
        cta="Open Experiment Builder"
        href="/ui/builder.html"
      />
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<IndexApp />);

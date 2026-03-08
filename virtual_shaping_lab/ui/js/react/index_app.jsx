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
      <p>Choose how you want to start.</p>

      <HomeCard
        title="Presets"
        description="Choose from predefined experiments and run them quickly."
        cta="Browse Presets"
        href="/ui/presets.html"
      />

      <HomeCard
        title="Builder"
        description="Create an experiment by editing only the allowed parameters."
        cta="Open Builder"
        href="/ui/builder.html"
      />
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<IndexApp />);

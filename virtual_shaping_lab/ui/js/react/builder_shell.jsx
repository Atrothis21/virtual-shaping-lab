window.VSLReact = window.VSLReact || {};

function BuilderShellApp() {
  return (
    <>
      <h1>Virtual Shaping Lab - Builder</h1>
      <p>React migration shell. Legacy builder is loaded below for behavior parity.</p>

      <div className="actions">
        <button className="btn" onClick={() => { window.location.href = "/ui/index.html"; }}>
          Back to Menu
        </button>
        <a className="btn secondary" href="/ui/builder_legacy.html">Open Legacy Builder</a>
      </div>

      <div className="panel">
        <iframe
          title="legacy-builder"
          src="/ui/builder_legacy.html"
          style={{ width: "100%", minHeight: "78vh", border: "1px solid #ddd", borderRadius: "6px" }}
        />
      </div>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<BuilderShellApp />);

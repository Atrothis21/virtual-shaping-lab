window.VSLReact = window.VSLReact || {};

function BuilderPhaseList({ phases, activePhaseIndex, onSelectPhase, onAddPhase }) {
  return (
    <div className="panel">
      <h3>Phases</h3>
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "0.7rem" }}>
        {phases.map((phase, idx) => (
          <button
            key={`${phase.name}-${idx}`}
            className="btn"
            onClick={() => onSelectPhase(idx)}
            style={{ background: idx === activePhaseIndex ? "#dbeafe" : "#fff" }}
          >
            {phase.name}
          </button>
        ))}
      </div>
      <button className="btn" onClick={onAddPhase}>Add Phase</button>
    </div>
  );
}

window.VSLReact.BuilderPhaseList = BuilderPhaseList;

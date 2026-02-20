function renderPhaseList() {
  const list = document.getElementById("phase-list");
  list.innerHTML = "";

  payload.experiment.phases.forEach((p, i) => {
    const btn = document.createElement("button");
    btn.textContent = p.name || `Phase ${i + 1}`;
    btn.className = i === activePhaseIndex ? "phase-btn active" : "phase-btn";
    btn.onclick = () => {
      activePhaseIndex = i;
      renderPhaseList();
      renderPhaseEditor();
    };
    list.appendChild(btn);
  });
}

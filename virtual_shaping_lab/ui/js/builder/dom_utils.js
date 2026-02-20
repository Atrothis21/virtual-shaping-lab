function populateStimuli(select, values) {
  if (!select) return;
  select.innerHTML = "";
  STIMULI.forEach(stim => {
    const opt = document.createElement("option");
    opt.value = stim;
    opt.textContent = stim;
    if (values.includes(stim)) opt.selected = true;
    select.appendChild(opt);
  });
}

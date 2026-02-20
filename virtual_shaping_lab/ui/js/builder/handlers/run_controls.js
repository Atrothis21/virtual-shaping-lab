function initRunControls() {
  const runBtn = document.getElementById("run-btn");
  const output = document.getElementById("run-output");
  if (!runBtn || !output) {
    return;
  }

  runBtn.onclick = async () => {
    const output = document.getElementById("run-output");
    output.classList.remove("error");

    if (typeof validateBeforeRun === "function") {
      try {
        validateBeforeRun(payload);
      } catch (err) {
        output.textContent = err.message;
        output.classList.add("error");
        return;
      }
    }

    output.textContent = "Running...";

    const res = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await res.json();
    output.textContent = JSON.stringify(result, null, 2);

    if (result.status === "success" && result.run_id) {
      window.location.href = `/ui/results.html?run_id=${result.run_id}`;
    }
  };
}

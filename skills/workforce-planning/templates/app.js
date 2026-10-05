// Browser glue for the staffing plan. Runs in the same module as
// staffing-core.mjs, so validate/analyze/renderApp are in scope.
const root = document.getElementById("app");
const data = validate(JSON.parse(document.getElementById("plan-data").textContent));
const initialScenario = JSON.parse(document.getElementById("plan-scenario").textContent);
let state = { data, scenario: structuredClone(initialScenario) };
let lastForm = null;

function setStatus(message) {
  const status = document.getElementById("status");
  if (status) status.textContent = message;
}

function render(message = "") {
  const focusId = document.activeElement?.id;
  const analysis = analyze(state.data, state.scenario);
  root.innerHTML = renderApp(state.data, state.scenario, analysis);
  if (lastForm) {
    const form = document.getElementById("move-form");
    for (const [key, value] of Object.entries(lastForm)) {
      if (form.elements[key] && key !== "note") form.elements[key].value = value;
    }
  }
  if (focusId) document.getElementById(focusId)?.focus();
  setStatus(message);
}

function download(name, type, text) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const link = Object.assign(document.createElement("a"), { href: url, download: name });
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

const slug = () => state.data.company.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

function addMove(move, message) {
  const scenario = { ...state.scenario, moves: [...state.scenario.moves, move] };
  try {
    validateScenario(state.data, scenario);
  } catch (error) {
    return setStatus(error.message.replace(/\n- /g, " "));
  }
  state.scenario = scenario;
  render(message);
}

root.addEventListener("change", (event) => {
  const input = event.target;
  if (input.matches("input[data-pursuit]")) {
    state.scenario = { ...state.scenario, pursuits: { ...state.scenario.pursuits, [input.dataset.pursuit]: input.value } };
    render(`${input.dataset.pursuit} set to ${input.value}.`);
  } else if (input.id === "import-json" && input.files?.[0]) {
    input.files[0]
      .text()
      .then((text) => {
        const loaded = JSON.parse(text);
        if (loaded.format !== "staffing-plan") throw new Error("Not a staffing plan export.");
        const nextData = validate(loaded.data);
        const scenario = validateScenario(nextData, loaded.scenario);
        state = { data: nextData, scenario };
        lastForm = null;
        render(`Imported scenario from ${input.files[0].name}.`);
      })
      .catch((error) => setStatus(`Import failed: ${error.message.replace(/\n- /g, " ")}`));
  }
});

root.addEventListener("submit", (event) => {
  if (event.target.id !== "move-form") return;
  event.preventDefault();
  const form = Object.fromEntries(new FormData(event.target));
  lastForm = form;
  const move = { person: form.person, job: form.job, role: form.role, from: form.from, to: form.to, pct: Number(form.pct) };
  if (form.note?.trim()) move.note = form.note.trim();
  addMove(move, "Move added. Totals recalculated.");
});

root.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;
  if (button.classList.contains("try")) {
    const move = JSON.parse(button.dataset.try);
    addMove({ ...move, note: "Tried from unfilled seats" }, "What-if move added from the unfilled seat.");
  } else if (button.dataset.removeMove !== undefined) {
    const moves = state.scenario.moves.filter((_, i) => i !== Number(button.dataset.removeMove));
    state.scenario = { ...state.scenario, moves };
    render("Move removed.");
  } else if (button.id === "export-json") {
    const payload = { format: "staffing-plan", version: 1, exportedAt: new Date().toISOString(), data: state.data, scenario: state.scenario };
    download(`${slug()}-staffing-scenario.json`, "application/json", `${JSON.stringify(payload, null, 2)}\n`);
    setStatus("Scenario exported. Import it next meeting to pick up where you left off.");
  } else if (button.id === "export-csv") {
    download(`${slug()}-staffing-grid.csv`, "text/csv", gridCsv(state.data, analyze(state.data, state.scenario)));
    setStatus("Grid exported as CSV.");
  } else if (button.id === "reset") {
    state.scenario = structuredClone(initialScenario);
    lastForm = null;
    render("Scenario reset to the supplied files.");
  }
});

document.documentElement.classList.add("js");
render();

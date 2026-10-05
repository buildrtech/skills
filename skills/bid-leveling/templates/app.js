// Browser glue for the bid tab. Runs in the same module as leveling-core.mjs,
// so validate/analyze/renderApp/workbook are in scope.
const root = document.getElementById("app");
const data = validate(JSON.parse(document.getElementById("tab-data").textContent));
const initialScenario = JSON.parse(document.getElementById("tab-scenario").textContent);
let state = { data, scenario: structuredClone(initialScenario) };

function setStatus(message) {
  const status = document.getElementById("status");
  if (status) status.textContent = message;
}

function render(message = "") {
  const focusId = document.activeElement?.id;
  root.innerHTML = renderApp(state.data, state.scenario, analyze(state.data, state.scenario));
  if (focusId) document.getElementById(focusId)?.focus();
  setStatus(message);
}

function update(next, message) {
  try {
    state.scenario = validateScenario(state.data, next);
  } catch (error) {
    return setStatus(error.message.replace(/\n- /g, " "));
  }
  render(message);
}

function download(name, type, body) {
  const url = URL.createObjectURL(new Blob([body], { type }));
  const link = Object.assign(document.createElement("a"), { href: url, download: name });
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

const slug = () => state.data.package.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const label = (bidId) => state.data.bids.find((b) => b.id === bidId)?.bidder ?? bidId;

function findGap(target) {
  for (const r of analyze(state.data, state.scenario).results) for (const g of r.gaps) if (`${r.bid.id}:${g.row.key}` === target) return g;
  return null;
}

root.addEventListener("change", (event) => {
  const input = event.target;
  if (input.matches("input[data-basis]")) {
    update({ ...state.scenario, basis: { ...state.scenario.basis, [input.dataset.basis]: input.value } }, input.value === "carry" ? "Carried in every bid. Totals recalculated." : "Back to as bid. Totals recalculated.");
  } else if (input.matches("input[data-alternate]")) {
    update({ ...state.scenario, alternates: { ...state.scenario.alternates, [input.dataset.alternate]: input.checked } }, input.checked ? "Alternate carried in every total." : "Alternate removed from the totals.");
  } else if (input.id === "import-json" && input.files?.[0]) {
    const file = input.files[0];
    file
      .text()
      .then((text) => {
        const loaded = JSON.parse(text);
        if (loaded.format !== "bid-tab") throw new Error("Not a bid tab export.");
        const nextData = validate(loaded.data);
        state = { data: nextData, scenario: validateScenario(nextData, loaded.scenario) };
        render(`Imported scenario from ${file.name}.`);
      })
      .catch((error) => setStatus(`Import failed: ${error.message.replace(/\n- /g, " ")}`));
  }
});

root.addEventListener("submit", (event) => {
  const form = event.target;
  event.preventDefault();
  const fields = Object.fromEntries(new FormData(form));
  const amount = parseMoney(fields.amount);
  const source = String(fields.source ?? "").trim();
  if (amount === null) return setStatus("Enter an amount in dollars, like 8,500.");
  if (!source) return setStatus("Say where the figure came from, so the plug can be checked later.");
  if (form.dataset.plug) {
    update({ ...state.scenario, plugs: { ...state.scenario.plugs, [form.dataset.plug]: { amount, source, kind: "entered" } } }, `Plug ${money(amount)} entered. Totals recalculated.`);
  } else if (form.dataset.basisEntry) {
    update({ ...state.scenario, basisEntries: { ...state.scenario.basisEntries, [form.dataset.basisEntry]: { amount, source } } }, `${money(amount)} carried. Totals recalculated.`);
  } else if (form.id === "adj-form") {
    const description = String(fields.description ?? "").trim();
    if (!description) return setStatus("Describe the adjustment.");
    update({ ...state.scenario, adjustments: [...state.scenario.adjustments, { bid: fields.bid, amount, description, source }] }, `Adjustment added to ${label(fields.bid)}.`);
  }
});

root.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;
  const { acceptPlug, clearPlug, acceptAdjustment, removeAdjustment, clearBasis } = button.dataset;
  if (acceptPlug) {
    const gap = findGap(acceptPlug);
    if (!gap?.suggestion) return setStatus("That suggestion is no longer available.");
    update({ ...state.scenario, plugs: { ...state.scenario.plugs, [acceptPlug]: { amount: gap.suggestion.amount, source: gap.suggestion.source, kind: "accepted" } } }, `Suggested plug ${money(gap.suggestion.amount)} accepted.`);
  } else if (clearPlug) {
    const { [clearPlug]: _, ...plugs } = state.scenario.plugs;
    update({ ...state.scenario, plugs }, "Plug cleared. The gap is open again.");
  } else if (acceptAdjustment) {
    const suggestion = analyze(state.data, state.scenario).results.flatMap((r) => r.suggestedAdjustments).find((a) => a.from === acceptAdjustment);
    if (!suggestion) return setStatus("That suggestion is no longer available.");
    update({ ...state.scenario, adjustments: [...state.scenario.adjustments, suggestion] }, `Adjustment ${money(suggestion.amount)} accepted.`);
  } else if (removeAdjustment !== undefined) {
    update({ ...state.scenario, adjustments: state.scenario.adjustments.filter((_, i) => i !== Number(removeAdjustment)) }, "Adjustment removed.");
  } else if (clearBasis) {
    const { [clearBasis]: _, ...basisEntries } = state.scenario.basisEntries;
    update({ ...state.scenario, basisEntries }, "Figure cleared.");
  } else if (button.id === "export-json") {
    const payload = { format: "bid-tab", version: 1, exportedAt: new Date().toISOString(), data: state.data, scenario: state.scenario };
    download(`${slug()}-scenario.json`, "application/json", `${JSON.stringify(payload, null, 2)}\n`);
    setStatus("Scenario exported. Import it later to pick up where you left off.");
  } else if (button.id === "export-xlsx") {
    download(`${slug()}-bid-tab.xlsx`, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", workbook(state.data, state.scenario, analyze(state.data, state.scenario)));
    setStatus("Excel workbook exported with the current plugs and choices.");
  } else if (button.id === "reset") {
    state.scenario = structuredClone(initialScenario);
    render("Reset to the scenario this tab was built with.");
  }
});

document.documentElement.classList.add("js");
render();

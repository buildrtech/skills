#!/usr/bin/env node
// Build the interactive bid tab, the brief, and optionally the Excel workbook.
//
//   node level.mjs BIDS.json OUTPUT.html [--scenario SCENARIO.json] [--brief BRIEF.md] [--xlsx TAB.xlsx]
//   node level.mjs BIDS.json --json [--scenario SCENARIO.json]
//
// Without --brief the brief prints to stdout. --json prints the analysis instead.
import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { analyze, defaultScenario, renderApp, renderBrief, validate, validateScenario, workbook } from "./leveling-core.mjs";

const args = process.argv.slice(2);
const flag = (name) => {
  const i = args.indexOf(name);
  if (i === -1) return null;
  const value = args[i + 1];
  if (!value || value.startsWith("--")) throw new Error(`${name} needs a value`);
  args.splice(i, 2);
  return value;
};

try {
  const scenarioPath = flag("--scenario");
  const briefPath = flag("--brief");
  const xlsxPath = flag("--xlsx");
  const json = args.includes("--json");
  const [dataPath, outPath] = args.filter((a) => a !== "--json");
  if (!dataPath || (!json && !outPath)) {
    console.error("Usage: node level.mjs BIDS.json OUTPUT.html [--scenario SCENARIO.json] [--brief BRIEF.md] [--xlsx TAB.xlsx]\n       node level.mjs BIDS.json --json [--scenario SCENARIO.json]");
    process.exit(2);
  }
  const data = validate(JSON.parse(await readFile(dataPath, "utf8")));
  let scenario = defaultScenario(data);
  if (scenarioPath) {
    const loaded = JSON.parse(await readFile(scenarioPath, "utf8"));
    // Accept either a bare scenario or an export from the HTML tab.
    scenario = validateScenario(data, loaded.format === "bid-tab" ? loaded.scenario : loaded);
  }
  const analysis = analyze(data, scenario);

  if (json) {
    const summary = analysis.results.map((r) => ({
      bid: r.bid.id,
      bidder: r.bid.bidder,
      base: r.bid.total,
      plugs: r.plugs,
      adjustments: r.adjustmentTotal,
      alternates: r.alternateTotal,
      basis: r.basisTotal,
      leveled: r.leveled,
      complete: r.complete,
      missing: r.missing,
      withSuggestions: r.withSuggestions,
      completeWithSuggestions: r.completeWithSuggestions,
      gaps: r.gaps.map((g) => ({ scope: g.row.key, status: g.cell.status, plug: g.plug, suggestion: g.suggestion })),
      flags: r.flags.map((f) => ({ kind: f.kind, text: f.text, ref: f.ref ?? null })),
      questions: r.questions,
    }));
    process.stdout.write(`${JSON.stringify({ lowest: analysis.lowest?.bid.id ?? null, openGaps: analysis.openGaps, superseded: analysis.superseded.map((b) => b.id), results: summary }, null, 2)}\n`);
  } else {
    const here = (file) => fileURLToPath(new URL(file, import.meta.url));
    const [template, core, app] = await Promise.all([
      readFile(here("../templates/tab.html"), "utf8"),
      readFile(here("./leveling-core.mjs"), "utf8"),
      readFile(here("../templates/app.js"), "utf8"),
    ]);
    const script = `${core}\n${app}`;
    if (/<\/script/i.test(script)) throw new Error("Bundled script must not contain a closing script tag");
    // JSON inside <script> must not be able to close the element.
    const embed = (value) => JSON.stringify(value).replace(/</g, "\\u003c");
    const html = template
      .replace("{{TITLE}}", () => `${data.package.name} bid tab`.replace(/[<>&"]/g, ""))
      .replace("{{APP}}", () => renderApp(data, scenario, analysis))
      .replace("{{DATA}}", () => embed(data))
      .replace("{{SCENARIO}}", () => embed(scenario))
      .replace("{{SCRIPT}}", () => script);
    await writeFile(outPath, html);
    if (xlsxPath) await writeFile(xlsxPath, workbook(data, scenario, analysis));
    const brief = renderBrief(data, scenario, analysis);
    if (briefPath) await writeFile(briefPath, brief);
    else process.stdout.write(brief);
    console.error(`Wrote ${[outPath, xlsxPath, briefPath].filter(Boolean).join(", ")}`);
  }
} catch (error) {
  console.error(error.message);
  process.exit(1);
}

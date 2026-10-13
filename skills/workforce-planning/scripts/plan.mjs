#!/usr/bin/env node
// Build the interactive staffing plan and the meeting brief from normalized data.
//
//   node plan.mjs DATA.json OUTPUT.html [--scenario SCENARIO.json] [--brief BRIEF.md]
//   node plan.mjs DATA.json --json [--scenario SCENARIO.json]
//
// Without --brief the brief prints to stdout. --json prints the analysis instead.
import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { analyze, defaultScenario, renderApp, renderBrief, validate, validateScenario } from "./staffing-core.mjs";

const args = process.argv.slice(2);
const flag = (name) => {
  const i = args.indexOf(name);
  if (i === -1) return null;
  const value = args[i + 1];
  if (!value || value.startsWith("--")) throw new Error(`${name} needs a value`);
  args.splice(i, 2);
  return value;
};
const scenarioPath = flag("--scenario");
const briefPath = flag("--brief");
const json = args.includes("--json");
const [dataPath, outPath] = args.filter((a) => a !== "--json");
if (!dataPath || (!json && !outPath)) {
  console.error("Usage: node plan.mjs DATA.json OUTPUT.html [--scenario SCENARIO.json] [--brief BRIEF.md]\n       node plan.mjs DATA.json --json");
  process.exit(2);
}

try {
  const data = validate(JSON.parse(await readFile(dataPath, "utf8")));
  let scenario = defaultScenario(data);
  if (scenarioPath) {
    const loaded = JSON.parse(await readFile(scenarioPath, "utf8"));
    // Accept either a bare scenario or an export from the HTML plan.
    const raw = loaded.format === "staffing-plan" ? loaded.scenario : loaded;
    scenario = validateScenario(data, { pursuits: { ...scenario.pursuits, ...raw.pursuits }, moves: raw.moves ?? [] });
  }
  const analysis = analyze(data, scenario);

  if (json) {
    const { jobs, ...rest } = analysis;
    process.stdout.write(`${JSON.stringify(rest, null, 2)}\n`);
  } else {
    const here = (file) => fileURLToPath(new URL(file, import.meta.url));
    const [template, core, app] = await Promise.all([
      readFile(here("../templates/plan.html"), "utf8"),
      readFile(here("./staffing-core.mjs"), "utf8"),
      readFile(here("../templates/app.js"), "utf8"),
    ]);
    const script = `${core}\n${app}`;
    if (/<\/script/i.test(script)) throw new Error("Bundled script must not contain a closing script tag");
    // JSON inside <script> must not be able to close the element.
    const embed = (value) => JSON.stringify(value).replace(/</g, "\\u003c");
    const html = template
      .replace("{{TITLE}}", () => `${data.company.name} staffing plan`.replace(/[<>&"]/g, ""))
      .replace("{{APP}}", () => renderApp(data, scenario, analysis))
      .replace("{{DATA}}", () => embed(data))
      .replace("{{SCENARIO}}", () => embed(scenario))
      .replace("{{SCRIPT}}", () => script);
    await writeFile(outPath, html);
    const brief = renderBrief(data, scenario, analysis);
    if (briefPath) await writeFile(briefPath, brief);
    else process.stdout.write(brief);
    console.error(`Wrote ${outPath}${briefPath ? ` and ${briefPath}` : ""}`);
  }
} catch (error) {
  console.error(error.message);
  process.exit(1);
}

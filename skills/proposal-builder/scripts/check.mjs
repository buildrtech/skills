#!/usr/bin/env node
// Compliance check for a proposal: requirement coverage, required forms, page
// limit (measured on the rendered PDF), stale or conflicting claims, and fee.
//
//   node check.mjs proposal.json [--pdf proposal.pdf] [--out compliance-check.md] [--json]
//
// --pdf needs Poppler (pdfinfo, pdftotext). Exits 1 when anything blocks submission.
import { readFile, writeFile } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { analyze, renderCheck, validate } from "../templates/proposal-core.mjs";

const squash = (s) => s.replace(/\s+/g, " ").trim().toLowerCase();

// Each section starts on a new page with its title. Find where each one begins.
export function measurePages(pdf, sections) {
  const info = execFileSync("pdfinfo", [pdf], { encoding: "utf8" });
  const total = Number(/Pages:\s+(\d+)/.exec(info)?.[1]);
  if (!total) throw new Error(`Could not read a page count from ${pdf}`);
  const pages = [];
  for (let n = 1; n <= total; n++) pages.push(squash(execFileSync("pdftotext", ["-f", String(n), "-l", String(n), "-layout", pdf, "-"], { encoding: "utf8" })));
  const starts = [];
  let from = 1; // page 0 is the cover
  for (const s of sections) {
    const title = squash(s.title);
    let found = -1;
    for (let i = from; i < total; i++) if (pages[i].includes(title)) {
      found = i;
      break;
    }
    if (found === -1) throw new Error(`Section "${s.title}" was not found in ${pdf}. Re-render after editing the data.`);
    starts.push(found);
    from = found + 1;
  }
  const bySection = {};
  sections.forEach((s, i) => (bySection[s.id] = (i + 1 < starts.length ? starts[i + 1] : total) - starts[i]));
  return { total, bySection };
}

async function main(argv) {
  const args = [...argv];
  const take = (name) => {
    const i = args.indexOf(name);
    if (i === -1) return null;
    const v = args[i + 1];
    if (!v || v.startsWith("--")) throw new Error(`${name} needs a value`);
    args.splice(i, 2);
    return v;
  };
  const pdf = take("--pdf");
  const out = take("--out");
  const json = args.includes("--json");
  const [input] = args.filter((x) => x !== "--json");
  if (!input) {
    console.error("Usage: node check.mjs proposal.json [--pdf proposal.pdf] [--out compliance-check.md] [--json]");
    return 2;
  }
  const p = validate(JSON.parse(await readFile(input, "utf8")));
  const a = analyze(p, pdf ? measurePages(pdf, p.sections) : null);
  if (json) process.stdout.write(`${JSON.stringify({ blocking: a.blocking, warnings: a.warnings, gaps: a.gaps.map((x) => x.req.id), missingForms: a.missingForms.map((x) => x.form.id), pageCheck: a.pageCheck, unconfirmed: a.unconfirmed.length, stale: a.stale.map((x) => x.source.id), conflicts: a.conflicts.map((c) => ({ key: c.key, usesOlder: c.usesOlder.length > 0 })) }, null, 2)}\n`);
  else {
    const report = renderCheck(p, a);
    if (out) await writeFile(out, report);
    else process.stdout.write(report);
  }
  console.error(a.blocking ? `Not ready: ${a.blocking} blocking, ${a.warnings} warnings` : `No blocking items; ${a.warnings} warnings`);
  return a.blocking ? 1 : 0;
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  main(process.argv.slice(2)).then(
    (code) => process.exit(code),
    (error) => {
      console.error(error.message);
      process.exit(2);
    },
  );
}

import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { analyze, money, monthsBetween, renderCheck, validate } from "../../../skills/proposal-builder/templates/proposal-core.mjs";
import { measurePages } from "../../../skills/proposal-builder/scripts/check.mjs";

const skill = fileURLToPath(new URL("../../../skills/proposal-builder/", import.meta.url));
const check = join(skill, "scripts/check.mjs");
const sample = () => JSON.parse(readFileSync(join(skill, "samples/proposal.json"), "utf8"));
const pdf = join(skill, "samples/output-proposal.pdf");
const poppler = spawnSync("pdfinfo", ["-v"]).status === 0;
const section = (p, id) => p.sections.find((s) => s.id === id);
const write = (p) => {
  const file = join(mkdtempSync(join(tmpdir(), "proposal-")), "proposal.json");
  writeFileSync(file, JSON.stringify(p));
  return file;
};

// The sample with its planted problems fixed: Tab G answered, Form 2 included.
function ready() {
  const p = sample();
  p.sections.splice(6, 0, { id: "sbe", tab: "Tab G", kind: "narrative", title: "Small and local business participation", answers: ["G"], items: [{ text: "Outreach plan supplied by the user.", source: { id: "dana" } }] });
  Object.assign(p.rfp.forms[1], { included: true, section: "forms" });
  return p;
}

test("bundled compliance check matches a fresh run on the bundled PDF", { skip: !poppler && "Poppler not installed" }, () => {
  const out = spawnSync(process.execPath, [check, join(skill, "samples/proposal.json"), "--pdf", pdf], { encoding: "utf8" });
  assert.equal(out.status, 1, out.stderr);
  assert.equal(out.stdout, readFileSync(join(skill, "samples/output-compliance-check.md"), "utf8"));
});

test("pages are measured per section from the rendered PDF", { skip: !poppler && "Poppler not installed" }, () => {
  const p = sample();
  const pages = measurePages(pdf, p.sections);
  assert.equal(pages.total, 10);
  assert.deepEqual(pages.bySection, { letter: 1, qualifications: 1, team: 1, precon: 1, construction: 1, safety: 1, fee: 1, forms: 1, matrix: 1 });
  const a = analyze(p, pages);
  assert.equal(a.pageCheck.counted, 6);
  assert.equal(a.pageCheck.ok, true);
});

test("sample: Tab G and Form 2 block submission; old claims are flagged", () => {
  const a = analyze(validate(sample()));
  assert.deepEqual(a.gaps.map((x) => x.req.id), ["G"]);
  assert.deepEqual(a.missingForms.map((x) => x.form.id), ["F2"]);
  assert.equal(a.blocking, 2);
  assert.equal(a.unconfirmed.length, 1);
  assert.match(a.unconfirmed[0].item.text, /within 3% of the final GMP/);
  assert.deepEqual(a.stale.map((x) => x.source.id), ["prior-2024"]);
  assert.deepEqual(a.conflicts.map((c) => [c.key, c.usesOlder.length]), [["emr", 0], ["garfield-value", 0]]);
});

test("fixing the gaps clears every blocking item", () => {
  const a = analyze(validate(ready()));
  assert.equal(a.blocking, 0);
  const out = spawnSync(process.execPath, [check, write(ready())], { encoding: "utf8" });
  assert.equal(out.status, 0, out.stderr);
  assert.match(out.stdout, /\*\*No blocking items\.\*\*/);
});

test("using the older of two conflicting values is flagged", () => {
  const p = sample();
  const garfield = section(p, "qualifications").items[1];
  garfield.source = { id: "prior-2024", page: 1 };
  garfield.confirmed = true;
  const a = analyze(validate(p));
  const c = a.conflicts.find((x) => x.key === "garfield-value");
  assert.equal(c.usesOlder.length, 1);
  assert.match(renderCheck(p, a), /The proposal uses the older value\*\* in Firm qualifications/);
});

test("a requirement answered only by unconfirmed prior claims is weak until confirmed", () => {
  const p = ready();
  section(p, "sbe").items = [{ text: "Outreach meeting before every package.", source: { id: "prior-2024", page: 2 } }];
  let a = analyze(validate(p));
  assert.equal(a.matrix.find((x) => x.req.id === "G").status, "unconfirmed");
  section(p, "sbe").items[0].confirmed = true;
  a = analyze(validate(p));
  assert.equal(a.matrix.find((x) => x.req.id === "G").status, "answered");
});

test("page limits count only the sections the RFP counts", () => {
  const p = validate(sample());
  const bySection = Object.fromEntries(p.sections.map((s) => [s.id, 4]));
  const a = analyze(p, { total: 37, bySection });
  assert.equal(a.pageCheck.counted, 24); // six counted sections, four pages each
  assert.equal(a.pageCheck.ok, false);
  assert.equal(a.blocking, 3);
  assert.match(renderCheck(p, a), /24 counted pages against a limit of 20/);
});

test("an absent fee is unpriced, never zero", () => {
  const p = sample();
  p.fee = { status: "unpriced", note: "Fee worksheet not received." };
  const a = analyze(validate(p));
  assert.equal(a.blocking, 3);
  assert.match(renderCheck(p, a), /The fee is unpriced: Fee worksheet not received\./);
  const zero = sample();
  zero.fee.lines[0].cents = 0;
  zero.fee.totalCents = 61200000;
  assert.throws(() => validate(zero), /lump sum must be positive integer cents/);
  const mixed = sample();
  mixed.fee.status = "unpriced";
  mixed.fee.note = "x";
  assert.throws(() => validate(mixed), /must not carry lines or a total/);
});

test("fee totals reconcile, and options stay out", () => {
  const p = sample();
  p.fee.totalCents += 1;
  assert.throws(() => validate(p), /must equal the lump-sum lines \(66000000\)/);
  const opt = sample();
  opt.fee.lines.push({ id: "alt", label: "Extended general conditions", basis: "lump", cents: 5000000, option: true, source: { id: "dana" } });
  assert.doesNotThrow(() => validate(opt));
});

test("validation refuses unsourced or inconsistent data", () => {
  const bad = (mutate, pattern) => {
    const p = sample();
    mutate(p);
    assert.throws(() => validate(p), pattern);
  };
  bad((p) => delete section(p, "team").items[0].source, /needs a source/);
  bad((p) => (section(p, "precon").items[1].source.page = 7), /page 7 is not in prior-2024 \(2 pages\)/);
  bad((p) => (section(p, "safety").items[0].source = { id: "nope" }), /source "nope" is not in sources/);
  bad((p) => (section(p, "safety").answers = ["Z"]), /answers "Z", which is not a requirement/);
  bad((p) => (section(p, "safety").items[0].facts = ["garfield-value"]), /uses fact "garfield-value" from lib-safety/);
  bad((p) => delete p.rfp.forms[0].section, /form F1: included, so section must name/);
  bad((p) => (p.meta.currency = "JPY"), /does not use two decimal places/);
  bad((p) => (p.sections[1].id = p.sections[0].id), /section id "letter" is repeated/);
  bad((p) => (section(p, "team").items = []), /items must be a nonempty list/);
});

test("helpers", () => {
  assert.equal(money(66000000), "$660,000.00");
  assert.equal(money(-125050), "-$1,250.50");
  assert.equal(monthsBetween("2024-03-12", "2026-10-06"), 30);
  assert.equal(monthsBetween("2026-02-15", "2026-10-06"), 7);
  assert.equal(monthsBetween("2026-01-31", "2026-02-28"), 0);
});

test("CLI exits 2 on invalid data", () => {
  const p = sample();
  p.meta.status = "FINAL";
  const out = spawnSync(process.execPath, [check, write(p)], { encoding: "utf8" });
  assert.equal(out.status, 2);
  assert.match(out.stderr, /meta.status must be DRAFT or FOR REVIEW/);
});

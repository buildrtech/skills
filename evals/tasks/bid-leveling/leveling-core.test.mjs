import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  analyze,
  defaultScenario,
  money,
  parseMoney,
  renderApp,
  renderBrief,
  validate,
  validateScenario,
  workbook,
} from "../../../skills/bid-leveling/scripts/leveling-core.mjs";

const skill = fileURLToPath(new URL("../../../skills/bid-leveling/", import.meta.url));
const level = join(skill, "scripts/level.mjs");
const sample = () => JSON.parse(readFileSync(join(skill, "samples/bid-data.json"), "utf8"));
const sampleScenario = () => JSON.parse(readFileSync(join(skill, "samples/estimator-scenario.json"), "utf8")).scenario;

// A small, readable package for rule-level tests.
function pkg(overrides = {}) {
  const ev = (prefix) => [
    { ref: `${prefix}-1`, file: `${prefix}.pdf`, location: "page 1", quote: "Scope and price." },
    { ref: `${prefix}-2`, file: `${prefix}.pdf`, location: "page 2", quote: "Exclusions." },
  ];
  const bid = (id, total, scope, extra = {}) => ({
    id, bidder: id.toUpperCase(), received: "2027-03-01", files: [`${id}.pdf`], total, totalRef: `${id}-1`,
    addendaAcknowledged: [1], scope, alternates: {}, basis: {}, evidence: ev(id), ...extra,
  });
  const inc = (ref, amount) => (amount === undefined ? { status: "included", ref } : { status: "included", amount, ref });
  return {
    package: {
      project: "Test Clinic", name: "Drywall", asOf: "2027-03-02",
      addenda: [{ number: 1, date: "2027-02-01", summary: "Adds lobby." }],
      rows: [
        { key: "framing", label: "Framing", class: "base" },
        { key: "batts", label: "Sound batts", class: "base" },
        { key: "act", label: "ACT ceilings", class: "outside" },
      ],
      alternates: [{ key: "alt1", label: "Alternate 1", kind: "add" }],
      basis: [{ key: "bond", label: "Bond" }],
    },
    bids: [
      bid("a", 100000, { framing: inc("a-1"), batts: { status: "excluded", note: "by others", ref: "a-2" }, act: { status: "excluded", ref: "a-2" } }),
      bid("b", 120000, { framing: inc("b-1", 90000), batts: inc("b-1", 20000), act: inc("b-1", 10000) }),
      bid("c", 110000, { framing: inc("c-1", 95000), batts: inc("c-1", 15000), act: { status: "omitted", ref: "c-2" } }),
    ],
    openQuestions: [],
    ...overrides,
  };
}

const run = (data, scenario = defaultScenario(data)) => analyze(data, validateScenario(data, scenario));
const result = (analysis, id) => analysis.results.find((r) => r.bid.id === id);

test("bundled outputs match a fresh build exactly", () => {
  const dir = mkdtempSync(join(tmpdir(), "bid-tab-"));
  const out = spawnSync(process.execPath, [level, join(skill, "samples/bid-data.json"), join(dir, "tab.html"), "--scenario", join(skill, "samples/estimator-scenario.json"), "--brief", join(dir, "brief.md"), "--xlsx", join(dir, "tab.xlsx")], { encoding: "utf8" });
  assert.equal(out.status, 0, out.stderr);
  assert.equal(readFileSync(join(dir, "tab.html"), "utf8"), readFileSync(join(skill, "samples/output-bid-tab.html"), "utf8"));
  assert.equal(readFileSync(join(dir, "brief.md"), "utf8"), readFileSync(join(skill, "samples/output-bid-brief.md"), "utf8"));
  assert.deepEqual(readFileSync(join(dir, "tab.xlsx")), readFileSync(join(skill, "samples/output-bid-tab.xlsx")));
});

test("sample: the estimator's first pass makes Prairie the lowest complete bid", () => {
  const data = validate(sample());
  const a = run(data, sampleScenario());
  assert.equal(a.lowest.bid.id, "prairie");
  assert.equal(a.lowest.leveled, 83370000); // 871,200 + 8,500 blocking - 46,000 ACT
  assert.equal(result(a, "northgate").leveled, 89350000);
  assert.equal(result(a, "summit").leveled, 84390000);
  const ridgeline = result(a, "ridgeline-rev");
  assert.equal(ridgeline.complete, false);
  assert.equal(ridgeline.missing.length, 8);
  assert.deepEqual(a.superseded.map((b) => b.id), ["ridgeline-orig"]);
  assert.equal(a.lowestBase.bid.id, "ridgeline-rev");
});

test("sample: nothing is complete before the estimator acts", () => {
  const data = validate(sample());
  const a = run(data);
  assert.equal(a.lowest, null);
  assert.equal(a.openGaps, 14);
  assert.ok(a.results.every((r) => r.plugs === 0 && r.adjustmentTotal === 0));
  assert.match(renderBrief(data, defaultScenario(data), a), /\*\*No bid is complete yet\.\*\*/);
});

test("sample: planted problems are flagged", () => {
  const a = run(validate(sample()));
  const flags = (id) => result(a, id).flags.map((f) => f.kind);
  assert.deepEqual(flags("prairie").sort(), ["outside", "sum"]);
  assert.match(result(a, "prairie").flags.find((f) => f.kind === "sum").text, /\$872,700.*\$871,200/);
  assert.deepEqual(flags("summit").sort(), ["addenda", "proposed"]);
  assert.equal(result(a, "prairie").suggestedAdjustments[0].amount, -4600000);
});

test("suggested plugs use the highest itemized price and never count until accepted", () => {
  const data = validate(pkg());
  const a = run(data);
  const gap = result(a, "a").gaps[0];
  assert.equal(gap.suggestion.amount, 20000);
  assert.match(gap.suggestion.source, /^B's itemized line \(b-1\), the highest of 2 itemized prices/);
  assert.equal(result(a, "a").leveled, 100000);
  assert.equal(result(a, "a").complete, false);
  assert.equal(result(a, "a").withSuggestions, 120000);
  assert.equal(result(a, "a").completeWithSuggestions, true);
  const accepted = run(data, { plugs: { "a:batts": { amount: 20000, source: gap.suggestion.source, kind: "accepted" } } });
  assert.equal(result(accepted, "a").leveled, 120000);
  assert.equal(result(accepted, "a").complete, true);
});

test("no suggestion for unclear scope or when no other bid itemizes it", () => {
  const data = pkg();
  data.bids[0].scope.batts = { status: "unknown", note: "per plans", ref: "a-2" };
  let a = run(validate(data));
  assert.equal(result(a, "a").gaps[0].suggestion, null);
  assert.match(result(a, "a").questions.map((q) => q.text).join(" "), /confirm whether sound batts is in your price/);
  const data2 = pkg();
  data2.bids[1].scope.batts = { status: "included", ref: "b-1" };
  data2.bids[2].scope.batts = { status: "included", ref: "c-1" };
  a = run(validate(data2));
  assert.equal(result(a, "a").gaps[0].suggestion, null);
  assert.equal(result(a, "a").completeWithSuggestions, false);
});

test("validation refuses incomplete or uncited extractions", () => {
  const missingRow = pkg();
  delete missingRow.bids[0].scope.batts;
  assert.throws(() => validate(missingRow), /scope row "batts" is missing/);
  const amountOnGap = pkg();
  amountOnGap.bids[0].scope.batts.amount = 500;
  assert.throws(() => validate(amountOnGap), /has an amount but is not included/);
  const badRef = pkg();
  badRef.bids[1].scope.framing.ref = "b-9";
  assert.throws(() => validate(badRef), /cites evidence "b-9" that does not exist/);
  const floatCents = pkg();
  floatCents.bids[1].total = 1200.5;
  assert.throws(() => validate(floatCents), /total must be integer cents/);
  const oneBid = pkg();
  oneBid.bids = oneBid.bids.slice(0, 1);
  assert.throws(() => validate(oneBid), /At least two bids/);
});

test("two submissions from one bidder need a governing choice", () => {
  const data = pkg();
  data.bids.push({ ...structuredClone(data.bids[0]), id: "a2", bidderKey: "a", total: 99000 });
  data.bids[0].bidderKey = "a";
  assert.throws(() => validate(structuredClone(data)), /Ask which one governs/);
  data.package.governing = { a: "a2" };
  const a = run(validate(data));
  assert.deepEqual(a.results.map((r) => r.bid.id), ["b", "c", "a2"]);
  assert.deepEqual(a.superseded.map((b) => b.id), ["a"]);
  const switched = run(data, { governing: { a: "a" } });
  assert.ok(switched.results.some((r) => r.bid.id === "a"));
});

test("plugs only land on real gaps and always carry a source", () => {
  const data = validate(pkg());
  assert.throws(() => validateScenario(data, { plugs: { "b:batts": { amount: 1, source: "x" } } }), /already includes/);
  assert.throws(() => validateScenario(data, { plugs: { "a:act": { amount: 1, source: "x" } } }), /only to base scope rows/);
  assert.throws(() => validateScenario(data, { plugs: { "a:batts": { amount: 100, source: " " } } }), /say where the amount came from/);
  assert.throws(() => validateScenario(data, { plugs: { "a:batts": { amount: 1.5, source: "x" } } }), /integer cents/);
  assert.throws(() => validateScenario(data, { plugs: { "z:batts": { amount: 1, source: "x" } } }), /does not exist/);
});

test("outside scope carried with a price suggests a sourced adjustment", () => {
  const data = validate(pkg());
  const a = run(data);
  const b = result(a, "b");
  assert.equal(b.flags.find((f) => f.kind === "outside").amount, 10000);
  const [adj] = b.suggestedAdjustments;
  assert.equal(adj.amount, -10000);
  const applied = run(data, { adjustments: [adj] });
  assert.equal(result(applied, "b").leveled, 110000);
  assert.equal(result(applied, "b").suggestedAdjustments.length, 0);
});

test("itemized lines that don't add up are flagged with a question", () => {
  const data = pkg();
  data.bids[1].total = 121500;
  const b = result(run(validate(data)), "b");
  assert.match(b.flags.find((f) => f.kind === "sum").text, /add up to \$1,200, but the stated total is \$1,215 \(\$15 under\)/);
  assert.ok(b.questions.some((q) => /Which number governs/.test(q.text)));
});

test("carrying a basis item uses stated amounts or rates and needs a figure otherwise", () => {
  const data = pkg();
  data.bids[0].basis = { bond: { treatment: "excluded", percent: 1.5, ref: "a-2" } };
  data.bids[1].basis = { bond: { treatment: "included", ref: "b-1" } };
  validate(data);
  const carried = run(data, { basis: { bond: "carry" } });
  assert.equal(result(carried, "a").basisTotal, 1500);
  assert.equal(result(carried, "b").basisTotal, 0);
  assert.equal(result(carried, "c").complete, false);
  assert.match(result(carried, "c").missing.join(), /bond \(carried, no figure\)/);
  const entered = run(data, { basis: { bond: "carry" }, basisEntries: { "c:bond": { amount: 1650, source: "Surety quote" } } });
  assert.equal(result(entered, "c").basisTotal, 1650);
  assert.equal(result(entered, "c").complete, true);
  assert.match(renderBrief(data, defaultScenario(data), run(data)), /Bond is not on a common basis/);
});

test("an accepted alternate makes bids that didn't price it incomplete", () => {
  const data = pkg();
  data.bids[1].alternates = { alt1: { amount: 5000, printedLabel: "Alt 1", ref: "b-1" } };
  validate(data);
  const a = run(data, { alternates: { alt1: true } });
  assert.equal(result(a, "b").alternateTotal, 5000);
  assert.equal(result(a, "c").complete, false);
  assert.match(result(a, "c").missing.join(), /Alternate 1 \(accepted, not priced\)/);
  const negative = structuredClone(data);
  negative.bids[1].alternates.alt1.amount = -5000;
  assert.throws(() => validate(negative), /add alternate alt1 cannot be negative/);
});

test("missing addenda and silence on addenda are both asked about", () => {
  const data = pkg();
  data.package.addenda.push({ number: 2, date: "2027-02-10", summary: "Adds Alternate 1." });
  data.bids[2].addendaAcknowledged = null;
  const a = run(validate(data));
  assert.match(result(a, "a").flags.find((f) => f.kind === "addenda").text, /Addendum 2/);
  assert.match(result(a, "c").flags.find((f) => f.kind === "addenda").text, /Doesn't say which addenda/);
});

test("money formatting and parsing", () => {
  assert.equal(money(84250000), "$842,500");
  assert.equal(money(1263750), "$12,637.50");
  assert.equal(money(-4600000), "-$46,000");
  assert.equal(money(500, { sign: true }), "+$5");
  assert.equal(money(null), "n/a");
  assert.equal(parseMoney("8,500"), 850000);
  assert.equal(parseMoney("$8,500.5"), 850050);
  assert.equal(parseMoney("-46000"), -4600000);
  assert.equal(parseMoney("abc"), null);
  assert.equal(parseMoney("1.234"), null);
});

test("names and quotes from bids are escaped in the HTML", () => {
  const data = pkg();
  data.bids[0].bidder = '<img src=x onerror="alert(1)">';
  data.bids[0].evidence[0].quote = "</script><script>alert(2)</script>";
  validate(data);
  const html = renderApp(data, defaultScenario(data), run(data));
  assert.ok(!html.includes("<img src=x"));
  assert.ok(!html.includes("</script>"));
  assert.ok(html.includes("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;"));
  const dir = mkdtempSync(join(tmpdir(), "bid-tab-"));
  writeFileSync(join(dir, "data.json"), JSON.stringify(data));
  const out = spawnSync(process.execPath, [level, join(dir, "data.json"), join(dir, "tab.html"), "--brief", join(dir, "brief.md")], { encoding: "utf8" });
  assert.equal(out.status, 0, out.stderr);
  const page = readFileSync(join(dir, "tab.html"), "utf8");
  assert.equal(page.match(/<\/script>/g).length, 3); // the two JSON blocks and the module
});

test("the workbook is a valid xlsx with formulas behind the totals", () => {
  const data = validate(sample());
  const bytes = workbook(data, sampleScenario(), run(data, sampleScenario()));
  const dir = mkdtempSync(join(tmpdir(), "bid-tab-"));
  writeFileSync(join(dir, "tab.xlsx"), bytes);
  const py = spawnSync("python3", ["-c", `
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
assert z.testzip() is None
names = z.namelist()
assert "xl/workbook.xml" in names and "xl/worksheets/sheet6.xml" in names
s = z.read("xl/worksheets/sheet1.xml").decode()
assert "SUMIFS('Gaps and plugs'!E:E" in s and "<f>SUM(B3:F3)</f><v>833700</v>" in s, s[:400]
print("ok")
`, join(dir, "tab.xlsx")], { encoding: "utf8" });
  assert.equal(py.stdout.trim(), "ok", py.stderr);
});

test("CLI: --json summary, exported scenarios, and clear errors", () => {
  const dir = mkdtempSync(join(tmpdir(), "bid-tab-"));
  const data = join(skill, "samples/bid-data.json");
  const json = spawnSync(process.execPath, [level, data, "--json", "--scenario", join(skill, "samples/estimator-scenario.json")], { encoding: "utf8" });
  assert.equal(json.status, 0, json.stderr);
  assert.equal(JSON.parse(json.stdout).lowest, "prairie");
  writeFileSync(join(dir, "bare.json"), JSON.stringify(sampleScenario()));
  const bare = spawnSync(process.execPath, [level, data, "--json", "--scenario", join(dir, "bare.json")], { encoding: "utf8" });
  assert.equal(JSON.parse(bare.stdout).lowest, "prairie");
  const broken = sample();
  delete broken.bids[0].scope.blocking;
  writeFileSync(join(dir, "broken.json"), JSON.stringify(broken));
  const bad = spawnSync(process.execPath, [level, join(dir, "broken.json"), join(dir, "x.html")], { encoding: "utf8" });
  assert.equal(bad.status, 1);
  assert.match(bad.stderr, /bid "northgate": scope row "blocking" is missing/);
  const usage = spawnSync(process.execPath, [level], { encoding: "utf8" });
  assert.equal(usage.status, 2);
});

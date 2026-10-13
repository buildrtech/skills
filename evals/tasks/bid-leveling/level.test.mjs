import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { level, money, validate, workbook } from "../../../skills/bid-leveling/scripts/level.mjs";

const skill = fileURLToPath(new URL("../../../skills/bid-leveling/", import.meta.url));
const script = join(skill, "scripts/level.mjs");
const sample = () => JSON.parse(readFileSync(join(skill, "samples/bid-data.json"), "utf8"));

// A small package for rule-level tests: A excludes batts, C itemizes everything.
function pkg(overrides = {}) {
  const inc = (amount) => (amount === undefined ? { status: "included", quote: "Included." } : { status: "included", amount, quote: `$${amount}` });
  const bid = (bidder, total, scope, extra = {}) => ({ bidder, file: `${bidder}.md`, total, addenda: [1], scope, ...extra });
  return {
    project: "Test Clinic",
    package: "Drywall",
    asOf: "2027-03-02",
    addenda: [1],
    scope: [
      { key: "framing", label: "Framing" },
      { key: "batts", label: "Sound batts" },
    ],
    bids: [
      bid("A", 1000, { framing: inc(), batts: { status: "excluded", quote: "Batts by others." } }),
      bid("B", 1200, { framing: inc(900), batts: inc(150) }),
      bid("C", 1100, { framing: inc(950), batts: inc(200) }),
    ],
    plugs: [],
    ...overrides,
  };
}
const result = (data, bidder) => level(validate(data)).results.find((r) => r.bid.bidder === bidder);

// Read the stored (uncompressed) zip the script writes.
function unzip(bytes) {
  const files = {};
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  for (let at = 0; view.getUint32(at, true) === 0x04034b50; ) {
    const size = view.getUint32(at + 18, true);
    const nameLength = view.getUint16(at + 26, true);
    const name = new TextDecoder().decode(bytes.subarray(at + 30, at + 30 + nameLength));
    files[name] = new TextDecoder().decode(bytes.subarray(at + 30 + nameLength, at + 30 + nameLength + size));
    at += 30 + nameLength + size;
  }
  return files;
}
const cell = (sheet, ref) => sheet.match(new RegExp(`<c r="${ref}"[^>]*>(.*?)</c>`))?.[1] ?? null;

test("bundled workbook matches a fresh build exactly", () => {
  const fresh = workbook(validate(sample()));
  assert.deepEqual(Buffer.from(fresh), readFileSync(join(skill, "samples/output-bid-tab.xlsx")));
});

test("sample: the lowest base bid isn't the lowest complete leveled total", () => {
  const analysis = level(validate(sample()));
  const by = Object.fromEntries(analysis.results.map((r) => [r.bid.bidder.split(" ")[0], r]));
  assert.equal(analysis.lowestBase.bid.bidder, "Northgate Drywall & Acoustics");
  assert.equal(analysis.lowestComplete.bid.bidder, "Prairie Wall & Ceiling Co.");
  assert.deepEqual([by.Northgate.leveled, by.Northgate.open], [80780000, 1]);
  assert.deepEqual([by.Prairie.leveled, by.Prairie.open], [80380000, 0]);
  assert.deepEqual([by.Ridgeline.leveled, by.Ridgeline.open], [82210000, 0]);
  assert.ok(by.Northgate.questions.some((q) => /Confirm you received Addendum 2/.test(q)));
  assert.ok(by.Ridgeline.questions.some((q) => /\$781,000/.test(q)));
});

test("suggested plugs use the highest itemized price and count by default", () => {
  const a = result(pkg(), "A");
  assert.equal(a.gaps.length, 1);
  assert.equal(a.gaps[0].amount, 20000);
  assert.equal(a.gaps[0].carry, true);
  assert.match(a.gaps[0].source, /^Suggested: C itemized \$200 /);
  assert.equal(a.leveled, 120000);
  assert.equal(a.complete, true);
});

test("unclear scope, or scope nobody itemizes, stays open with no plug", () => {
  const unclear = pkg();
  unclear.bids[0].scope.batts = { status: "unclear", quote: "Insulation per plans." };
  const a = result(unclear, "A");
  assert.deepEqual([a.gaps[0].amount, a.gaps[0].carry, a.complete, a.leveled], [null, false, false, 100000]);
  assert.match(a.questions.at(-1), /Does your base bid include sound batts\?/);

  const nobody = pkg();
  for (const bid of nobody.bids.slice(1)) bid.scope.batts = { status: "included", quote: "Batts." };
  assert.match(result(nobody, "A").gaps[0].source, /no other bid itemizes/);
});

test("entered plugs replace suggestions and must land on a gap with a source", () => {
  const data = pkg({ plugs: [{ bidder: "A", scope: "batts", amount: 175.5, source: "GC budget line 0921" }] });
  const a = result(data, "A");
  assert.deepEqual([a.gaps[0].amount, a.leveled], [17550, 117550]);
  assert.equal(a.gaps[0].source, "Entered: GC budget line 0921");

  const bad = pkg({ plugs: [
    { bidder: "B", scope: "batts", amount: 10, source: "x" },
    { bidder: "A", scope: "batts", amount: 10, source: "" },
    { bidder: "Z", scope: "batts", amount: 10, source: "x" },
  ] });
  assert.throws(() => validate(bad), (e) => /nothing to plug/.test(e.message) && /say where the figure came from/.test(e.message) && /no bid from "Z"/.test(e.message));
});

test("validation refuses incomplete or uncited extractions", () => {
  const data = pkg();
  delete data.bids[0].scope.framing;
  data.bids[1].scope.batts = { status: "excluded" };
  data.bids[2].scope.framing = { status: "omitted", amount: 5 };
  data.bids[2].total = 10.005;
  data.bids.push({ ...data.bids[1] });
  assert.throws(() => validate(data), (e) =>
    [/no entry for scope line "framing"/, /B \/ batts: quote the bid's words/, /only included lines carry an amount/, /C: total must be/, /bidder "B" must be named and unique/]
      .every((pattern) => pattern.test(e.message)));
  assert.throws(() => validate(pkg({ bids: pkg().bids.slice(0, 1) })), /at least two bids/);
});

test("addenda that are missing or unstated are asked about", () => {
  const data = pkg({ addenda: [1, 2] });
  data.bids[2].addenda = null;
  assert.match(result(data, "A").questions[0], /acknowledges Addendum 1\. Confirm you received Addendum 2/);
  assert.match(result(data, "C").questions[0], /doesn't say which addenda/);
});

test("the workbook's totals are formulas over the Plugs sheet, with cached values", () => {
  const data = pkg();
  data.bids[0].scope.framing = { status: "unclear", quote: "Framing & board." };
  const files = unzip(workbook(validate(data)));
  assert.match(files["xl/workbook.xml"], /fullCalcOnLoad="1"/);
  assert.match(files["xl/workbook.xml"], /name="Leveled totals".*name="Scope".*name="Plugs".*name="Questions"/);
  const totals = files["xl/worksheets/sheet1.xml"];
  assert.equal(cell(totals, "C2"), `<f>SUMIFS(Plugs!$D:$D,Plugs!$A:$A,$A2,Plugs!$F:$F,&quot;Yes&quot;)</f><v>200</v>`);
  assert.equal(cell(totals, "D2"), "<f>B2+C2</f><v>1200</v>");
  assert.match(cell(totals, "E2"), /COUNTIFS.*<v>1<\/v>$/);
  assert.match(cell(totals, "F2"), /<v>Incomplete<\/v>$/);
  // A is incomplete, so the lowest complete is C at $1,100, not A at $1,200.
  assert.match(cell(totals, "B8"), /_xlfn\.MINIFS.*<v>C<\/v>$/);
  assert.match(cell(totals, "D8"), /<v>1100<\/v>$/);
  const plugs = files["xl/worksheets/sheet3.xml"];
  assert.match(plugs, /Unclear: &quot;Framing &amp; board\.&quot;/);
  assert.match(cell(plugs, "F3"), /Yes/);
});

test("no complete bid is reported as none", () => {
  const data = pkg();
  for (const bid of data.bids) bid.scope.batts = { status: "unclear", quote: "Insulation?" };
  const analysis = level(validate(data));
  assert.equal(analysis.lowestComplete, null);
  assert.match(cell(unzip(workbook(data, analysis))["xl/worksheets/sheet1.xml"], "B8"), /<v>None complete<\/v>$/);
});

test("money formatting", () => {
  assert.equal(money(80380000), "$803,800");
  assert.equal(money(17550), "$175.50");
  assert.equal(money(-950), "-$9.50");
});

test("CLI: writes the workbook, prints --json, and reports every problem", () => {
  const dir = mkdtempSync(join(tmpdir(), "bid-leveling-"));
  const good = join(dir, "bid-data.json");
  writeFileSync(good, JSON.stringify(sample()));
  const out = join(dir, "bid-tab.xlsx");
  const run = spawnSync(process.execPath, [script, good, out], { encoding: "utf8" });
  assert.equal(run.status, 0, run.stderr);
  assert.match(run.stderr, /Lowest complete: Prairie Wall & Ceiling Co\. at \$803,800/);
  assert.deepEqual(readFileSync(out), readFileSync(join(skill, "samples/output-bid-tab.xlsx")));

  const json = JSON.parse(spawnSync(process.execPath, [script, good, "--json"], { encoding: "utf8" }).stdout);
  assert.equal(json.lowestComplete, "Prairie Wall & Ceiling Co.");
  assert.equal(json.results[0].leveled, 807800);

  const bad = join(dir, "bad.json");
  writeFileSync(bad, JSON.stringify({ ...sample(), asOf: "Aug 22", bids: [] }));
  const failed = spawnSync(process.execPath, [script, bad, out], { encoding: "utf8" });
  assert.equal(failed.status, 1);
  assert.match(failed.stderr, /2 problems:\n- asOf must be YYYY-MM-DD\n- at least two bids/);
  assert.equal(spawnSync(process.execPath, [script], { encoding: "utf8" }).status, 2);
});

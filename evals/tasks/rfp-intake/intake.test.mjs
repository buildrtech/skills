import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { analyze, daysBetween, formatDate, money, renderBrief, validate } from "../../../skills/rfp-intake/scripts/intake.mjs";

const skill = fileURLToPath(new URL("../../../skills/rfp-intake/", import.meta.url));
const script = join(skill, "scripts/intake.mjs");
const load = (name) => JSON.parse(readFileSync(join(skill, "samples", name), "utf8"));
const sample = () => ({ data: load("intake-data.json"), profile: load("company-profile.json") });
const gate = (a, key) => a.gates.find((g) => g.key === key);
const run = ({ data, profile }) => {
  validate(data, profile);
  return analyze(data, profile);
};

// A small opportunity that passes everything, for rule-level tests.
function clean() {
  const cite = (page) => ({ doc: "rfp", page });
  const data = {
    opportunity: { name: "Clinic", owner: "County", asOf: "2027-01-04", estimatedValue: 500000000, estimatedValueCite: cite(1) },
    documents: [{ id: "rfp", title: "RFP", supplied: true, pages: 3 }],
    dates: [
      { key: "prebid", label: "Pre-bid", date: "2027-01-08", mandatory: true, cite: cite(1) },
      { key: "bid_due", label: "Bids due", date: "2027-02-01", time: "14:00", tz: "ET", cite: cite(1) },
    ],
    bonds: { text: "100% P&P", performancePercent: 100, cite: cite(2) },
    insurance: [{ key: "umbrella", label: "Umbrella", required: 500000000, cite: cite(2) }],
    licenses: [{ key: "state-gc", label: "State GC", when: "bid", cite: cite(2) }],
    terms: [],
    criteria: [{ key: "fit", score: 4, reason: "Core sector.", cite: cite(3) }, { key: "risk", score: 4, reason: "Standard terms.", cite: cite(3) }],
  };
  const profile = {
    company: "GC",
    licenses: [{ key: "state-gc", label: "State GC" }],
    bonding: { singleLimit: 2000000000, aggregateLimit: 6000000000, currentBonded: 1000000000 },
    insurance: { umbrella: 1000000000 },
    minDaysToBid: 14,
    disqualifyingTerms: [{ key: "no_damages_for_delay", label: "No damages for delay" }],
    criteria: [{ key: "fit", label: "Fit", weight: 60 }, { key: "risk", label: "Risk", weight: 40 }],
    thresholds: { go: 65, noGo: 45, maxUnknownWeight: 25 },
  };
  return { data, profile };
}

test("bundled brief matches a fresh build exactly", () => {
  const dir = mkdtempSync(join(tmpdir(), "intake-"));
  const out = spawnSync(process.execPath, [script, join(skill, "samples/intake-data.json"), join(skill, "samples/company-profile.json"), "--brief", join(dir, "brief.md")], { encoding: "utf8" });
  assert.equal(out.status, 0, out.stderr);
  assert.equal(readFileSync(join(dir, "brief.md"), "utf8"), readFileSync(join(skill, "samples/output-intake-brief.md"), "utf8"));
});

test("sample: go with conditions for the license, pollution cover, and a middling score", () => {
  const a = run(sample());
  assert.equal(a.verdict, "Go with conditions");
  assert.equal(a.score, 63);
  assert.equal(a.unknownWeight, 20);
  assert.equal(gate(a, "license_city-cedar-hollow-class-a").status, "unknown");
  assert.equal(gate(a, "insurance").status, "unknown");
  assert.match(gate(a, "insurance").detail, /pollution liability/);
  assert.equal(gate(a, "bonding").status, "pass");
  assert.match(gate(a, "bonding").detail, /91% of the \$20,000,000 single-job limit/);
  assert.equal(a.risks[0].title, "Bond close to the single-job limit");
  assert.equal(gate(a, "mandatory_prebid").status, "pass");
  assert.deepEqual(a.soon.map((d) => d.key), ["prebid"]);
  assert.equal(a.conditions.length, 3);
});

test("a clean opportunity is a go", () => {
  const a = run(clean());
  assert.ok(a.gates.every((g) => g.status === "pass"), JSON.stringify(a.gates));
  assert.equal(a.score, 80);
  assert.equal(a.verdict, "Go");
});

test("each failed gate forces no-go regardless of score", () => {
  const cases = {
    "license at bid": (x) => (x.profile.licenses = []),
    "over single bond": (x) => (x.data.opportunity.estimatedValue = 2500000000),
    "over aggregate bond": (x) => (x.profile.bonding.currentBonded = 5600000000),
    "short insurance": (x) => (x.profile.insurance.umbrella = 200000000),
    "missed meeting": (x) => (x.data.opportunity.asOf = "2027-01-09"),
    "too little time": (x) => (x.profile.minDaysToBid = 30),
    "disqualifying term": (x) => x.data.terms.push({ key: "no_damages_for_delay", label: "No damages for delay", cite: { doc: "rfp", page: 2 } }),
  };
  for (const [name, mutate] of Object.entries(cases)) {
    const x = clean();
    mutate(x);
    const a = run(x);
    assert.equal(a.verdict, "No-go", name);
    assert.ok(a.gates.some((g) => g.status === "fail"), name);
  }
});

test("unknown company facts make the recommendation conditional, never a pass", () => {
  const x = clean();
  delete x.profile.licenses;
  delete x.profile.minDaysToBid;
  x.profile.insurance = {};
  const a = run(x);
  assert.equal(a.verdict, "Go with conditions");
  assert.deepEqual(a.gates.filter((g) => g.status === "unknown").map((g) => g.key).sort(), ["due_date", "insurance", "license_state-gc"]);
  assert.equal(a.conditions.length, 3);
});

test("a license needed only at contract is a condition, not a failure", () => {
  const x = clean();
  x.data.licenses[0].when = "contract";
  x.profile.licenses = [];
  const a = run(x);
  assert.equal(gate(a, "license_state-gc").status, "unknown");
  assert.equal(a.verdict, "Go with conditions");
});

test("the score uses weights, leaves unknowns out, and respects thresholds", () => {
  const x = clean();
  x.data.criteria[0].score = 2; // 2*60 + 4*40 = 280 of 500
  let a = run(x);
  assert.equal(a.score, 56);
  assert.equal(a.verdict, "Go with conditions");
  x.data.criteria[0].score = 1; // 220 of 500
  a = run(x);
  assert.equal(a.score, 44);
  assert.equal(a.verdict, "No-go");
  const y = clean();
  y.data.criteria[1] = { key: "risk", score: null, reason: "Contract not supplied." };
  a = run(y);
  assert.equal(a.score, 80);
  assert.equal(a.unknownWeight, 40);
  assert.equal(a.verdict, "Go with conditions");
  assert.match(a.conditions.join(), /40% of the criteria weight is unknown/);
});

test("default criteria apply when the profile has none, and the brief says so", () => {
  const x = clean();
  delete x.profile.criteria;
  x.data.criteria = ["owner_relationship", "delivery_contract", "schedule", "scope_fit", "size_fit", "competition", "risk_allocation", "capacity"].map((key) => ({ key, score: 3, reason: "Neutral.", cite: { doc: "rfp", page: 3 } }));
  const a = run(x);
  assert.equal(a.score, 60);
  assert.ok(a.usedDefaults);
  assert.match(renderBrief(x.data, x.profile, a), /the skill's defaults/);
});

test("citations must point at supplied pages that exist", () => {
  const bad = (mutate, pattern) => {
    const x = clean();
    mutate(x);
    assert.throws(() => validate(x.data, x.profile), pattern);
  };
  bad((x) => (x.data.dates[1].cite.page = 9), /page 9 is not in rfp \(3 pages\)/);
  bad((x) => (x.data.dates[1].cite = { doc: "manual", page: 1 }), /cites document "manual", which is not in documents/);
  bad((x) => {
    x.data.documents.push({ id: "manual", title: "Project Manual", supplied: false });
    x.data.insurance[0].cite = { doc: "manual", page: 4 };
  }, /which was not supplied/);
  bad((x) => (x.data.dates = x.data.dates.slice(0, 1)), /must include key "bid_due"/);
  bad((x) => (x.data.criteria = x.data.criteria.slice(0, 1)), /"risk" \(Risk\) is not scored/);
  bad((x) => (x.data.criteria[0].score = 6), /integer 0 to 5/);
  bad((x) => delete x.data.criteria[0].cite, /needs a cite from the solicitation or a profileField/);
  bad((x) => (x.data.opportunity.estimatedValue = 5e8 + 0.5), /integer cents/);
});

test("formatting helpers", () => {
  assert.equal(money(1820000000), "$18,200,000");
  assert.equal(money(null), "not stated");
  assert.equal(formatDate("2026-10-29", "14:00", "CT"), "Thu Oct 29, 2026, 2:00 p.m. CT");
  assert.equal(formatDate("2026-10-08", "10:00"), "Thu Oct 8, 2026, 10:00 a.m.");
  assert.equal(formatDate("2026-10-08", "00:30"), "Thu Oct 8, 2026, 12:30 a.m.");
  assert.equal(daysBetween("2026-10-05", "2026-10-29"), 24);
  assert.equal(daysBetween("2026-12-31", "2027-01-01"), 1);
});

test("CLI: --json, clear errors, and usage", () => {
  const data = join(skill, "samples/intake-data.json");
  const profile = join(skill, "samples/company-profile.json");
  const json = spawnSync(process.execPath, [script, data, profile, "--json"], { encoding: "utf8" });
  assert.equal(json.status, 0, json.stderr);
  assert.equal(JSON.parse(json.stdout).verdict, "Go with conditions");
  const dir = mkdtempSync(join(tmpdir(), "intake-"));
  const broken = load("intake-data.json");
  broken.risks[0].cite.page = 12;
  writeFileSync(join(dir, "broken.json"), JSON.stringify(broken));
  const bad = spawnSync(process.execPath, [script, join(dir, "broken.json"), profile], { encoding: "utf8" });
  assert.equal(bad.status, 1);
  assert.match(bad.stderr, /page 12 is not in itb \(8 pages\)/);
  assert.equal(spawnSync(process.execPath, [script], { encoding: "utf8" }).status, 2);
});

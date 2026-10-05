import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  analyze,
  defaultScenario,
  renderApp,
  renderBrief,
  validate,
  validateScenario,
} from "../../../skills/workforce-planning/scripts/staffing-core.mjs";

const skill = fileURLToPath(new URL("../../../skills/workforce-planning/", import.meta.url));
const plan = join(skill, "scripts/plan.mjs");
const sample = JSON.parse(readFileSync(join(skill, "samples/staffing-data.json"), "utf8"));

// A small, readable company for rule-level tests.
function company(overrides = {}) {
  return {
    company: { name: "Test GC" },
    asOf: "2027-01-04",
    horizon: { start: "2027-01", months: 6 },
    thresholds: { default: 1, "Project Manager": 1.2 },
    roleFits: { Superintendent: { stepUp: ["Assistant Superintendent"] } },
    people: [
      { id: "pm", name: "Pat PM", role: "Project Manager", sectors: ["healthcare"], certs: [] },
      { id: "s1", name: "Sam Super", role: "Superintendent", sectors: ["healthcare"], certs: ["ICRA"] },
      { id: "s2", name: "Lee Super", role: "Superintendent", sectors: ["industrial"], certs: [] },
      { id: "as", name: "Ash Assistant", role: "Assistant Superintendent", sectors: ["healthcare"], certs: ["ICRA"] },
    ],
    projects: [
      {
        id: "HOS", name: "Hospital", sector: "healthcare",
        seats: [
          { role: "Project Manager", from: "2027-01", to: "2027-06", fraction: 1 },
          { role: "Superintendent", from: "2027-01", to: "2027-06", fraction: 1, requires: { certs: ["ICRA"] } },
        ],
      },
    ],
    pursuits: [
      {
        id: "NEW", name: "New Clinic", sector: "healthcare", probability: 0.5, start: "2027-03",
        seats: [{ role: "Superintendent", from: "2027-03", to: "2027-06", fraction: 1 }],
      },
    ],
    assignments: [
      { person: "pm", job: "HOS", role: "Project Manager", from: "2027-01", to: "2027-06", fraction: 1, source: "sheet row 2" },
      { person: "s1", job: "HOS", role: "Superintendent", from: "2027-01", to: "2027-06", fraction: 1, source: "sheet row 3" },
    ],
    ...overrides,
  };
}

const run = (data, scenario) => analyze(validate(structuredClone(data)), scenario ?? defaultScenario(data));

test("bundled outputs are exactly what the script produces from the bundled data", () => {
  const dir = mkdtempSync(join(tmpdir(), "wf-"));
  execFileSync("node", [plan, join(skill, "samples/staffing-data.json"), join(dir, "plan.html"), "--brief", join(dir, "brief.md")], { stdio: "pipe" });
  assert.equal(readFileSync(join(dir, "plan.html"), "utf8"), readFileSync(join(skill, "samples/output-staffing-plan.html"), "utf8"));
  assert.equal(readFileSync(join(dir, "brief.md"), "utf8"), readFileSync(join(skill, "samples/output-staffing-brief.md"), "utf8"));
});

test("the sample surfaces the situations the request asks about", () => {
  const a = run(sample);
  const titles = a.decisions.map((d) => d.title);
  assert.ok(titles.includes("Wash Park Medical Office Building has 2 unfilled seats from Nov 26"));
  assert.ok(titles.includes("Union Station Lofts has 6 unfilled seats from May 27"));
  assert.ok(titles.includes("Arvada Distribution Center needs a Superintendent (25–100%) from Apr 27"));
  assert.ok(titles.includes("Megan Doyle is assigned while on leave"));
  assert.ok(titles.includes("Sam Okafor is over capacity Nov 26 to Feb 27"));
  assert.ok(titles.includes("Dave Kowalski is pencilled on Riverside Medical Office Building without ICRA"));
  // Tony retires after March: his capacity is zero from April.
  assert.equal(a.cells.trusso["2027-04"].capacity, 0);
  assert.equal(a.cells.trusso["2027-03"].committed, 100);
});

test("validation lists every problem instead of guessing", () => {
  const bad = company();
  bad.people.push({ id: "pm", name: "Duplicate", role: "Project Manager" });
  bad.assignments.push({ person: "ghost", job: "NOPE", role: "Project Manager", from: "2027-05", to: "2027-02", fraction: 0.333, source: "" });
  bad.pursuits[0].probability = 1.5;
  bad.projects[0].seats[0].from = "2027-13";
  assert.throws(() => validate(bad), (error) => {
    for (const fragment of ["duplicate id pm", "unknown person ghost", "unknown job NOPE", "from is after to", "whole percent", "probability", "must be a month", "source: must be nonempty text"]) {
      assert.match(error.message, new RegExp(fragment));
    }
    return true;
  });
  assert.throws(() => validate({ company: { name: "x" } }), /people: must be a list/);
  assert.throws(() => validate(null), /must be an object/);
});

test("scenario validation rejects unknown ids, bad modes, and out-of-horizon moves", () => {
  const data = validate(company());
  assert.throws(() => validateScenario(data, { pursuits: { NOPE: "won", NEW: "maybe" }, moves: [] }), /unknown pursuit NOPE[\s\S]*mode must be/);
  assert.throws(
    () => validateScenario(data, { pursuits: {}, moves: [{ person: "s2", job: "HOS", role: "Superintendent", from: "2026-12", to: "2027-02", pct: 50 }] }),
    /inside the horizon/,
  );
  assert.throws(
    () => validateScenario(data, { pursuits: {}, moves: [{ person: "s2", job: "HOS", role: "Superintendent", from: "2027-01", to: "2027-02", pct: 0 }] }),
    /not 0/,
  );
});

test("leave, start, and end dates reduce capacity and expose assigned-while-unavailable conflicts", () => {
  const data = company();
  data.people[0].leave = [{ from: "2027-02", to: "2027-03", fraction: 1, note: "leave" }];
  data.people[1].end = "2027-04";
  data.people.push({ id: "new", name: "Nia New", role: "Project Manager", start: "2027-03" });
  data.assignments.push({ person: "new", job: "HOS", role: "Project Manager", from: "2027-01", to: "2027-01", fraction: 0.5, source: "row 9" });
  const a = run(data);
  assert.equal(a.cells.pm["2027-02"].capacity, 0);
  assert.equal(a.cells.s1["2027-05"].capacity, 0);
  const conflicts = a.conflicts.map((c) => `${c.person} ${c.status} ${c.from}-${c.to}`);
  assert.deepEqual(conflicts.sort(), ["new not started 2027-01-2027-01", "pm leave 2027-02-2027-03", "s1 departed 2027-05-2027-06"]);
  // Leave months are conflicts, not overloads.
  assert.equal(a.overloads.filter((o) => o.person === "pm").length, 0);
});

test("overloads use a rolling three-month window against the role limit", () => {
  const data = company();
  // Superintendent at 150% for one month, 100% otherwise: Jan-Mar average 117% > 100%.
  data.assignments.push({ person: "s1", job: "NEW", role: "Superintendent", from: "2027-03", to: "2027-03", fraction: 0.5, source: "row" });
  let a = run(data, { pursuits: { NEW: "won" }, moves: [] });
  assert.deepEqual(a.overloads.map((o) => [o.person, o.from, o.to, o.peak]), [["s1", "2027-01", "2027-05", 150]]);
  // A PM at 110% stays under a 120% limit.
  const pm = company();
  pm.assignments[0].fraction = 0.9;
  pm.assignments.push({ person: "pm", job: "NEW", role: "Project Manager", from: "2027-01", to: "2027-06", fraction: 0.2, source: "row" });
  a = run(pm, { pursuits: { NEW: "won" }, moves: [] });
  assert.equal(a.overloads.length, 0);
});

test("pursuit modes: weighted is pencilled, won commits, lost removes", () => {
  const data = company();
  data.assignments.push({ person: "s2", job: "NEW", role: "Superintendent", from: "2027-03", to: "2027-06", fraction: 1, source: "row" });
  const weighted = run(data);
  assert.equal(weighted.cells.s2["2027-03"].committed, 0);
  assert.equal(weighted.cells.s2["2027-03"].tentative, 100);
  assert.equal(weighted.seatGaps.filter((g) => g.job === "NEW").length, 0, "pencilled person fills the if-won seat");
  assert.equal(weighted.roleBalance.Superintendent.find((r) => r.month === "2027-03").weighted, 50);

  const won = run(data, { pursuits: { NEW: "won" }, moves: [] });
  assert.equal(won.cells.s2["2027-03"].committed, 100);
  assert.equal(won.roleBalance.Superintendent.find((r) => r.month === "2027-03").weighted, 0);

  const lost = run(data, { pursuits: { NEW: "lost" }, moves: [] });
  assert.equal(lost.cells.s2["2027-03"].tentative, 0);
  assert.equal(lost.seatGaps.filter((g) => g.job === "NEW").length, 0);
});

test("unfilled seats merge into ranges and mark pursuit gaps as if-won", () => {
  const data = company();
  data.assignments[0] = { ...data.assignments[0], to: "2027-02" };
  data.assignments.push({ person: "pm", job: "HOS", role: "Project Manager", from: "2027-03", to: "2027-04", fraction: 0.5, source: "row" });
  const a = run(data);
  const pmGap = a.seatGaps.find((g) => g.job === "HOS" && g.role === "Project Manager");
  assert.deepEqual([pmGap.from, pmGap.to, pmGap.gapMin, pmGap.gap], ["2027-03", "2027-06", 50, 100]);
  const ifWon = a.seatGaps.find((g) => g.job === "NEW");
  assert.equal(ifWon.ifWon, true);
  assert.ok(!a.decisions.some((d) => d.title.includes("New Clinic needs")), "if-won gaps are not committed decisions");
});

test("candidates rank direct fits with certifications above step-ups, with a usable what-if move", () => {
  const data = company();
  data.assignments = data.assignments.filter((x) => x.person !== "s1");
  data.assignments.push({ person: "s1", job: "HOS", role: "Superintendent", from: "2027-01", to: "2027-02", fraction: 1, source: "row" });
  const a = run(data);
  const gap = a.seatGaps.find((g) => g.job === "HOS" && g.role === "Superintendent");
  assert.deepEqual(gap.certs, ["ICRA"]);
  // Sam frees up in March, holds ICRA; Lee is free but lacks ICRA; Ash is a step-up.
  assert.deepEqual(gap.candidates.map((c) => c.person), ["s1", "s2", "as"]);
  assert.deepEqual(gap.candidates[1].missingCerts, ["ICRA"]);
  assert.equal(gap.candidates[2].fit, "step-up");
  assert.deepEqual(gap.candidates[0].move, { person: "s1", job: "HOS", role: "Superintendent", from: "2027-03", to: "2027-06", pct: 100 });
  // Applying the suggested move closes the gap.
  const after = run(data, { pursuits: { NEW: "weighted" }, moves: [gap.candidates[0].move] });
  assert.equal(after.seatGaps.filter((g) => g.job === "HOS" && g.role === "Superintendent").length, 0);
  assert.equal(after.cells.s1["2027-04"].parts[0].moved, true);
});

test("negative moves release allocation and are capped at zero with a visible issue", () => {
  const data = company();
  const a = run(data, { pursuits: { NEW: "weighted" }, moves: [{ person: "pm", job: "HOS", role: "Project Manager", from: "2027-01", to: "2027-01", pct: -100 }] });
  assert.equal(a.cells.pm["2027-01"].committed, 0);
  assert.equal(a.moveIssues.length, 0);
  const over = run(data, { pursuits: { NEW: "weighted" }, moves: [{ person: "s2", job: "HOS", role: "Superintendent", from: "2027-01", to: "2027-01", pct: -50 }] });
  assert.equal(over.cells.s2["2027-01"].committed, 0);
  assert.match(over.moveIssues[0].message, /below 0%/);
});

test("certification gaps flag people in seats they are not certified for", () => {
  const data = company();
  data.assignments[1] = { ...data.assignments[1], person: "s2" };
  const a = run(data);
  assert.deepEqual(a.certIssues.map((c) => [c.person, c.job, c.missing.join(), c.tentative]), [["s2", "HOS", "ICRA", false]]);
  assert.ok(a.decisions.some((d) => d.title === "Lee Super is assigned to Hospital without ICRA" && d.urgency === "now"));
});

test("roll-offs and hiring signals come from month-to-month changes", () => {
  const data = company();
  data.assignments[1] = { ...data.assignments[1], to: "2027-03" };
  const a = run(data);
  assert.deepEqual(a.rollOffs.map((r) => [r.person, r.month, r.from, r.to, r.jobs.join()]), [["s1", "2027-04", 100, 0, "HOS"]]);
  // Two supers, one HOS seat, and a 50% pursuit: not short. Add a second required super seat to force a gap.
  data.projects[0].seats.push({ role: "Superintendent", from: "2027-01", to: "2027-06", fraction: 2 });
  data.people = data.people.filter((p) => p.id !== "as");
  const short = run(data);
  const signal = short.hiring.find((h) => h.role === "Superintendent");
  assert.ok(signal, "superintendents are short");
  assert.ok(signal.peakShort >= 50);
});

test("rendering escapes names and notes from source files", () => {
  const data = company();
  data.people[0].name = `<img src=x onerror=alert(1)>`;
  data.openQuestions = [{ text: `<script>alert(1)</script>`, source: `"><b>` }];
  const a = run(data);
  const html = renderApp(data, defaultScenario(data), a);
  assert.ok(!html.includes("<img src=x"));
  assert.ok(!html.includes("<script>"));
  assert.ok(html.includes("&lt;img src=x onerror=alert(1)&gt;"));
  const brief = renderBrief(data, defaultScenario(data), a);
  assert.ok(brief.startsWith("# Staffing meeting brief: Test GC"));
});

test("the CLI embeds data safely, replays exported scenarios, and rejects bad data", () => {
  const dir = mkdtempSync(join(tmpdir(), "wf-cli-"));
  const data = company();
  data.company.name = "Evil </script><script>alert(1)</script> GC";
  writeFileSync(join(dir, "data.json"), JSON.stringify(data));
  execFileSync("node", [plan, join(dir, "data.json"), join(dir, "plan.html"), "--brief", join(dir, "brief.md")], { stdio: "pipe" });
  const html = readFileSync(join(dir, "plan.html"), "utf8");
  assert.equal((html.match(/<\/script>/g) ?? []).length, 3, "only the three real script tags close");
  assert.ok(html.includes("\\u003c/script>"));

  const exported = { format: "staffing-plan", version: 1, data, scenario: { pursuits: { NEW: "won" }, moves: [] } };
  writeFileSync(join(dir, "scenario.json"), JSON.stringify(exported));
  const out = execFileSync("node", [plan, join(dir, "data.json"), "--json", "--scenario", join(dir, "scenario.json")], { encoding: "utf8" });
  assert.equal(JSON.parse(out).seatGaps.find((g) => g.job === "NEW").ifWon, false);

  writeFileSync(join(dir, "bad.json"), JSON.stringify({ ...data, assignments: [{ person: "nobody" }] }));
  const bad = spawnSync("node", [plan, join(dir, "bad.json"), join(dir, "x.html")], { encoding: "utf8" });
  assert.equal(bad.status, 1);
  assert.match(bad.stderr, /unknown person nobody/);
});

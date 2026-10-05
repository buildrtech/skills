#!/usr/bin/env node
// Go/no-go intake: validate the extraction and company profile, check the
// must-pass gates, score the criteria, and write the Markdown brief.
//
//   node intake.mjs INTAKE.json PROFILE.json [--brief BRIEF.md] [--json]
//
// Dependency-free. Money is integer cents; dates are YYYY-MM-DD.
import { readFile, writeFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";

export const DEFAULT_CRITERIA = [
  { key: "owner_relationship", label: "Owner and relationship", weight: 10 },
  { key: "delivery_contract", label: "Delivery method and contract", weight: 10 },
  { key: "schedule", label: "Schedule and site constraints", weight: 15 },
  { key: "scope_fit", label: "Scope and sector fit", weight: 20 },
  { key: "size_fit", label: "Size fit", weight: 10 },
  { key: "competition", label: "Competition", weight: 10 },
  { key: "risk_allocation", label: "Risk allocation", weight: 15 },
  { key: "capacity", label: "Team and capacity", weight: 10 },
];
export const DEFAULT_THRESHOLDS = { go: 65, noGo: 45, maxUnknownWeight: 25 };
const VERDICTS = { go: "Go", conditions: "Go with conditions", noGo: "No-go" };
const DATE = /^\d{4}-\d{2}-\d{2}$/;
const KEY = /^[a-z0-9][a-z0-9_-]*$/;

// ---------- formatting ----------

export function money(cents) {
  if (cents === null || cents === undefined) return "not stated";
  const abs = Math.abs(cents);
  const text = `$${Math.floor(abs / 100).toLocaleString("en-US")}${abs % 100 ? `.${String(abs % 100).padStart(2, "0")}` : ""}`;
  return cents < 0 ? `-${text}` : text;
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
export function formatDate(iso, time, tz) {
  const [y, m, d] = iso.split("-").map(Number);
  const day = DAYS[new Date(Date.UTC(y, m - 1, d)).getUTCDay()];
  let text = `${day} ${MONTHS[m - 1]} ${d}, ${y}`;
  if (time) {
    const [hh, mm] = time.split(":").map(Number);
    text += `, ${((hh + 11) % 12) + 1}:${String(mm).padStart(2, "0")} ${hh < 12 ? "a.m." : "p.m."}`;
  }
  return tz ? `${text} ${tz}` : text;
}

export function daysBetween(fromIso, toIso) {
  const ms = (iso) => Date.UTC(...iso.split("-").map((n, i) => Number(n) - (i === 1 ? 1 : 0)));
  return Math.round((ms(toIso) - ms(fromIso)) / 86400000);
}

const md = (v) => String(v ?? "").replace(/\|/g, "\\|").replace(/\s*\n\s*/g, " ");
const plural = (n, one, many = `${one}s`) => `${n} ${n === 1 ? one : many}`;

// ---------- validation ----------

export function validate(data, profile) {
  const problems = [];
  const need = (cond, message) => cond || problems.push(message);
  const opp = data?.opportunity ?? {};
  need(typeof opp.name === "string" && opp.name, "opportunity.name is required");
  need(typeof opp.owner === "string" && opp.owner, "opportunity.owner is required");
  need(DATE.test(opp.asOf ?? ""), "opportunity.asOf must be YYYY-MM-DD");
  const docs = new Map();
  for (const [i, doc] of (data?.documents ?? []).entries()) {
    need(KEY.test(doc?.id ?? ""), `documents[${i}].id must be lowercase letters, digits, - or _`);
    need(!docs.has(doc?.id), `document id "${doc?.id}" is repeated`);
    need(typeof doc?.title === "string" && doc.title, `document ${doc?.id} needs a title`);
    need(typeof doc?.supplied === "boolean", `document ${doc?.id}: supplied must be true or false`);
    if (doc?.supplied) need(Number.isInteger(doc?.pages) && doc.pages > 0, `document ${doc?.id}: pages must be a positive integer for a supplied document`);
    docs.set(doc?.id, doc);
  }
  need(docs.size > 0, "documents must list the solicitation documents");
  const checkCite = (cite, where) => {
    if (!cite || typeof cite !== "object") return problems.push(`${where}: needs a cite { doc, page }`);
    const doc = docs.get(cite.doc);
    if (!doc) return problems.push(`${where}: cites document "${cite.doc}", which is not in documents`);
    if (!doc.supplied) return problems.push(`${where}: cites "${cite.doc}", which was not supplied. Facts must come from documents you read`);
    if (!Number.isInteger(cite.page) || cite.page < 1 || cite.page > doc.pages) problems.push(`${where}: page ${cite.page} is not in ${cite.doc} (${doc.pages} pages)`);
  };
  if (opp.estimatedValue !== null && opp.estimatedValue !== undefined) {
    need(Number.isInteger(opp.estimatedValue), "opportunity.estimatedValue must be integer cents or null");
    checkCite(opp.estimatedValueCite, "opportunity.estimatedValue");
  }
  for (const key of ["deliveryMethod", "contract", "location", "sector"]) if (opp[key]) checkCite(opp[`${key}Cite`], `opportunity.${key}`);

  const dateKeys = new Set();
  for (const [i, d] of (data?.dates ?? []).entries()) {
    const where = `dates[${i}] (${d?.label ?? "?"})`;
    need(KEY.test(d?.key ?? ""), `${where}: key is invalid`);
    need(!dateKeys.has(d?.key), `${where}: key is repeated`);
    dateKeys.add(d?.key);
    need(DATE.test(d?.date ?? ""), `${where}: date must be YYYY-MM-DD`);
    need(d?.time === undefined || d?.time === null || /^\d{2}:\d{2}$/.test(d.time), `${where}: time must be HH:MM (24-hour)`);
    checkCite(d?.cite, where);
    if (d?.was) {
      need(DATE.test(d.was.date ?? ""), `${where}: was.date must be YYYY-MM-DD`);
      checkCite(d.was.cite, `${where} (superseded value)`);
    }
  }
  need(dateKeys.has("bid_due"), 'dates must include key "bid_due"');
  for (const [i, c] of (data?.changes ?? []).entries()) {
    need(c?.item && c?.now, `changes[${i}] needs item and now`);
    checkCite(c?.cite, `changes[${i}] (${c?.item})`);
    if (c?.was) checkCite(c?.wasCite, `changes[${i}] (${c?.item}) superseded value`);
  }
  for (const [i, r] of (data?.requirements ?? []).entries()) {
    need(r?.text, `requirements[${i}] needs text`);
    checkCite(r?.cite, `requirements[${i}]`);
  }
  for (const [i, l] of (data?.licenses ?? []).entries()) {
    need(KEY.test(l?.key ?? ""), `licenses[${i}].key is invalid`);
    need(["bid", "award", "contract"].includes(l?.when), `licenses[${i}].when must be bid, award, or contract`);
    checkCite(l?.cite, `licenses[${i}] (${l?.label})`);
  }
  for (const [i, ins] of (data?.insurance ?? []).entries()) {
    need(KEY.test(ins?.key ?? ""), `insurance[${i}].key is invalid`);
    need(Number.isInteger(ins?.required), `insurance[${i}].required must be integer cents`);
    checkCite(ins?.cite, `insurance[${i}] (${ins?.label})`);
  }
  if (data?.bonds) checkCite(data.bonds.cite, "bonds");
  for (const [i, t] of (data?.terms ?? []).entries()) {
    need(KEY.test(t?.key ?? ""), `terms[${i}].key is invalid`);
    checkCite(t?.cite, `terms[${i}] (${t?.label})`);
  }
  for (const [i, r] of (data?.risks ?? []).entries()) {
    need(r?.title && r?.says && r?.consequence, `risks[${i}] needs title, says, and consequence`);
    checkCite(r?.cite, `risks[${i}] (${r?.title})`);
  }
  for (const [i, q] of (data?.ownerQuestions ?? []).entries()) {
    need(q?.text, `ownerQuestions[${i}] needs text`);
    checkCite(q?.cite, `ownerQuestions[${i}]`);
  }
  const criteria = profile?.criteria ?? DEFAULT_CRITERIA;
  const scored = new Map((data?.criteria ?? []).map((c) => [c?.key, c]));
  for (const c of criteria) {
    const s = scored.get(c.key);
    if (!s) {
      problems.push(`criteria: "${c.key}" (${c.label}) is not scored. Score it 0 to 5, or null with a reason if unknown`);
      continue;
    }
    need(s.score === null || (Number.isInteger(s.score) && s.score >= 0 && s.score <= 5), `criteria ${c.key}: score must be an integer 0 to 5, or null`);
    need(typeof s.reason === "string" && s.reason.trim(), `criteria ${c.key}: give a reason`);
    if (s.score !== null) {
      if (s.cite) checkCite(s.cite, `criteria ${c.key}`);
      else need(s.profileField, `criteria ${c.key}: a score needs a cite from the solicitation or a profileField from the company profile`);
    }
  }
  for (const key of scored.keys()) need(criteria.some((c) => c.key === key), `criteria "${key}" is not one of the company's criteria`);

  // Profile.
  need(profile && typeof profile === "object", "A company profile is required (it may be mostly empty)");
  need(typeof profile?.company === "string" && profile.company, "profile.company is required");
  for (const [k, v] of Object.entries(profile?.bonding ?? {})) need(v === null || Number.isInteger(v), `profile.bonding.${k} must be integer cents or null`);
  for (const [k, v] of Object.entries(profile?.insurance ?? {})) need(v === null || Number.isInteger(v), `profile.insurance.${k} must be integer cents or null`);
  if (profile?.criteria) {
    const total = profile.criteria.reduce((s, c) => s + (c.weight ?? 0), 0);
    need(total > 0, "profile.criteria weights must add up to more than zero");
    for (const c of profile.criteria) need(KEY.test(c.key ?? "") && c.label && Number.isFinite(c.weight) && c.weight >= 0, `profile.criteria "${c.key}" needs key, label, and a non-negative weight`);
  }
  const t = { ...DEFAULT_THRESHOLDS, ...(profile?.thresholds ?? {}) };
  need(t.noGo <= t.go, "profile.thresholds.noGo must not be above go");
  if (problems.length) throw new Error(`Intake data has ${plural(problems.length, "problem")}:\n- ${problems.join("\n- ")}`);
  return { data, profile };
}

// ---------- analysis ----------

const cite = (c, docs) => {
  if (!c) return "";
  const doc = docs.get(c.doc);
  return `${doc?.short ?? doc?.title ?? c.doc} p. ${c.page}${c.section ? `, ${c.section}` : ""}`;
};

export function analyze(data, profile) {
  const docs = new Map(data.documents.map((d) => [d.id, d]));
  const c = (x) => cite(x, docs);
  const opp = data.opportunity;
  const asOf = opp.asOf;
  const gates = [];
  const gate = (key, label, status, detail, evidence, action) => gates.push({ key, label, status, detail, evidence, action: action ?? `${label}: ${detail}` });

  // Licenses.
  const held = new Set((profile.licenses ?? []).map((l) => l.key));
  for (const l of data.licenses ?? []) {
    const label = `License: ${l.label}`;
    if (!profile.licenses) gate(`license_${l.key}`, label, "unknown", `Required ${l.when === "bid" ? "at bid" : `before ${l.when}`}. The profile doesn't list licenses.`, c(l.cite), `Confirm you hold the ${l.label} license, required ${l.when === "bid" ? "at bid" : `before ${l.when}`}.`);
    else if (held.has(l.key)) gate(`license_${l.key}`, label, "pass", "Held.", c(l.cite));
    else if (l.when === "bid") gate(`license_${l.key}`, label, "fail", "Required at bid and not held.", c(l.cite));
    else gate(`license_${l.key}`, label, "unknown", `Not held. Required before ${l.when === "award" ? "award" : "contract execution"}, so it can be obtained in time if the issuer's process allows.`, c(l.cite), `Find out how long the ${l.label} license takes; ${profile.company} doesn't hold it and needs it before ${l.when === "award" ? "award" : "contract execution"}.`);
  }

  // Bonding.
  const value = opp.estimatedValue ?? null;
  const bonding = profile.bonding ?? {};
  let bondNote = null;
  if (data.bonds?.performancePercent) {
    if (value === null) gate("bonding", "Bonding capacity", "unknown", "The solicitation states no estimate to test against the bonding limits.", c(data.bonds.cite));
    else if (!Number.isInteger(bonding.singleLimit)) gate("bonding", "Bonding capacity", "unknown", `Estimate ${money(value)}. The profile has no single-job bonding limit.`, c(opp.estimatedValueCite));
    else {
      const share = Math.round((value / bonding.singleLimit) * 100);
      const aggregateAfter = Number.isInteger(bonding.aggregateLimit) && Number.isInteger(bonding.currentBonded) ? bonding.currentBonded + value : null;
      if (value > bonding.singleLimit) gate("bonding", "Bonding capacity", "fail", `Estimate ${money(value)} is over the ${money(bonding.singleLimit)} single-job limit.`, c(opp.estimatedValueCite));
      else if (aggregateAfter !== null && aggregateAfter > bonding.aggregateLimit) gate("bonding", "Bonding capacity", "fail", `Bonded backlog would reach ${money(aggregateAfter)}, over the ${money(bonding.aggregateLimit)} aggregate limit.`, c(opp.estimatedValueCite));
      else {
        const agg = aggregateAfter === null ? " Aggregate capacity is not in the profile." : ` Bonded backlog would be ${money(aggregateAfter)} of ${money(bonding.aggregateLimit)} aggregate.`;
        gate("bonding", "Bonding capacity", aggregateAfter === null ? "unknown" : "pass", `Estimate ${money(value)} is ${share}% of the ${money(bonding.singleLimit)} single-job limit.${agg}`, c(opp.estimatedValueCite));
        if (share >= 85) bondNote = { title: "Bond close to the single-job limit", says: `Estimate ${money(value)} against a ${money(bonding.singleLimit)} single-job limit (${share}%).`, consequence: "A bid over the estimate, or growth through change orders, could exceed what the surety will write. Confirm with the surety before bid day.", cite: opp.estimatedValueCite };
      }
    }
  }

  // Insurance.
  const ins = data.insurance ?? [];
  if (ins.length) {
    const carried = profile.insurance ?? {};
    const short = ins.filter((i) => Number.isInteger(carried[i.key]) && carried[i.key] < i.required);
    const unknown = ins.filter((i) => !Number.isInteger(carried[i.key]));
    if (short.length) gate("insurance", "Insurance limits", "fail", `Below requirement: ${short.map((i) => `${i.label} ${money(carried[i.key])} carried, ${money(i.required)} required`).join("; ")}.`, short.map((i) => c(i.cite)).join("; "));
    else if (unknown.length) gate("insurance", "Insurance limits", "unknown", `Not in the profile: ${unknown.map((i) => `${i.label.toLowerCase()} (${money(i.required)} required)`).join("; ")}.`, unknown.map((i) => c(i.cite)).join("; "), `Ask the broker whether ${profile.company} carries ${unknown.map((i) => `${i.label.toLowerCase()} at ${money(i.required)}`).join(" and ")}.`);
    else gate("insurance", "Insurance limits", "pass", `All ${ins.length} required limits are met.`, [...new Set(ins.map((i) => c(i.cite)))].join("; "));
  }

  // Mandatory events and the due date.
  const dates = (data.dates ?? []).map((d) => ({ ...d, days: daysBetween(asOf, d.date) }));
  for (const d of dates.filter((x) => x.mandatory)) {
    if (d.days < 0) gate(`mandatory_${d.key}`, `Mandatory: ${d.label}`, "fail", `It was ${formatDate(d.date, d.time, d.tz)}, which has passed.`, c(d.cite));
    else gate(`mandatory_${d.key}`, `Mandatory: ${d.label}`, "pass", `${formatDate(d.date, d.time, d.tz)}, in ${plural(d.days, "day")}. Someone must attend.`, c(d.cite));
  }
  const due = dates.find((d) => d.key === "bid_due");
  const minDays = profile.minDaysToBid;
  if (due.days < 0) gate("due_date", "Time to bid", "fail", `Bids were due ${formatDate(due.date, due.time, due.tz)}.`, c(due.cite));
  else if (!Number.isInteger(minDays)) gate("due_date", "Time to bid", "unknown", `${plural(due.days, "day")} to bid. The profile doesn't say how many days the team needs.`, c(due.cite));
  else gate("due_date", "Time to bid", due.days >= minDays ? "pass" : "fail", `${plural(due.days, "day")} to bid; the team needs ${minDays}.`, c(due.cite));

  // Disqualifying terms.
  const disq = profile.disqualifyingTerms;
  if (!disq) gate("terms", "Disqualifying terms", "unknown", "The profile doesn't list terms the company won't accept.", "");
  else {
    const hits = (data.terms ?? []).filter((t) => disq.some((d) => d.key === t.key));
    if (hits.length) gate("terms", "Disqualifying terms", "fail", hits.map((t) => t.label).join("; "), hits.map((t) => c(t.cite)).join("; "));
    else gate("terms", "Disqualifying terms", "pass", `None of the ${plural(disq.length, "term")} the company won't accept: ${disq.map((d) => d.label.toLowerCase()).join(", ")}.`, "");
  }

  // Score.
  const criteria = profile.criteria ?? DEFAULT_CRITERIA;
  const scored = new Map(data.criteria.map((x) => [x.key, x]));
  const totalWeight = criteria.reduce((s, x) => s + x.weight, 0);
  const rows = criteria.map((x) => ({ ...x, ...scored.get(x.key), label: x.label, weight: x.weight }));
  const known = rows.filter((r) => r.score !== null);
  const knownWeight = known.reduce((s, r) => s + r.weight, 0);
  const score = knownWeight ? Math.round((known.reduce((s, r) => s + r.weight * r.score, 0) / (knownWeight * 5)) * 100) : null;
  const unknownWeight = Math.round(((totalWeight - knownWeight) / totalWeight) * 100);
  const thresholds = { ...DEFAULT_THRESHOLDS, ...(profile.thresholds ?? {}) };

  // Recommendation.
  const failed = gates.filter((g) => g.status === "fail");
  const unknownGates = gates.filter((g) => g.status === "unknown");
  const conditions = [];
  let verdict;
  let reason;
  if (failed.length) {
    verdict = VERDICTS.noGo;
    reason = `Fails ${failed.length === 1 ? "a must-pass gate" : `${failed.length} must-pass gates`}: ${failed.map((g) => `${g.label.replace(/^(License|Mandatory): /, "")} (${g.detail.replace(/\.$/, "")})`).join("; ")}.`;
  } else {
    for (const g of unknownGates) conditions.push(g.action);
    if (unknownWeight > thresholds.maxUnknownWeight) conditions.push(`${unknownWeight}% of the criteria weight is unknown (limit ${thresholds.maxUnknownWeight}%): ${rows.filter((r) => r.score === null).map((r) => r.label).join(", ")}.`);
    if (score === null) {
      verdict = VERDICTS.conditions;
      reason = "No criterion could be scored from the documents and profile.";
    } else if (score < thresholds.noGo) {
      verdict = VERDICTS.noGo;
      reason = `Scores ${score}, below the company's no-go line of ${thresholds.noGo}.`;
    } else if (score >= thresholds.go && !conditions.length) {
      verdict = VERDICTS.go;
      reason = `Passes every gate and scores ${score}, at or above the go line of ${thresholds.go}.`;
    } else {
      verdict = VERDICTS.conditions;
      if (score < thresholds.go) conditions.unshift(`Score ${score} is between the no-go line (${thresholds.noGo}) and the go line (${thresholds.go}). Decide on the weakest criteria: ${known.filter((r) => r.score <= 2).map((r) => r.label).join(", ") || "none below 3"}.`);
      reason = `Passes every gate it can check and scores ${score}${score < thresholds.go ? `, short of the go line of ${thresholds.go}` : ""}, but ${plural(conditions.length, "condition needs", "conditions need")} an answer first.`;
    }
  }

  const risks = [...(bondNote ? [bondNote] : []), ...(data.risks ?? [])];
  const teamQuestions = [
    ...unknownGates.map((g) => g.action),
    ...rows.filter((r) => r.score === null).map((r) => `${r.label}: ${r.reason}`),
    ...(data.teamQuestions ?? []).map((q) => q.text ?? q),
  ];
  const soon = dates.filter((d) => d.days >= 0 && d.days <= 7 && (d.mandatory || d.key === "questions_due" || d.key === "bid_due"));
  return { soon, opp, docs, dates, gates, rows, score, unknownWeight, thresholds, verdict, reason, conditions, risks, teamQuestions, usedDefaults: !profile.criteria };
}

// ---------- brief ----------

export function renderBrief(data, profile, a) {
  const c = (x) => cite(x, a.docs);
  const opp = a.opp;
  const L = [];
  L.push(`# Go/no-go brief: ${opp.name}`, "");
  L.push(`${opp.owner}${opp.number ? `, ${opp.number}` : ""}. Prepared for ${profile.company} as of ${formatDate(opp.asOf)}.`, "");
  L.push(`**Recommendation:** ${a.verdict}`, "", `**Why in one line:** ${a.reason}`, "");
  for (const d of a.soon) L.push(`**This week:** ${d.label.toLowerCase()}${d.mandatory ? " (mandatory)" : ""}, ${formatDate(d.date, d.time, d.tz)}, in ${plural(d.days, "day")} (${c(d.cite)}).`, "");
  if (a.conditions.length) {
    L.push("Conditions to clear before committing:", "");
    a.conditions.forEach((x, i) => L.push(`${i + 1}. ${x}`));
    L.push("");
  }
  L.push("This is advice for the go/no-go meeting. The decision is the team's, and nothing here is legal advice.", "");

  L.push("## Gates", "", "Any failed gate means no-go. An unknown gate makes the recommendation conditional.", "");
  L.push("| Gate | Result | Detail | Source |", "|---|---|---|---|");
  for (const g of a.gates) L.push(`| ${md(g.label)} | ${g.status === "pass" ? "Pass" : g.status === "fail" ? "**Fail**" : "Unknown"} | ${md(g.detail)} | ${md(g.evidence) || "company profile"} |`);
  L.push("");

  L.push("## Go/no-go scorecard", "");
  L.push(`Score: **${a.score ?? "n/a"}** out of 100 on the criteria that could be scored. Go at ${a.thresholds.go} or above, no-go below ${a.thresholds.noGo}. Unknown: ${a.unknownWeight}% of the weight (limit ${a.thresholds.maxUnknownWeight}%).${a.usedDefaults ? " The company has not set its own criteria, so these are the skill's defaults." : ""}`, "");
  L.push("| Criterion | Weight | Score (0 to 5) | Why | Source |", "|---|---|---|---|---|");
  for (const r of a.rows) L.push(`| ${md(r.label)} | ${r.weight} | ${r.score ?? "Unknown"} | ${md(r.reason)} | ${r.cite ? md(c(r.cite)) : r.profileField ? `company profile (${md(r.profileField)})` : "none"} |`);
  L.push("");

  L.push("## Key dates", "", "| Milestone | When | Days from today | Source |", "|---|---|---|---|");
  for (const d of [...a.dates].sort((x, y) => x.date.localeCompare(y.date) || (x.time ?? "").localeCompare(y.time ?? ""))) {
    const when = `${formatDate(d.date, d.time, d.tz)}${d.mandatory ? " (mandatory)" : ""}${d.was ? `; was ${formatDate(d.was.date, d.was.time, d.tz)}` : ""}`;
    L.push(`| ${md(d.label)} | ${md(when)} | ${d.days < 0 ? `passed ${-d.days} days ago` : d.days} | ${md(c(d.cite))}${d.was ? `; was ${md(c(d.was.cite))}` : ""} |`);
  }
  L.push("");

  L.push("## Project snapshot", "");
  const snap = [
    ["Owner", opp.owner, opp.ownerCite],
    ["Location", opp.location, opp.locationCite],
    ["Sector", opp.sector, opp.sectorCite],
    ["Delivery", opp.deliveryMethod, opp.deliveryMethodCite],
    ["Contract", opp.contract, opp.contractCite],
    ["Owner's estimate", opp.estimatedValue === undefined || opp.estimatedValue === null ? null : money(opp.estimatedValue), opp.estimatedValueCite],
  ];
  for (const [k, v, ct] of snap) L.push(`- **${k}:** ${v ?? "not stated"}${v && ct ? ` (${c(ct)})` : ""}`);
  L.push("");
  if (data.scope) L.push("## Scope summary", "", `${data.scope.text} (${c(data.scope.cite)})`, "");

  const changes = data.changes ?? [];
  if (changes.length) {
    L.push("## Changed by addenda", "", "| Item | Now | Was | Source |", "|---|---|---|---|");
    for (const ch of changes) L.push(`| ${md(ch.item)} | ${md(ch.now)} | ${md(ch.was ?? "new")} | ${md(c(ch.cite))}${ch.wasCite ? `; was ${md(c(ch.wasCite))}` : ""} |`);
    L.push("");
  }

  L.push("## Requirements to bid", "");
  const groups = new Map();
  for (const r of data.requirements ?? []) groups.set(r.category ?? "Other", [...(groups.get(r.category ?? "Other") ?? []), r]);
  if (data.bonds) L.push(`- **Bonds:** ${data.bonds.text} (${c(data.bonds.cite)})`);
  for (const i of data.insurance ?? []) L.push(`- **Insurance, ${i.label}:** ${money(i.required)}${Number.isInteger(profile.insurance?.[i.key]) ? `; ${profile.company} carries ${money(profile.insurance[i.key])}` : ""} (${c(i.cite)})`);
  for (const l of data.licenses ?? []) L.push(`- **License:** ${l.label}, required ${l.when === "bid" ? "at bid" : `before ${l.when === "award" ? "award" : "contract execution"}`} (${c(l.cite)})`);
  for (const [cat, list] of groups) for (const r of list) L.push(`- **${cat}:** ${r.text}${r.mandatory ? " Grounds for rejection if missed." : ""} (${c(r.cite)})`);
  L.push("");

  L.push("## Risk flags", "");
  if (!a.risks.length) L.push("None found.");
  for (const r of a.risks) L.push(`- **${r.title}.** ${r.says} ${r.consequence}${r.offset ? ` Offsetting: ${r.offset}` : ""} (${c(r.cite)})`);
  L.push("");

  L.push("## Open questions", "", "### For the owner", "");
  const qDeadline = a.dates.find((d) => d.key === "questions_due");
  if (qDeadline) L.push(`Submit before ${formatDate(qDeadline.date, qDeadline.time, qDeadline.tz)} (${c(qDeadline.cite)}).`, "");
  (data.ownerQuestions ?? []).forEach((q, i) => L.push(`${i + 1}. ${q.text} (${c(q.cite)})`));
  if (!(data.ownerQuestions ?? []).length) L.push("None.");
  L.push("");
  L.push("### For the team", "");
  a.teamQuestions.forEach((q, i) => L.push(`${i + 1}. ${q}`));
  if (!a.teamQuestions.length) L.push("None.");
  L.push("");

  L.push("## Sources", "");
  for (const d of data.documents) L.push(`- ${d.title}${d.supplied ? `: ${plural(d.pages, "page")}, reviewed` : ": **not supplied, not reviewed**"}${d.note ? `. ${d.note}` : ""}`);
  L.push(`- Company profile for ${profile.company}${profile.asOf ? ` (as of ${formatDate(profile.asOf)})` : ""}`);
  L.push("");
  L.push("No estimate or pricing has been prepared. Pricing belongs to a separate estimating pass.");
  return `${L.join("\n")}\n`;
}

// ---------- CLI ----------

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
  const briefPath = take("--brief");
  const json = args.includes("--json");
  const [dataPath, profilePath] = args.filter((x) => x !== "--json");
  if (!dataPath || !profilePath) {
    console.error("Usage: node intake.mjs INTAKE.json PROFILE.json [--brief BRIEF.md] [--json]");
    return 2;
  }
  const [data, profile] = await Promise.all([dataPath, profilePath].map(async (p) => JSON.parse(await readFile(p, "utf8"))));
  validate(data, profile);
  const a = analyze(data, profile);
  if (json) {
    const { docs, opp, ...rest } = a;
    process.stdout.write(`${JSON.stringify(rest, null, 2)}\n`);
    return 0;
  }
  const brief = renderBrief(data, profile, a);
  if (briefPath) {
    await writeFile(briefPath, brief);
    console.error(`Wrote ${briefPath}: ${a.verdict}`);
  } else process.stdout.write(brief);
  return 0;
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  main(process.argv.slice(2)).then(
    (code) => process.exit(code),
    (error) => {
      console.error(error.message);
      process.exit(1);
    },
  );
}

// Proposal data: validation and compliance analysis. Dependency-free, shared by
// render.tsx (in the workspace) and scripts/check.mjs (in the skill).
// Money is integer cents. An absent fee is "unpriced", never zero.

const DATE = /^\d{4}-\d{2}-\d{2}$/;
const KEY = /^[A-Za-z0-9][A-Za-z0-9_.-]*$/;
export const SECTION_KINDS = ["letter", "narrative", "projects", "team", "schedule", "fee", "forms", "matrix", "appendix"];
export const SOURCE_KINDS = ["rfp", "library", "prior", "user"];

const plural = (n, one, many = `${one}s`) => `${n} ${n === 1 ? one : many}`;
const md = (v) => String(v ?? "").replace(/\|/g, "\\|").replace(/\s*\n\s*/g, " ");

export function money(cents, currency = "USD") {
  const abs = Math.abs(cents);
  const fmt = new Intl.NumberFormat("en-US", { style: "currency", currency });
  const text = fmt.format(`${Math.floor(abs / 100)}.${String(abs % 100).padStart(2, "0")}`);
  return cents < 0 ? `-${text}` : text;
}

export function monthsBetween(fromIso, toIso) {
  const [y1, m1, d1] = fromIso.split("-").map(Number);
  const [y2, m2, d2] = toIso.split("-").map(Number);
  return (y2 - y1) * 12 + (m2 - m1) - (d2 < d1 ? 1 : 0);
}

// ---------- validation ----------

export function validate(p) {
  const problems = [];
  const need = (cond, message) => cond || problems.push(message);
  const text = (v) => typeof v === "string" && v.trim().length > 0;
  if (!p || typeof p !== "object" || Array.isArray(p)) throw new Error("Proposal must be a JSON object");

  const m = p.meta ?? {};
  for (const k of ["project", "client", "proposer", "reference"]) need(text(m[k]), `meta.${k} is required`);
  need(DATE.test(m.date ?? ""), "meta.date must be YYYY-MM-DD (the draft date)");
  need(["DRAFT", "FOR REVIEW"].includes(m.status), "meta.status must be DRAFT or FOR REVIEW");
  need(/^[A-Z]{3}$/.test(m.currency ?? ""), "meta.currency must be an ISO code");
  if (/^[A-Z]{3}$/.test(m.currency ?? "")) {
    let digits = null;
    try {
      digits = new Intl.NumberFormat("en-US", { style: "currency", currency: m.currency }).resolvedOptions().maximumFractionDigits;
    } catch {
      problems.push(`meta.currency ${m.currency} is not a known currency`);
    }
    if (digits !== null) need(digits === 2, `meta.currency ${m.currency} does not use two decimal places; amounts would be rounded on the page`);
  }
  need(m.freshnessMonths === undefined || (Number.isInteger(m.freshnessMonths) && m.freshnessMonths > 0), "meta.freshnessMonths must be a positive integer");

  // Sources.
  const sources = new Map();
  for (const [i, s] of (p.sources ?? []).entries()) {
    need(KEY.test(s?.id ?? ""), `sources[${i}].id is invalid`);
    need(!sources.has(s?.id), `source id "${s?.id}" is repeated`);
    need(SOURCE_KINDS.includes(s?.kind), `source ${s?.id}: kind must be one of ${SOURCE_KINDS.join(", ")}`);
    need(text(s?.title), `source ${s?.id}: title is required`);
    need(DATE.test(s?.date ?? ""), `source ${s?.id}: date (when it was written or last verified) must be YYYY-MM-DD`);
    sources.set(s?.id, s);
  }
  need(sources.size > 0, "sources must list the RFP, library files, prior proposals, and user inputs used");
  const checkSource = (ref, where) => {
    if (!text(ref?.id)) return problems.push(`${where}: needs a source { id, page? }`);
    const s = sources.get(ref.id);
    if (!s) return problems.push(`${where}: source "${ref.id}" is not in sources`);
    if (ref.page !== undefined) need(Number.isInteger(ref.page) && ref.page > 0 && (!s.pages || ref.page <= s.pages), `${where}: page ${ref.page} is not in ${ref.id}${s.pages ? ` (${s.pages} pages)` : ""}`);
  };

  // RFP.
  const rfp = p.rfp ?? {};
  need(text(rfp.title), "rfp.title is required");
  const reqIds = new Set();
  for (const [i, r] of (rfp.requirements ?? []).entries()) {
    need(KEY.test(r?.id ?? ""), `rfp.requirements[${i}].id is invalid`);
    need(!reqIds.has(r?.id), `requirement id "${r?.id}" is repeated`);
    reqIds.add(r?.id);
    need(["submittal", "criterion", "question", "format"].includes(r?.kind), `requirement ${r?.id}: kind must be submittal, criterion, question, or format`);
    need(text(r?.text), `requirement ${r?.id}: text is required`);
    need(r?.points === undefined || (Number.isFinite(r.points) && r.points >= 0), `requirement ${r?.id}: points must be a non-negative number`);
    checkSource(r?.source, `requirement ${r?.id}`);
  }
  need(reqIds.size > 0, "rfp.requirements must list what the RFP asks for");
  const formIds = new Set();
  for (const [i, f] of (rfp.forms ?? []).entries()) {
    need(KEY.test(f?.id ?? ""), `rfp.forms[${i}].id is invalid`);
    need(!formIds.has(f?.id), `form id "${f?.id}" is repeated`);
    formIds.add(f?.id);
    need(text(f?.name), `form ${f?.id}: name is required`);
    need(typeof f?.included === "boolean", `form ${f?.id}: included must be true or false`);
    checkSource(f?.source, `form ${f?.id}`);
  }
  if (rfp.pageLimit) {
    need(Number.isInteger(rfp.pageLimit.max) && rfp.pageLimit.max > 0, "rfp.pageLimit.max must be a positive integer");
    need(Array.isArray(rfp.pageLimit.excludes ?? []), "rfp.pageLimit.excludes must be a list of section kinds or ids");
    checkSource(rfp.pageLimit.source, "rfp.pageLimit");
  }

  // Facts that can conflict between sources.
  for (const [i, f] of (p.facts ?? []).entries()) {
    need(KEY.test(f?.key ?? ""), `facts[${i}].key is invalid`);
    need(text(f?.label) && text(f?.value), `fact ${f?.key}: label and value are required`);
    need(DATE.test(f?.asOf ?? ""), `fact ${f?.key}: asOf must be YYYY-MM-DD`);
    checkSource(f?.source, `fact ${f?.key}`);
  }

  // Sections.
  const sectionIds = new Set();
  need(Array.isArray(p.sections) && p.sections.length > 0, "sections must list the proposal sections in order");
  for (const [i, s] of (p.sections ?? []).entries()) {
    const where = `section ${s?.id ?? i}`;
    need(KEY.test(s?.id ?? ""), `sections[${i}].id is invalid`);
    need(!sectionIds.has(s?.id), `section id "${s?.id}" is repeated`);
    sectionIds.add(s?.id);
    need(text(s?.title), `${where}: title is required`);
    need(SECTION_KINDS.includes(s?.kind), `${where}: kind must be one of ${SECTION_KINDS.join(", ")}`);
    for (const r of s?.answers ?? []) need(reqIds.has(r), `${where}: answers "${r}", which is not a requirement`);
    if (!["fee", "forms", "matrix"].includes(s?.kind)) need(Array.isArray(s?.items) && s.items.length > 0, `${where}: items must be a nonempty list`);
    for (const [j, item] of (s?.items ?? []).entries()) {
      need(text(item?.text), `${where} item ${j + 1}: text is required`);
      checkSource(item?.source, `${where} item ${j + 1}`);
      for (const [k, extra] of (item?.alsoFrom ?? []).entries()) checkSource(extra, `${where} item ${j + 1} alsoFrom[${k}]`);
      for (const key of item?.facts ?? []) need((p.facts ?? []).some((f) => f.key === key && f.source?.id === item.source?.id), `${where} item ${j + 1}: uses fact "${key}" from ${item?.source?.id}, but no such fact is recorded from that source`);
      if (item?.fields) need(typeof item.fields === "object" && Object.values(item.fields).every((v) => typeof v === "string"), `${where} item ${j + 1}: fields must be text values`);
    }
  }
  for (const f of rfp.forms ?? []) if (f.included) need(sectionIds.has(f.section), `form ${f.id}: included, so section must name the section it is in`);

  // Fee.
  const fee = p.fee ?? {};
  need(["priced", "unpriced"].includes(fee.status), 'fee.status must be "priced" or "unpriced". An absent fee is unpriced, never zero');
  if (fee.status === "unpriced") {
    need(!fee.lines?.length && fee.totalCents === undefined, "an unpriced fee must not carry lines or a total");
    need(text(fee.note), "an unpriced fee needs a note saying what is missing");
  } else if (fee.status === "priced") {
    need(Array.isArray(fee.lines) && fee.lines.some((l) => l.basis === "lump"), "a priced fee needs at least one lump-sum line");
    const ids = new Set();
    for (const [i, l] of (fee.lines ?? []).entries()) {
      need(KEY.test(l?.id ?? "") && !ids.has(l?.id), `fee.lines[${i}].id is invalid or repeated`);
      ids.add(l?.id);
      need(text(l?.label), `fee line ${l?.id}: label is required`);
      need(["lump", "percent"].includes(l?.basis), `fee line ${l?.id}: basis must be lump or percent`);
      if (l?.basis === "lump") need(Number.isSafeInteger(l?.cents) && l.cents > 0, `fee line ${l?.id}: a lump sum must be positive integer cents. If it isn't known, the fee is unpriced`);
      if (l?.basis === "percent") need(typeof l?.percent === "number" && l.percent > 0 && l.percent < 100, `fee line ${l?.id}: percent must be between 0 and 100`);
      checkSource(l?.source, `fee line ${l?.id}`);
    }
    const lump = (fee.lines ?? []).filter((l) => l.basis === "lump" && !l.option).reduce((s, l) => s + (l.cents ?? 0), 0);
    need(fee.totalCents === lump, `fee.totalCents (${fee.totalCents}) must equal the lump-sum lines (${lump}); options stay out of the total`);
  }

  for (const [i, q] of (p.questions ?? []).entries()) need(text(q?.text), `questions[${i}]: text is required`);
  if (problems.length) throw new Error(`Proposal data has ${plural(problems.length, "problem")}:\n- ${problems.join("\n- ")}`);
  return p;
}

// ---------- analysis ----------

// pages: optional { total, bySection: { id: count } } measured from the rendered PDF.
export function analyze(p, pages = null) {
  const sources = new Map(p.sources.map((s) => [s.id, s]));
  const freshness = p.meta.freshnessMonths ?? 12;
  const asOf = p.meta.date;
  const items = p.sections.flatMap((s) => (s.items ?? []).map((item) => ({ section: s, item })));

  // Requirement coverage.
  const matrix = p.rfp.requirements.map((r) => {
    const sections = p.sections.filter((s) => (s.answers ?? []).includes(r.id));
    const support = sections.flatMap((s) => s.items ?? []);
    const weak = support.length > 0 && support.every((it) => sources.get(it.source.id)?.kind === "prior" && !it.confirmed);
    const status = !sections.length ? "gap" : weak ? "unconfirmed" : "answered";
    return { req: r, sections, status };
  });

  // Forms.
  const forms = (p.rfp.forms ?? []).map((f) => ({ form: f, section: p.sections.find((s) => s.id === f.section) ?? null }));

  // Claims lifted from prior proposals and not yet confirmed.
  const unconfirmed = items.filter(({ item }) => sources.get(item.source.id)?.kind === "prior" && !item.confirmed);

  // Stale sources actually used.
  const used = new Set(items.map(({ item }) => item.source.id));
  const stale = p.sources
    .filter((s) => ["library", "prior"].includes(s.kind) && used.has(s.id))
    .map((s) => ({ source: s, months: monthsBetween(s.date, asOf) }))
    .filter((x) => x.months > freshness);

  // Conflicting facts, and items that use a value another source supersedes.
  const byKey = new Map();
  for (const f of p.facts ?? []) byKey.set(f.key, [...(byKey.get(f.key) ?? []), f]);
  const conflicts = [];
  for (const [key, list] of byKey) {
    if (new Set(list.map((f) => f.value)).size < 2) continue;
    const latest = [...list].sort((a, b) => b.asOf.localeCompare(a.asOf))[0];
    const users = items.filter(({ item }) => (item.facts ?? []).includes(key));
    const usesOlder = users.filter(({ item }) => item.source.id !== latest.source.id);
    conflicts.push({ key, label: list[0].label, list, latest, users, usesOlder });
  }

  // Page limit.
  let pageCheck = null;
  if (p.rfp.pageLimit && pages) {
    const excludes = new Set(p.rfp.pageLimit.excludes ?? []);
    const counted = p.sections.filter((s) => !excludes.has(s.kind) && !excludes.has(s.id));
    const countedPages = counted.reduce((n, s) => n + (pages.bySection[s.id] ?? 0), 0);
    pageCheck = { max: p.rfp.pageLimit.max, counted: countedPages, total: pages.total, ok: countedPages <= p.rfp.pageLimit.max, bySection: pages.bySection, excludes: [...excludes] };
  }

  const gaps = matrix.filter((x) => x.status === "gap");
  const missingForms = forms.filter((x) => !x.form.included);
  const blocking = gaps.length + missingForms.length + (pageCheck && !pageCheck.ok ? 1 : 0) + (p.fee.status === "unpriced" ? 1 : 0);
  const warnings = matrix.filter((x) => x.status === "unconfirmed").length + unconfirmed.length + stale.length + conflicts.filter((c) => c.usesOlder.length).length;
  return { matrix, forms, unconfirmed, stale, conflicts, pageCheck, gaps, missingForms, blocking, warnings, freshness };
}

// ---------- compliance check (Markdown) ----------

export function renderCheck(p, a) {
  const src = (ref) => {
    const s = p.sources.find((x) => x.id === ref.id);
    return `${s?.short ?? s?.title ?? ref.id}${ref.page ? ` p. ${ref.page}` : ""}${ref.section ? `, ${ref.section}` : ""}`;
  };
  const L = [];
  L.push(`# Compliance check: ${p.meta.project}`, "");
  L.push(`${p.rfp.title}. Proposal ${p.meta.reference}, ${p.meta.status.toLowerCase()} of ${p.meta.date}.`, "");
  if (a.blocking) L.push(`**Not ready to submit: ${plural(a.blocking, "blocking item")}.** ${plural(a.warnings, "warning")} to review.`, "");
  else L.push(`**No blocking items.** ${a.warnings ? `${plural(a.warnings, "warning")} to review before submission.` : "Nothing else to review."}`, "");
  const blockers = [
    ...a.gaps.map((x) => `Requirement ${x.req.id} is not answered: ${x.req.text} (${src(x.req.source)})`),
    ...a.missingForms.map((x) => `${x.form.name} is required and not included (${src(x.form.source)})`),
    ...(a.pageCheck && !a.pageCheck.ok ? [`${a.pageCheck.counted} counted pages against a limit of ${a.pageCheck.max}`] : []),
    ...(p.fee.status === "unpriced" ? [`The fee is unpriced: ${p.fee.note}`] : []),
  ];
  if (blockers.length) {
    L.push("Blocking:", "");
    blockers.forEach((b, i) => L.push(`${i + 1}. ${b}`));
    L.push("");
  }

  L.push("## Compliance matrix", "", "| Req. | Requirement | Points | Answered in | Status |", "|---|---|---|---|---|");
  for (const x of a.matrix) {
    const status = x.status === "gap" ? "**Gap**" : x.status === "unconfirmed" ? "Unconfirmed claims only" : "Answered";
    L.push(`| ${x.req.id} | ${md(x.req.text)} (${md(src(x.req.source))}) | ${x.req.points ?? ""} | ${md(x.sections.map((s) => s.title).join("; ")) || "nothing"} | ${status} |`);
  }
  L.push("");

  L.push("## Required forms", "", "| Form | Status | Source |", "|---|---|---|");
  for (const x of a.forms) L.push(`| ${md(x.form.name)} | ${x.form.included ? `Included in ${md(x.section?.title)}` : "**Missing**"} | ${md(src(x.form.source))} |`);
  if (!a.forms.length) L.push("| none required | | |");
  L.push("");

  L.push("## Page limit", "");
  if (!p.rfp.pageLimit) L.push("The RFP states no page limit.");
  else if (!a.pageCheck) L.push(`Limit ${p.rfp.pageLimit.max} pages (${src(p.rfp.pageLimit.source)}). Not checked: run with \`--pdf\` on the rendered proposal.`);
  else {
    L.push(`${a.pageCheck.counted} of ${a.pageCheck.max} pages counted (${a.pageCheck.ok ? "within the limit" : "**over the limit**"}). The PDF has ${a.pageCheck.total} pages in all; ${a.pageCheck.excludes.length ? `${a.pageCheck.excludes.join(", ")} sections and the cover don't count` : "the cover doesn't count"} (${src(p.rfp.pageLimit.source)}).`, "");
    L.push("| Section | Pages | Counts |", "|---|---|---|");
    for (const s of p.sections) L.push(`| ${md(s.title)} | ${a.pageCheck.bySection[s.id] ?? 0} | ${a.pageCheck.excludes.includes(s.kind) || a.pageCheck.excludes.includes(s.id) ? "no" : "yes"} |`);
  }
  L.push("");

  L.push("## Claims to confirm", "");
  if (!a.unconfirmed.length && !a.stale.length && !a.conflicts.length) L.push("None.");
  for (const { section, item } of a.unconfirmed) L.push(`- **From a prior proposal, not yet confirmed** (${section.title}): "${item.text}" (${src(item.source)}). Confirm it is still true, or add it to the library.`);
  for (const x of a.stale) L.push(`- **Stale source:** ${x.source.title} was last verified ${x.source.date}, ${x.months} months ago (limit ${a.freshness}).`);
  for (const c of a.conflicts) {
    const values = c.list.map((f) => `${f.value} in ${src(f.source)} (as of ${f.asOf})`).join("; ");
    const use = c.usesOlder.length ? ` **The proposal uses the older value** in ${c.usesOlder.map(({ section }) => section.title).join(", ")}.` : c.users.length ? ` The proposal uses the latest value.` : "";
    L.push(`- **${c.label} differs between sources:** ${values}.${use}`);
  }
  L.push("");

  L.push("## Fee", "");
  if (p.fee.status === "unpriced") L.push(`Unpriced draft: ${p.fee.note}`);
  else {
    L.push("| Line | Basis | Amount | Source |", "|---|---|---|---|");
    for (const l of p.fee.lines) L.push(`| ${md(l.label)}${l.option ? " (option)" : ""} | ${l.basis === "lump" ? "Lump sum" : "Percent"} | ${l.basis === "lump" ? money(l.cents, p.meta.currency) : `${l.percent}%${l.of ? ` of ${l.of}` : ""}`} | ${md(src(l.source))} |`);
    L.push("", `Lump-sum total ${money(p.fee.totalCents, p.meta.currency)}, reconciled to the lines. Percentage fees are not added to it.`);
  }
  L.push("");
  if ((p.questions ?? []).length) {
    L.push("## Open questions", "");
    p.questions.forEach((q, i) => L.push(`${i + 1}. ${q.text}`));
    L.push("");
  }
  L.push("Draft for review. Nothing has been submitted or signed.");
  return `${L.join("\n")}\n`;
}

// Bid leveling core: validation, leveling arithmetic, HTML, brief, and XLSX.
// Dependency-free so the same module runs under Node and inside the HTML tab.
// Money is integer cents everywhere. Nothing here invents a price: suggested
// plugs come only from other bidders' itemized lines and never count until
// the estimator accepts them.

const STATUSES = ["included", "excluded", "omitted", "unknown"];
const GAP_STATUSES = ["excluded", "omitted", "unknown"];
const ROW_CLASSES = ["base", "outside", "review"];
const ALT_KINDS = ["add", "deduct"];
const BASIS_TREATMENTS = ["included", "excluded", "notStated"];
const KEY = /^[a-z0-9][a-z0-9_-]*$/;

// ---------- formatting ----------

export function money(cents, { sign = false } = {}) {
  if (cents === null || cents === undefined) return "n/a";
  const negative = cents < 0;
  const abs = Math.abs(cents);
  const dollars = Math.floor(abs / 100).toLocaleString("en-US");
  const rest = abs % 100;
  const text = `$${dollars}${rest ? `.${String(rest).padStart(2, "0")}` : ""}`;
  if (negative) return `-${text}`;
  return sign && cents > 0 ? `+${text}` : text;
}

// Parse what a person types into an amount field ("8,500", "$8,500.00", "-46000").
export function parseMoney(text) {
  const cleaned = String(text ?? "").trim().replace(/[$,\s]/g, "");
  if (!/^-?\d+(\.\d{1,2})?$/.test(cleaned)) return null;
  const [whole, frac = ""] = cleaned.replace("-", "").split(".");
  const cents = Number(whole) * 100 + Number(frac.padEnd(2, "0"));
  return cleaned.startsWith("-") ? -cents : cents;
}

export function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

const md = (value) => String(value ?? "").replace(/\|/g, "\\|").replace(/\s*\n\s*/g, " ");
const plural = (n, one, many = `${one}s`) => `${n} ${n === 1 ? one : many}`;
// "Exterior sheathing" reads as "exterior sheathing" mid-sentence; acronyms stay.
const lower = (label) => (/^[A-Z][a-z]/.test(label) && !/^[A-Z][a-z]+ \d/.test(label) ? label[0].toLowerCase() + label.slice(1) : label);
const STATUS_LABEL = { included: "Included", excluded: "Excluded", omitted: "Not mentioned", unknown: "Unclear" };

// ---------- validation ----------

const isInt = (v) => Number.isInteger(v);
const isCents = (v) => v === null || isInt(v);

export function validate(data) {
  const problems = [];
  const need = (cond, message) => {
    if (!cond) problems.push(message);
  };
  if (!data || typeof data !== "object") throw new Error("Bid data must be a JSON object.");
  const pkg = data.package ?? {};
  need(typeof pkg.name === "string" && pkg.name, "package.name is required");
  need(typeof pkg.project === "string" && pkg.project, "package.project is required");
  need(/^\d{4}-\d{2}-\d{2}$/.test(pkg.asOf ?? ""), "package.asOf must be YYYY-MM-DD");
  const rows = Array.isArray(pkg.rows) ? pkg.rows : [];
  need(rows.length > 0, "package.rows must list the scope rows");
  const rowKeys = new Set();
  for (const [i, row] of rows.entries()) {
    need(KEY.test(row?.key ?? ""), `package.rows[${i}].key must be lowercase letters, digits, - or _`);
    need(!rowKeys.has(row?.key), `package.rows key "${row?.key}" is repeated`);
    rowKeys.add(row?.key);
    need(typeof row?.label === "string" && row.label, `package.rows "${row?.key}" needs a label`);
    need(ROW_CLASSES.includes(row?.class ?? "base"), `package.rows "${row?.key}" class must be one of ${ROW_CLASSES.join(", ")}`);
  }
  const altKeys = new Set();
  for (const [i, alt] of (pkg.alternates ?? []).entries()) {
    need(KEY.test(alt?.key ?? ""), `package.alternates[${i}].key is invalid`);
    need(!altKeys.has(alt?.key), `package.alternates key "${alt?.key}" is repeated`);
    altKeys.add(alt?.key);
    need(typeof alt?.label === "string" && alt.label, `package.alternates "${alt?.key}" needs a label`);
    need(ALT_KINDS.includes(alt?.kind), `package.alternates "${alt?.key}" kind must be add or deduct`);
  }
  const basisKeys = new Set();
  for (const [i, item] of (pkg.basis ?? []).entries()) {
    need(KEY.test(item?.key ?? ""), `package.basis[${i}].key is invalid`);
    need(!basisKeys.has(item?.key), `package.basis key "${item?.key}" is repeated`);
    basisKeys.add(item?.key);
    need(typeof item?.label === "string" && item.label, `package.basis "${item?.key}" needs a label`);
  }
  const addenda = new Set((pkg.addenda ?? []).map((a) => a.number));
  for (const a of pkg.addenda ?? []) need(isInt(a?.number) && a.number > 0, "package.addenda numbers must be positive integers");

  const bids = Array.isArray(data.bids) ? data.bids : [];
  need(bids.length >= 2, "At least two bids are needed to level");
  const ids = new Set();
  const byBidder = new Map();
  for (const bid of bids) {
    const where = `bid "${bid?.id ?? "?"}"`;
    need(KEY.test(bid?.id ?? ""), `${where}: id must be lowercase letters, digits, - or _`);
    need(!ids.has(bid?.id), `${where}: id is repeated`);
    ids.add(bid?.id);
    need(typeof bid?.bidder === "string" && bid.bidder, `${where}: bidder name is required`);
    const bidderKey = bid?.bidderKey ?? bid?.id;
    byBidder.set(bidderKey, [...(byBidder.get(bidderKey) ?? []), bid?.id]);
    need(isCents(bid?.total ?? null), `${where}: total must be integer cents or null`);
    need(Array.isArray(bid?.files) && bid.files.length > 0, `${where}: files must list the source documents`);
    const refs = new Set();
    for (const ev of bid?.evidence ?? []) {
      need(typeof ev?.ref === "string" && ev.ref, `${where}: every evidence entry needs a ref`);
      need(!refs.has(ev?.ref), `${where}: evidence ref ${ev?.ref} is repeated`);
      refs.add(ev?.ref);
      need(typeof ev?.quote === "string" && ev.quote, `${where}: evidence ${ev?.ref} needs a quote`);
      need((bid.files ?? []).includes(ev?.file), `${where}: evidence ${ev?.ref} file "${ev?.file}" is not in files`);
    }
    const cite = (ref, label) => need(refs.has(ref), `${where}: ${label} cites evidence "${ref}" that does not exist`);
    if (bid?.total !== null) cite(bid?.totalRef, "total");
    if (bid?.addendaAcknowledged !== null && bid?.addendaAcknowledged !== undefined) {
      need(Array.isArray(bid.addendaAcknowledged), `${where}: addendaAcknowledged must be a list or null`);
      for (const n of bid.addendaAcknowledged ?? []) need(addenda.has(n), `${where}: acknowledges Addendum ${n}, which the package does not list`);
    }
    const scope = bid?.scope ?? {};
    for (const key of rowKeys) {
      const cell = scope[key];
      if (!cell) {
        problems.push(`${where}: scope row "${key}" is missing. Re-read the bid and record it as included, excluded, omitted, or unknown`);
        continue;
      }
      need(STATUSES.includes(cell.status), `${where}: ${key} status must be one of ${STATUSES.join(", ")}`);
      need(isCents(cell.amount ?? null), `${where}: ${key} amount must be integer cents or null`);
      need(cell.status === "included" || cell.amount === undefined || cell.amount === null, `${where}: ${key} has an amount but is not included`);
      cite(cell.ref, key);
    }
    for (const key of Object.keys(scope)) need(rowKeys.has(key), `${where}: scope row "${key}" is not in package.rows`);
    for (const [key, alt] of Object.entries(bid?.alternates ?? {})) {
      need(altKeys.has(key), `${where}: alternate "${key}" is not in package.alternates`);
      need(isCents(alt?.amount ?? null), `${where}: alternate ${key} amount must be integer cents or null`);
      const kind = (pkg.alternates ?? []).find((a) => a.key === key)?.kind;
      if (isInt(alt?.amount)) {
        need(kind !== "add" || alt.amount >= 0, `${where}: add alternate ${key} cannot be negative`);
        need(kind !== "deduct" || alt.amount <= 0, `${where}: deduct alternate ${key} must be zero or negative`);
      }
      cite(alt?.ref, `alternate ${key}`);
    }
    for (const [i, alt] of (bid?.proposedAlternates ?? []).entries()) {
      need(typeof alt?.label === "string" && alt.label, `${where}: proposedAlternates[${i}] needs a label`);
      need(isCents(alt?.amount ?? null), `${where}: proposedAlternates[${i}] amount must be integer cents or null`);
      cite(alt?.ref, `proposed alternate ${i + 1}`);
    }
    for (const [key, b] of Object.entries(bid?.basis ?? {})) {
      need(basisKeys.has(key), `${where}: basis "${key}" is not in package.basis`);
      need(BASIS_TREATMENTS.includes(b?.treatment), `${where}: basis ${key} treatment must be one of ${BASIS_TREATMENTS.join(", ")}`);
      need(isCents(b?.amount ?? null), `${where}: basis ${key} amount must be integer cents or null`);
      need(b?.percent === undefined || b?.percent === null || (typeof b.percent === "number" && b.percent >= 0 && b.percent < 100), `${where}: basis ${key} percent must be a number from 0 to 100`);
      if (b?.treatment !== "notStated") cite(b?.ref, `basis ${key}`);
    }
    for (const [i, u] of (bid?.unitPrices ?? []).entries()) {
      need(isCents(u?.price ?? null), `${where}: unitPrices[${i}] price must be integer cents or null`);
      cite(u?.ref, `unit price ${i + 1}`);
    }
    for (const q of bid?.qualifications ?? []) if (q?.ref) cite(q.ref, "qualification");
    for (const q of bid?.questions ?? []) if (q?.ref) cite(q.ref, "question");
  }
  for (const [bidderKey, list] of byBidder) {
    if (list.length < 2) continue;
    const governing = pkg.governing?.[bidderKey];
    need(list.includes(governing), `Bidder "${bidderKey}" sent ${list.length} submissions (${list.join(", ")}). Ask which one governs and record it in package.governing.${bidderKey}`);
  }
  if (problems.length) throw new Error(`Bid data has ${plural(problems.length, "problem")}:\n- ${problems.join("\n- ")}`);
  return data;
}

// ---------- scenario ----------

export function defaultScenario(data) {
  return { plugs: {}, adjustments: [], alternates: {}, basis: {}, basisEntries: {}, governing: { ...(data.package.governing ?? {}) } };
}

export function validateScenario(data, raw = {}) {
  const scenario = { ...defaultScenario(data), ...raw };
  scenario.governing = { ...(data.package.governing ?? {}), ...(raw.governing ?? {}) };
  const problems = [];
  const bids = new Map(data.bids.map((b) => [b.id, b]));
  const rows = new Map(data.package.rows.map((r) => [r.key, r]));
  for (const [bidderKey, id] of Object.entries(scenario.governing)) {
    const bid = bids.get(id);
    if (!bid || (bid.bidderKey ?? bid.id) !== bidderKey) problems.push(`Governing bid for ${bidderKey} is "${id}", which is not one of that bidder's submissions`);
  }
  for (const [target, plug] of Object.entries(scenario.plugs ?? {})) {
    const [bidId, rowKey] = target.split(":");
    const bid = bids.get(bidId);
    const row = rows.get(rowKey);
    if (!bid || !row) {
      problems.push(`Plug ${target} names a bid or scope row that does not exist`);
      continue;
    }
    if (row.class !== "base" && row.class !== undefined) problems.push(`Plug ${target}: plugs apply only to base scope rows`);
    if (bid.scope[rowKey].status === "included") problems.push(`Plug ${target}: ${bid.bidder} already includes ${row.label}`);
    if (!isInt(plug?.amount)) problems.push(`Plug ${target}: amount must be integer cents`);
    if (!String(plug?.source ?? "").trim()) problems.push(`Plug ${target}: say where the amount came from`);
  }
  for (const [i, adj] of (scenario.adjustments ?? []).entries()) {
    if (!bids.has(adj?.bid)) problems.push(`Adjustment ${i + 1} names bid "${adj?.bid}", which does not exist`);
    if (!isInt(adj?.amount)) problems.push(`Adjustment ${i + 1}: amount must be integer cents`);
    if (!String(adj?.description ?? "").trim() || !String(adj?.source ?? "").trim()) problems.push(`Adjustment ${i + 1}: description and source are required`);
  }
  const altKeys = new Set((data.package.alternates ?? []).map((a) => a.key));
  for (const key of Object.keys(scenario.alternates ?? {})) if (!altKeys.has(key)) problems.push(`Alternate "${key}" is not in the package`);
  const basisKeys = new Set((data.package.basis ?? []).map((b) => b.key));
  for (const [key, mode] of Object.entries(scenario.basis ?? {})) {
    if (!basisKeys.has(key)) problems.push(`Basis "${key}" is not in the package`);
    if (!["asBid", "carry"].includes(mode)) problems.push(`Basis ${key} must be asBid or carry`);
  }
  for (const [target, entry] of Object.entries(scenario.basisEntries ?? {})) {
    const [bidId, key] = target.split(":");
    if (!bids.has(bidId) || !basisKeys.has(key)) problems.push(`Basis entry ${target} names a bid or basis item that does not exist`);
    if (!isInt(entry?.amount)) problems.push(`Basis entry ${target}: amount must be integer cents`);
    if (!String(entry?.source ?? "").trim()) problems.push(`Basis entry ${target}: say where the amount came from`);
  }
  if (problems.length) throw new Error(`Scenario has ${plural(problems.length, "problem")}:\n- ${problems.join("\n- ")}`);
  return scenario;
}

// ---------- analysis ----------

const rowClass = (row) => row.class ?? "base";

export function governingBids(data, scenario) {
  const governing = scenario.governing ?? {};
  return data.bids.filter((bid) => {
    const key = bid.bidderKey ?? bid.id;
    return !(key in governing) || governing[key] === bid.id;
  });
}

// Suggested plug for one gap: the highest itemized price other bidders gave for
// the same scope. A leveling convention, not what this bidder would charge.
function suggestPlug(bid, row, active) {
  if (!["excluded", "omitted"].includes(bid.scope[row.key].status)) return null;
  const priced = active
    .filter((other) => other.id !== bid.id)
    .map((other) => ({ other, cell: other.scope[row.key] }))
    .filter(({ cell }) => cell.status === "included" && isInt(cell.amount));
  if (!priced.length) return null;
  priced.sort((a, b) => b.cell.amount - a.cell.amount || a.other.bidder.localeCompare(b.other.bidder));
  const top = priced[0];
  const others = priced.slice(1).map(({ other, cell }) => `${other.bidder} ${money(cell.amount)}`);
  const basis = priced.length === 1 ? "the only itemized price" : `the highest of ${priced.length} itemized prices`;
  return {
    amount: top.cell.amount,
    source: `${top.other.bidder}'s itemized line (${top.cell.ref}), ${basis} for this scope${others.length ? `; others: ${others.join(", ")}` : ""}. A leveling figure, not a price from ${bid.bidder}.`,
  };
}

export function analyze(data, scenario) {
  const active = governingBids(data, scenario);
  const superseded = data.bids.filter((b) => !active.includes(b));
  const rows = data.package.rows;
  const alternates = data.package.alternates ?? [];
  const basisItems = data.package.basis ?? [];
  const addenda = data.package.addenda ?? [];

  const results = active.map((bid) => {
    const gaps = [];
    const flags = [];
    const questions = [];
    const missing = [];
    let plugs = 0;
    let pending = 0;
    let pendingUnresolved = 0;

    for (const row of rows) {
      const cell = bid.scope[row.key];
      const klass = rowClass(row);
      if (klass === "base" && cell.status !== "included") {
        const plug = scenario.plugs?.[`${bid.id}:${row.key}`] ?? null;
        const suggestion = plug ? null : suggestPlug(bid, row, active);
        gaps.push({ row, cell, plug, suggestion });
        if (plug) plugs += plug.amount;
        else {
          missing.push(`${lower(row.label)} (${STATUS_LABEL[cell.status].toLowerCase()}, no plug)`);
          if (suggestion) pending += suggestion.amount;
          else pendingUnresolved += 1;
        }
      }
      if (klass === "outside" && cell.status === "included") {
        if (isInt(cell.amount)) flags.push({ kind: "outside", text: `Carries ${lower(row.label)} (${money(cell.amount)}) inside the bid. It belongs to another package.`, ref: cell.ref, row, amount: cell.amount });
        else flags.push({ kind: "outside", text: `Carries ${lower(row.label)} inside the bid without a price. Ask for the breakout.`, ref: cell.ref, row });
      }
      if (klass === "review" && cell.status !== "omitted") flags.push({ kind: "review", text: `${row.label}: ${STATUS_LABEL[cell.status].toLowerCase()}. Decide whether this belongs in the package.`, ref: cell.ref });
      if (klass === "outside") {
        // Excluding another package's work is correct; nothing to ask.
      } else if (cell.status === "excluded") questions.push({ text: `Your bid excludes ${lower(row.label)}${cell.note ? ` (${cell.note})` : ""}. What would you add to include it?`, ref: cell.ref });
      else if (cell.status === "omitted") questions.push({ text: `Your bid doesn't mention ${lower(row.label)}. Is it included? If not, what would you add?`, ref: cell.ref });
      else if (cell.status === "unknown") questions.push({ text: `Please confirm whether ${lower(row.label)} is in your price${cell.note ? `. Your bid says: ${cell.note}` : ""}.`, ref: cell.ref });
      if (klass === "outside" && cell.status === "included" && !isInt(cell.amount)) questions.push({ text: `Please break ${lower(row.label)} out of your total so it can be moved to its own package.`, ref: cell.ref });
    }

    // Itemized lines vs stated total, when the bid itemizes every included row.
    const included = rows.filter((r) => bid.scope[r.key].status === "included");
    const itemizedAll = included.length > 0 && included.every((r) => isInt(bid.scope[r.key].amount));
    if (itemizedAll && isInt(bid.total)) {
      const inTotal = Object.values(bid.basis ?? {}).filter((b) => b.treatment === "included" && b.inTotal && isInt(b.amount));
      const sum = included.reduce((s, r) => s + bid.scope[r.key].amount, 0) + inTotal.reduce((s, b) => s + b.amount, 0);
      if (sum !== bid.total) {
        flags.push({ kind: "sum", text: `Itemized lines add up to ${money(sum)}, but the stated total is ${money(bid.total)} (${money(Math.abs(sum - bid.total))} ${sum > bid.total ? "over" : "under"}).`, ref: bid.totalRef });
        questions.push({ text: `Your itemized lines add up to ${money(sum)}, but your total is ${money(bid.total)}. Which number governs?`, ref: bid.totalRef });
      }
    }

    // Addenda.
    if (addenda.length) {
      if (bid.addendaAcknowledged === null || bid.addendaAcknowledged === undefined) {
        flags.push({ kind: "addenda", text: "Doesn't say which addenda the price includes." });
        questions.push({ text: `Please confirm your price includes ${addenda.map((a) => `Addendum ${a.number}`).join(" and ")}.` });
      } else {
        for (const a of addenda.filter((x) => !bid.addendaAcknowledged.includes(x.number))) {
          flags.push({ kind: "addenda", text: `Doesn't acknowledge Addendum ${a.number} (${a.date}): ${a.summary.replace(/\.$/, "")}.` });
          questions.push({ text: `Your bid doesn't acknowledge Addendum ${a.number}, which ${lower(a.summary.replace(/\.$/, ""))}. Does your price include it?` });
        }
      }
    }

    // Adjustments.
    const adjustments = (scenario.adjustments ?? []).filter((a) => a.bid === bid.id);
    const adjustmentTotal = adjustments.reduce((s, a) => s + a.amount, 0);
    const suggestedAdjustments = flags
      .filter((f) => f.kind === "outside" && isInt(f.amount))
      .filter((f) => !adjustments.some((a) => a.from === `${bid.id}:${f.row.key}`))
      .map((f) => ({ from: `${bid.id}:${f.row.key}`, bid: bid.id, amount: -f.amount, description: `Remove ${lower(f.row.label)}; it belongs to another package`, source: `${bid.bidder}'s itemized line (${f.ref})` }));

    // Alternates.
    let alternateTotal = 0;
    const altCells = alternates.map((alt) => {
      const priced = bid.alternates?.[alt.key];
      const accepted = Boolean(scenario.alternates?.[alt.key]);
      if (accepted) {
        if (priced && isInt(priced.amount)) alternateTotal += priced.amount;
        else missing.push(`${lower(alt.label)} (accepted, not priced)`);
      }
      if (!priced || !isInt(priced.amount)) questions.push({ text: `Please price ${lower(alt.label)}.`, ref: priced?.ref });
      return { alt, priced, accepted };
    });
    for (const p of bid.proposedAlternates ?? []) flags.push({ kind: "proposed", text: `Offers an alternate nobody asked for: ${p.label} (${money(p.amount)}). Not comparable across bids.`, ref: p.ref });

    // Common basis for tax, bond, and similar items.
    let basisTotal = 0;
    const basisCells = basisItems.map((item) => {
      const b = bid.basis?.[item.key] ?? { treatment: "notStated" };
      const mode = scenario.basis?.[item.key] ?? "asBid";
      const entry = scenario.basisEntries?.[`${bid.id}:${item.key}`] ?? null;
      let add = 0;
      let needs = false;
      let how = "";
      if (mode === "carry" && b.treatment !== "included") {
        if (entry) {
          add = entry.amount;
          how = entry.source;
        } else if (isInt(b.amount)) {
          add = b.amount;
          how = `${bid.bidder}'s stated amount (${b.ref})`;
        } else if (typeof b.percent === "number" && isInt(bid.total)) {
          add = Math.round((bid.total * b.percent) / 100);
          how = `${b.percent}% of the base bid, ${bid.bidder}'s stated rate (${b.ref})`;
        } else {
          needs = true;
          missing.push(`${lower(item.label)} (carried, no figure)`);
        }
      }
      basisTotal += add;
      if (b.treatment === "notStated") questions.push({ text: `Does your price include ${lower(item.label)}? If not, what would you add?` });
      else if (b.treatment === "excluded" && !isInt(b.amount) && typeof b.percent !== "number") questions.push({ text: `Your bid excludes ${lower(item.label)}. What would you add for it?`, ref: b.ref });
      return { item, b, mode, entry, add, needs, how };
    });

    for (const q of bid.questions ?? []) questions.push(q);
    if (!isInt(bid.total)) missing.unshift("no stated total");

    const leveled = isInt(bid.total) ? bid.total + plugs + adjustmentTotal + alternateTotal + basisTotal : null;
    const complete = leveled !== null && missing.length === 0;
    // What the total would be if the estimator accepted every suggestion.
    const suggestedAdj = suggestedAdjustments.reduce((s, a) => s + a.amount, 0);
    const otherMissing = missing.length - gaps.filter((g) => !g.plug).length;
    const withSuggestions = leveled === null ? null : leveled + pending + suggestedAdj;
    const completeWithSuggestions = leveled !== null && pendingUnresolved === 0 && otherMissing === 0;

    return {
      bid, gaps, flags, questions, missing, plugs, adjustments, adjustmentTotal, suggestedAdjustments,
      altCells, alternateTotal, basisCells, basisTotal, leveled, complete, withSuggestions, completeWithSuggestions,
      pendingSuggestions: gaps.filter((g) => !g.plug && g.suggestion).length + suggestedAdjustments.length,
    };
  });

  const completeResults = results.filter((r) => r.complete).sort((a, b) => a.leveled - b.leveled);
  const lowest = completeResults[0] ?? null;
  const lowestBase = results.filter((r) => isInt(r.bid.total)).sort((a, b) => a.bid.total - b.bid.total)[0] ?? null;
  const openGaps = results.reduce((n, r) => n + r.gaps.filter((g) => !g.plug).length, 0);
  const pendingSuggestions = results.reduce((n, r) => n + r.pendingSuggestions, 0);
  return { results, superseded, lowest, lowestBase, openGaps, pendingSuggestions };
}

// ---------- shared text ----------

function headline(analysis) {
  const { lowest, results } = analysis;
  const incomplete = results.filter((r) => !r.complete);
  if (lowest) {
    const tail = incomplete.length ? ` ${plural(incomplete.length, "bid is", "bids are")} still incomplete.` : " Every bid is complete.";
    return { lead: `Lowest complete leveled total: ${lowest.bid.bidder} at ${money(lowest.leveled)}.`, tail };
  }
  return { lead: "No bid is complete yet.", tail: ` ${plural(analysis.openGaps, "gap needs", "gaps need")} a plug before the totals compare.` };
}

function statusText(r) {
  if (r.leveled === null) return "No stated total";
  if (r.complete) return "Complete";
  return `Incomplete: ${plural(r.missing.length, "open item")}`;
}

// ---------- HTML ----------

const h = escapeHtml;
const refLink = (bid, ref) => (ref ? ` <a class="ref" href="#ev-${h(bid.id)}-${h(ref)}">${h(ref)}</a>` : "");

export function renderApp(data, scenario, analysis) {
  const pkg = data.package;
  const { results } = analysis;
  const head = headline(analysis);
  const lowestId = analysis.lowest?.bid.id;
  const out = [];

  out.push(`<header class="top"><div>
<p class="eyebrow">Bid tab · ${h(pkg.project)} · as of ${h(pkg.asOf)}</p>
<h1>${h(pkg.name)}</h1>
<p class="summary"><strong>${h(head.lead)}</strong>${h(head.tail)}${analysis.pendingSuggestions ? ` ${h(plural(analysis.pendingSuggestions, "suggestion waits", "suggestions wait"))} for your review.` : ""}</p>
</div>
<div class="actions">
<button type="button" id="export-json">Export scenario</button>
<label class="file">Import scenario<input type="file" id="import-json" accept="application/json,.json"></label>
<button type="button" id="export-xlsx">Export to Excel</button>
<button type="button" id="reset">Reset</button>
</div></header>
<p class="status" id="status" role="status" aria-live="polite"></p>`);

  // Totals.
  out.push(`<section aria-labelledby="totals-h"><h2 id="totals-h">Leveled totals</h2>
<p class="hint">Leveled total = base bid + plugs + adjustments + accepted alternates + common-basis items. Suggested plugs don't count until you accept them.</p>
<div class="table-wrap"><table><thead><tr><th scope="col">Bidder</th><th scope="col" class="num">Base bid</th><th scope="col" class="num">Plugs</th><th scope="col" class="num">Adjustments</th><th scope="col" class="num">Alternates</th><th scope="col" class="num">Basis</th><th scope="col" class="num">Leveled total</th><th scope="col">Status</th><th scope="col" class="num">If suggestions accepted</th></tr></thead><tbody>`);
  for (const r of results) {
    const cls = r.bid.id === lowestId ? ' class="low"' : "";
    out.push(`<tr${cls}><th scope="row">${h(r.bid.bidder)}${r.bid.id === lowestId ? ' <span class="pill">Lowest complete</span>' : ""}<span class="sub">${h(r.bid.files.join(", "))}</span></th>
<td class="num">${money(r.bid.total)}${refLink(r.bid, r.bid.totalRef)}</td><td class="num">${money(r.plugs)}</td><td class="num">${money(r.adjustmentTotal)}</td><td class="num">${money(r.alternateTotal)}</td><td class="num">${money(r.basisTotal)}</td>
<td class="num total">${money(r.leveled)}</td><td class="${r.complete ? "ok" : "warn"}">${h(r.complete ? "Complete" : r.leveled === null ? "No stated total" : `Incomplete: ${plural(r.missing.length, "open item")}`)}</td>
<td class="num">${r.withSuggestions === null ? "n/a" : `${money(r.withSuggestions)}${r.completeWithSuggestions ? "" : " <span class='sub'>still incomplete</span>"}`}</td></tr>`);
  }
  out.push("</tbody></table></div>");
  for (const note of basisMismatch(pkg, scenario, analysis)) out.push(`<p class="hint warn-note">${h(note.replace("Carry it in the tab to level it.", "Carry it below to level it."))}</p>`);
  if (analysis.superseded.length) out.push(`<p class="hint">Superseded and not leveled: ${h(analysis.superseded.map((b) => `${b.bidder} (${b.files.join(", ")})`).join("; "))}.</p>`);
  out.push("</section>");

  // Gaps and plugs.
  out.push(`<section aria-labelledby="gaps-h"><h2 id="gaps-h">Gaps and plugs <span class="sub">${h(plural(analysis.openGaps, "open gap"))}</span></h2>
<p class="hint">Each gap is scope the package needs that a bid excludes, doesn't mention or leaves unclear. Accept a suggestion, enter your own figure with its source, or leave it open and ask the bidder.</p>`);
  const allGaps = results.flatMap((r) => r.gaps.map((g) => ({ r, g })));
  const gapRows = [...allGaps.filter(({ g }) => !g.plug), ...allGaps.filter(({ g }) => g.plug)];
  if (!gapRows.length) out.push('<p class="empty">No gaps on base scope.</p>');
  else {
    out.push('<ul class="gaps">');
    for (const { r, g } of gapRows) {
      const id = `${r.bid.id}:${g.row.key}`;
      const domId = id.replace(":", "--");
      if (g.plug) {
        out.push(`<li class="gap done"><div class="gap-head"><strong>${h(r.bid.bidder)}</strong> · ${h(g.row.label)}: plug ${money(g.plug.amount)} <button type="button" class="small" data-clear-plug="${h(id)}">Clear</button></div>
<p class="says">${h(STATUS_LABEL[g.cell.status])}${g.cell.note ? `: ${h(g.cell.note)}` : ""}${refLink(r.bid, g.cell.ref)}. ${h(g.plug.kind === "accepted" ? "Accepted suggestion" : "Your figure")}: ${h(g.plug.source)}</p>`);
      } else {
        out.push(`<li class="gap open"><div class="gap-head"><strong>${h(r.bid.bidder)}</strong> · ${h(g.row.label)}</div>
<p class="says">${h(STATUS_LABEL[g.cell.status])}${g.cell.note ? `: ${h(g.cell.note)}` : ""}${refLink(r.bid, g.cell.ref)}</p>`);
        if (g.suggestion) out.push(`<p class="suggest">Suggested ${money(g.suggestion.amount)} <span class="sub">${h(g.suggestion.source)}</span> <button type="button" class="small" data-accept-plug="${h(id)}">Accept</button></p>`);
        else out.push(`<p class="suggest none">${g.cell.status === "unknown" ? "Unclear in the bid, so no suggestion. Ask the bidder, or enter your own figure." : "No other bid itemizes this scope. Enter your own figure, or ask the bidder."}</p>`);
        out.push(`<form class="plug-form" data-plug="${h(id)}"><label>Plug<input name="amount" id="amt-${h(domId)}" inputmode="decimal" placeholder="$0" autocomplete="off"></label><label class="wide">Source<input name="source" id="src-${h(domId)}" placeholder="e.g. our estimate, line 06 10 00" autocomplete="off"></label><button type="submit">Use</button></form>`);
      }
      out.push("</li>");
    }
    out.push("</ul>");
  }
  out.push("</section>");

  // Adjustments.
  const suggestedAdj = results.flatMap((r) => r.suggestedAdjustments);
  const madeAdj = scenario.adjustments ?? [];
  out.push(`<section aria-labelledby="adj-h"><h2 id="adj-h">Adjustments</h2>
<p class="hint">Changes to a bid for reasons other than a gap, such as removing work that belongs to another package.</p>`);
  if (suggestedAdj.length) {
    out.push('<ul class="gaps">');
    for (const a of suggestedAdj) {
      const bid = data.bids.find((b) => b.id === a.bid);
      out.push(`<li class="gap open"><div class="gap-head"><strong>${h(bid.bidder)}</strong> · ${h(a.description)}</div><p class="suggest">Suggested ${money(a.amount)} <span class="sub">${h(a.source)}</span> <button type="button" class="small" data-accept-adjustment="${h(a.from)}">Accept</button></p></li>`);
    }
    out.push("</ul>");
  }
  if (madeAdj.length) {
    out.push('<ul class="moves">');
    madeAdj.forEach((a, i) => {
      const bid = data.bids.find((b) => b.id === a.bid);
      out.push(`<li><span><strong>${h(bid?.bidder ?? a.bid)}</strong> ${money(a.amount, { sign: true })}: ${h(a.description)} <span class="sub">(${h(a.source)})</span></span><button type="button" class="small" data-remove-adjustment="${i}">Remove</button></li>`);
    });
    out.push("</ul>");
  } else if (!suggestedAdj.length) out.push('<p class="empty">No adjustments.</p>');
  out.push(`<form class="plug-form adj-form" id="adj-form"><label>Bidder<select name="bid" id="adj-bid">${results.map((r) => `<option value="${h(r.bid.id)}">${h(r.bid.bidder)}</option>`).join("")}</select></label><label>Amount<input name="amount" id="adj-amount" inputmode="decimal" placeholder="-$0" autocomplete="off"></label><label class="wide">What and why<input name="description" id="adj-desc" autocomplete="off"></label><label class="wide">Source<input name="source" id="adj-src" autocomplete="off"></label><button type="submit">Add adjustment</button></form></section>`);

  // Common basis.
  if ((pkg.basis ?? []).length) {
    out.push(`<section aria-labelledby="basis-h"><h2 id="basis-h">Tax, bond and other basis items</h2>
<p class="hint">Choose whether every bid should carry each item. "Carry" adds it where a bid leaves it out, using the bidder's own stated amount or rate. Where the bid gives none, enter a figure.</p>`);
    for (const item of pkg.basis) {
      const mode = scenario.basis?.[item.key] ?? "asBid";
      out.push(`<div class="basis"><fieldset class="segmented"><legend class="sr-only">${h(item.label)}</legend>${["asBid", "carry"].map((m) => `<label class="seg${m === mode ? " on" : ""}"><input type="radio" name="basis-${h(item.key)}" value="${m}" data-basis="${h(item.key)}"${m === mode ? " checked" : ""}>${m === "asBid" ? "As bid" : "Carry in all bids"}</label>`).join("")}</fieldset> <strong>${h(item.label)}</strong></div>
<div class="table-wrap"><table><thead><tr><th scope="col">Bidder</th><th scope="col">Bid says</th><th scope="col" class="num">Added</th></tr></thead><tbody>`);
      for (const r of results) {
        const c = r.basisCells.find((x) => x.item.key === item.key);
        const says = c.b.treatment === "included" ? `Included${isInt(c.b.amount) ? ` (${money(c.b.amount)})` : ""}` : c.b.treatment === "excluded" ? `Excluded${typeof c.b.percent === "number" ? `; add ${c.b.percent}%` : isInt(c.b.amount) ? `; add ${money(c.b.amount)}` : ""}` : "Not stated";
        const id = `${r.bid.id}:${item.key}`;
        let added = c.add ? `${money(c.add)} <span class="sub">${h(c.how)}</span>` : "none";
        if (c.entry) added += ` <button type="button" class="small" data-clear-basis="${h(id)}">Clear</button>`;
        if (c.needs) added = `<form class="plug-form inline" data-basis-entry="${h(id)}"><label>Amount<input name="amount" id="bamt-${h(id.replace(":", "--"))}" inputmode="decimal" autocomplete="off"></label><label class="wide">Source<input name="source" id="bsrc-${h(id.replace(":", "--"))}" autocomplete="off"></label><button type="submit">Use</button></form>`;
        out.push(`<tr><th scope="row">${h(r.bid.bidder)}</th><td>${h(says)}${refLink(r.bid, c.b.ref)}</td><td class="num${c.needs ? " warn" : ""}">${added}</td></tr>`);
      }
      out.push("</tbody></table></div>");
    }
    out.push("</section>");
  }

  // Alternates.
  out.push(`<section aria-labelledby="alt-h"><h2 id="alt-h">Alternates</h2><p class="hint">Turn an alternate on to carry it in every leveled total. A bid that didn't price it becomes incomplete.</p>`);
  if ((pkg.alternates ?? []).length) {
    out.push(`<div class="table-wrap"><table><thead><tr><th scope="col">Alternate</th><th scope="col">In totals</th>${results.map((r) => `<th scope="col" class="num">${h(r.bid.bidder)}</th>`).join("")}</tr></thead><tbody>`);
    for (const alt of pkg.alternates) {
      const on = Boolean(scenario.alternates?.[alt.key]);
      out.push(`<tr><th scope="row">${h(alt.label)} <span class="sub">${h(alt.kind)}</span></th><td><label class="toggle"><input type="checkbox" data-alternate="${h(alt.key)}"${on ? " checked" : ""}> ${on ? "Accepted" : "Not accepted"}</label></td>`);
      for (const r of results) {
        const c = r.altCells.find((x) => x.alt.key === alt.key);
        out.push(`<td class="num${on && !isInt(c.priced?.amount) ? " warn" : ""}">${c.priced ? `${money(c.priced.amount)}${refLink(r.bid, c.priced.ref)}` : "Not offered"}</td>`);
      }
      out.push("</tr>");
    }
    out.push("</tbody></table></div>");
  }
  const proposed = results.flatMap((r) => (r.bid.proposedAlternates ?? []).map((p) => ({ r, p })));
  if (proposed.length) out.push(`<p class="hint">Offered without being asked: ${proposed.map(({ r, p }) => `${h(r.bid.bidder)}, ${h(p.label)} ${money(p.amount)}${refLink(r.bid, p.ref)}`).join("; ")}. Not in the totals and not comparable across bids.</p>`);
  out.push("</section>");

  // Matrix.
  out.push(`<section aria-labelledby="matrix-h"><h2 id="matrix-h">Scope matrix</h2>${pkg.scopeSource ? `<p class="hint">Rows from ${h(pkg.scopeSource)}.</p>` : '<p class="hint">No scope sheet was provided. Rows are the scope the bids mention.</p>'}
<div class="table-wrap matrix"><table><thead><tr><th scope="col">Scope</th>${results.map((r) => `<th scope="col">${h(r.bid.bidder)}</th>`).join("")}</tr></thead><tbody>`);
  for (const klass of ROW_CLASSES) {
    const classRows = pkg.rows.filter((row) => rowClass(row) === klass);
    if (!classRows.length) continue;
    if (klass !== "base") out.push(`<tr class="group"><th colspan="${results.length + 1}">${klass === "outside" ? "Belongs to another package" : "Needs a decision"}</th></tr>`);
    for (const row of classRows) {
      out.push(`<tr><th scope="row">${h(row.label)}</th>`);
      for (const r of results) {
        const cell = r.bid.scope[row.key];
        const plug = scenario.plugs?.[`${r.bid.id}:${row.key}`];
        const gap = klass === "base" && cell.status !== "included";
        out.push(`<td class="st-${cell.status}${gap ? (plug ? " plugged" : " gap") : ""}">${h(STATUS_LABEL[cell.status])}${isInt(cell.amount) ? ` ${money(cell.amount)}` : ""}${refLink(r.bid, cell.ref)}${plug ? `<span class="sub">plug ${money(plug.amount)}</span>` : ""}</td>`);
      }
      out.push("</tr>");
    }
  }
  out.push("</tbody></table></div></section>");

  // Flags and questions.
  out.push(`<section aria-labelledby="q-h"><h2 id="q-h">Review flags and questions for bidders</h2><div class="bidders">`);
  for (const r of results) {
    out.push(`<div class="bidder"><h3>${h(r.bid.bidder)}</h3>`);
    if (r.flags.length) out.push(`<ul class="flags">${r.flags.map((f) => `<li>${h(f.text)}${refLink(r.bid, f.ref)}</li>`).join("")}</ul>`);
    out.push(r.questions.length ? `<ol class="questions">${r.questions.map((q) => `<li>${h(q.text)}${refLink(r.bid, q.ref)}</li>`).join("")}</ol>` : '<p class="empty">No questions.</p>');
    out.push("</div>");
  }
  out.push("</div>");
  if ((data.openQuestions ?? []).length) out.push(`<h3>Open questions for you</h3><ul class="questions">${data.openQuestions.map((q) => `<li>${h(q.text)}${q.source ? ` <span class="sub">(${h(q.source)})</span>` : ""}</li>`).join("")}</ul>`);
  out.push("</section>");

  // Unit prices and qualifications.
  const units = results.flatMap((r) => (r.bid.unitPrices ?? []).map((u) => ({ r, u })));
  const quals = results.flatMap((r) => (r.bid.qualifications ?? []).map((q) => ({ r, q })));
  if (units.length || quals.length) {
    out.push(`<section aria-labelledby="terms-h"><h2 id="terms-h">Unit prices and qualifications</h2><p class="hint">Listed for comparison. Never added to the totals.</p>`);
    if (units.length) out.push(`<div class="table-wrap"><table><thead><tr><th scope="col">Bidder</th><th scope="col">Unit price</th><th scope="col" class="num">Price</th></tr></thead><tbody>${units.map(({ r, u }) => `<tr><th scope="row">${h(r.bid.bidder)}</th><td>${h(u.description)}</td><td class="num">${money(u.price)} / ${h(u.unit)}${refLink(r.bid, u.ref)}</td></tr>`).join("")}</tbody></table></div>`);
    if (quals.length) out.push(`<ul class="quals">${quals.map(({ r, q }) => `<li><strong>${h(r.bid.bidder)}:</strong> ${h(q.text)}${refLink(r.bid, q.ref)}</li>`).join("")}</ul>`);
    out.push("</section>");
  }

  // Evidence.
  out.push(`<section aria-labelledby="ev-h"><h2 id="ev-h">Evidence</h2><p class="hint">Every amount and status in this tab cites a quote from the bid.</p><div class="bidders">`);
  for (const bid of [...results.map((r) => r.bid), ...analysis.superseded]) {
    out.push(`<div class="bidder"><h3>${h(bid.bidder)}${analysis.superseded.includes(bid) ? ' <span class="sub">superseded</span>' : ""}</h3><dl class="evidence">${(bid.evidence ?? []).map((ev) => `<div id="ev-${h(bid.id)}-${h(ev.ref)}"><dt>${h(ev.ref)} <span class="sub">${h(ev.file)}, ${h(ev.location)}</span></dt><dd>${h(ev.quote)}</dd></div>`).join("")}</dl></div>`);
  }
  out.push("</div></section>");
  out.push(`<p class="foot">A comparison, not an award recommendation. Plugs and basis figures are the estimator's judgment. Nothing here was sent to a bidder.</p>`);
  return out.join("\n");
}

// ---------- Markdown brief ----------

// Basis items left "as bid" where the bids disagree, so the totals are not on one basis.
function basisMismatch(pkg, scenario, analysis) {
  const notes = [];
  for (const item of pkg.basis ?? []) {
    if ((scenario.basis?.[item.key] ?? "asBid") !== "asBid") continue;
    const groups = { included: [], excluded: [], notStated: [] };
    for (const r of analysis.results) {
      const b = r.bid.basis?.[item.key] ?? { treatment: "notStated" };
      groups[b.treatment].push(`${r.bid.bidder}${b.treatment === "excluded" && typeof b.percent === "number" ? ` (adds ${b.percent}%)` : ""}`);
    }
    const used = Object.entries(groups).filter(([, list]) => list.length);
    if (used.length < 2) continue;
    const words = { included: "included by", excluded: "excluded by", notStated: "not stated by" };
    notes.push(`${item.label} is not on a common basis: ${used.map(([k, list]) => `${words[k]} ${list.join(", ")}`).join("; ")}. Carry it in the tab to level it.`);
  }
  return notes;
}

export function renderBrief(data, scenario, analysis) {
  const pkg = data.package;
  const head = headline(analysis);
  const lines = [];
  lines.push(`# Bid leveling brief: ${pkg.name}`, "");
  lines.push(`${pkg.project}. As of ${pkg.asOf}.${pkg.bidDue ? ` Bids due ${pkg.bidDue}.` : ""} ${plural(analysis.results.length, "bid")} leveled${analysis.superseded.length ? `, ${analysis.superseded.length} superseded` : ""}.`, "");
  lines.push(`**${head.lead}**${head.tail}`, "");
  if (analysis.lowestBase && analysis.lowestBase !== analysis.lowest) {
    const r = analysis.lowestBase;
    lines.push(`The lowest base bid is ${r.bid.bidder} at ${money(r.bid.total)}, but ${r.complete ? `it levels to ${money(r.leveled)}` : `it is incomplete with ${plural(r.missing.length, "open item")}`}.`, "");
  }
  lines.push("## Leveled totals", "");
  lines.push("| Bidder | Base bid | Plugs | Adjustments | Alternates | Basis | Leveled total | Status | If suggestions accepted |");
  lines.push("|---|---|---|---|---|---|---|---|---|");
  for (const r of analysis.results) {
    lines.push(`| ${md(r.bid.bidder)} | ${money(r.bid.total)} | ${money(r.plugs)} | ${money(r.adjustmentTotal)} | ${money(r.alternateTotal)} | ${money(r.basisTotal)} | ${money(r.leveled)} | ${md(statusText(r))} | ${r.withSuggestions === null ? "n/a" : `${money(r.withSuggestions)}${r.completeWithSuggestions ? "" : " (still incomplete)"}`} |`);
  }
  lines.push("");
  const accepted = Object.values(scenario.alternates ?? {}).some(Boolean);
  const carried = (pkg.basis ?? []).filter((b) => scenario.basis?.[b.key] === "carry").map((b) => b.label.toLowerCase());
  lines.push(`Assumptions: ${accepted ? `alternates accepted: ${pkg.alternates.filter((a) => scenario.alternates?.[a.key]).map((a) => a.label).join(", ")}` : "no alternates accepted"}; ${carried.length ? `carried in every bid: ${carried.join(", ")}` : "tax, bond and similar items as bid"}.`, "");
  for (const note of basisMismatch(pkg, scenario, analysis)) lines.push(`- ${note}`);
  if (basisMismatch(pkg, scenario, analysis).length) lines.push("");

  lines.push("## Plugs to confirm", "");
  const plugRows = analysis.results.flatMap((r) => r.gaps.map((g) => ({ r, g })));
  if (!plugRows.length) lines.push("No gaps on base scope.", "");
  else {
    lines.push("| Bidder | Scope | Bid says | Plug | Source |", "|---|---|---|---|---|");
    for (const { r, g } of plugRows) {
      const says = `${STATUS_LABEL[g.cell.status]}${g.cell.note ? `: ${g.cell.note}` : ""} (${g.cell.ref})`;
      const plug = g.plug ? money(g.plug.amount) : g.suggestion ? `open; suggested ${money(g.suggestion.amount)}` : "open";
      const source = g.plug ? g.plug.source : g.suggestion ? g.suggestion.source : g.cell.status === "unknown" ? "Unclear in the bid. Ask the bidder." : "No other bid itemizes it. Needs your figure.";
      lines.push(`| ${md(r.bid.bidder)} | ${md(g.row.label)} | ${md(says)} | ${plug} | ${md(source)} |`);
    }
    lines.push("");
  }
  const adj = [...(scenario.adjustments ?? []).map((a) => ({ ...a, state: "applied" })), ...analysis.results.flatMap((r) => r.suggestedAdjustments.map((a) => ({ ...a, state: "suggested" })))];
  if (adj.length) {
    lines.push("## Adjustments", "", "| Bidder | Adjustment | Amount | Source | State |", "|---|---|---|---|---|");
    for (const a of adj) lines.push(`| ${md(data.bids.find((b) => b.id === a.bid)?.bidder)} | ${md(a.description)} | ${money(a.amount, { sign: true })} | ${md(a.source)} | ${a.state} |`);
    lines.push("");
  }
  lines.push("## Review flags", "");
  const flags = analysis.results.flatMap((r) => r.flags.map((f) => `- **${r.bid.bidder}:** ${f.text}${f.ref ? ` (${f.ref})` : ""}`));
  lines.push(...(flags.length ? flags : ["None."]), "");
  lines.push("## Questions for bidders", "");
  for (const r of analysis.results) {
    lines.push(`### ${r.bid.bidder}`, "");
    if (!r.questions.length) lines.push("No questions.");
    r.questions.forEach((q, i) => lines.push(`${i + 1}. ${q.text}${q.ref ? ` (${q.ref})` : ""}`));
    lines.push("");
  }
  if ((data.openQuestions ?? []).length) {
    lines.push("## Open questions for you", "");
    for (const q of data.openQuestions) lines.push(`- ${q.text}${q.source ? ` (${q.source})` : ""}`);
    lines.push("");
  }
  if (analysis.superseded.length) lines.push(`Superseded and not leveled: ${analysis.superseded.map((b) => `${b.bidder} (${b.files.join(", ")})`).join("; ")}.`, "");
  lines.push("This is a comparison, not an award recommendation. Plugs and basis figures are the estimator's judgment, and nothing was sent to a bidder.");
  return `${lines.join("\n")}\n`;
}

// ---------- XLSX (no dependencies) ----------

const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(bytes) {
  let c = 0xffffffff;
  for (const b of bytes) c = CRC_TABLE[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

// Stored (uncompressed) zip with a fixed timestamp, so output is reproducible.
function zip(files) {
  const enc = new TextEncoder();
  const chunks = [];
  const central = [];
  let offset = 0;
  for (const [name, text] of files) {
    const nameBytes = enc.encode(name);
    const data = enc.encode(text);
    const crc = crc32(data);
    const local = new DataView(new ArrayBuffer(30));
    local.setUint32(0, 0x04034b50, true);
    local.setUint16(4, 20, true);
    local.setUint16(10, 0, true);
    local.setUint16(12, 0x21, true); // 1980-01-01
    local.setUint32(14, crc, true);
    local.setUint32(18, data.length, true);
    local.setUint32(22, data.length, true);
    local.setUint16(26, nameBytes.length, true);
    chunks.push(new Uint8Array(local.buffer), nameBytes, data);
    const entry = new DataView(new ArrayBuffer(46));
    entry.setUint32(0, 0x02014b50, true);
    entry.setUint16(4, 20, true);
    entry.setUint16(6, 20, true);
    entry.setUint16(14, 0x21, true);
    entry.setUint32(16, crc, true);
    entry.setUint32(20, data.length, true);
    entry.setUint32(24, data.length, true);
    entry.setUint16(28, nameBytes.length, true);
    entry.setUint32(42, offset, true);
    central.push(new Uint8Array(entry.buffer), nameBytes);
    offset += 30 + nameBytes.length + data.length;
  }
  const centralSize = central.reduce((n, c) => n + c.length, 0);
  const end = new DataView(new ArrayBuffer(22));
  end.setUint32(0, 0x06054b50, true);
  end.setUint16(8, files.length, true);
  end.setUint16(10, files.length, true);
  end.setUint32(12, centralSize, true);
  end.setUint32(16, offset, true);
  const parts = [...chunks, ...central, new Uint8Array(end.buffer)];
  const out = new Uint8Array(parts.reduce((n, p) => n + p.length, 0));
  let at = 0;
  for (const p of parts) {
    out.set(p, at);
    at += p.length;
  }
  return out;
}

const xml = (v) => String(v ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g, "");
const colName = (i) => {
  let s = "";
  for (let n = i + 1; n > 0; n = Math.floor((n - 1) / 26)) s = String.fromCharCode(65 + ((n - 1) % 26)) + s;
  return s;
};

// Cells: string, number (dollars), {f, v, money}, {money: cents}, or null.
// Styles: 0 default, 1 bold header, 2 currency, 3 bold currency, 4 wrapped text.
function sheetXml(rows, widths) {
  const body = rows
    .map((row, r) => {
      const cells = row
        .map((cell, c) => {
          if (cell === null || cell === undefined || cell === "") return "";
          const ref = `${colName(c)}${r + 1}`;
          const header = r === 0;
          if (typeof cell === "object" && "f" in cell) return `<c r="${ref}" s="${cell.bold ? 3 : 2}"><f>${xml(cell.f)}</f><v>${cell.v / 100}</v></c>`;
          if (typeof cell === "object" && "money" in cell) return `<c r="${ref}" s="2"><v>${cell.money / 100}</v></c>`;
          if (typeof cell === "number") return `<c r="${ref}"><v>${cell}</v></c>`;
          return `<c r="${ref}" t="inlineStr" s="${header ? 1 : 4}"><is><t xml:space="preserve">${xml(cell)}</t></is></c>`;
        })
        .join("");
      return `<row r="${r + 1}">${cells}</row>`;
    })
    .join("");
  const cols = widths.map((w, i) => `<col min="${i + 1}" max="${i + 1}" width="${w}" customWidth="1"/>`).join("");
  return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>${cols}</cols><sheetData>${body}</sheetData></worksheet>`;
}

export function workbook(data, scenario, analysis) {
  const { results } = analysis;
  const names = new Map(results.map((r) => [r.bid.id, r.bid.bidder]));
  const plugRows = [["Bidder", "Scope", "Bid says", "Suggested", "Plug", "Source", "Counts (Yes/No)"]];
  for (const r of results) {
    for (const g of r.gaps) {
      plugRows.push([
        r.bid.bidder,
        g.row.label,
        `${STATUS_LABEL[g.cell.status]}${g.cell.note ? `: ${g.cell.note}` : ""} (${g.cell.ref})`,
        g.suggestion ? { money: g.suggestion.amount } : null,
        g.plug ? { money: g.plug.amount } : null,
        g.plug?.source ?? (g.suggestion ? g.suggestion.source : "Open"),
        g.plug ? "Yes" : "No",
      ]);
    }
  }
  const adjRows = [["Bidder", "Adjustment", "Amount", "Source"]];
  for (const a of scenario.adjustments ?? []) adjRows.push([names.get(a.bid) ?? a.bid, a.description, { money: a.amount }, a.source]);

  const leveled = [["Bidder", "Base bid", "Plugs", "Adjustments", "Alternates", "Basis", "Leveled total", "Status"]];
  results.forEach((r, i) => {
    const n = i + 2;
    leveled.push([
      r.bid.bidder,
      r.bid.total === null ? null : { money: r.bid.total },
      { f: `SUMIFS('Gaps and plugs'!E:E,'Gaps and plugs'!A:A,A${n},'Gaps and plugs'!G:G,"Yes")`, v: r.plugs },
      { f: `SUMIFS(Adjustments!C:C,Adjustments!A:A,A${n})`, v: r.adjustmentTotal },
      { money: r.alternateTotal },
      { money: r.basisTotal },
      r.leveled === null ? "No stated total" : { f: `SUM(B${n}:F${n})`, v: r.leveled, bold: true },
      statusText(r),
    ]);
  });
  leveled.push([]);
  leveled.push([`Plugs and adjustments recompute from their sheets: set a plug's "Counts" to Yes to carry it. Alternates and basis are values from the HTML tab as exported ${data.package.asOf}.`]);

  const matrix = [["Scope", "Class", ...results.map((r) => r.bid.bidder)]];
  for (const row of data.package.rows) {
    matrix.push([row.label, rowClass(row), ...results.map((r) => {
      const cell = r.bid.scope[row.key];
      return `${STATUS_LABEL[cell.status]}${isInt(cell.amount) ? ` ${money(cell.amount)}` : ""}${cell.note ? `: ${cell.note}` : ""} (${cell.ref})`;
    })]);
  }
  const questions = [["Bidder", "Question", "Evidence"]];
  for (const r of results) for (const q of r.questions) questions.push([r.bid.bidder, q.text, q.ref ?? ""]);
  const evidence = [["Bidder", "Ref", "File", "Location", "Quote"]];
  for (const bid of data.bids) for (const ev of bid.evidence ?? []) evidence.push([bid.bidder, ev.ref, ev.file, ev.location, ev.quote]);

  const sheets = [
    ["Leveled totals", sheetXml(leveled, [34, 14, 14, 14, 14, 14, 16, 60])],
    ["Gaps and plugs", sheetXml(plugRows, [30, 40, 50, 14, 14, 70, 14])],
    ["Adjustments", sheetXml(adjRows, [30, 50, 14, 60])],
    ["Scope matrix", sheetXml(matrix, [48, 10, ...results.map(() => 36)])],
    ["Questions", sheetXml(questions, [30, 90, 10])],
    ["Evidence", sheetXml(evidence, [30, 8, 28, 28, 90])],
  ];
  const files = [
    ["[Content_Types].xml", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>${sheets.map((_, i) => `<Override PartName="/xl/worksheets/sheet${i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`).join("")}</Types>`],
    ["_rels/.rels", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>`],
    ["xl/workbook.xml", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>${sheets.map(([name], i) => `<sheet name="${xml(name)}" sheetId="${i + 1}" r:id="rId${i + 1}"/>`).join("")}</sheets><calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>`],
    ["xl/_rels/workbook.xml.rels", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">${sheets.map((_, i) => `<Relationship Id="rId${i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i + 1}.xml"/>`).join("")}<Relationship Id="rId${sheets.length + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>`],
    ["xl/styles.xml", `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><numFmts count="1"><numFmt numFmtId="164" formatCode="&quot;$&quot;#,##0.00"/></numFmts><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf/></cellStyleXfs><cellXfs count="5"><xf/><xf fontId="1" applyFont="1"/><xf numFmtId="164" applyNumberFormat="1"/><xf numFmtId="164" fontId="1" applyNumberFormat="1" applyFont="1"/><xf applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf></cellXfs></styleSheet>`],
    ...sheets.map(([, body], i) => [`xl/worksheets/sheet${i + 1}.xml`, body]),
  ];
  return zip(files);
}

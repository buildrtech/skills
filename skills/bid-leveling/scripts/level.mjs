#!/usr/bin/env node
// Level sub bids into one Excel workbook with live formulas.
//
//   node level.mjs bid-data.json bid-tab.xlsx
//   node level.mjs bid-data.json --json      (print the leveled totals instead)
//
// No dependencies. Money in the JSON is dollars; the script works in cents.
import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const STATUSES = ["included", "excluded", "omitted", "unclear"];
const KEY = /^[a-z0-9][a-z0-9_-]*$/;

const cents = (dollars) => Math.round(dollars * 100);
const isMoney = (v) => typeof v === "number" && Number.isFinite(v) && Math.abs(v * 100 - Math.round(v * 100)) < 1e-6;
const isText = (v) => typeof v === "string" && v.trim() !== "";

export function money(c) {
  const abs = Math.abs(c);
  const text = `$${Math.floor(abs / 100).toLocaleString("en-US")}${abs % 100 ? `.${String(abs % 100).padStart(2, "0")}` : ""}`;
  return c < 0 ? `-${text}` : text;
}

export function validate(data) {
  const errors = [];
  const need = (ok, message) => ok || errors.push(message);
  need(isText(data?.project), "project is required");
  need(isText(data?.package), "package is required");
  need(/^\d{4}-\d{2}-\d{2}$/.test(data?.asOf ?? ""), "asOf must be YYYY-MM-DD");
  need(Array.isArray(data?.addenda) && data.addenda.every((n) => Number.isInteger(n) && n > 0), "addenda must be a list of addendum numbers ([] for none)");
  const scope = Array.isArray(data?.scope) ? data.scope : [];
  need(scope.length > 0, "scope must list at least one scope line");
  const keys = new Set();
  for (const row of scope) {
    need(KEY.test(row?.key ?? "") && !keys.has(row.key), `scope key "${row?.key}" must be unique: lowercase letters, digits, - or _`);
    need(isText(row?.label), `scope line "${row?.key}" needs a label`);
    keys.add(row?.key);
  }
  const bids = Array.isArray(data?.bids) ? data.bids : [];
  need(bids.length >= 2, "at least two bids are needed to level");
  const bidders = new Set();
  for (const bid of bids) {
    const who = bid?.bidder ?? "(unnamed bid)";
    need(isText(bid?.bidder) && !bidders.has(bid.bidder), `bidder "${who}" must be named and unique`);
    bidders.add(bid?.bidder);
    need(isText(bid?.file), `${who}: file is required`);
    need(isMoney(bid?.total) && bid.total > 0, `${who}: total must be the stated base bid in dollars`);
    need(bid?.addenda === null || (Array.isArray(bid?.addenda) && bid.addenda.every(Number.isInteger)), `${who}: addenda must list acknowledged addendum numbers, or be null when the bid doesn't say`);
    for (const field of ["notes", "questions"]) need(bid?.[field] === undefined || (Array.isArray(bid[field]) && bid[field].every(isText)), `${who}: ${field} must be a list of text`);
    const cells = bid?.scope ?? {};
    for (const key of keys) {
      const cell = cells[key];
      if (!cell) {
        errors.push(`${who}: no entry for scope line "${key}" (use "omitted" if the bid doesn't mention it)`);
        continue;
      }
      need(STATUSES.includes(cell.status), `${who} / ${key}: status must be one of ${STATUSES.join(", ")}`);
      need(cell.status === "omitted" || isText(cell.quote), `${who} / ${key}: quote the bid's words`);
      need(cell.amount === undefined || (cell.status === "included" && isMoney(cell.amount)), `${who} / ${key}: only included lines carry an amount, in dollars`);
    }
    for (const key of Object.keys(cells)) need(keys.has(key), `${who}: "${key}" is not a scope line`);
  }
  const plugged = new Set();
  for (const plug of Array.isArray(data?.plugs) ? data.plugs : []) {
    const bid = bids.find((b) => b?.bidder === plug?.bidder);
    const where = `plug ${plug?.bidder} / ${plug?.scope}`;
    need(bid, `${where}: no bid from "${plug?.bidder}"`);
    need(keys.has(plug?.scope), `${where}: not a scope line`);
    need(!bid || !keys.has(plug?.scope) || (bid.scope?.[plug.scope] && bid.scope[plug.scope].status !== "included"), `${where}: the bid includes this line, so there is nothing to plug`);
    need(isMoney(plug?.amount), `${where}: amount must be in dollars`);
    need(isText(plug?.source), `${where}: say where the figure came from`);
    need(!plugged.has(`${plug?.bidder}\n${plug?.scope}`), `${where}: plugged twice`);
    plugged.add(`${plug?.bidder}\n${plug?.scope}`);
  }
  need(data?.plugs === undefined || Array.isArray(data.plugs), "plugs must be a list");
  if (errors.length) throw new Error(`bid data has ${errors.length} problem${errors.length === 1 ? "" : "s"}:\n- ${errors.join("\n- ")}`);
  return data;
}

// The highest price another bidder itemized for the same line, or null.
function suggest(data, bid, key) {
  let best = null;
  for (const other of data.bids) {
    const cell = other.scope[key];
    if (other === bid || cell.status !== "included" || cell.amount === undefined) continue;
    if (!best || cents(cell.amount) > best.amount) best = { amount: cents(cell.amount), bidder: other.bidder };
  }
  return best;
}

// "Level 5 finish (Addendum 2)" reads as "level 5 finish (Addendum 2)" mid-sentence; acronyms stay.
const lower = (label) => (/^[A-Z][a-z]/.test(label) ? label[0].toLowerCase() + label.slice(1) : label);
const said = (quote) => `Your bid says "${quote}"${/[.!?]$/.test(quote) ? "" : "."}`;
const QUESTION = {
  excluded: (label, quote) => `${said(quote)} Confirm your bid excludes ${lower(label)}, or give us an add price.`,
  omitted: (label) => `Your bid doesn't mention ${lower(label)}. Is it in your base bid? If not, what would you add?`,
  unclear: (label, quote) => `${said(quote)} Does your base bid include ${lower(label)}?`,
};

export function level(data) {
  const entered = new Map((data.plugs ?? []).map((p) => [`${p.bidder}\n${p.scope}`, p]));
  const results = data.bids.map((bid) => {
    const gaps = [];
    const questions = [];
    const missing = bid.addenda ? data.addenda.filter((n) => !bid.addenda.includes(n)) : [];
    if (bid.addenda === null && data.addenda.length) questions.push(`Your bid doesn't say which addenda it covers. Confirm it includes Addenda ${data.addenda.join(" and ")}.`);
    if (missing.length) questions.push(`Your bid acknowledges ${bid.addenda.length ? `Addend${bid.addenda.length === 1 ? "um" : "a"} ${bid.addenda.join(" and ")}` : "no addenda"}. Confirm you received Addend${missing.length === 1 ? "um" : "a"} ${missing.join(" and ")} and that your price covers ${missing.length === 1 ? "it" : "them"}.`);
    for (const row of data.scope) {
      const cell = bid.scope[row.key];
      if (cell.status === "included") continue;
      const plug = entered.get(`${bid.bidder}\n${row.key}`);
      const suggestion = cell.status === "unclear" ? null : suggest(data, bid, row.key);
      let gap;
      if (plug) gap = { amount: cents(plug.amount), source: `Entered: ${plug.source}` };
      else if (suggestion) gap = { amount: suggestion.amount, source: `Suggested: ${suggestion.bidder} itemized ${money(suggestion.amount)} for this line` };
      else gap = { amount: null, source: cell.status === "unclear" ? "Open: ask the bidder what the wording covers" : "Open: no other bid itemizes this line" };
      gaps.push({ row, cell, ...gap, carry: gap.amount !== null });
      questions.push(QUESTION[cell.status](row.label, cell.quote));
    }
    questions.push(...(bid.questions ?? []));
    const base = cents(bid.total);
    const plugs = gaps.reduce((sum, g) => sum + (g.carry ? g.amount : 0), 0);
    const open = gaps.filter((g) => !g.carry).length;
    return { bid, base, plugs, leveled: base + plugs, open, complete: open === 0, gaps, questions, missing };
  });
  const complete = results.filter((r) => r.complete);
  const lowestComplete = complete.length ? complete.reduce((a, b) => (b.leveled < a.leveled ? b : a)) : null;
  const lowestBase = results.reduce((a, b) => (b.base < a.base ? b : a));
  return { results, lowestBase, lowestComplete };
}

// ---------- XLSX ----------

const CRC_TABLE = Array.from({ length: 256 }, (_, n) => {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});

function crc32(bytes) {
  let c = 0xffffffff;
  for (const b of bytes) c = CRC_TABLE[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

// Stored (uncompressed) zip with a fixed timestamp, so output is reproducible.
function zip(files) {
  const enc = new TextEncoder();
  const parts = [];
  const central = [];
  let offset = 0;
  for (const [name, text] of files) {
    const nameBytes = enc.encode(name);
    const data = enc.encode(text);
    const header = (size, signature) => {
      const view = new DataView(new ArrayBuffer(size));
      view.setUint32(0, signature, true);
      return view;
    };
    const local = header(30, 0x04034b50);
    local.setUint16(4, 20, true);
    local.setUint16(12, 0x21, true); // 1980-01-01
    local.setUint32(14, crc32(data), true);
    local.setUint32(18, data.length, true);
    local.setUint32(22, data.length, true);
    local.setUint16(26, nameBytes.length, true);
    parts.push(new Uint8Array(local.buffer), nameBytes, data);
    const entry = header(46, 0x02014b50);
    entry.setUint16(4, 20, true);
    entry.setUint16(6, 20, true);
    entry.setUint16(14, 0x21, true);
    entry.setUint32(16, crc32(data), true);
    entry.setUint32(20, data.length, true);
    entry.setUint32(24, data.length, true);
    entry.setUint16(28, nameBytes.length, true);
    entry.setUint32(42, offset, true);
    central.push(new Uint8Array(entry.buffer), nameBytes);
    offset += 30 + nameBytes.length + data.length;
  }
  const size = central.reduce((n, c) => n + c.length, 0);
  const end = new DataView(new ArrayBuffer(22));
  end.setUint32(0, 0x06054b50, true);
  end.setUint16(8, files.length, true);
  end.setUint16(10, files.length, true);
  end.setUint32(12, size, true);
  end.setUint32(16, offset, true);
  const all = [...parts, ...central, new Uint8Array(end.buffer)];
  const out = new Uint8Array(all.reduce((n, p) => n + p.length, 0));
  let at = 0;
  for (const p of all) {
    out.set(p, at);
    at += p.length;
  }
  return out;
}

const xml = (v) => String(v ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g, "");
const col = (i) => {
  let s = "";
  for (let n = i + 1; n > 0; n = Math.floor((n - 1) / 26)) s = String.fromCharCode(65 + ((n - 1) % 26)) + s;
  return s;
};

// Cells: text, {bold: text}, {money: cents}, or a formula with its cached value:
// {f, money: cents} or {f, n: number} or {f, text}. Formulas take bold. Null is empty.
// Styles: 1 bold, 2 currency, 3 bold currency, 4 wrapped text.
function sheetXml(rows, widths) {
  const body = rows
    .map((row, r) => {
      const cells = row
        .map((cell, c) => {
          if (cell === null || cell === undefined || cell === "") return "";
          const ref = `${col(c)}${r + 1}`;
          if (typeof cell === "string") return `<c r="${ref}" t="inlineStr" s="${r === 0 ? 1 : 4}"><is><t xml:space="preserve">${xml(cell)}</t></is></c>`;
          const f = "f" in cell ? `<f>${xml(cell.f)}</f>` : "";
          if ("money" in cell) return `<c r="${ref}" s="${cell.bold ? 3 : 2}">${f}<v>${cell.money / 100}</v></c>`;
          if ("n" in cell) return `<c r="${ref}">${f}<v>${cell.n}</v></c>`;
          if ("text" in cell) return `<c r="${ref}" t="str"${cell.bold ? ' s="1"' : ""}>${f}<v>${xml(cell.text)}</v></c>`;
          return `<c r="${ref}" t="inlineStr" s="1"><is><t xml:space="preserve">${xml(cell.bold)}</t></is></c>`;
        })
        .join("");
      return `<row r="${r + 1}">${cells}</row>`;
    })
    .join("");
  const cols = widths.map((w, i) => `<col min="${i + 1}" max="${i + 1}" width="${w}" customWidth="1"/>`).join("");
  return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>${cols}</cols><sheetData>${body}</sheetData></worksheet>`;
}

const SAYS = { excluded: "Excluded", omitted: "Not mentioned", unclear: "Unclear" };

export function workbook(data, analysis = level(data)) {
  const { results, lowestBase, lowestComplete } = analysis;

  const plugs = [["Bidder", "Scope", "Bid says", "Plug", "Source", "Carry (Yes/No)"]];
  for (const r of results) {
    for (const g of r.gaps) {
      plugs.push([r.bid.bidder, g.row.label, g.cell.quote ? `${SAYS[g.cell.status]}: "${g.cell.quote}"` : SAYS[g.cell.status], g.amount === null ? null : { money: g.amount }, g.source, g.carry ? "Yes" : "No"]);
    }
  }

  const last = results.length + 1;
  const range = (c) => `$${c}$2:$${c}$${last}`;
  const totals = [["Bidder", "Base bid", "Plugs", "Leveled total", "Open gaps", "Status", "Bid file", "Notes"]];
  results.forEach((r, i) => {
    const n = i + 2;
    totals.push([
      r.bid.bidder,
      { money: r.base },
      { f: `SUMIFS(Plugs!$D:$D,Plugs!$A:$A,$A${n},Plugs!$F:$F,"Yes")`, money: r.plugs },
      { f: `B${n}+C${n}`, money: r.leveled, bold: true },
      { f: `COUNTIFS(Plugs!$A:$A,$A${n})-COUNTIFS(Plugs!$A:$A,$A${n},Plugs!$F:$F,"Yes",Plugs!$D:$D,"<>")`, n: r.open },
      { f: `IF(E${n}=0,"Complete","Incomplete")`, text: r.complete ? "Complete" : "Incomplete" },
      r.bid.file,
      (r.bid.notes ?? []).join(" "),
    ]);
  });
  const anyComplete = `COUNTIF(${range("E")},0)=0`;
  const lowestRow = `MATCH(1,INDEX((${range("D")}=_xlfn.MINIFS(${range("D")},${range("E")},0))*(${range("E")}=0),0),0)`;
  totals.push(
    [],
    [{ bold: "Lowest" }, { bold: "Bidder" }, null, { bold: "Amount" }],
    [
      "Base bid",
      { f: `INDEX(${range("A")},MATCH(MIN(${range("B")}),${range("B")},0))`, text: lowestBase.bid.bidder },
      null,
      { f: `MIN(${range("B")})`, money: lowestBase.base },
    ],
    [
      "Complete leveled total",
      { f: `IF(${anyComplete},"None complete",INDEX(${range("A")},${lowestRow}))`, text: lowestComplete?.bid.bidder ?? "None complete", bold: true },
      null,
      { f: `IF(${anyComplete},"",_xlfn.MINIFS(${range("D")},${range("E")},0))`, ...(lowestComplete ? { money: lowestComplete.leveled } : { text: "" }), bold: true },
    ],
    [],
    [`Leveled total = base bid + plugs marked Carry "Yes" on the Plugs sheet. A bid is complete when every gap carries a plug. Suggested plugs are the highest price another bidder itemized for the same line; change the amount, or set Carry to "No", on the Plugs sheet. As of ${data.asOf}. This is a comparison, not an award recommendation.`],
  );

  const scope = [["Scope", ...results.map((r) => r.bid.bidder)]];
  for (const row of data.scope) {
    scope.push([row.label, ...results.map((r) => {
      const cell = r.bid.scope[row.key];
      if (cell.status === "included") return cell.amount === undefined ? "Included" : `Included ${money(cents(cell.amount))}`;
      return cell.quote ? `${SAYS[cell.status]}: "${cell.quote}"` : SAYS[cell.status];
    })]);
  }
  scope.push([{ bold: "Addenda" }, ...results.map((r) => (r.bid.addenda === null ? "Not stated" : `${r.bid.addenda.length ? r.bid.addenda.join(", ") : "None"}${r.missing.length ? ` (missing ${r.missing.join(", ")})` : ""}`))]);
  scope.push([{ bold: "Base bid" }, ...results.map((r) => ({ money: r.base }))]);

  const questions = [["Bidder", "Question"]];
  for (const r of results) for (const q of r.questions) questions.push([r.bid.bidder, q]);

  const sheets = [
    ["Leveled totals", sheetXml(totals, [32, 16, 14, 16, 11, 13, 26, 60])],
    ["Scope", sheetXml(scope, [40, ...results.map(() => 34)])],
    ["Plugs", sheetXml(plugs, [30, 36, 50, 14, 56, 14])],
    ["Questions", sheetXml(questions, [30, 100])],
  ];
  return zip([
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
  ]);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [dataPath, outPath] = process.argv.slice(2);
  if (!dataPath || !outPath) {
    console.error("Usage: node level.mjs bid-data.json bid-tab.xlsx\n       node level.mjs bid-data.json --json");
    process.exit(2);
  }
  try {
    const data = validate(JSON.parse(await readFile(dataPath, "utf8")));
    const analysis = level(data);
    if (outPath === "--json") {
      const summary = analysis.results.map((r) => ({
        bidder: r.bid.bidder,
        base: r.base / 100,
        plugs: r.plugs / 100,
        leveled: r.leveled / 100,
        openGaps: r.open,
        gaps: r.gaps.map((g) => ({ scope: g.row.key, status: g.cell.status, plug: g.amount === null ? null : g.amount / 100, source: g.source })),
        questions: r.questions,
      }));
      process.stdout.write(`${JSON.stringify({ lowestBase: analysis.lowestBase.bid.bidder, lowestComplete: analysis.lowestComplete?.bid.bidder ?? null, results: summary }, null, 2)}\n`);
    } else {
      await writeFile(outPath, workbook(data, analysis));
      const low = analysis.lowestComplete;
      console.error(`Wrote ${outPath}. Lowest complete: ${low ? `${low.bid.bidder} at ${money(low.leveled)}` : "none (every bid has an open gap)"}.`);
    }
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

#!/usr/bin/env node

import { readFileSync, writeFileSync } from "node:fs";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatMoney(cents) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(Number(cents ?? 0) / 100);
}

function renderDivisionRows(divisions) {
  return (divisions ?? [])
    .flatMap((division) => [
      `<tr class="division"><td colspan="3">Division ${escapeHtml(division.code)} — ${escapeHtml(division.name)}</td><td class="numeric">${formatMoney(division.totalCents)}</td></tr>`,
      ...(division.lineItems ?? []).map(
        (item) => `<tr>
          <td>${escapeHtml(item.description)}</td>
          <td>${escapeHtml(item.quantity)}</td>
          <td>${escapeHtml(division.code)}</td>
          <td class="numeric">${formatMoney(item.totalCents)}</td>
        </tr>`,
      ),
    ])
    .join("\n");
}

function renderSimpleRows(rows) {
  return (rows ?? [])
    .map(
      (row) => `<tr><td>${escapeHtml(row.description)}</td><td class="numeric">${formatMoney(row.totalCents)}</td></tr>`,
    )
    .join("\n");
}

function renderNotes(notes) {
  return (notes ?? []).map((note) => `<li>${escapeHtml(note)}</li>`).join("\n");
}

function renderPreparedLine(data) {
  const parts = [];
  if (data.preparedBy) parts.push(`Prepared by ${escapeHtml(data.preparedBy)}`);
  if (data.preparedFor) parts.push(`for ${escapeHtml(data.preparedFor)}`);
  return parts.length ? `<p class="meta">${parts.join(" ")}</p>` : "";
}

function render(data) {
  const totals = data.totals ?? {};

  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Construction Budget Export</title>
  <style>
    :root { --ink: #1f2937; --muted: #6b7280; --primary: #334155; --accent: #0f766e; --surface: #f1f5f9; --border: #cbd5e1; --font-body: "Liberation Sans", "DejaVu Sans", sans-serif; }
    body { margin: 0; color: var(--ink); font-family: var(--font-body); font-size: 10pt; line-height: 1.35; }
    .pdf-page { box-sizing: border-box; min-height: 10in; page-break-after: always; padding: 0.45in; }
    .pdf-page:last-of-type { page-break-after: auto; }
    .keep-together { break-inside: avoid; }
    h1 { color: var(--primary); font-size: 24pt; margin: 0; }
    h2 { background: var(--surface); border-left: 5px solid var(--accent); color: var(--primary); font-size: 13pt; padding: 7px 9px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 14px; }
    thead { display: table-header-group; }
    th { background: var(--primary); color: #ffffff; font-size: 7.5pt; padding: 6px; text-align: left; text-transform: uppercase; }
    td { border: 1px solid var(--border); padding: 5px 6px; vertical-align: top; }
    .numeric { font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }
    .division td { background: var(--surface); color: var(--primary); font-weight: 800; }
    .meta { color: var(--muted); margin: 4px 0 6px; }
    .meta + .meta { margin-bottom: 18px; }
    .totals { margin-left: auto; width: 45%; }
    .totals tr:last-child td { background: var(--primary); color: #ffffff; font-weight: 800; }
  </style>
</head>
<body>
  <section class="pdf-page">
    <p>Construction Budget Export</p>
    <h1>${escapeHtml(data.project)}</h1>
    <p class="meta">Estimate date: ${escapeHtml(data.estimateDate)}</p>
    ${renderPreparedLine(data)}
    <h2>Division Detail</h2>
    <table>
      <thead><tr><th>Description</th><th>Quantity</th><th>Division</th><th class="numeric">Total</th></tr></thead>
      <tbody>${renderDivisionRows(data.divisions)}</tbody>
    </table>
    <div class="keep-together">
      <h2>Alternates</h2>
      <table><thead><tr><th>Alternate</th><th class="numeric">Total</th></tr></thead><tbody>${renderSimpleRows(data.alternates)}</tbody></table>
      <h2>Markups</h2>
      <table><thead><tr><th>Markup</th><th class="numeric">Total</th></tr></thead><tbody>${renderSimpleRows(data.markups)}</tbody></table>
      <table class="totals">
        <tbody>
          <tr><td>Subtotal</td><td class="numeric">${formatMoney(totals.subtotalCents)}</td></tr>
          <tr><td>Markups</td><td class="numeric">${formatMoney(totals.markupCents)}</td></tr>
          <tr><td>Total</td><td class="numeric">${formatMoney(totals.grandTotalCents)}</td></tr>
        </tbody>
      </table>
    </div>
    <h2>Notes</h2>
    <ul>${renderNotes(data.notes)}</ul>
  </section>
</body>
</html>
`;
}

const [inputPath, outputPath] = process.argv.slice(2);
if (!inputPath || !outputPath) {
  console.error("Usage: node render.mjs input.json output.html");
  process.exit(1);
}

const data = JSON.parse(readFileSync(inputPath, "utf8"));
const html = render(data);
writeFileSync(outputPath, html);

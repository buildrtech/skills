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

function renderList(items) {
  return (items ?? []).map((item) => `<li>${escapeHtml(item)}</li>`).join("\n");
}

function renderDivisionRows(divisions) {
  return (divisions ?? [])
    .map(
      (division) => `<tr>
        <td>Division ${escapeHtml(division.code)}</td>
        <td>${escapeHtml(division.name)}</td>
        <td>${escapeHtml(division.notes)}</td>
        <td class="numeric">${formatMoney(division.totalCents)}</td>
      </tr>`,
    )
    .join("\n");
}

function renderApprovalRows(approvals) {
  return (approvals ?? [])
    .map(
      (approval) => `<tr>
        <td>${escapeHtml(approval.name)}</td>
        <td>${escapeHtml(approval.status)}</td>
        <td>${escapeHtml(approval.date)}</td>
      </tr>`,
    )
    .join("\n");
}

function render(data) {
  const summary = data.summary ?? {};

  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Milestone Export</title>
  <style>
    :root { --ink: #1f2937; --muted: #6b7280; --primary: #334155; --accent: #0f766e; --surface: #f1f5f9; --border: #cbd5e1; --font-body: "Liberation Sans", "DejaVu Sans", sans-serif; }
    body { margin: 0; color: var(--ink); font-family: var(--font-body); font-size: 10.5pt; line-height: 1.4; }
    .pdf-page { box-sizing: border-box; min-height: 10in; page-break-after: always; padding: 0.5in; }
    .pdf-page:last-of-type { page-break-after: auto; }
    .keep-together { break-inside: avoid; }
    h1 { color: var(--primary); font-size: 25pt; margin: 0; }
    h2 { background: var(--surface); border-left: 5px solid var(--accent); color: var(--primary); font-size: 13pt; padding: 8px 10px; }
    table { width: 100%; border-collapse: collapse; }
    thead { display: table-header-group; }
    th { background: var(--primary); color: #ffffff; font-size: 7.5pt; padding: 6px; text-align: left; text-transform: uppercase; }
    td { border: 1px solid var(--border); padding: 7px; vertical-align: top; }
    .numeric { font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }
    .meta { color: var(--muted); margin: 4px 0 18px; }
    .summary-grid { display: grid; gap: 10px; grid-template-columns: repeat(4, 1fr); }
    .summary-card { background: var(--surface); border-top: 4px solid var(--accent); padding: 10px; }
    .summary-card strong { display: block; font-size: 14pt; }
    .columns { display: grid; gap: 18px; grid-template-columns: 1fr 1fr; }
  </style>
</head>
<body>
  <section class="pdf-page">
    <p>Milestone Export</p>
    <h1>${escapeHtml(data.project)}</h1>
    <p class="meta">${escapeHtml(data.milestone)} · ${escapeHtml(summary.estimateDate)}</p>
    <div class="summary-grid keep-together">
      <div class="summary-card"><span>Milestone</span><strong>${escapeHtml(data.milestone)}</strong></div>
      <div class="summary-card"><span>Area</span><strong>${escapeHtml(summary.grossSquareFeet)}</strong></div>
      <div class="summary-card"><span>Cost</span><strong>${formatMoney(summary.constructionCostCents)}</strong></div>
      <div class="summary-card"><span>Cost / SF</span><strong>${formatMoney(summary.costPerSquareFootCents)}</strong></div>
    </div>
    <div class="columns">
      <div>
        <h2>Inclusions</h2>
        <ul>${renderList(data.inclusions)}</ul>
      </div>
      <div>
        <h2>Exclusions</h2>
        <ul>${renderList(data.exclusions)}</ul>
      </div>
    </div>
    <h2>Division Totals</h2>
    <table>
      <thead><tr><th>Code</th><th>Division</th><th>Notes</th><th class="numeric">Total</th></tr></thead>
      <tbody>${renderDivisionRows(data.divisions)}</tbody>
    </table>
    <h2>Approvals</h2>
    <table>
      <thead><tr><th>Name</th><th>Status</th><th>Date</th></tr></thead>
      <tbody>${renderApprovalRows(data.approvals)}</tbody>
    </table>
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

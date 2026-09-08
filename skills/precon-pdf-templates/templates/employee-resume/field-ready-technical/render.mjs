#!/usr/bin/env node

import { runGenerator } from "../../../scripts/generator-utils.mjs";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderList(items) {
  return (items ?? []).map((item) => `<li>${escapeHtml(item)}</li>`).join("\n");
}

function renderProjects(projects) {
  return (projects ?? [])
    .map(
      (project) => `<tr>
        <td><strong>${escapeHtml(project.project)}</strong><br>${escapeHtml(project.role)}</td>
        <td>${escapeHtml(project.value)}</td>
        <td>${escapeHtml(project.details)}</td>
      </tr>`,
    )
    .join("\n");
}

function render(data) {
  const employee = data.employee ?? {};
  const certifications = (employee.certifications ?? [])
    .map((certification) => `<span>${escapeHtml(certification)}</span>`)
    .join("\n");

  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Employee Resume</title>
  <style>
    @page { size: letter; margin: 0.45in; }
    :root { --ink: #1f2937; --muted: #6b7280; --primary: #334155; --accent: #0f766e; --surface: #f1f5f9; --border: #cbd5e1; --font-body: "Liberation Sans", "DejaVu Sans", sans-serif; }
    body { margin: 0; color: var(--ink); font-family: var(--font-body); font-size: 10.5pt; line-height: 1.45; }
    .pdf-page { box-sizing: border-box; page-break-after: always; padding: 0; }
    .pdf-page:last-of-type { page-break-after: auto; }
    h1, h2 { break-after: avoid; }
    tr { break-inside: avoid; }
    .division { break-after: avoid; }
    .keep-together { break-inside: avoid; }
    h1 { color: var(--primary); font-size: 28pt; margin: 0; }
    h2 { background: var(--surface); border-left: 5px solid var(--accent); color: var(--primary); font-size: 14pt; padding: 8px 10px; }
    table { width: 100%; border-collapse: collapse; }
    thead { display: table-header-group; }
    th { background: var(--primary); color: #ffffff; font-size: 7.5pt; padding: 6px; text-align: left; text-transform: uppercase; }
    td { border: 1px solid var(--border); padding: 7px; vertical-align: top; }
    .meta { color: var(--muted); font-size: 11pt; margin: 6px 0 18px; }
    .chips span { background: var(--surface); border: 1px solid var(--border); display: inline-block; margin: 0 6px 6px 0; padding: 4px 8px; }
    .summary { border-left: 4px solid var(--accent); padding-left: 12px; }
  </style>
</head>
<body>
  <section class="pdf-page">
    <p>Employee Resume</p>
    <h1>${escapeHtml(employee.name)}</h1>
    <p class="meta">${[employee.role, employee.location, employee.yearsExperience == null ? null : `${employee.yearsExperience} years experience`].filter(value => value != null && value !== "").map(escapeHtml).join(" · ")}</p>
    <div class="summary keep-together">${escapeHtml(data.summary)}</div>
    <h2>Certifications</h2>
    <div class="chips">${certifications}</div>
    <h2>Project Experience</h2>
    <table>
      <thead><tr><th>Project / Role</th><th>Value</th><th>Relevant experience</th></tr></thead>
      <tbody>${renderProjects(data.projectExperience)}</tbody>
    </table>
    <h2>Differentiators</h2>
    <ul>${renderList(data.differentiators)}</ul>
  </section>
</body>
</html>
`;
}

runGenerator(render);

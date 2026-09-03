# Template catalog

Every template is a self-contained HTML document with its theme CSS inlined
in a `<style>` block, so a rendered file needs no external stylesheet.
The matching standalone stylesheet in `themes/` exists for when you build a
document from scratch or restyle a blueprint.

Sample content in the blueprints (owner "Owner Name", contractor
"Contractor Name", project "Riverside Medical Office Renovation", dollar
amounts, dates, and names) is placeholder text. Replace all of it with the
user's data; never ship a sample value.

## Themes

| Theme | File | Character | Default for |
|-------|------|-----------|-------------|
| Architectural Ink | `themes/architectural-ink.css` | Deep navy with copper accents, serif display type, structured cover. | Proposal (premium pursuits) |
| Bid Ledger Minimal | `themes/bid-ledger-minimal.css` | Contract-led, serif typography, ledger rules, restrained tables. | Proposal (contract-heavy owners) |
| Civic Blueprint | `themes/civic-blueprint.css` | Sheet-style headers, blue technical linework, quiet budget schedules. | Proposal (public and institutional) |
| Editorial Bid Book | `themes/editorial-bid-book.css` | Bookish type, chapter pacing, high-touch commercial pages. | Proposal (owner-facing narrative) |
| Field Ops Manual | `themes/field-ops-manual.css` | Safety tags, control sheets, dense field-readable tables. | Proposal (operations-led) |
| Swiss Transit Technical | inline only | Twelve-column grid, tight sans type, numbered routes and budget sheets. | Proposal (technical reviewers) |
| Executive Dark | `themes/executive-dark.css` | Dark gradient cover, KPI cards, high-contrast status tags. | Executive report |
| Field-Ready Technical | `themes/field-ready-technical.css` | Dense, legible tables with repeating headers. | Budget export, milestone export, resume |
| Warm Owner-Facing | `themes/warm-owner-facing.css` | Approachable tone for owners and non-technical readers. | Restyling any blueprint |

Apply exactly one theme per document. Fonts are declared as system
fallbacks (`Liberation Sans`, `DejaVu Sans`, and their serif equivalents)
so the same file renders consistently on most Linux and container images;
if the user supplies brand fonts, add them as flat sibling files and update
the `--font-body` and `--font-display` variables.

## Project proposal

Production path: blueprint (copy and edit).

| Theme | Path |
|-------|------|
| Architectural Ink | `templates/proposal/architectural-ink/index.html` |
| Bid Ledger Minimal | `templates/proposal/bid-ledger-minimal/index.html` |
| Civic Blueprint | `templates/proposal/civic-blueprint/index.html` |
| Editorial Bid Book | `templates/proposal/editorial-bid-book/index.html` |
| Field Ops Manual | `templates/proposal/field-ops-manual/index.html` |
| Swiss Transit Technical | `templates/proposal/swiss-transit-technical/index.html` |

Expected inputs: client or owner, project name, proposal date and validity,
pursuit summary, scope of work, schedule phases, project team, pricing and
alternates, terms, signature blocks. Optional: owner priorities, budget
ledger or route tables (the longer blueprints include appendix pages for
these).

Blocks to map, in order: cover, meta grid, executive summary, scope, schedule
table, commercial summary, team, terms and signatures. Delete an entire
block if the user has no content for it.

## Executive report

Production path: blueprint (copy and edit).

Path: `templates/executive-report/executive-dark/index.html`

Expected inputs: reporting period, project or account summary, four KPIs
(budget variance, schedule status, open items, safety), key decisions with
owner action and due date, risk register, budget and schedule movement
(previous vs. current), next steps with owner and due date.

Status tags use the classes `green`, `amber`, and `red`; pick them from the
user's stated status, not from your own reading of the numbers.

## Construction budget export

Production path: generator.

- Generator: `templates/construction-budget-export/field-ready-technical/render.mjs`
- Schema: `schemas/construction-budget-export.schema.json`
- Sample: `templates/construction-budget-export/field-ready-technical/sample-data.json`
- QA notes: `templates/construction-budget-export/field-ready-technical/qa.md`

Expected inputs: project, estimate date, optional preparedBy and
preparedFor, divisions (code, name, line items with description, quantity,
totalCents, and a division totalCents), alternates, markups, totals
(subtotalCents, markupCents, grandTotalCents), notes.

All money is in integer cents. The generator formats but does not compute;
check that division totals equal their line items and that
subtotal + markups = grand total before rendering, and report any mismatch
to the user instead of fixing it silently.

## Milestone estimate export

Production path: generator.

- Generator: `templates/milestone-export/field-ready-technical/render.mjs`
- Schema: `schemas/milestone-export.schema.json`
- Sample: `templates/milestone-export/field-ready-technical/sample-data.json`
- QA notes: `templates/milestone-export/field-ready-technical/qa.md`

Expected inputs: project, milestone name (for example Schematic Design,
Design Development, GMP), summary (estimateDate, grossSquareFeet,
constructionCostCents, costPerSquareFootCents), inclusions, exclusions,
divisions (code, name, notes, totalCents), approvals (name, status, date).

## Employee resume / team bio

Production path: generator. Run it once per person.

- Generator: `templates/employee-resume/field-ready-technical/render.mjs`
- Schema: `schemas/employee-resume.schema.json`
- Sample: `templates/employee-resume/field-ready-technical/sample-data.json`
- QA notes: `templates/employee-resume/field-ready-technical/qa.md`

Expected inputs: employee (name, role, location, yearsExperience,
certifications), summary, projectExperience (project, role, value,
details), differentiators.

Project values on a resume are references supplied by the user, not
computed totals; keep them as the strings the user gave.

## Running a generator

From the skill directory:

```bash
node templates/construction-budget-export/field-ready-technical/render.mjs data.json out/document.html
```

Each generator takes exactly two arguments, the input JSON path and the
output HTML path, and exits non-zero with a usage message otherwise.
Requires Node 18 or later; no npm packages.

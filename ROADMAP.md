# Roadmap

The v1 catalog, all shipped as of September 2026. Neutral skills work anywhere.
Buildr-connected skills use the Buildr MCP server.

| # | Skill | Tier | Status | Notes |
|---|---|---|---|---|
| 1 | rfp-intake | Neutral | Shipped | Bid/no-bid intake review with cited key dates, requirements, risks, and scorecard. |
| 2 | bid-leveling | Neutral | Shipped | Extract subcontractor bids into a common schema, classify scope rows, find gaps and plugs, produce a leveled comparison as Markdown or XLSX. |
| 3 | bid-leveling-buildr | Buildr-connected | Shipped | Same intake and leveling model, persisted to Buildr bid packages, submissions, and line items. |
| 4 | drawing-scope-extraction | Neutral | Shipped | Pull drawing-backed scope items from a PDF set with a coverage ledger, support-level tagging, and CSI division sanity checks. |
| 5 | precon-pdf-templates | Neutral | Shipped | Proposal, executive report, budget export, milestone estimate, and team resume templates with sample data and a render-and-inspect QA loop. |
| 6 | workforce-planning | Buildr-connected | Shipped | Utilization, bench, demand, and assignment analysis over Buildr workforce data. |
| 7 | financial-forecasting | Buildr-connected | Shipped | Portfolio forecast, closed-period actuals, percent complete, over/under billing over Buildr financials. |
| 8 | rfi-drafter | Neutral | Shipped | Draft RFIs with spec section and sheet citations, a suggested answer where the documents support one, and a log export. |
| 9 | pay-app-review | Neutral | Shipped | Check a G702/G703-style pay application: schedule of values math, retainage, previous-billed continuity, and flags for review. Never approves. |
| 10 | construction-connectors | Neutral | Shipped | How to work RFIs, submittals, and budgets well over construction MCP servers (Procore, JobTread, Bluebeam, Autodesk) without inventing data. |

Ideas not yet scheduled: change-order narrative with markup rules, daily log
summarizer, toolbox talk generator, subcontractor prequalification review,
schedule (XER) analysis, closeout checklist.

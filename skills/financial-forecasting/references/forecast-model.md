# Forecast model

The entities, period types, populations, sequencing rules, and formulas this
skill works with. Read this at workflow step 2 before pulling data.

## Entities

Buildr has one portfolio forecast and three project-level period models:

```text
Account
  `-- forecast periods (listForecastPeriods; portfolio aggregation)
        |-- metadata: metric, tab, grouping, date range, project count
        |-- totals: amount by month, quarter, or year (amount_in_dollars)
        `-- projects: optional project rows for dimensional analysis

Project
  |-- prime contract + approved change orders  -> contract value
  |-- budget and budget milestones             -> current estimate
  |-- forecast periods: planned percent complete by month
  |-- closed periods: actual cost, billed amount, and EAC by month (cents)
  `-- billing periods: derived monthly view combining forecast and actuals
```

## Period types

| Type | Source of truth | Mutable? | Contains |
|---|---|---|---|
| Forecast period | `listFinancialsForecastPeriods` | Yes, via `updateFinancialsForecastPeriod` | Planned percent complete for a future month. |
| Closed period | `listFinancialsClosedPeriods` | Yes, via create/update/delete | Actual cost to date, billed amount to date, and estimate at completion (EAC) as of that month. |
| Billing period | `listFinancialsBillingPeriods` | No; derived | One row per month across the project, each marked by `type` (actual or forecast) with the month's revenue, cost, margin, and probability. |

Closed periods record what happened. Buildr uses cost-to-cost completion
from the latest closed period to reforecast the remaining forecast periods,
so a new close changes every later forecast month. Billing periods are the
combined view and are the default source for trend, variance, and
forecast-health analysis. To change planned completion, update a forecast
period; to change actuals or EAC, create or update a closed period.

Units: closed-period cost, billed, and EAC fields are in cents. Account
forecast `totals[].amount_in_dollars` is already in dollars. Project
`probability` on account forecast rows is a 0 to 1 fraction. Convert once,
say that you did, and present dollars.

## Tab populations

The account forecast `tab` selects a materially different project
population. Never pick one silently for a portfolio question.

| Tab | Population |
|---|---|
| `all` | Every project in the account regardless of stage. |
| `pursuits` | Projects being chased; not yet awarded. Revenue here is probability-weighted when weighted metrics are requested. |
| `backlog` | Awarded projects that have not started construction. |
| `wip` | Work in progress: projects under construction with at least one closed period or active forecast. |
| `in_construction` | Projects currently in a construction stage, whether or not periods have been closed. |
| `wip_and_pursuits` | `wip` plus `pursuits`; the common "what we have plus what we are chasing" view. |
| `pursuits_and_backlog` | `pursuits` plus `backlog`; the forward-looking pipeline without in-flight work. |

The exact stage-to-tab mapping is the account's own configuration. When a
project's placement matters to the finding, confirm it with
`getProjectById` and `listProjectStages` rather than assuming.

Account-forecast guidance:

- For pure totals, request totals without project rows.
- For a breakdown by market sector, company, stage, or project, request
  project rows and compute subtotals from them. Treat `totals` as the full
  filtered result set.
- Compare scenarios (two tabs, two date ranges) with separate calls.
- Default to unweighted revenue and profit. Show probability-weighted
  figures only when asked, and label them weighted.

## Closed-period sequencing rules

Before preparing any `createFinancialsClosedPeriod`, read the project with
`getProjectById`, paginate through `listFinancialsForecastPeriods`, and
paginate through `listFinancialsClosedPeriods`. Then check:

1. The first closed period on a project must be the project's start month.
2. Every later closed period must be the month immediately after the latest
   existing closed period. No gaps, no duplicates.
3. Every closed month must fall between the project start month and the
   last forecast month, inclusive.
4. When the user asks for several months, sort them ascending and prepare
   one contiguous sequence that begins with the next required month. If the
   requested months cannot form that sequence (a gap, a month already
   closed, a month before the start), explain the conflict and prepare
   nothing. Do not fill missing months or guess values.
5. Once any closed period exists, the project's construction `start_date`
   is locked. There is no flow that remaps closed periods to a new start.
   Before proposing a `start_date` change, list closed periods; if any
   exist, explain the lock instead of attempting the update. To unlock,
   closed periods must be deleted latest-first until none remain, each on
   explicit instruction.
6. Construction `end_date` can still change, but not to a date before the
   latest closed period plus any trailing forecast months.

## Formulas

Show each formula once in the output with the inputs it used. All examples
below use one synthetic project so the arithmetic can be checked.

Inputs (synthetic, project `prj_1001`, January close `cp_1001_2027-01`):

| Input | Value | Source |
|---|---|---|
| Prime contract | $12,000,000 | `listFinancialsPrimeContracts` |
| Approved change orders | $400,000 | `listFinancialsChangeOrders`, status approved |
| Actual cost to date | $6,919,200 | closed period, cost field (cents / 100) |
| Billed to date | $7,750,000 | closed period, billed field (cents / 100) |
| Estimate at completion (EAC) | $11,532,000 | closed period, EAC field (cents / 100) |
| Prior EAC (December close) | $11,160,000 | closed period `cp_1001_2026-12` |

**Contract value** = prime contract + approved change orders
= $12,000,000 + $400,000 = **$12,400,000**.

**Percent complete (cost-to-cost)** = actual cost to date / EAC
= $6,919,200 / $11,532,000 = **60.0%**.

**Earned revenue** = percent complete x contract value
= 0.600 x $12,400,000 = **$7,440,000**.

**Estimated profit at completion** = contract value - EAC
= $12,400,000 - $11,532,000 = **$868,000**.

**Margin** = estimated profit at completion / contract value
= $868,000 / $12,400,000 = **7.0%**.

**Over/under billing** = billed to date - earned revenue
= $7,750,000 - $7,440,000 = **+$310,000 overbilled**.
Positive means billings exceed earned revenue (a liability on the WIP
schedule); negative means underbilled (an asset).

**Margin movement** = margin now - margin at prior close.
Prior margin = ($12,400,000 - $11,160,000) / $12,400,000 = 10.0%.
Movement = 7.0% - 10.0% = **-3.0 points**.

**Cost growth** = EAC now - prior EAC
= $11,532,000 - $11,160,000 = **+$372,000**. The closed period records the
new EAC; it does not record the reason. Approved change orders that raise
contract value offset cost growth; pending change orders do not count until
approved.

**Probability-weighted amount** = amount x probability
= $12,400,000 x 0.35 = $4,340,000 for a pursuit at 35%. Only for pursuit
populations and only when asked.

**Remaining revenue** = contract value - earned revenue
= $12,400,000 - $7,440,000 = $4,960,000, spread across the remaining
forecast periods by their planned percent complete.

Rounding: compute at full precision, present dollars to the nearest dollar
and percentages to one decimal place, and note when rounding makes a
column not foot exactly.

## Basis, reconciliation, and unavailable values

Confirm the discovered schema's units and cumulative/period basis. Closed cost
and billed-to-date snapshots must not be summed across months. Period revenue
and profit may be summed over the requested window. Convert cents exactly once.
A portfolio month is actual only if all included contributions are actual;
otherwise label mixed, forecast, or unknown from the evidence. A single latest
close does not establish a common portfolio cutoff. Reconcile project subtotals
to portfolio totals for the same filters and weighting before claiming coverage.
Never multiply an already weighted amount by probability again.

Use each close's contract value as of that close, not today's approved total
for both periods. Missing historical contract evidence makes the historical
margin or attribution unavailable. For C0/E0 (earlier contract/EAC) and C1/E1
(later), an explicit contract-first bridge is:
- contract effect = ((1 - E0/C1) - (1 - E0/C0)) * 100 points;
- EAC effect = ((1 - E1/C1) - (1 - E0/C1)) * 100 points.
These sum to the margin movement; ordering is an attribution convention, not
proof of a business cause. Actual-cost corrections alone do not change
completion margin unless contract value or EAC also changes.

If EAC is zero or negative, completion, earned revenue and billing position
are unavailable. If contract value is zero or negative, margin is unavailable.
Keep available inputs visible. Flag cost above EAC rather than silently capping
completion at 100%. Do not impute missing inputs or unexplained causes.

### Local calculator input

Run `python3 scripts/forecast_math.py input.json` from this skill directory.
The input is normalized local JSON, not an MCP schema: `project_id`, `period_id`,
`contract_dollars` (approved value as of this period), `cost_to_date_cents`,
`billed_to_date_cents`, and `eac_cents`. All amounts are required finite numbers;
missing values are errors. Output money is in dollars, percentages in percent
units, undefined measures are null with warnings. It has no network or writes.

# Report templates

Use the template that matches the question. Lead with the finding, keep
the first screen readable without the detail tables, label every number as
actual or forecast, and cite the project id and period id each figure came
from. Show each formula once, with its inputs, in a "Formulas" section at
the end.

## Portfolio summary

For portfolio-forecast questions from `listForecastPeriods`.

```
# Forecast: <tab> revenue and profit, <window>

**Finding:** <one line: the total, and the one thing that stands out>
**Population:** <tab> (<n> projects; source: listForecastPeriods metadata)
**Actual through:** <last closed month>; later months are forecast.
**Weighting:** unweighted | probability-weighted (only if asked)

## Totals
| Period | Revenue | Profit | Margin | Actual/forecast |
|---|---|---|---|---|
| <month or quarter> | | | | |
| **Total** | | | | |

## By project (only when a breakdown was requested)
| Project | Id | Revenue | Profit | Margin | Notes |
|---|---|---|---|---|---|

## Flags
One bullet per project that crossed the user's threshold, with the
numbers and the period ids behind them.

## Sources
Which call produced each table; which months are actual (closed periods)
and which are forecast; any tab or window assumption the user should
confirm.

## Formulas
Each formula used, once, with the inputs from one row.
```

## Project health card

For single-project questions, built from contracts, change orders, budget,
and billing periods.

```
# Project health: <project name> (<project id>)

**Finding:** <one line: percent complete, margin, and billing position>
**Stage:** <stage> | **Start:** <date> | **End:** <date> (getProjectById)
**Latest close:** <month> (<closed period id>) | **Forecast through:** <month>

| Measure | Value | Actual/forecast | Derived from |
|---|---|---|---|
| Contract value | | actual | prime contract + approved COs (ids) |
| Estimate at completion | | forecast | closed period <id> |
| Actual cost to date | | actual | closed period <id> |
| Percent complete (cost-to-cost) | | derived | cost / EAC |
| Earned revenue | | derived | % complete x contract value |
| Billed to date | | actual | closed period <id> |
| Over/(under) billing | | derived | billed - earned |
| Estimated profit at completion | | forecast | contract value - EAC |
| Margin | | forecast | profit / contract value |
| Margin at prior close | | actual | closed period <id> |
| Margin movement | | derived | now - prior, in points |

## Period detail (when asked)
| Month | Type | Revenue | Cost | Margin | Period id |
|---|---|---|---|---|---|
Preserve `type`, `month_label`, and margin values as returned.

## Read
Two to four sentences on trend, margin, profit, and billing position.
Name what the data does not explain and who to ask.

## Sources / Formulas
```

## Margin bridge

For "why did margin move" questions. One bridge per project.

```
# Margin bridge: <project name> (<project id>), <earlier close> to <later close>

**Finding:** margin moved <+/-x.x> points, from <a%> to <b%>; <the one driver>.

| Step | Amount | Margin effect | Source |
|---|---|---|---|
| Margin at <earlier month> | | a% | closed period <id> |
| Approved change orders added | +$ | +x.x pts | change order ids |
| EAC change (cost growth or savings) | +/-$ | -x.x pts | closed period <id> vs <id> |
| Correction to prior actuals (if any) | | | |
| Margin at <later month> | | b% | closed period <id> |

**Unexplained:** <what the records do not say, and who can say it>

## Formulas
```

The steps must reconcile: earlier margin plus the effects equals the later
margin, within rounding. If they do not, say so and show the residual.

## Over/under billing table

For billing-position questions across several projects.

```
# Over/under billing: <population>, as of <latest close>

**Finding:** <net position across the set, and the largest single item>

| Project | Id | Close | % complete | Earned revenue | Billed to date | Over/(under) | Period id |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
| **Net** | | | | | | | |

## Read
Which positions are routine (early-job mobilization overbilling) and which
warrant a look (underbilling on a job with pending change orders; overbilling
that will unwind when EAC rises).

## Sources / Formulas
```

## Dry run (before any mutation)

```
## Dry run: <operation> on <project name> (<project id>)

| Field | Current | Proposed | Why / source |
|---|---|---|---|
| month | (none) | 2027-02 | next required month after <latest close id> |
| actual cost to date | (none) | $ | user's February cost report |
| billed to date | (none) | $ | pay application 9 (user) |
| EAC | $ (Jan close) | $ | unchanged / user revised because ... |

Sequencing check: first close = start month? / follows latest close? /
within start..forecast end? -> pass | fail (reason)
Effect after close: remaining forecast periods will be reforecast from the
new EAC; start date becomes locked (or is already locked).

Reply "yes" to run this, or tell me what to change.
```

After execution, repeat the table with a "Verified" column populated from
the re-read, not from the values sent.

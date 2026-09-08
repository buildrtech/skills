# Project health: Quarry Annex (syn_qa_92), April 2027 close

**Finding:** Quarry Annex is **50.0% complete** at the April close, carrying an estimated **20.0% margin ($720,000 profit)** on a $3,600,000 contract, and is **underbilled by $100,000** — billings of $1,700,000 sit behind $1,800,000 of earned revenue.

**Latest close:** April 2027 (`syn_qa_apr`) | **Start:** March 2027 | **Forecast through:** September 2027
**Closed months:** March and April 2027 only. May through September are forecast.
**Data source:** the export supplied in the request. No MCP connection exists and none was attempted; nothing was read from or written to any remote system.

All figures are explicitly synthetic.

## Health card

| Measure | Value | Actual / forecast | Derived from |
|---|---|---|---|
| Contract value | $3,600,000 | actual | prime contract $3,400,000 + approved change orders $200,000 (export) |
| Pending change order (excluded) | $150,000 | not counted | pending; excluded until approved |
| Actual cost to date | $1,440,000 | **actual** | closed period `syn_qa_apr`, 144,000,000 cents ÷ 100 |
| Billed to date | $1,700,000 | **actual** | closed period `syn_qa_apr`, 170,000,000 cents ÷ 100 |
| Estimate at completion (EAC) | $2,880,000 | **estimate** | closed period `syn_qa_apr`, 288,000,000 cents ÷ 100 |
| Percent complete (cost-to-cost) | 50.0% | derived | cost to date ÷ EAC |
| Earned revenue | $1,800,000 | derived (rests on an estimate) | % complete × contract value |
| Over/(under) billing | **($100,000) underbilled** | derived | billed to date − earned revenue |
| Estimated profit at completion | $720,000 | **estimate** | contract value − EAC |
| Estimated margin at completion | **20.0%** | **estimate** | profit ÷ contract value |
| Cost to complete | $1,440,000 | estimate | EAC − cost to date |
| Remaining revenue | $1,800,000 | estimate | contract value − earned revenue |
| Margin at prior close (March) | not provided | — | March closed period not in this export |
| Margin movement | **not computable** | — | needs the March closed period's cost, billed and EAC |

### Which figures are actual, and which are not

- **Actual (recorded facts as of the April close):** cost to date $1,440,000, billed to date $1,700,000, and the contract value of $3,600,000 including the $200,000 of approved change orders.
- **Estimate:** the EAC of $2,880,000. Everything that depends on it — percent complete, earned revenue, profit at completion, margin, cost to complete — inherits that estimate. A 20.0% margin is a forecast, not a result.
- **Derived:** percent complete, earned revenue, over/under billing, profit and margin. Each is computed below from the two actuals plus the EAC; none was supplied ready-made.
- **Excluded:** the $150,000 pending change order. It is not in contract value and not in any figure above.

## Formulas, with the inputs used

- **Contract value** = prime contract + approved change orders
  = $3,400,000 + $200,000 = **$3,600,000**
  (The export gives $3,600,000 "including $200,000 of approved change orders", so the prime contract is the $3,400,000 remainder. If your prime contract is not $3,400,000, the split is wrong even though the total is right — worth a check, though it changes none of the figures below.)
- **Percent complete (cost-to-cost)** = actual cost to date ÷ EAC
  = $1,440,000 ÷ $2,880,000 = 0.500 = **50.0%**
- **Earned revenue** = percent complete × contract value
  = 0.500 × $3,600,000 = **$1,800,000**
- **Estimated profit at completion** = contract value − EAC
  = $3,600,000 − $2,880,000 = **$720,000**
- **Margin** = profit at completion ÷ contract value
  = $720,000 ÷ $3,600,000 = 0.200 = **20.0%**
- **Over/under billing** = billed to date − earned revenue
  = $1,700,000 − $1,800,000 = **−$100,000**, i.e. **$100,000 underbilled**
  (Negative is underbilled: costs and estimated earnings in excess of billings, an asset on a WIP schedule.)
- **Remaining revenue** = contract value − earned revenue = $3,600,000 − $1,800,000 = $1,800,000, to be spread across May–September by planned percent complete.

Cents were converted to dollars once, at the point of entry into this table. Every figure divides evenly; no rounding was needed and every column foots.

## Read

The job is exactly at its halfway point on a cost basis and the numbers are unusually round — 50.0% complete, EAC at exactly 80% of contract, cost to complete equal to cost to date. That is what a synthetic export looks like; on a real job I would want to know whether the April EAC was genuinely reforecast or simply carried forward from the March close, because a stale EAC makes percent complete drift with spend alone.

The $100,000 underbilling is the item to act on. At 50% complete, being $100,000 behind earned revenue is a cash timing issue, and it sits alongside a $150,000 change order that is pending rather than approved. If work against that pending change order has already been performed, its cost is presumably inside the $1,440,000 spent to date while none of its value is in the $3,600,000 contract — which would understate both percent complete and margin. **This export does not say whether the pending change order's cost is in the EAC**, and that is the single question that most affects the margin figure above. Ask the project manager and the person who prepared the April cost report. If the $150,000 is approved, contract value goes to $3,750,000; the margin effect then depends on how much cost the EAC already carries for that work, which the export does not tell us.

Also missing here: the March close. Margin fade or gain over the first two months of the job is the normal early-warning signal, and it cannot be computed without March's cost, billed and EAC.

This is a forecast review, not an accounting close or a revenue recognition opinion. Percent-complete recognition and WIP schedule treatment are your accountant's call.

## Your request to close June: I cannot prepare it, and here is why

**No dry run is prepared and nothing is proposed for execution.** Two separate blockers stop it, and neither can be worked around by estimating.

### Blocker 1 — sequencing: May is the next required month, not June

Closed periods must be contiguous, starting at the project's start month:

| Check | Result |
|---|---|
| First close = project start month (March 2027)? | pass — March is closed |
| June immediately follows the latest close? | **fail** — latest close is April 2027 (`syn_qa_apr`); the next required month is **May 2027** |
| June falls within start month through last forecast month (Mar–Sep 2027)? | pass |

Closing June would leave a gap at May. Gaps are not permitted, and I will not fill May with an estimate — you said you have no May actuals, so the honest state of May is "not closed", not a guess.

### Blocker 2 — basis: the June figures are period-only, not cumulative

A closed period records **cumulative cost to date** and **cumulative billed to date** as of that month. You supplied June-*only* amounts:

| Figure you gave | Basis given | Basis required |
|---|---|---|
| June cost $90,000 | month only | cumulative cost to date through June |
| June billings $110,000 | month only | cumulative billed to date through June |
| June EAC $2,880,000 | point in time | point in time — **usable as-is**, and unchanged from the April close |

These cannot be converted without May. Cumulative June cost would be $1,440,000 (April) + May cost + $90,000, and cumulative June billings $1,700,000 + May billings + $110,000. May is the unknown in both, so neither total can be produced. I am not going to treat the June-only figures as if they were cumulative — doing so would post a June cost to date of $90,000 against $1,440,000 already spent and corrupt every downstream forecast month.

### What I need to close June

Give me these five figures and I will prepare a dry run for **two** closed periods, May then June, in that order:

1. May 2027 cumulative cost to date
2. May 2027 cumulative billed to date
3. May 2027 EAC as of the May close
4. June 2027 cumulative cost to date (or May's cumulatives, from which the $90,000 and $110,000 you already gave will roll forward)
5. June 2027 cumulative billed to date (same)

June's EAC of $2,880,000 is already in hand.

If instead you want to close **only May**, I need items 1–3 alone and can prepare that dry run immediately.

### One thing to know before either close

The project's start date is **already locked**. Closed periods exist for March and April, and once any closed period exists the construction start date cannot be changed; unlocking requires deleting closed periods latest-first, one at a time, on explicit instruction. The end date can still move, but not earlier than the latest close plus trailing forecast months.

Each close also reforecasts every later month from the new EAC, so closing May and June will rewrite the July–September forecast periods. Since the June EAC you gave matches the April EAC exactly, that reforecast will move percent complete only through the new cost figures — another reason to confirm the EAC was actually revisited in May and June rather than carried forward.

## Sources

- Everything above comes from the request's synthetic export for Quarry Annex (`syn_qa_92`), April close (`syn_qa_apr`). No other file, project, or period was read.
- No MCP connection exists for this task, so no `search` or `execute` call was made and no operation (`listFinancialsClosedPeriods`, `createFinancialsClosedPeriod`, or any other) was run.
- Nothing was written. No period was closed, reopened, edited or deleted.

# Project health: Quarry Annex (syn_qa_92), April 2027 close

**Finding:** At the April close Quarry Annex is **50.0% complete**, has earned
**$1,800,000** of revenue against **$3,600,000** of contract value, carries an
estimated **20.0% margin ($720,000 profit) at completion**, and is
**underbilled by $100,000** ($1,700,000 billed against $1,800,000 earned).

**Requested June close: not prepared.** May 2027 is not closed, so June is not
the next available month, and the June figures supplied are month-only amounts
where a close needs cumulative balances. Details and what is needed are in
"June close request" below.

**Evidence basis:** offline synthetic export only. No Buildr MCP connection
exists in this session, so nothing was read from or written to a live account.
All ids (`syn_qa_92`, `syn_qa_apr`) are the export's own placeholders. The
arithmetic below was checked with the skill's local calculator
(`scripts/forecast_math.py`, no network, no writes); its input snapshot is saved
alongside this file as `apr-close-input.json`.

**Project window:** started March 2027; forecasts run through September 2027.
March and April 2027 are the only closed months (stated by you; not verifiable
from any other record in this export).

## Measures

| Measure | Value | Actual / forecast | Derived from |
|---|---|---|---|
| Contract value | $3,600,000 | actual (as of April) | prime contract $3,400,000 + $200,000 approved change orders, per your April statement |
| Pending change order (excluded) | $150,000 | not counted | pending, excluded from contract value until approved |
| Actual cost to date | $1,440,000 | actual | April close `syn_qa_apr`, 144,000,000 cents / 100 |
| Billed to date | $1,700,000 | actual | April close `syn_qa_apr`, 170,000,000 cents / 100 |
| Estimate at completion (EAC) | $2,880,000 | **estimate** | April close `syn_qa_apr`, 288,000,000 cents / 100 |
| Percent complete (cost-to-cost) | 50.0% | derived (actual cost ÷ estimated EAC) | cost to date ÷ EAC |
| Earned revenue | $1,800,000 | derived (part actual, part estimate) | % complete × contract value |
| Estimated profit at completion | $720,000 | **estimate** | contract value − EAC |
| Margin at completion | 20.0% | **estimate** | profit ÷ contract value |
| Over/(under) billing | **($100,000) underbilled** | derived | billed to date − earned revenue |
| Margin at prior (March) close | not available | — | no March contract value, cost, billed, or EAC supplied |
| Margin movement Mar → Apr | not available | — | requires the March close figures above |

Cents were converted to dollars exactly once, at the point of entry above.
The $3,400,000 prime contract is inferred by subtracting the $200,000 of
approved change orders you named from the $3,600,000 contract total; the export
does not carry a separate prime-contract record. That split does not affect any
figure in this review, because every formula uses the $3,600,000 total.

## Arithmetic

- **Contract value** = prime contract + approved change orders
  = $3,400,000 + $200,000 = **$3,600,000**.
  The $150,000 pending change order is excluded.
- **Percent complete (cost-to-cost)** = actual cost to date ÷ EAC
  = $1,440,000 ÷ $2,880,000 = 0.500 = **50.0%**.
- **Earned revenue** = percent complete × contract value
  = 0.500 × $3,600,000 = **$1,800,000**.
- **Estimated profit at completion** = contract value − EAC
  = $3,600,000 − $2,880,000 = **$720,000**.
- **Margin** = estimated profit ÷ contract value
  = $720,000 ÷ $3,600,000 = 0.200 = **20.0%**.
- **Over/under billing** = billed to date − earned revenue
  = $1,700,000 − $1,800,000 = **−$100,000**, i.e. $100,000 **underbilled**
  (an asset on a WIP schedule: costs and estimated earnings in excess of
  billings).
- **Remaining revenue** = contract value − earned revenue
  = $3,600,000 − $1,800,000 = **$1,800,000** across May–September 2027.
- **Remaining cost to complete** = EAC − actual cost to date
  = $2,880,000 − $1,440,000 = **$1,440,000**, an estimate.

Every figure rounds exactly; no column is off by rounding.

## Which figures are actual, which are estimates

- **Actual (recorded):** cost to date $1,440,000, billed to date $1,700,000,
  contract value $3,600,000 including the $200,000 of approved change orders.
- **Estimate:** EAC $2,880,000, and therefore estimated profit at completion
  $720,000 and margin 20.0%. EAC stays an estimate even though April is a
  closed period — closing a month records what was spent and billed, it does
  not settle what the job will finally cost.
- **Derived (an actual divided by an estimate, so partly estimated):** percent
  complete 50.0%, earned revenue $1,800,000, and the $100,000 underbilling that
  follows from earned revenue. If the EAC moves, all three move without any new
  work being put in place.
- **Not available from this export:** March close figures, so no margin trend
  and no margin bridge; May 2027 actuals; the reason behind the current EAC;
  the planned percent complete on the May–September forecast periods; and any
  billing-period rows, so the month-by-month revenue/cost/margin table cannot
  be shown. Anything after April 2027 is forecast.

## Read

Half the estimated cost is spent and half the contract is earned, with a
$720,000 estimated profit still intact at 20.0%. The one live item is cash: at
50% complete the job is $100,000 behind on billings, about 5.6% of the revenue
earned so far. Underbilling this early is a cash and change-order warning sign
rather than a margin problem, and the natural questions are whether the May
application catches it up and whether unbilled work relates to the pending
$150,000 change order. This export does not answer either — no billing detail,
no change-order dates, no notes. Ask the project manager and whoever prepares
the pay applications.

The pending $150,000 change order is deliberately excluded above. For context
only, if it is later approved and EAC does not move, contract value becomes
$3,750,000, estimated profit $870,000, margin 23.2%, earned revenue at the
current 50.0% completion $1,875,000, and the underbilling widens to $175,000.
That is a sensitivity, not the current position, and it assumes the change order
carries no added cost — which is the assumption most likely to be wrong.

This is a forecast review, not an accounting close, a revenue recognition
opinion, or an approval. Percentage-of-completion treatment and the WIP
schedule are your accountant's call.

## June close request

No dry run is prepared, and nothing was written. Two independent blockers:

**1. June is not the next closable month (sequencing).** Closed periods must be
contiguous from the project start month with no gaps. March and April 2027 are
closed, so the next required month is **May 2027**. Closing June while May is
open would leave a gap, which the model does not allow. You said you have no May
actuals yet, so the sequence cannot be built and I have prepared nothing rather
than a partial or gap-filling sequence. I will not estimate May from the June
figures.

**2. The June amounts supplied are month-only, not cumulative.** A close records
cumulative cost to date and cumulative billed to date. You gave June-*only* cost
$90,000 and June-*only* billings $110,000. Those cannot be converted without the
cumulative May balances, which do not exist yet. For the record, the April
cumulative basis is cost $1,440,000 and billed $1,700,000; June cumulative
figures would be April plus all of May plus June, and May is the unknown.

The June EAC you supplied, $2,880,000, is unchanged from the April close.

**To close May, then June, send:**

| Month | Needed | Status |
|---|---|---|
| May 2027 | cumulative cost to date, cumulative billed to date, EAC as of May | all three missing |
| June 2027 | cumulative cost to date, cumulative billed to date, EAC as of June ($2,880,000 confirmed) | two cumulative balances missing |

If your source system reports monthly rather than cumulative amounts, send the
May and June monthly cost and billings and I will add them to the April
cumulative basis and show that addition explicitly in the dry run before
anything is written. Both months fall inside March–September 2027, so once the
balances exist the window test passes.

Two things to know before the first of these closes goes in: closing May will
reforecast every later month from the May EAC, and the project's construction
start date is already locked by the existing March close (unlocking it would
mean deleting closed periods latest-first, on explicit instruction only).

## Sources

- April figures, contract value, change-order status, project dates, and the
  March/April close state: your request, treated as the synthetic export. No
  other record in this workspace carries them.
- Formulas, sequencing rules, units, and labeling conventions:
  `references/forecast-model.md` and `references/glossary.md` in the
  financial-forecasting skill.
- Arithmetic check: `scripts/forecast_math.py` on `output/apr-close-input.json`
  — completion 50.0%, earned $1,800,000, margin 20.0%, profit $720,000,
  over/under −$100,000, no warnings. Offline arithmetic replay; not a live MCP
  test.
- No Buildr MCP connection was available, none was attempted, and no mutation
  was prepared or run.

Next step if useful: the March close figures would let me run the margin bridge
from March to April and tell you whether the 20.0% is holding, fading, or
improving.
